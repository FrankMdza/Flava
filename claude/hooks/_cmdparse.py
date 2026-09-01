#!/usr/bin/env python3
"""Shell-line parsing shared by the PreToolUse guards.

Golden rule: **parse, don't regex**. A `grep -E 'push.*force'` is evaded by
`git push --fo\\rce`, by `$(echo git) push -f`, or by putting the push in the second
leg of an `&&`. This module splits the line into simple commands while respecting
quotes, recurses into `$(...)` and backticks, and returns argv already tokenized by
shlex.

Anything that cannot be resolved statically (the executable name comes out of a
substitution) is marked with the SUBST sentinel, and the guards treat it as
"this could be my binary" — fail-closed.

Heredoc bodies are data, not commands, and are removed before any of that happens. A
document written with `cat > notes.md <<'EOF'` used to be parsed line by line as if it
were a script, and prose blocked itself. Markdown backticks looked like command
substitution, and the words after them looked like its arguments. With an unquoted `<<EOF`
the shell really does expand $(…) and backticks inside the body, so those keep being
scanned and the rest of the body is dropped.
"""

import json
import os
import re
import shlex
import sys

# Sentinel for a token whose value comes from $(...) or `...` and is not known statically.
SUBST = "\x00SUBST"

# If a live check proves `exit 2` no longer denies in your Claude Code version, set this
# to True: the guards will additionally emit the JSON decision on stdout.
# Verified on 2.1.220, where the embedded docs say
#   PreToolUse -> "Exit code 2 - show stderr to model and block tool call"
EMIT_JSON_DECISION = False

ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

# Wrappers that get stripped to reach the real command.
WRAPPERS = {
    "env", "sudo", "doas", "nohup", "time", "command", "builtin", "exec",
    "stdbuf", "nice", "ionice", "setsid", "timeout", "xargs", "nice",
}

SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "busybox"}

_DURATION = re.compile(r"^[0-9]+(\.[0-9]+)?[smhd]?$")


# --------------------------------------------------------------------- scanning


def _match_paren(text, start):
    """`start` points at the first character after `$(`. Returns (inner, index_after_close)."""
    depth = 1
    i = start
    quote = None
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\" and quote == '"' and i + 1 < len(text):
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            i += 1
            continue
        if ch == "\\":
            i += 2
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[start:i], i + 1
        i += 1
    return text[start:], len(text)


def _match_backtick(text, start):
    i = start
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "`":
            return text[start:i], i + 1
        i += 1
    return text[start:], len(text)


# --------------------------------------------------------------------- heredocs

# What ends a bare heredoc delimiter word.
_DELIM_END = set(" \t\n;&|<>()")


def _heredoc_op(text, i):
    """`i` points at the `<<` of a heredoc redirection.

    Returns (delimiter, expand, dash, index_after_the_word), or None if what follows is
    not a delimiter. `expand` is True only for a bare delimiter: `<<'EOF'`, `<<"EOF"` and
    `<<\\EOF` all make the body literal.
    """
    n = len(text)
    j = i + 2
    dash = False
    if j < n and text[j] == "-":
        dash = True
        j += 1
    while j < n and text[j] in " \t":
        j += 1

    word = []
    expand = True
    while j < n:
        ch = text[j]
        if ch in ("'", '"'):
            close = text.find(ch, j + 1)
            if close == -1:
                return None
            expand = False
            word.append(text[j + 1:close])
            j = close + 1
            continue
        if ch == "\\" and j + 1 < n:
            expand = False
            word.append(text[j + 1])
            j += 2
            continue
        if ch in _DELIM_END:
            break
        word.append(ch)
        j += 1

    delimiter = "".join(word)
    return (delimiter, expand, dash, j) if delimiter else None


def _substitutions(text):
    """Inner text of every $(…) and `…` in a chunk with no quoting rules of its own."""
    found = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\\" and i + 1 < n:
            i += 2
            continue
        if ch == "$" and text.startswith("((", i + 1):
            _, i = _match_paren(text, i + 2)  # arithmetic, not a command
            continue
        if ch == "$" and i + 1 < n and text[i + 1] == "(":
            inner, i = _match_paren(text, i + 2)
            found.append(inner)
            continue
        if ch == "`":
            inner, i = _match_backtick(text, i + 1)
            found.append(inner)
            continue
        i += 1
    return found


def _feeds_a_shell(line):
    """True if the heredoc on this line ends up as stdin of a shell.

    `bash <<EOF` and `cat <<EOF | bash` run the body as a script, so it is code and has
    to be scanned. Only the last command of the line matters: that is the one the body
    reaches.
    """
    segments = split_segments(line)
    if not segments:
        return False
    argv = to_argv(segments[-1])
    while argv:
        head = argv[0]
        if ENV_ASSIGN.match(head):
            argv.pop(0)
            continue
        base = os.path.basename(head).lower()
        if base in WRAPPERS:
            argv.pop(0)
            while argv and (argv[0].startswith("-") or _DURATION.match(argv[0])):
                argv.pop(0)
            continue
        return base in SHELLS
    return False


def _consume_bodies(text, i, pending, sources, script):
    """Skip the bodies of the heredocs opened on the line that just ended.

    Bash matches the terminator against the whole line, so a line with anything else on
    it does not close the body. An unterminated heredoc runs to the end of the input,
    here as in bash: everything after it is data that never gets executed.
    """
    n = len(text)
    for delimiter, expand, dash in pending:
        body = []
        while i < n:
            eol = text.find("\n", i)
            line = text[i:eol] if eol != -1 else text[i:]
            candidate = line.lstrip("\t") if dash else line
            if candidate.rstrip("\r") == delimiter:
                i = n if eol == -1 else eol + 1
                break
            body.append(line)
            if eol == -1:
                i = n
                break
            i = eol + 1
        if not body:
            continue
        if script:
            sources.append("\n".join(body))
        elif expand:
            sources.extend(_substitutions("\n".join(body)))
    return i


def _strip_heredocs(raw, seen=None):
    """Remove heredoc bodies from the line.

    Returns the line without them, plus the substitutions found inside the bodies of
    unquoted heredocs, which the shell does execute. `seen` collects (delimiter, expand)
    for callers that only want to know what kind of heredoc was there.
    """
    if "<<" not in raw:
        return raw, []

    out = []
    sources = []
    pending = []
    line_start = 0
    quote = None
    i = 0
    n = len(raw)

    while i < n:
        ch = raw[i]

        if quote:
            if ch == "\\" and quote == '"' and i + 1 < n:
                out.append(raw[i:i + 2])
                i += 2
                continue
            out.append(ch)
            if ch == quote:
                quote = None
            i += 1
            continue

        if ch == "\\" and i + 1 < n:
            out.append(raw[i:i + 2])
            i += 2
            continue

        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            i += 1
            continue

        # `$(( 1 << 2 ))` is a left shift, not a heredoc. Copy arithmetic through whole.
        if ch == "$" and raw.startswith("((", i + 1):
            _, j = _match_paren(raw, i + 2)
            out.append(raw[i:j])
            i = j
            continue

        if ch == "<" and raw.startswith("<<", i) and not raw.startswith("<<<", i):
            parsed = _heredoc_op(raw, i)
            if parsed:
                delimiter, expand, dash, j = parsed
                pending.append((delimiter, expand, dash))
                if seen is not None:
                    seen.append((delimiter, expand))
                out.append(" ")  # the redirection goes, the command around it stays
                i = j
                continue

        if ch == "\n":
            line = "".join(out[line_start:])
            out.append("\n")
            line_start = len(out)
            i += 1
            if pending:
                i = _consume_bodies(raw, i, pending, sources, _feeds_a_shell(line))
                pending = []
            continue

        out.append(ch)
        i += 1

    return "".join(out), sources


def has_unquoted_heredoc(raw):
    """True if the line opens a heredoc whose body the shell expands."""
    if not isinstance(raw, str) or "<<" not in raw:
        return False
    seen = []
    _strip_heredocs(raw, seen)
    return any(expand for _, expand in seen)


# --------------------------------------------------------------------- splitting


def split_segments(raw):
    """Split the line into simple commands.

    Splits on `;` `&&` `||` `|` `&` and newlines without cutting inside quotes.
    The inside of `$(...)` and backticks comes back as its own segment, and the outer
    command gets a SUBST token in its place.
    """
    if not isinstance(raw, str) or not raw.strip():
        return []

    raw, heredoc_sources = _strip_heredocs(raw)

    segments = []
    buf = []
    quote = None
    i = 0
    n = len(raw)

    def flush():
        text = "".join(buf).strip()
        del buf[:]
        if text:
            segments.append(text)

    while i < n:
        ch = raw[i]

        if quote == "'":
            buf.append(ch)
            if ch == "'":
                quote = None
            i += 1
            continue

        if quote == '"':
            if ch == "\\" and i + 1 < n:
                buf.append(raw[i:i + 2])
                i += 2
                continue
            if ch == "$" and i + 1 < n and raw[i + 1] == "(":
                inner, j = _match_paren(raw, i + 2)
                if i + 2 < n and raw[i + 2] == "(":
                    buf.append("0")  # $((…)) is arithmetic: yields a number, not a command
                else:
                    segments.extend(split_segments(inner))
                    buf.append(SUBST)
                i = j
                continue
            if ch == "`":
                inner, j = _match_backtick(raw, i + 1)
                segments.extend(split_segments(inner))
                buf.append(SUBST)
                i = j
                continue
            buf.append(ch)
            if ch == '"':
                quote = None
            i += 1
            continue

        # outside quotes
        if ch == "\\" and i + 1 < n:
            buf.append(raw[i:i + 2])
            i += 2
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if ch == "$" and i + 1 < n and raw[i + 1] == "(":
            inner, j = _match_paren(raw, i + 2)
            if i + 2 < n and raw[i + 2] == "(":
                # $((…)) is ARITHMETIC expansion, not command substitution. Treating it as
                # a subshell made the resulting SUBST token trip the aws fail-closed rule
                # against the garbage inside ('aws / 4'). A real false positive.
                buf.append(" 0 ")
            else:
                segments.extend(split_segments(inner))
                buf.append(" " + SUBST + " ")
            i = j
            continue
        if ch == "`":
            inner, j = _match_backtick(raw, i + 1)
            segments.extend(split_segments(inner))
            buf.append(" " + SUBST + " ")
            i = j
            continue
        if ch in ";\n&|":
            flush()
            while i < n and raw[i] in ";\n&|":
                i += 1
            continue

        buf.append(ch)
        i += 1

    flush()
    for source in heredoc_sources:
        segments.extend(split_segments(source))
    return segments


def to_argv(segment):
    """shlex in posix mode: resolves quotes and escapes (`--fo\\rce` -> `--force`)."""
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        try:
            lex = shlex.shlex(segment, posix=True)
            lex.whitespace_split = True
            return list(lex)
        except ValueError:
            return segment.split()


def _normalize(argv, depth):
    """Drop environment assignments and wrappers; recurse into `bash -c '...'`."""
    argv = list(argv)
    while argv:
        head = argv[0]
        if ENV_ASSIGN.match(head):
            argv.pop(0)
            continue

        base = os.path.basename(head).lower()

        if base in SHELLS:
            for k in range(1, len(argv)):
                if argv[k] in ("-c", "-lc", "-ic", "--command") and k + 1 < len(argv):
                    return commands(argv[k + 1], depth + 1)
            break

        if base in WRAPPERS:
            argv.pop(0)
            # drop the wrapper's own flags and durations (`timeout 30`, `nice -n 10`)
            while argv and (argv[0].startswith("-") or _DURATION.match(argv[0])):
                argv.pop(0)
            continue

        break

    return [argv] if argv else []


def commands(raw, depth=0):
    """Return the argv list of every simple command on the line."""
    if depth > 6:
        return []
    out = []
    for segment in split_segments(raw):
        out.extend(_normalize(to_argv(segment), depth))
    return out


def starts_of(argv, name):
    """Indices where a `name` command could start.

    SUBST counts: if the executable comes from a substitution it could be anything, so it
    is evaluated as if it were `name`. That is what catches `$(echo git) push -f`.
    And it looks at every position, not just argv[0], to cover wrappers we did not model.
    """
    hits = []
    for i, token in enumerate(argv):
        if token == SUBST:
            hits.append(i)
            continue
        base = os.path.basename(token).lower()
        if base == name or base == name + ".exe":
            hits.append(i)
    return hits


# ------------------------------------------------------------------------- hook I/O


def read_hook_input():
    try:
        return json.loads(sys.stdin.read() or "{}") or {}
    except Exception:
        return {}


def bash_command(payload):
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    value = tool_input.get("command")
    return value if isinstance(value, str) else ""


def deny(reason):
    """Deny the call. stderr + exit 2 is the PreToolUse contract as of 2.1.220."""
    if EMIT_JSON_DECISION:
        sys.stdout.write(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))
    sys.stderr.write(reason + "\n")
    sys.exit(2)


def allow():
    sys.exit(0)


def run(checker, payload=None, panic=None):
    """Shared wrapper.

    If a guard crashes it allows by default: a bug must not leave the session without Bash.
    The exception is `panic`, a raw last-resort pattern — if the command matches something
    unmistakably destructive, safety beats convenience.
    """
    payload = payload if payload is not None else read_hook_input()
    try:
        reason = checker(payload)
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        raw = bash_command(payload)
        if panic is not None and raw and panic.search(raw):
            deny("The guard crashed ({0}) but the command matches the panic pattern. "
                 "Blocked as a precaution.".format(exc))
        sys.stderr.write("guard error (allowing by default): {0}\n".format(exc))
        sys.exit(0)
    if reason:
        if has_unquoted_heredoc(bash_command(payload)):
            reason += ("\nIf this came from the heredoc body: an unquoted <<EOF lets the shell "
                       "expand $(...) and backticks inside it. Quote the delimiter, <<'EOF', "
                       "and the body is left alone.")
        deny(reason)
    allow()

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


# --------------------------------------------------------------------- splitting


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


def split_segments(raw):
    """Split the line into simple commands.

    Splits on `;` `&&` `||` `|` `&` and newlines without cutting inside quotes.
    The inside of `$(...)` and backticks comes back as its own segment, and the outer
    command gets a SUBST token in its place.
    """
    if not isinstance(raw, str) or not raw.strip():
        return []

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
        deny(reason)
    allow()

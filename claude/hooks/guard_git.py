#!/usr/bin/env python3
"""PreToolUse/Bash — blocks destructive git and pushes to protected branches.

Blocks:
  · force push in any form (--force, -f, clusters like -uf, --force-with-lease,
    --force-if-includes, refspec +src:dst)
  · push whose destination is dev / main / master (incl. HEAD:main, `origin dev`,
    refs/heads/main)
  · push --mirror / --all (they move every ref at once without naming any)
  · --force/-f on clean, checkout, rm, switch, restore, worktree, submodule; branch -D
  · direct ref writes: update-ref and symbolic-ref in their write form
  · deleting the safety net: reflog expire, gc --prune=<date>, stash clear/drop
  · reset --hard (discards uncommitted changes and moves the branch)
  · git config on alias.* (an alias can wrap a force push)
  · git remote set-url (repointing the remote evades the protected-branch check)
  · unknown subcommands in primary position (possible aliases)

On update-ref: `git branch -D x` was blocked while `git update-ref -d refs/heads/x` did
exactly the same thing with nobody watching. Blocking the porcelain and leaving the
equivalent plumbing open is not a guardrail, it is a sign. Verified live on 2026-08-19:
the branch disappeared just the same.

The block is per repo, not per cwd: global options (-C, --git-dir, …) are consumed before
reading the subcommand.

Edit PROTECTED and REMOTES below to match your own branch conventions.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _cmdparse import SUBST, bash_command, commands, run, starts_of  # noqa: E402

PROTECTED = {"dev", "main", "master"}
REMOTES = {"origin", "upstream"}

FORCE_FLAGS = {"--force", "-f", "--force-with-lease", "--force-if-includes"}
# short-flag cluster: -f, -uf, -fu … but not --follow-tags or --format=x
SHORT_FORCE = re.compile(r"^-[a-zA-Z]*f[a-zA-Z]*$")

GLOBAL_VALUE_OPTS = {
    "-C", "-c", "--git-dir", "--work-tree", "--exec-path", "--namespace", "--super-prefix",
}

DESTRUCTIVE_WITH_FORCE = {
    "clean", "checkout", "rm", "switch", "restore", "worktree", "submodule",
}

# `push --mirror` deletes every remote ref that does not exist locally; `--all` pushes
# every local branch at once, so it reaches dev/main without ever naming them.
PUSH_MASS_FLAGS = {"--mirror", "--all"}

KNOWN_SUBCOMMANDS = {
    "add", "am", "annotate", "apply", "archive", "bisect", "blame", "branch", "bundle",
    "cat-file", "check-ignore", "checkout", "cherry", "cherry-pick", "clean", "clone",
    "commit", "config", "count-objects", "describe", "diff", "diff-tree", "difftool",
    "fetch", "for-each-ref", "format-patch", "fsck", "gc", "grep", "hash-object", "help",
    "init", "log", "ls-files", "ls-remote", "ls-tree", "maintenance", "merge", "merge-base",
    "mergetool", "mv", "name-rev", "notes", "pull", "push", "range-diff", "rebase", "reflog",
    "remote", "repack", "replace", "request-pull", "rerere", "reset", "restore", "revert",
    "rm", "rev-list", "rev-parse", "shortlog", "show", "show-branch", "show-ref",
    "sparse-checkout", "stash", "status", "stripspace", "submodule", "subtree", "switch",
    "symbolic-ref", "tag", "update-ref", "var", "verify-commit", "version", "whatchanged",
    "worktree",
}

# Safety net for when the parser itself blows up on a weird line.
PANIC = re.compile(
    r"push[^\n]*(--force|--force-with-lease|-f\b)|push[^\n]*:(dev|main|master)\b"
    r"|\bupdate-ref\b|push[^\n]*--mirror\b|reflog[^\n]*expire\b|reset[^\n]*--hard\b"
)


def _non_flags(args):
    return [a for a in args if not a.startswith("-")]


def is_force(token):
    if token in FORCE_FLAGS:
        return True
    if token.startswith("--force-with-lease=") or token.startswith("--force-if-includes"):
        return True
    return bool(SHORT_FORCE.match(token))


def check_push(args):
    for token in args:
        if is_force(token):
            return ("force git push blocked ({0}): it rewrites already published history. "
                    "If you really need it, run it yourself with the ! prefix.".format(token))

    for token in args:
        if token in PUSH_MASS_FLAGS:
            return ("git push {0} blocked: it updates every remote ref at once, so it reaches "
                    "dev/main without naming them; --mirror also deletes anything on the "
                    "remote that does not exist locally.".format(token))

    non_flags = [a for a in args if not a.startswith("-")]
    for index, token in enumerate(non_flags):
        if token.startswith("+"):
            return "git push with a forced refspec blocked ('{0}'): the '+' is a hidden force.".format(token)

        if ":" in token:
            dest = token.rsplit(":", 1)[1]
        elif index == 0:
            continue  # this is the remote name
        else:
            dest = token

        if dest == SUBST or SUBST in dest:
            return ("git push to a destination coming from a substitution: I cannot verify "
                    "it is not a protected branch, so I am blocking it.")

        for prefix in ("refs/heads/", "refs/remotes/"):
            if dest.startswith(prefix):
                dest = dest[len(prefix):]

        candidates = {dest.lower()}
        head, _, tail = dest.partition("/")
        if head.lower() in REMOTES and tail:
            candidates.add(tail.lower())

        hit = candidates & PROTECTED
        if hit:
            return ("git push to the protected branch '{0}' blocked: protected branches take "
                    "changes through pull requests. Push a feature branch and open a PR."
                    .format(sorted(hit)[0]))
    return None


def inspect(tokens, full):
    """`full=False` for a git found in a non-primary position: high-confidence rules only,
    so `grep git README` is not flagged as if it were a git command."""
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in GLOBAL_VALUE_OPTS:
            i += 2
            continue
        if token.startswith("--") and "=" in token and token.split("=", 1)[0] in GLOBAL_VALUE_OPTS:
            i += 1
            continue
        if token.startswith("-"):
            i += 1
            continue
        break

    if i >= len(tokens):
        return None

    sub = tokens[i]
    args = tokens[i + 1:]

    if sub == SUBST:
        if not full:
            return None
        return ("git with a subcommand coming from a substitution: I cannot verify it is not "
                "a force push, so I am blocking it.")

    sub = sub.lower()

    if sub == "push":
        return check_push(args)

    if sub in DESTRUCTIVE_WITH_FORCE and any(is_force(a) for a in args):
        return "git {0} with --force/-f blocked: it discards local work with no recovery.".format(sub)

    if sub == "branch" and (("-D" in args) or ("--delete" in args and any(is_force(a) for a in args))):
        return "git branch with a forced delete blocked: -D discards unmerged commits."

    # --- direct ref writes: the plumbing twin of branch -D / push --force ---
    if sub == "update-ref":
        return ("git update-ref blocked: it writes or deletes a ref directly, bypassing both "
                "push and branch and therefore all of their checks. '-d refs/heads/x' is "
                "'branch -D x' under another name, and on a bare repo it amounts to a force push.")

    if sub == "symbolic-ref" and (("-d" in args) or ("--delete" in args) or len(_non_flags(args)) >= 2):
        return ("git symbolic-ref in write form blocked: it repoints HEAD (on a bare repo, the "
                "repository's default branch). To read it use 'git symbolic-ref --short HEAD'.")

    # --- deleting the safety net that makes everything else reversible ---
    if sub == "reflog" and args and args[0].lower() == "expire":
        return ("git reflog expire blocked: the reflog is the only way to undo a reset --hard "
                "or a branch -D. Deleting it turns the recoverable into the unrecoverable.")

    if sub == "gc" and any(a.startswith("--prune=") for a in args):
        return ("git gc --prune=<date> blocked: it removes already-unreachable objects, which "
                "are exactly the ones that rescue a reset or an amend. Plain 'git gc' passes.")

    if sub == "stash" and args and args[0].lower() in ("clear", "drop"):
        return ("git stash {0} blocked: it discards saved work. 'stash', 'stash list' and "
                "'stash pop' still pass.".format(args[0].lower()))

    if sub == "reset" and "--hard" in args:
        return ("git reset --hard blocked: it discards uncommitted changes and moves the branch "
                "in one shot. --soft and --mixed pass; if you want the --hard, run it with the ! prefix.")

    if not full:
        return None

    if sub == "config" and any("alias." in a.lower() for a in args):
        return ("git config on alias.* blocked: an alias can wrap a force push and slip past "
                "this guard.")

    if sub == "remote" and args and args[0].lower() == "set-url":
        return "git remote set-url blocked: repointing the remote evades the protected-branch check."

    if sub not in KNOWN_SUBCOMMANDS:
        return ("'git {0}' is not a known subcommand: it could be an alias wrapping a "
                "destructive operation.".format(sub))

    return None


def check(payload):
    raw = bash_command(payload)
    if not raw:
        return None
    for argv in commands(raw):
        for position in starts_of(argv, "git"):
            verdict = inspect(argv[position + 1:], full=(position == 0))
            if verdict:
                return verdict
    return None


if __name__ == "__main__":
    run(check, panic=PANIC)

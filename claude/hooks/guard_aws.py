#!/usr/bin/env python3
"""PreToolUse/Bash — fail-closed allowlist over the AWS CLI.

Allows read operations only: describe* / list* / get* / search* / lookup*, plus scan, ls
and help. A new verb nobody anticipated is blocked by default, which is the whole point of
being fail-closed.

Two deliberate adjustments:
  · `aws configure …` and `aws sso …` are always denied, even when the subcommand looks
    like a read — they mutate local credentials.
  · `aws codeartifact login` is explicitly allowed. Without it, `uv sync` and `pip install`
    fail on any repo that pulls private packages from CodeArtifact, which makes it the most
    common cause of "fresh clone won't install".

Edit ALLOW_PAIRS to add your own exceptions.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _cmdparse import SUBST, bash_command, commands, run, starts_of  # noqa: E402

READ_PREFIXES = ("describe", "list", "get", "search", "lookup")
READ_EXACT = {"scan", "ls", "help"}

# Denied wholesale: they mutate credentials or local state, whatever they start with.
DENY_SERVICES = {"configure", "sso"}

# Explicit exceptions, as (service, operation).
ALLOW_PAIRS = {("codeartifact", "login")}

GLOBAL_VALUE_OPTS = {
    "--region", "--profile", "--output", "--endpoint-url", "--query", "--ca-bundle",
    "--cli-read-timeout", "--cli-connect-timeout", "--color", "--cli-binary-format",
}

PANIC = re.compile(r"\baws\s+(configure|sso)\b|\baws\s+s3\s+(cp|mv|rm|sync|rb)\b")


def _next_word(tokens, start):
    """Next token from `start` that is neither a flag nor a flag's value."""
    i = start
    while i < len(tokens):
        token = tokens[i]
        if token in GLOBAL_VALUE_OPTS:
            i += 2
            continue
        if token.startswith("-"):
            i += 1
            continue
        return token, i
    return None, i


def inspect(tokens, full):
    service, index = _next_word(tokens, 0)
    if service is None:
        return None  # bare `aws` just prints help

    if service == SUBST:
        return ("aws with a service coming from a substitution: I cannot verify it is a read "
                "operation, so I am blocking it.")

    operation, _ = _next_word(tokens, index + 1)

    if service.lower() in DENY_SERVICES:
        if not full and operation is None:
            return None  # avoids flagging things like `grep aws configure`
        return ("'aws {0}' blocked: it mutates credentials or local state, it is not a read. "
                "If you need it, run it yourself with the ! prefix.".format(service.lower()))

    if operation is None:
        return None  # `aws s3` with no operation prints help

    if operation == SUBST:
        return ("aws with an operation coming from a substitution: I cannot verify it is a "
                "read, so I am blocking it.")

    pair = (service.lower(), operation.lower())
    if pair in ALLOW_PAIRS:
        return None

    op = operation.lower()
    if op in READ_EXACT or op.startswith(READ_PREFIXES):
        return None

    return ("'aws {0} {1}' blocked: the allowlist is fail-closed and only lets through "
            "describe*/list*/get*/search*/lookup*, scan, ls and help. If it is legitimate, "
            "run it yourself with the ! prefix.".format(pair[0], pair[1]))


def check(payload):
    raw = bash_command(payload)
    if not raw:
        return None
    for argv in commands(raw):
        for position in starts_of(argv, "aws"):
            verdict = inspect(argv[position + 1:], full=(position == 0))
            if verdict:
                return verdict
    return None


if __name__ == "__main__":
    run(check, panic=PANIC)

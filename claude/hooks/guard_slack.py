#!/usr/bin/env python3
"""PreToolUse — blocks anything that sends to Slack.

Two surfaces:
  · Slack MCP tools: only reads pass (read/search/list/get). Sending, scheduling, creating
    channels or canvases, even reacting, are all blocked.
  · Bash: curl/wget against hooks.slack.com (webhooks) or against slack.com/api/<method>
    when the method is not a read.

It is fail-closed: an API method missing from the read list gets blocked.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _cmdparse import SUBST, bash_command, commands, run, starts_of  # noqa: E402

MCP_READ_PREFIXES = ("slack_read", "slack_search", "slack_list", "slack_get")

NET_CLIENTS = {"curl", "wget", "http", "https", "httpie", "xh", "wget2"}

WEBHOOK = re.compile(r"hooks\.slack\.com", re.IGNORECASE)
API_CALL = re.compile(r"slack\.com/api/([A-Za-z0-9_.]+)", re.IGNORECASE)

API_READ_METHODS = {
    "auth.test", "conversations.history", "conversations.info", "conversations.list",
    "conversations.members", "conversations.replies", "emoji.list", "files.info",
    "files.list", "reactions.get", "search.messages", "team.info", "users.conversations",
    "users.info", "users.list", "users.profile.get",
}

PANIC = re.compile(r"hooks\.slack\.com|slack\.com/api/(chat\.|files\.upload|conversations\.create)")


def check_mcp(tool_name):
    leaf = tool_name.rsplit("__", 1)[-1].lower()
    if leaf.startswith(MCP_READ_PREFIXES):
        return None
    return ("'{0}' blocked: it writes to Slack. This guard only lets read tools through "
            "(read/search/list/get). If you want to send something, send it yourself.".format(leaf))


def check_bash(raw):
    for argv in commands(raw):
        if not argv:
            continue
        head = argv[0]
        is_client = head == SUBST or os.path.basename(head).lower() in NET_CLIENTS
        if not is_client:
            continue

        blob = " ".join(argv)
        if WEBHOOK.search(blob):
            return ("Blocked: Slack webhook (hooks.slack.com). A webhook can only post, "
                    "never read.")

        for method in API_CALL.findall(blob):
            if method.lower().rstrip(".") not in API_READ_METHODS:
                return ("Blocked: slack.com/api/{0} is not on the read-method list. "
                        "The allowlist is fail-closed.".format(method))
    return None


def check(payload):
    tool_name = payload.get("tool_name") or ""
    if "slack" in tool_name.lower() and tool_name.startswith("mcp__"):
        return check_mcp(tool_name)

    raw = bash_command(payload)
    if not raw:
        return None
    return check_bash(raw)


if __name__ == "__main__":
    run(check, panic=PANIC)

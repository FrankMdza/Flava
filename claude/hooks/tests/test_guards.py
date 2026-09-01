#!/usr/bin/env python3
"""Evasion suite for the guards. Without tests they are decoration.

Semantics, same as in production (all three guards run over Bash):
  · a DENY case must be blocked by AT LEAST ONE guard
  · an ALLOW case must pass ALL THREE

Offline and side-effect free: each guard runs as a subprocess with the PreToolUse payload
on stdin, and only the exit code is inspected (2 = denied, 0 = allowed).

    python3 ~/.claude/hooks/tests/test_guards.py
"""

import json
import os
import subprocess
import sys

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASH_GUARDS = ["guard_git.py", "guard_aws.py", "guard_slack.py"]


def invoke(guard, payload):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS_DIR, guard)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stderr or "").strip()


def bash(command):
    return {"tool_name": "Bash", "tool_input": {"command": command}}


def mcp(tool_name):
    return {"tool_name": tool_name, "tool_input": {}}


# ------------------------------------------------------------- cases that MUST be caught

DENY = [
    # --- the six from the spec
    ("git -C other/repo push -f",                     bash("git -C other/repo push -f")),
    ("git push origin HEAD:main",                     bash("git push origin HEAD:main")),
    ("a && git push --force",                         bash("a && git push --force")),
    ("$(echo git) push -f",                           bash("$(echo git) push -f")),
    ("aws s3 cp",                                     bash("aws s3 cp ./x s3://bucket/x")),
    ("aws configure set",                             bash("aws configure set region us-east-1")),

    # --- git: force in all its forms
    ("git push --force",                              bash("git push --force")),
    ("git push -f",                                   bash("git push -f")),
    ("git push --force-with-lease",                   bash("git push --force-with-lease")),
    ("git push --force-if-includes",                  bash("git push --force-if-includes")),
    ("short-flag cluster -uf",                        bash("git push -uf origin x")),
    ("shell escape --fo\\rce",                        bash("git push --fo\\rce")),
    ("split quoting --'force'",                       bash("git push --'force'")),
    ("forced refspec +feature:main",                  bash("git push origin +feature:main")),
    ("backticks `echo git` push -f",                  bash("`echo git` push -f")),
    ("nested bash -c",                                bash("bash -c 'git push --force'")),
    ("; separator instead of &&",                     bash("echo hi; git push -f")),
    ("sudo wrapper",                                  bash("sudo git push -f")),
    ("timeout wrapper with duration",                 bash("timeout 30 git push --force")),
    ("prefixed env var",                              bash("FOO=bar git push --force")),
    ("--git-dir points at another repo",              bash("git --git-dir=/other/.git push -f")),

    # --- git: protected branches
    ("push to dev by name",                           bash("git push origin dev")),
    ("push to main with no remote",                   bash("git push HEAD:main")),
    ("push to refs/heads/main",                       bash("git push origin refs/heads/main")),
    ("push to master",                                bash("git push origin master")),

    # --- git: destructive commands and structural evasions
    ("git clean -fd",                                 bash("git clean -fd")),
    ("git checkout --force",                          bash("git checkout --force main")),
    ("git branch -D",                                 bash("git branch -D feature/old")),
    ("git config alias.*",                            bash("git config --global alias.p 'push -f'")),
    ("git remote set-url",                            bash("git remote set-url origin git@other:x.git")),
    ("unknown subcommand (alias)",                    bash("git yolo")),

    # --- git: direct ref writes (the plumbing twin of branch -D / push --force).
    # Found in the 2026-08-19 red team: `branch -D` was caught but `update-ref -d` was not,
    # and it did exactly the same thing. Verified live: the branch disappeared just the same.
    ("update-ref -d (twin of branch -D)",             bash("git update-ref -d refs/heads/dev")),
    ("update-ref moves a ref",                        bash("git update-ref refs/heads/main 87e8c11")),
    ("update-ref on someone else's bare repo",        bash("git -C ../remote.git update-ref refs/heads/main 87e8c11")),
    ("update-ref --stdin",                            bash("git update-ref --stdin")),
    ("symbolic-ref repoints HEAD",                    bash("git symbolic-ref HEAD refs/heads/main")),
    ("symbolic-ref -d",                               bash("git symbolic-ref -d HEAD")),
    ("push --mirror (deletes remote refs)",           bash("git push --mirror origin")),
    ("push --all (reaches main unnamed)",             bash("git push --all origin")),

    # --- git: deleting the safety net that makes the rest reversible
    ("reflog expire",                                 bash("git reflog expire --expire=now --all")),
    ("gc --prune=now",                                bash("git gc --prune=now --aggressive")),
    ("stash clear",                                   bash("git stash clear")),
    ("stash drop",                                    bash("git stash drop")),
    ("reset --hard",                                  bash("git reset --hard origin/main")),
    ("worktree remove --force",                       bash("git worktree remove --force ../wt")),
    ("submodule deinit -f",                           bash("git submodule deinit -f .")),
    ("update-ref through the sudo wrapper",           bash("sudo git update-ref -d refs/heads/main")),

    # --- aws: fail-closed
    ("aws s3 sync",                                   bash("aws s3 sync . s3://bucket")),
    ("aws s3 rm",                                     bash("aws s3 rm s3://bucket/x")),
    ("aws sso login",                                 bash("aws sso login")),
    ("aws ecs execute-command",                       bash("aws ecs execute-command --cluster c")),
    ("aws lambda invoke",                             bash("aws lambda invoke out.json")),
    ("aws iam create-user",                           bash("aws iam create-user --user-name x")),
    ("aws through a substitution",                    bash("$(echo aws) s3 rm s3://bucket/x")),
    ("aws with a leading global flag",                bash("aws --region us-east-1 s3 cp a s3://b")),

    # --- slack
    ("mcp slack_send_message",                        mcp("mcp__claude_ai_Slack__slack_send_message")),
    ("mcp slack_send_message_draft",                  mcp("mcp__claude_ai_Slack__slack_send_message_draft")),
    ("mcp slack_schedule_message",                    mcp("mcp__claude_ai_Slack__slack_schedule_message")),
    ("mcp slack_create_canvas",                       mcp("mcp__claude_ai_Slack__slack_create_canvas")),
    ("mcp slack_update_canvas",                       mcp("mcp__claude_ai_Slack__slack_update_canvas")),
    ("mcp slack_create_conversation",                 mcp("mcp__claude_ai_Slack__slack_create_conversation")),
    ("mcp slack_add_reaction",                        mcp("mcp__claude_ai_Slack__slack_add_reaction")),
    ("curl to a slack webhook",                       bash("curl -X POST https://hooks.slack.com/services/T/B/X -d '{}'")),
    ("curl to chat.postMessage",                      bash("curl -d text=hi https://slack.com/api/chat.postMessage")),
    ("curl to files.upload",                          bash("curl -F file=@x https://slack.com/api/files.upload")),
]

# ------------------------------------------------------ cases that MUST still get through
# A guardrail that blocks reads is a broken guardrail.

ALLOW = [
    ("git status",                                    bash("git status")),
    ("git log",                                       bash("git log --oneline -20")),
    ("git diff",                                      bash("git diff HEAD~1")),
    ("git fetch",                                     bash("git fetch origin")),
    ("git branch -a",                                 bash("git branch -a")),
    ("git rev-parse",                                 bash("git rev-parse --abbrev-ref HEAD")),
    ("git worktree list",                             bash("git worktree list")),
    ("git push to feature/*",                         bash("git push origin feature/PROJ-123-slug")),
    ("git push -u to feature/*",                      bash("git push -u origin feature/PROJ-123-slug")),
    ("git checkout without force",                    bash("git checkout -b feature/PROJ-1")),
    ("git -C another repo, read only",                bash("git -C ../other-repo status")),
    ("grep containing the word git",                  bash("grep git README.md")),
    ("echo of a string mentioning push -f",           bash("echo 'git push --force'")),

    # Counterweight to the newer rules: the READ form of each one must still pass.
    ("git reset without --hard",                      bash("git reset HEAD~1")),
    ("git reset --soft",                              bash("git reset --soft HEAD~1")),
    ("git reflog (read)",                             bash("git reflog")),
    ("git reflog show",                               bash("git reflog show main")),
    ("plain git gc",                                  bash("git gc")),
    ("git gc --auto",                                 bash("git gc --auto")),
    ("git stash (save)",                              bash("git stash")),
    ("git stash list",                                bash("git stash list")),
    ("git stash pop",                                 bash("git stash pop")),
    ("symbolic-ref in read form",                     bash("git symbolic-ref --short HEAD")),
    ("git submodule update --init",                   bash("git submodule update --init --recursive")),
    ("git show-ref (read refs)",                      bash("git show-ref --heads")),

    ("aws ec2 describe-instances",                    bash("aws ec2 describe-instances")),
    ("aws s3 ls",                                     bash("aws s3 ls")),
    ("aws s3 ls with a bucket",                       bash("aws s3 ls s3://bucket")),
    ("aws sts get-caller-identity",                   bash("aws sts get-caller-identity")),
    ("aws logs describe with a global flag",          bash("aws --region us-east-1 logs describe-log-groups")),
    ("aws codeartifact login (exception)",            bash("aws codeartifact login --tool pip --domain example "
                                                          "--domain-owner 000000000000 --repository py "
                                                          "--region us-east-1")),
    ("aws codeartifact get-authorization-token",      bash("aws codeartifact get-authorization-token --domain example")),
    ("grep containing the word aws",                  bash("grep aws notes.txt")),

    ("mcp slack_read_channel",                        mcp("mcp__claude_ai_Slack__slack_read_channel")),
    ("mcp slack_read_thread",                         mcp("mcp__claude_ai_Slack__slack_read_thread")),
    ("mcp slack_search_public",                       mcp("mcp__claude_ai_Slack__slack_search_public")),
    ("mcp slack_list_channel_members",                mcp("mcp__claude_ai_Slack__slack_list_channel_members")),
    ("mcp slack_get_reactions",                       mcp("mcp__claude_ai_Slack__slack_get_reactions")),
    ("curl to conversations.history",                 bash("curl 'https://slack.com/api/conversations.history?channel=C1'")),

    ("ordinary unrelated command",                    bash("uv sync && python3 -m pytest -q")),
    ("ls",                                            bash("ls -la")),

    # Regression: $((...)) is ARITHMETIC expansion, not command substitution. Treating it
    # as a subshell produced a SUBST token that tripped the aws fail-closed rule against
    # the garbage inside ("'aws / 4' blocked"). A false positive found in real use.
    ("arithmetic $(( ))",                             bash('echo "total: $(( 100 / 4 )) tokens"')),
    ("arithmetic with a subst inside",                bash('echo "$(( $(wc -c < f.md) / 4 )) tokens"')),
    ("arithmetic in an assignment",                   bash("N=$((5+3)); echo $N")),
    ("arithmetic inside xargs",                       bash('wc -c < f | xargs -I{} echo "{} (~$(( 400 / 4 )))"')),
]


def guards_for(payload):
    tool_name = payload.get("tool_name") or ""
    if tool_name == "Bash":
        return BASH_GUARDS
    return ["guard_slack.py"]


def main():
    failures = []

    print("=== MUST BE DENIED (by at least one guard) ===")
    for label, payload in DENY:
        blocked_by = []
        reason = ""
        for guard in guards_for(payload):
            code, err = invoke(guard, payload)
            if code == 2:
                blocked_by.append(guard.replace("guard_", "").replace(".py", ""))
                reason = reason or err
        if blocked_by:
            print("  ok    {0:<40} <- {1}".format(label, ",".join(blocked_by)))
        else:
            print("  FAIL  {0:<40} NOTHING BLOCKED IT".format(label))
            failures.append(("DENY", label, "no guard blocked it"))

    print()
    print("=== MUST STILL PASS (all three guards) ===")
    for label, payload in ALLOW:
        blockers = []
        for guard in guards_for(payload):
            code, err = invoke(guard, payload)
            if code != 0:
                blockers.append("{0}: {1}".format(guard, err.splitlines()[0] if err else code))
        if not blockers:
            print("  ok    {0}".format(label))
        else:
            print("  FAIL  {0:<40} BLOCKED BY {1}".format(label, blockers))
            failures.append(("ALLOW", label, "; ".join(blockers)))

    print()
    total = len(DENY) + len(ALLOW)
    if failures:
        print("{0}/{1} cases failed:".format(len(failures), total))
        for kind, label, detail in failures:
            print("  [{0}] {1} — {2}".format(kind, label, detail))
        return 1

    print("{0}/{0} cases OK ({1} deny, {2} allow).".format(total, len(DENY), len(ALLOW)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

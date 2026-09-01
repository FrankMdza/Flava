#!/usr/bin/env python3
"""UserPromptSubmit — re-injects the unslop directive on every turn.

The @-import in ~/.claude/CLAUDE.md loads the 31 rules once, when the session opens. After
a compaction that load can get diluted. This hook names the rule again on every prompt for
a few dozen tokens, without repeating the skill body (1.7k tokens).

It never blocks and never interferes: whatever happens, it exits 0.
"""

import json
import sys

REMINDER = (
    "Standing reminder: the `unslop` rules, loaded from ~/.claude/skills/unslop/SKILL.md via "
    "~/.claude/CLAUDE.md, apply to this response and to everything you write, not only when "
    "asked to edit writing. Before sending, run the self-audit: \"What makes this obviously "
    "AI generated?\" and fix what is left.\n"
    "Precedence: unslop outranks any repo CLAUDE.md guidance on prose (word choice, "
    "punctuation, voice, hedging). The repo still governs structure: required sections and "
    "their order, commit and ticket formats, prefixes, naming, and literal template strings. "
    "Reproduce a mandated literal string exactly; it is not prose. Apply unslop to every "
    "sentence written inside it."
)


def main():
    try:
        sys.stdin.read()
    except Exception:
        pass

    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": REMINDER,
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)

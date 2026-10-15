# Global instructions

@~/.claude/skills/unslop/SKILL.md

## Unslop is a standing rule

The `unslop` rules above apply to everything I write, not only when the task is to edit
writing. Prose in code comments, commit messages, PR descriptions, chat replies, and
documents all get the same pass. Before sending anything, run the self-audit: "What makes
this obviously AI generated?" and fix what is left.

## How unslop interacts with a repo's own conventions

`unslop` wins on prose: word choice, punctuation, voice, hedging, sentence rhythm.

The repo wins on structure: required sections and their order, commit and ticket formats,
prefixes, naming, and any literal string a tool parses. Reproduce a mandated literal string
exactly, it is not prose. Still apply unslop to every sentence written inside it.

## When to stop

When a step does not need my opinion, keep going, and put the status note in the same message
as the next action. Stop and ask only if you cannot continue without me, or before anything
destructive or outside the task: deleting data or branches, force-push, push to master, touching
files outside the task's repo, any order on a real trading account. Stops that a skill or a
handoff asks for (approve a plan, a table or a diff) count as necessary.

## Closing a long task

End with three sections, in this order: Pending from me, Changed, Found. Ask the same of every
subagent you launch.

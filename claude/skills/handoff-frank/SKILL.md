---
name: handoff-frank
description: Write a handoff document that closes the current session and continues the same task in a clean one without losing fidelity. Use it when context approaches the compaction or dump zone, or when the user says "handoff", "write the handoff", "let's prep the clear", "I'm running out of context", "I'm going to /clear", "wrap up so we can continue in another session", or asks to continue the work in a new session. Use it ALSO from the other side, to resume: when they say "pick up from the last handoff", "resume the task", "continue where we left off", or give the path of a file in ~/.claude/handoffs/. Also to update an existing handoff for the same task.
---

# Handoff

You produce **one file** that lets a clean session continue the task at the same fidelity,
without dragging the conversation along. Do not narrate the process: write the file and
return the resume line.

## Governing principle: filter by recoverability, not by importance

This is the only rule that keeps a handoff both small and faithful.

| Cheap to recover → **pointer** | Unrecoverable → **write it down** |
|---|---|
| File contents | Why X was chosen over Y |
| Code structure | What was tried and failed, and how it failed |
| Test and tool output | Environment traps discovered the hard way |
| Git history, diffs | Which requirement ended up covered where |
| Ticket description | What was verified, and with what evidence |

A file can be the most important thing in the task and still go in as a pointer: the fresh
agent reads it in seconds. A line that looks trivial, like "a bare `--` gets swallowed in
PowerShell 5.1", is untouchable: it cost hours and rereading the code will not bring it back.

**Corollary:** when in doubt about whether something belongs, ask *"can an agent with the
repo in front of it and none of this conversation find this out again?"* If yes, it is a
pointer.

## When to run it

In 🧹 **COMPACT**, not in 🗑️ DUMP. The agent writing the handoff needs to be sharp, and
asking for the session's most delicate work at its worst moment is exactly backwards. If
you are already in DUMP, write it anyway but warn the user that fidelity may have dropped
and that they should review it by hand.

It is **re-runnable**: if a handoff for this task already exists, update that same file
instead of creating a new one.

## Where it goes

```
~/.claude/handoffs/YYYY-MM-DD-<repo>-<task-slug>.md
```

**The date prefix is mandatory**: it makes `ls` sort them chronologically on its own, and
stops the folder from becoming, three weeks from now, a list of invented names nobody can
map back to a task. The slug: 2 to 4 kebab-case words, no date inside.

Outside the repo on purpose: `CLAUDE.md` is gitignored in most repos but a `HANDOFF.md`
would not be, and it gets committed by accident. It also survives switching repos. Create
the directory if it does not exist. If the user asks for another path, use theirs.

**Before creating a new one, list `~/.claude/handoffs/`.** If a handoff for this same task
already exists, update that file — do not create a duplicate under another slug.

### Keep the index

After writing the file, update `~/.claude/handoffs/INDEX.md`: one row per handoff, newest
on top, with date · file · one-line task · status. Without the index you have to open every
file to tell which is which.

### How to resume without remembering the name

The user should not have to remember the filename. In the new session, if they say *"pick
up from the last handoff"* or similar, resolve it like this:

```bash
ls -t ~/.claude/handoffs/*.md | head -1     # the most recent one
```

or read `INDEX.md` when there are several and a choice is needed. Only then open the handoff.

## File structure

Order matters: recall follows a U curve, so the critical parts go **at the start and at the
end**, never in the middle.

```markdown
# Handoff — <task>
<repo> · <branch> · <date> · status: <in progress | blocked>

## 1. Goal
What is being built and **what "done" looks like** (concrete acceptance criteria).

## 2. Next step
The next concrete, executable action. Exactly one. No ambiguity.

## 3. Current state
- [x] done — verified with `<command>` → `<result>`
- [ ] pending
Verified facts only. If something was assumed and never tested, say so.

## 4. Decisions made
| Decision | Why | Alternative rejected |
The things nobody should reopen.

## 5. Dead ends
What was tried, and exactly how it failed. Stops the cost from being paid twice.

## 6. Environment traps
What was expensive to discover and is written down nowhere else.

## 7. Pointers
`file.py:120-145` — what lives there and why it matters. Exact paths, never contents.

## 8. Verification
The exact command that proves section 3's state is true, with its expected output.
```

## Hard compression rules

These hold without exception; they are what keeps the handoff from turning into the
conversation:

1. **No code block longer than about 10 lines.** Use the pointer `file.py:120-145`.
2. **No pasted tool output.** Use the conclusion: "all 110 cases pass", not the log.
3. **No repeating what `CLAUDE.md`, the code or the ticket already says.** If it is written
   somewhere in the repo, it is a pointer.
4. **Budget: 4,000 tokens (~16,000 characters) or less.** Going over almost always means
   payloads crept in where pointers belong — go back to the recoverability table and cut.
   The budget is heuristic, not measured: below it you start losing the unrecoverable,
   above it you have moved the problem instead of solving it.
5. **No conversational history.** A handoff describes a *state*, not a journey.

## Verification: a subagent does it, not you

**You cannot verify your own handoff.** You have the entire conversation in context, so
when you read "continue from step 3" you fill the gaps without noticing. An in-context check
is systematically blind to exactly the failure it should catch.

The only valid test reproduces the real condition: **a clean window holding nothing but the
file**. Launch **one** `Explore` subagent (read-only: a verifier must not do the work) with
this prompt and **no other context** — passing it details from the conversation invalidates
the test:

```
Read <handoff-path> and the repo it mentions. You have NO prior context on the task
and cannot ask for any.

Answer only this:
1. Could you execute the "Next step" (section 2) without guessing? yes/no
2. If no: what specific information is missing.
3. Is there any "Current state" claim you cannot confirm from the pointers given?
4. Is there anything you had to infer that should have been written down?

Be brief: a list of what's missing, no preamble. If it is complete, say "sufficient".
```

Real cost: about 150 tokens for the call and 200 for the verdict. The subagent's window is
thrown away entirely.

With the verdict in hand:

- **"sufficient"** → done, return the output.
- **gaps** → add them to the file and **re-verify exactly once more**. Two rounds maximum:
  if something is still missing on the second pass, write it into the handoff as a *"known
  weak spot"* and tell the user. Iterating further burns the context you are trying to save.

What the subagent returns outweighs your intuition here: it is the one standing where the
continuing agent will stand.

## Output

Return exactly two things, no preamble:

1. The path of the file written and its approximate size in tokens.
2. The two ways to resume, so the user picks:

```
pick up from the last handoff
```

or, when several tasks are in flight and they want to be explicit:

```
Read ~/.claude/handoffs/YYYY-MM-DD-<file>.md, run the command in section 8 to confirm
the state, and continue from section 2.
```

3. The reminder that **writing the handoff does not lower context**: the file is the save,
   `/clear` is the reset. Without the `/clear` nothing is freed.

"Run the verification first" is not decoration: the handoff may have gone stale if the user
changed something in between. Confirming before building on top costs one command and avoids
working from a false premise.

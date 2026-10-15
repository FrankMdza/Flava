# Opus 5.5, how to use it in the way you work

Draft from 2026-09-28. None of this is applied. Every change in section 4 waits for your approval.

Source: "Getting the most out of Opus 5.5 in Claude and Claude Code", Addy Osmani, claude.dev blog, published on 22 September 2026. URL: https://claude.dev/blog/getting-the-most-out-of-opus-5-5/

I read the whole thing. WebFetch returned a summary, so I pulled the HTML with curl and extracted the full text. The quotes below come from that text, in English and verbatim.

## 1. What the article says

Summary by section. What goes here is from the article. My readings are in section 2.

### The thesis

The article opens with three differences from Opus 5: "it works for longer on its own, it tells you plainly what it did, and it thinks before every reply." Everything else follows from those three.

The three things it asks you to try first:

- "Hand over the whole task. Say what "done" looks like and when you want it to stop and ask. Then let it work."
- "Delete "think carefully" lines. Opus 5.5 already thinks before every reply."
- "When a long run ends, read what it needs from you first."

### How to ask

- **Say what "done" is and let it run.** Whole task in one message, with the goal line. The example: "Done means: every endpoint uses the new client, the old client is deleted, and the test suite passes. Stop and ask me only if a test fails for a reason you can't explain." The reason it gives is that its biggest gains are in multi-step work and that "Early testers had it run long coding tasks for hours with little oversight."
- **Remove "think hard".** "Opus 5.5 always thinks before it replies, and it decides how much." In their tests on a chat product, removing a "think carefully" made replies start sooner "with no clear drop in quality." For quick replies, "Answer directly." To change how much it thinks in Claude Code, "change effort."
- **Add things to a run in progress** by typing while it works, because restarting costs more now that runs are long.
- **In design, name the styles you don't want.** Without direction it falls back to a few default styles, and "A general instruction like "avoid a generic look" mostly swaps one default for another." A list of concrete patterns works better. If what it picks next isn't to your taste either, it goes on the list.

### Long runs in Claude Code

- **Tell it which stops you want.** Sometimes it stops to report when there is no need: "a summary that names the next step without taking it, an offer to continue, or a list of choices that don't block the work." It proposes this rule for CLAUDE.md:

  > When a step doesn't need my input, keep going. Put status notes in the same message as your next action.
  > Stop and ask only when you can't continue without me, or before anything destructive: deleting data, force-pushing, or changing anything outside this repository.

  It warns that fewer stops require keeping your own brakes: "Keep permission prompts on for destructive commands too." For pair programming it suggests the opposite, a one-line plan before and a short summary at the end.
- **Split big work across subagents and check each one's evidence.** The example asks: "When a subagent reports back, check its evidence before you accept it. Finish with one table: service, affected yes or no, and the evidence."
- **The task list in a file.** Claude Code summarizes old turns when the context fills up, and a list in a file survives that. Prompt: "Keep a checklist in TASKS.md. Tick each item when it's done, and add anything new you find."

### Reviewing the result

- **Read first what it needs from you.** To fix the format of the final summary, it proposes in CLAUDE.md: "End every run with three headings: Blocked on me, Changed, Found."
- **Ask it to review the code before a person does.** It quotes a tester: Opus 5.5 "at its lowest effort caught more bugs than Opus 5 at high effort, with fewer false alarms." Prompt: "List only problems you'd block the merge for. For each one, give the file and line, why it's wrong, and how to show it fails."
- **Mark what is unconfirmed.** "Mark anything you couldn't confirm, and say where you looked."

### Claude apps

Attach the chart or the screenshot instead of transcribing it. Ask it to review long documents looking for contradictions in numbers, dates and names. Ask for the finished file and not an outline. In projects with long chats, declare earlier answers closed, because sometimes it "goes back over an earlier answer while it thinks about a short follow-up", except in long analyses where a later step can correct an earlier one.

### Flagged messages

It is the first Opus with "Fable-level" bio and cyber safeguards. A flagged message goes to an older model and the session stays there. "Finding security vulnerabilities in source code is allowed." The check covers the whole conversation, files and search results included. In Claude Code: `/model` to switch back, Esc twice to edit the last message, `/config` to make it ask before switching, `/feedback` if the flag was a mistake.

Asking it to reproduce its internal reasoning in the reply "can be declined. It's one of the flag categories." The alternative: "Explain why you chose this approach in three sentences."

### Speed

`/fast` is the same model with faster output, in research preview, and costs more per token. It is useful when you read each reply before sending the next.

## 2. How to apply it to the way you work

What follows is my interpretation. I reviewed `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, the skills in `~/.claude/skills/`, `INDEX.md` and the handoff `2026-09-22-hydra-publish-and-launch.md`, the `puppets` skill and Hydra's `CLAUDE.md`, `src/provider/claude.rs`, the run prompt `task-build-134.txt` and the memory.

### What you already do well, according to the article

None of this needs changing, and it is worth knowing so you don't touch it more than needed.

- **No "think hard".** I searched for "think hard", "think carefully", "step by step", "ultrathink" and "show your reasoning" in CLAUDE.md, skills, handoffs and the Hydra prompts. There is none outside a Hydra test, `tests/drift.rs`, which uses it on purpose to measure thinking tokens. That one stays.
- **The definition of "done".** Section 1 of the handoff requires "what "done" looks like", and Hydra's has it written in two parts. It is what the article asks for in "Say what "done" looks like".
- **The list in a file.** Section 3 of the handoff, with `[x]` and `[ ]`, and the tickets with `Status:` in `.scratch/hydra/` do the job of TASKS.md. They survive compaction, which is the reason the article gives.
- **Checking subagent evidence.** The handoff asks for an Explore subagent that verifies cold, and Master of Puppets has three judges plus your reading of the diff. The memory about composer, which "invents numbers it didn't measure", is exactly the case for "check its evidence before you accept it".
- **Stops before anything destructive.** `settings.json` denies `git push --force` and `-f`, and `guard_git.py` blocks pushes to master. The article asks you to keep that even if the other stops are relaxed.

### Changes I do propose

**A. Stop rule in `~/.claude/CLAUDE.md`.**
Today your global CLAUDE.md only deals with unslop. It doesn't say when to stop. The article gives the rule from the "Tell it which stops you want" section. Your version has to reflect two things that are already rules of yours and are scattered across memory and handoffs: never place orders on the real IBKR account, and you do the push yourself. Proposal, in Spanish so it matches the memory:

> Cuando un paso no necesita mi opinión, sigue. Pon las notas de estado en el mismo mensaje que la siguiente acción.
> Para y pregunta solo si no puedes seguir sin mí, o antes de algo destructivo o fuera de la tarea: borrar datos o ramas, force-push, push a master, tocar ficheros fuera del repo de la tarea, cualquier orden en una cuenta real de trading.

Watch out for a conflict. In orchestrator sessions you approve plan, table and every diff, and the `puppets` skill requires those stops. The general rule must not override them. That is why it carries "o fuera de la tarea" and it is worth adding one line: "Las paradas que pide un skill cuentan como necesarias."

**B. Final summary format in `~/.claude/CLAUDE.md`.**
The article suggests "Blocked on me, Changed, Found". You work as a reviewer with several runs at once, so reading first what blocks you saves more than in a single session. Proposal: "Termina cada tarea larga con tres apartados: Pendiente de mí, Cambiado, Encontrado." It applies the same to the report of the subagents you launch.

**C. "Done means" and report format in the Hydra run prompts.**
`task-build-134.txt` already says what to include in the report and when to stop, which is good. It lacks an explicit "Done means" line, which today lives in the ticket, and a report order that puts up front what the run could not close. Concrete change in the `task-build-NNN.txt` template, and in the equivalent text that `puppets.py launch` generates: a line "Done means: <ticket criterion>" right after "Your ticket is", and the report should start with "Not confirmed / blocked". Backing: "Say what "done" looks like" and "Mark anything you couldn't confirm, and say where you looked". This attacks the problem you have already measured of agents claiming measurements they didn't make.

**D. Effort per task in Hydra.**
`claude --help` in 2.1.283 has `--effort <level>`. `src/provider/claude.rs` passes `--model` and never `--effort`, and neither `puppets.py` nor `vendors.json` mention it. The article says that the control over how much it thinks is effort, not the prompt, and it cites the case of Opus 5.5 at minimum effort finding more bugs than Opus 5 at high. Proposal: a map ticket to add `effort` as a column in the assignment table, next to provider, model and policy, which the claude provider translates to `--effort`. That way a diff judge can run at low and a `high` task at high. This is the only item on the list that touches code. I don't know which levels the CLI accepts or how it behaves in `--print`. It has to be measured before writing the ticket.

**E. Subagent instruction in `handoff-frank` and in how you delegate.**
The skill already delegates verification. What I would add is the article's sentence to the prompt with which you, as orchestrator, launch reading or audit subagents: check their evidence before accepting it and close with a table. In `handoff-frank/SKILL.md` nothing about the verifier changes, because its cold design is already stricter than what the article asks for.

**F. Checklist in a file for long Hermes Quant sessions.**
The Hydra handoff already solves this. In Hermes Quant, supervision rounds last hours and the state lives in the conversation until you write the handoff. Asking at the start of each round "Mantén un checklist en `docs/tickets/<fecha>/TASKS.md`, marca lo hecho y añade lo nuevo" gives you the list before reaching COMPACT, and the handoff then points to it. Backing: "Keep the task list in a file".

**G. What to say about flags in the Hydra handoff.**
Section 5 of the handoff says that "Un clasificador corta respuestas que describen el detalle de un fallo de seguridad". The article explains the mechanism: the session switches to an older model and the check covers the whole conversation, files included. Two consequences. An orchestrator session that reads `SECURITY.md` or findings reports can end up on another model without you noticing, so it is worth watching the notification and switching back with `/model`. And in Hydra runs with `--print` nobody sees the warning. It is worth checking whether the switched model shows up in the run record, and if not, opening a ticket. Unmeasured: I don't know what the CLI writes in stream-json when it switches model.

**H. Reasoning in the judge prompts.**
The judge prompts in `puppets.py` ask for a verdict and "the strongest reason", not for them to reproduce their thinking. That is fine according to the article. The only point to watch is `showThinkingSummaries` in `claude.rs`, which returns the thinking text to the stream. It is a setting, not a request in the prompt, so the article says nothing about it. I mention it so it isn't confused with what the article does advise against.

**I. List of banned styles in the web prompt.**
The session B prompt, `2026-09-26-hephaestuslab-web-prompt.md`, rebuilds hephaestuslab.co. It is the exact case of "name the styles you don't want". Add a concrete list: cream background, italic words in headings, "01 / 02 / 03" labels, monospaced labels, pill buttons, plus whatever you already dislike about the current site. If what comes out isn't to your taste either, it goes on the list.

## 3. What the article doesn't cover or where it doesn't apply

- **Models that aren't Opus 5.5.** The article only talks about Opus 5.5. Hydra launches codex, cursor-agent, agy and Claude sonnet. None of this transfers as is to them. Your memory says that codex and agy need tighter specifications, not looser. Letting it run with little supervision is advice for Opus 5.5, not for your workers.
- **"Let it cook" versus your rule of reviewing every diff.** The article pushes toward fewer stops. Your Master of Puppets design has three human approvals per decision, and the skill requires them. I see no reason to remove any: the article talks about stops that "don't block the work", and yours do block it.
- **8 GB machine.** The article talks about parallel subagents without mentioning resources. Your real limit is swap and one cargo run at a time. Splitting into subagents works for reads and audits, not for parallel builds.
- **Context.** It gives no numbers on context or degradation. Your `CONTEXT-PLAYBOOK.md` remains the reference, and the article only confirms that compaction erases detail, which is the reason for the handoffs.
- **Cost.** It says nothing about tokens except that `/fast` costs more. The blog has two related posts I didn't read: "Using Claude Code: Spending your effort" and "What a task costs on Opus 5.5", both from 25 September. The first one probably answers the open question in change D.
- **Trading.** Nothing in the article touches decisions involving money. Your Hermes Quant risk rules don't change.
- **Language.** The examples are in English. Nothing says that instructions in Spanish work worse, but nothing proves it either.
- **Claude apps.** Section 4 barely applies, because you work in Claude Code. The only useful part is the review of long documents, which can serve for the Show HN or the README before publishing.

## 4. Proposed changes, by impact

Approve them one by one. None is applied.

1. **Stop rule in `~/.claude/CLAUDE.md`**, with the stops for real trading, push and skills included. It is what changes the day to day the most and costs three lines. Section 2.A.
2. **"Done means" and "Not confirmed" in the Hydra run prompts**, in the `task-build-NNN.txt` template and in what `puppets.py` generates. It attacks the most expensive failure you have documented, agents inventing measurements. Section 2.C.
3. **Closing format "Pendiente de mí, Cambiado, Encontrado" in `~/.claude/CLAUDE.md`.** It saves you reading whole reports to find the decision that falls to you. Section 2.B.
4. **Measure `--effort` in the CLI and open a map ticket for an `effort` column in the Master of Puppets table.** The potential impact is high, but it depends on a measurement nobody made. Section 2.D.
5. **Check what a Hydra run leaves behind when a message is flagged and the model switches.** If the record doesn't say so, the provider ranking learns from a model that wasn't the one requested. Section 2.G.
6. **List of banned styles in the hephaestuslab web prompt.** Cheap and concrete. Section 2.I.
7. **Checklist in a file at the start of each Hermes Quant round.** Section 2.F.
8. **The sentence "check the evidence and close with a table" when delegating audits to subagents.** Section 2.E.

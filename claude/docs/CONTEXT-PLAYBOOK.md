# Context playbook

How to spend the attention budget without arriving degraded at the end of a session.
Written against Claude Code 2.1.220 running `opus[1m]`.

---

## 1. The central fact

The context window is not a hard drive. It is a **volatile cache with a finite budget**.
Attention spreads a probability mass that always sums to 1 across every token present.
Adding 500k tokens does not add capacity, it dilutes what you have.

The practical consequence: **being able to ingest ≠ being able to reason over what you
ingested**. A model with a 1M window retrieves a literal fact at 900k without trouble, and
fails to connect two facts at 60k.

Corollary from *Lost in the Middle*: retrieval follows a **U curve** — good at the start,
good at the end, bad in the middle. Put the critical material at the edges of the prompt.

---

## 2. The marks, and where each one comes from

This is what the statusline widget draws. **Every mark carries its provenance because they
are not worth the same.**

| State | Threshold | Source | How solid |
|---|---|---|---|
| 🧠 `HIFI` | < 32k | NoLiMa (arXiv:2502.05167) | **measured, but not on Claude 5** |
| 👍 `WORK` | 32k → 150k | derived middle zone | derived |
| 🧹 `COMPACT` | > 150k | Anthropic's compaction trigger | **published and current** |
| 🗑️ `DUMP` | > 40% of the window | heuristic | no measurement behind it |

The window is **not hardcoded**: Claude Code hands it over in the statusline payload
(`context_window.context_window_size`). That is the *effective* window, not the catalog
number — it honors the `[1m]` suffix, the `CLAUDE_CODE_MAX_CONTEXT_TOKENS` override and the
200k clamp.

Thresholds scale differently per model, which is exactly why there is a table and not a
single percentage: the 150k compact mark is **15%** of the window on Opus 5 and **75%** on
Haiku 4.5. One global percentage threshold would lie in both cases.

---

## 3. What this playbook does NOT claim

**No measured degradation curve exists for Opus 5, Sonnet 5, Fable 5 or Haiku 4.5.**

- **NoLiMa** (2025) measured 12 models. The only Claude in the set is **3.5 Sonnet**, whose
  effective length drops to about 4k and collapses below 50% at 32k. That is where the 32k
  line comes from, and it is *cross-model*, not Claude 5.
- **Context Rot** (Chroma, Jul 2025) tested 18 models including the Claude 4 family. Its
  conclusion about Claude is **qualitative**: it decays more slowly than the rest, but it
  degrades at *every* increment, not only near the limit.
- The 5 family postdates all of those papers.

Anyone handing you a per-model curve for the 5 family is extrapolating. The marks in the
table above are the best available approximation, not a measurement.

Two Context Rot findings are counterintuitive enough to keep in mind:

- Models retrieve **better** from shuffled text than from coherent text. A well-structured
  document invites compressing the internal representation, which blurs individual facts.
- **Thematically close distractors** do more damage than pure noise, and their effect grows
  superlinearly with length.

---

## 4. How to measure your own curve

If you want a number calibrated to your real tasks instead of somebody else's average, it
is a bounded experiment, not a project:

1. Pick a representative, verifiable task — for example *"find the bug in this diff"*.
2. Run **the same prompt** with irrelevant filler in front at **8k / 32k / 128k / 300k**.
3. Repeat each point several times and measure the hit rate.
4. Where it falls off is your threshold. That number is worth more than the whole table above.

---

## 5. The four practices

1. **Delegate bulk reading to subagents.** Each subagent has its own window; only the
   conclusion comes back to the main thread.
2. **One session, one track.** Mixing three unrelated workstreams makes them compete for the
   same attention. One session per track, with a `.md` bridging them.
3. **Write to disk, not to context.** Long reports go to a file. Context is for deciding,
   not for archiving.
4. **Compact yourself, before auto-compact.** Auto-compact fires when you are already in the
   degraded zone; the widget warns you earlier. And note this: compaction **prunes
   constraints** — in evaluations, the policy violation rate rises from 0% to about 30%
   after compacting, because the summary optimizes for task continuity and discards rules as
   though they were peripheral noise. That is why critical rules do not live in the prompt.
   They live in the hooks.

### Handoff: closing a session without losing the work

When the widget enters 🧹 `COMPACT`, the right move **is not `/compact`**. It is writing a
handoff to disk and running `/clear`.

`/compact` compresses well (measured in a real session: `preTokens 303,168 → postTokens
17,581`). The problem is not how much it compresses but **what it decides to throw away**:
it summarizes without knowing what you will need later, and optimizes for narrative
continuity, so the first things pruned are the constraints and decisions that look
peripheral. And if you compact while already in DUMP, the model writing that summary is
already degraded.

**The right filter is recoverability, not importance:**

| Cheap to recover → **pointer** | Unrecoverable → **write it down** |
|---|---|
| file contents, structure, diffs | why X was chosen over Y |
| test and tool output | what was tried and failed |
| git history, ticket description | environment traps found the hard way |

A file can be the most important thing in the task and still go in as a pointer — the fresh
agent reads it in seconds. A trivial-looking line that took hours to discover is untouchable.

The arithmetic, with measured numbers from this environment: fixed floor **~38k** + handoff
**≤4k** = you start at **~42k**, barely out of HIFI.

The flow: write the handoff **while you are still sharp** → read it yourself (30 seconds) →
`/clear` (not `/compact`) → in the new session, **run the verification first**, then
continue. Confirming before building on top costs one command and avoids working from a
false premise.

Automated in the **`handoff-frank`** skill, which enforces the ≤4k budget and **verifies
with a clean-window subagent**. That last part matters: whoever wrote the handoff cannot
judge whether it stands alone, because they have the whole conversation in context and fill
the gaps without noticing. Only a clean window reproduces the real condition. It costs about
350 tokens of the main context; the verifier's window is discarded.

**The anti-pattern:** pasting the previous conversation into the new session. That is not
starting fresh, that is relocating the problem.

### Connector hygiene — a measured correction

The original plan assumed MCP tools weighed **94k**, a figure taken from an old `/context`.
**Measured, that is false today.** The full fixed floor (system prompt + tools + MCP +
memory) comes to ~37–39k, and it is remarkably stable:

| session | fixed floor |
|---|---|
| 1 | 38,781 |
| 2 | 39,633 |
| 3 | 38,587 |
| 4 | 37,299 |
| 5 | 36,842 |

Later confirmed against a real `/context`:

```
System prompt          3.6k       MCP tools (deferred)   0 tokens   ← "76 tools · 0 tokens"
System tools          19.2k       Memory files           5.4k
Custom agents          129        Skills                 2.4k
                                  Messages             230.1k       ← 88% of the total
```

MCP tools are **deferred**: they cost **0 tokens** until invoked. The 56.1k showing in that
column is the *potential* cost if all of them loaded, not what you are paying.
Real fixed floor: **~30.7k**.

**Conclusion: turning connectors off saves almost nothing.** The task the original plan
flagged as the big win turned out to be noise. Real consumption is `Messages` — 88% of the
total — and you attack that with handoffs, subagents and one-track sessions, not by touching
connectors.

It is the perfect example of why you measure before acting instead of carrying an old
figure around: the 94k number would have justified half an hour of work for zero return.

### Surgical retrieval in Jira

`searchJiraIssuesUsingJql` **ignores the `fields` parameter** and always returns the full
description — a five-ticket query cost about 50KB. To discover, use Rovo's search (compact);
for detail, `getJiraIssue` on specific keys.

---

## 6. What is installed

| File | What it does |
|---|---|
| `~/.claude/statusline.py` | The 2-line widget. No network: everything comes from the stdin payload and the transcript |
| `~/.claude/model-thresholds.json` | The marks above, with `_provenance` per entry |
| `~/.claude/hooks/guard_git.py` | Blocks force push and pushes to dev/main/master |
| `~/.claude/hooks/guard_aws.py` | Fail-closed read allowlist, with an exception for `codeartifact login` |
| `~/.claude/hooks/guard_slack.py` | Blocks everything that sends to Slack |
| `~/.claude/hooks/unslop_reminder.py` | Re-injects the unslop directive on every turn |
| `~/.claude/hooks/tests/test_guards.py` | 110 cases: 65 evasion attempts + 45 reads that must pass |
| `~/.claude/skills/handoff-frank/SKILL.md` | Generates the handoff that closes a session and continues in a clean one |
| `~/.claude/handoffs/` | Where handoffs land, outside the repos so they never get committed |

### Hook contract — verified, not assumed

On **Claude Code 2.1.220**, the docs embedded in the binary say for `PreToolUse`:

> `Exit code 2 - show stderr to model and block tool call`

And it was confirmed **live**: `git push --force` in a scratch repo was denied and the stderr
reason came back to the model. Hooks reload when you edit `settings.json`, no session restart
needed.

That is why `EMIT_JSON_DECISION = False` in `~/.claude/hooks/_cmdparse.py`. If a future
version breaks that contract, setting it to `True` makes the guards additionally emit
`hookSpecificOutput.permissionDecision = "deny"`.

### Why the guards parse instead of using regex

A `grep -E 'push.*force'` is evaded by `git push --fo\rce`, by `$(echo git) push -f`, or by
putting the push in the second leg of an `&&`. The guards split the line into simple
commands while respecting quotes, recurse into `$(...)` and backticks, and tokenize with
`shlex`. An executable coming from a substitution is treated as *could be anything* → it
gets blocked. All of those cases are in the suite.

---

## 7. How to read the second line

```
base 59k · convo 159k · tools 39% resp 54% · in 917k out 381k · $9.16 · 166 msgs
```

- **`base`** — the session's fixed floor: system prompt + tool definitions + MCP + memory +
  first prompt. Measured as the input total of the **first** assistant message. Around
  **39–41k** in this environment. *Lowered by turning connectors off.*
- **`convo`** — everything accumulated since (`live − base`). *Lowered by compacting or
  delegating reads to subagents.*
- **`tools% / resp%`** — what that conversation is made of: tool results against assistant
  responses. The rest is your prompts. It varies wildly between sessions (measured: 69%
  tools in one, 39% in another) and it tells you **what** to fix: if `tools` dominates,
  delegate to subagents; if `resp` dominates, ask for shorter output or write to disk.
- **`in` / `out`** — fresh input (input + cache_creation) and generation. `cache_read` is not
  shown: in a 438-message session it was **267.7M** against 10.2M of fresh input, so it
  dominates the number without being actionable — it is cheap and it is exactly what you
  want happening.

**What this breakdown is NOT:** the one from `/context`. CC computes that in memory
(`getContextUsage`, `ToolTokens`) and neither persists it nor passes it to the statusline
payload, so separating "MCP tools" from "system prompt" from "memory files" is not possible
from here. `base` groups them into a single measured number.

The percentages are computed from transcript line size, not by tokenizing — a deliberate
approximation so the widget runs in 55ms over a 4.5MB transcript.

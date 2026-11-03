---
name: plain-prose
description: Edit prose so it reads like a careful person wrote it for one reader, without changing what it says. Use when writing or revising docs, READMEs, PR descriptions, commit messages, handoffs, reports, emails or chat replies, and when the user asks to remove AI slop, unslop or humanize text. Works in English and Spanish.
---

# Plain human prose

You are editing text so it reads like a careful person wrote it for one specific reader. The goal is fewer machine tells and a text that is easier to use. It is not to fool a detector, and it is never to change what the text says.

A language model picks the choice that fits the widest range of readers, so its prose comes out even, staged and generic. A person writes for one reader about one subject, so their choices are uneven and specific. Most tells are a version of that default, and the structural ones survive model updates while the word lists go stale. Work on structure first and words last.

## What to keep fixed

Keep every fact, number, name, path, command, step and claim. Do not add facts, examples, numbers, names, dates or citations that are not in the source. Do not invent opinions, feelings or anecdotes for the writer. If the writer already gives an opinion, keep it and make it plainer. Code blocks, inline code, links, frontmatter and quoted material stay as they are. Placeholders like [Name] stay. Keep the writer's level of certainty: "may" stays "may", "probably" stays "probably". Do not firm up a hedge or soften a claim. Keep the language of the source; the patterns below apply to Spanish as they do to English.

## The tells, strongest first

Staging comes first. Watch for a contrast that only adds weight ("not just X, it's Y", "this isn't about A, it's about B"), a one-line closer that repeats the paragraph, a run-up that announces the point before making it ("Here's the thing", "Let's break it down", "The short answer"), and arguing with an objection nobody raised. State the point instead.

Next is rhythm by rule. That means items forced into threes, every sentence the same length, the same opener repeated, and a dash or colon used as the joint between every pair of clauses. Use the number of items the content has. Join clauses with a period or a comma. Avoid em dashes, and do not swap them for parentheses or semicolons everywhere.

Then inflation and vague authority: "pivotal", "testament to", "plays a key role", "robust", "seamless", "experts say", "-ing" riders that comment on the sentence ("highlighting the importance of..."), and "serves as" or "boasts" where "is" or "has" works. Say what happened, with the number if the source has one.

Model grammar is the least obvious tell. Models turn verbs into nouns ("the implementation of the migration was carried out") about twice as often as people do. Give the action back to a verb and an actor: "we migrated". Do not overcorrect into forcing every sentence active. People use a passive when the actor does not matter, and models use that kind of passive less than people do.

Formatting comes next. Bold on every other phrase, a bold label with a colon in front of every bullet that repeats the line, headings for a three-paragraph note, and title case. Remove decoration, not structure. If the source is a README, report, release note or status update with real lists and sections the reader scans, keep them. Turn a list into prose only when its items are really one argument chopped into fragments.

Last, leftovers. Chat wrappers ("Great question", "I hope this helps", "Let me know if"), knowledge-cutoff disclaimers, a heading repeated in the first sentence, sentences about the document instead of its subject ("This section covers..."), and background the reader already has, which pushes the decision to the end.

Plain words beat clever ones: use, help, many, if, start, base. Abstract metaphor nouns (landscape, vector, surface, substrate, north star, flywheel) usually hide a concrete word. Find it. A sentence that could appear unchanged in another project's text says nothing about this one. Cut it or make it specific from the source.

## How to work

Read the whole text and mark the tells. A sentence with no tell stays as written; rewriting clean sentences for style is how facts get lost. Every tell you find gets fixed, however many there are. Then rewrite each paragraph that has tells around its main point. Do not patch flagged words one by one, because swapped-in synonyms become the next tell ("delve" turning into "dig into"). Lead with what the reader needs to act on. Vary sentence length because the content varies, not by formula.

Then check the draft against the source line by line: anything lost, anything added? Fix both. If a prose linter result is provided, treat each flag as a pointer to a sentence and rewrite that sentence. Skip flags that are false positives.

Stop there. A second round of polishing on text that is already clean makes it flat and choppy. Short is good, clipped is not. Keep connective words like "because", "so" and "but", which carry the reasoning.

## Example

Before: "Additionally, this update serves as a pivotal step in enhancing reliability — not just fixing bugs, but fundamentally transforming how the system handles failures, ensuring a seamless experience."

After: "This update makes the system retry failed downloads instead of stopping, so a dropped connection no longer loses the night's data."

The after version only works if the source says what the update does. If it does not, write the plain claim the source supports: "This update fixes several failure cases in the downloader."

## Flow for finished English text

When the text is a file you are about to hand over (doc, README, PR description, handoff), run `sg -v <file>` after your single editing pass. Read each flag as a pointer to a sentence. Rewrite the sentence when the flag is a real tell, and ignore false positives: a bold file name followed by new detail, a list that is really a list. Do not start a second full rewrite to raise the score. In tests a second pass raised the linter score from 60 to 89 and made the text worse for blind judges. `sg` does not understand Spanish, so skip it there.

# Flava

My development environment as a repo: Claude Code config, shell, terminal, and the Pokemon
that greets me when I open a tab. Clone it on a new machine, run one script, get the same
setup back.

Built and tested on WSL2 Ubuntu and written to install on macOS too. The pieces that cannot
be portable (the WSL domain in WezTerm, `batcat` vs `bat`, the Windows-only acrylic
backdrop) are detected at runtime rather than hardcoded.

## Install

```bash
git clone https://github.com/FrankMdza/Flava.git ~/Flava
cd ~/Flava
./install.sh
```

That symlinks everything into place, installs the missing packages through Homebrew or apt,
and runs the checks. Anything it would overwrite gets moved to `~/.flava-backup-<timestamp>/`
first, so a bad run is always reversible.

| Flag | What it does |
|---|---|
| `--copy` | Copy instead of symlink. The installed files stop tracking the repo. |
| `--no-deps` | Skip the package manager. Useful when you manage packages yourself. |
| `--only claude` | Install one component: `claude`, `shell`, `fastfetch`, `wezterm`. |
| `--dry-run` | Print every action, change nothing. Run this first if you are unsure. |

Symlinks are the default because editing a config and committing the change is the whole
point of a dotfiles repo. One exception worth knowing: under WSL, keeping the repo on
`/mnt/c` means every hook invocation reads across the 9p filesystem, which is slow enough to
notice on a busy session. Either clone into the Linux home instead, or use `--copy` there.

## What is inside

### `claude/` — Claude Code

The part I actually care about.

**Three PreToolUse guards** (`hooks/`) that block destructive commands before they run.
`guard_git.py` catches force pushes, pushes to `dev`/`main`/`master`, `reset --hard`,
`branch -D`, and the plumbing equivalents people forget to block (`update-ref -d` deletes a
branch exactly like `branch -D` does). `guard_aws.py` is a fail-closed read allowlist.
`guard_slack.py` blocks anything that sends to Slack, MCP tool or raw webhook.

They parse instead of grepping, which is the reason they work. A regex on `push.*force` is
evaded by `git push --fo\rce`, by `$(echo git) push -f`, or by hiding the push in the second
leg of an `&&`. The guards split the line into simple commands respecting quotes, recurse
into `$(...)` and backticks, and tokenize with `shlex`. An executable that comes out of a
substitution is treated as "could be anything" and blocked.

`hooks/tests/test_guards.py` holds 110 cases: 65 evasion attempts that must be caught and 45
ordinary reads that must still pass. Run it after any edit. A guardrail that blocks `git
status` is a broken guardrail, and the second half of the suite exists to catch exactly that.

**A two-line statusline** (`statusline.py`) that answers "how much context is left" and, more
usefully, "what is eating it":

```
Work Repos · feature/PROJ-123 · Opus 5 1M  [██░░░░░░░░░░░░░░░░░░]  🧠 HIFI · 90k/1M · 9%
base 39k · convo 51k · tools 39% resp 54% · in 917k out 381k · $9.16 · 166 msgs
```

`base` is the session's fixed floor, `convo` is everything since. The `tools%`/`resp%` split
tells you what to fix: tool results dominating means delegate to subagents, assistant
responses dominating means ask for shorter output. It never touches the network and always
exits 0, because a statusline that breaks the prompt is worse than no statusline.

The band thresholds live in `model-thresholds.json`, each with a `_provenance` field saying
where the number came from and how much to trust it. The 32k HIFI line is measured, but on
Claude 3.5 Sonnet, not on the 5 family. The dump mark is a heuristic with nothing behind it.
Marks that pretend to more certainty than they have are worse than no marks.

**`docs/CONTEXT-PLAYBOOK.md`** explains the reasoning behind all of it, including a measured
correction where my own assumption turned out to be wrong: I thought MCP tools were costing
94k and it was worth turning connectors off. Measured, they cost zero until invoked, and the
real consumption was 88% conversation. The playbook keeps the wrong number and the correction
because the mistake is the lesson.

**Skills** (`skills/`):

| Skill | What it does |
|---|---|
| `unslop` | Cuts AI tells from any writing. Wired into `CLAUDE.md` so it applies to everything, not just editing tasks. |
| `handoff-frank` | Writes a handoff so a clean session continues the task. Enforces a 4k budget and verifies with a clean-window subagent, because you cannot verify your own handoff. |
| `rust-writing` | Rules for idiomatic Rust, each with its source, plus nine reference files on errors, types, async, unsafe, tests, performance, dependencies and tooling. Written in Spanish. |
| `daily-agile-planner` | Pulls Jira and Google Calendar, ranks the work, and lays out a schedule measured from the moment you run it rather than from an imaginary 9am. |
| `claude-handoff`, `implement-spec`, `loop-me`, `retro`, `setup-ts-deep-modules`, `writing-beats`, `writing-fragments`, `writing-shape` | Local copies from [mattpocock/skills](https://github.com/mattpocock/skills), MIT licensed. `settings.template.json` also enables that marketplace, so you can drop these and take the upstream versions instead. |

**`CLAUDE.md`** makes `unslop` a standing rule and sets how it interacts with a repo's own
conventions: unslop wins on prose, the repo wins on structure and on any literal string a
tool parses.

### `shell/common.sh`

One file sourced by both `.bashrc` and `.zshrc`. Every alias is behind a `command -v` check,
so a machine missing a tool loses that one alias and nothing else.

`cd` becomes zoxide, `cat` becomes bat, `ls` becomes lsd with a one-level tree. The prompt
shows the git branch in both shells. On WSL it forces directory colors to plain blue, because
Windows drives mount world-writable and the default `ow` color is an unreadable green
background.

A random Pokemon prints on every new interactive shell. `FLAVA_NO_POKEMON=1` turns it off.

### `fastfetch/`

The config plus a Pikachu logo in ANSI. `pokemon-colorscripts` is a separate thing, installed
by `install.sh` from [its GitLab repo](https://gitlab.com/phoneybadger/pokemon-colorscripts)
into `~/.local/opt` with a symlink into `~/.local/bin`. It is about 50MB of sprites, which is
why it is cloned rather than vendored here.

### `wezterm/wezterm.lua`

Catppuccin Mocha, JetBrains Mono, 70% opacity. The resurrect plugin saves workspaces every 5
minutes and restores them on startup.

One thing that took a while to figure out and is commented in the file: `resurrect_on_gui_startup`
does not read the saved `.json` files directly, it looks for a `current_state` marker that
only `write_current_state` writes. Neither `save_state` nor `periodic_save` writes it, so
auto-restore failed silently every single time. The config now refreshes that marker after
every save.

`ALT+W` saves a workspace, `ALT+R` restores one through a fuzzy finder.

**On WSL this file does not go in the Linux home.** `wezterm.exe` runs natively on Windows
and reads `C:\Users\<you>\.wezterm.lua`. The installer says so and skips it rather than
putting the file somewhere that will never be read.

## What is deliberately not here

- **Anything work specific.** No internal URLs, client names, database schemas, PR templates,
  or MCP servers pointing at private repos. Those live on the work machine only. The guards
  keep their mechanism but their example values are generic.
- **Secrets.** No tokens, credentials, `.claude.json`, or `.credentials.json`. The
  `.gitignore` blocks them, but the rule is to never put them here in the first place.
- **Neovim.** Managed separately.
- **Git identity.** `git/gitconfig.example` has the useful settings, but name and email are
  per machine. Set them yourself after installing.

## After installing

```bash
exec $SHELL -l                                  # pick up the new shell config
python3 ~/.claude/hooks/tests/test_guards.py    # should print 110/110
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Then open Claude Code. The statusline appears at the bottom, and the first `git push --force`
you try gets refused.

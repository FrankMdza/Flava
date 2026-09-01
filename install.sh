#!/usr/bin/env bash
# Flava installer — puts this repo's config onto a fresh machine.
#
#   ./install.sh                 symlink everything, install missing packages
#   ./install.sh --copy          copy instead of symlink (files stop tracking the repo)
#   ./install.sh --no-deps       skip the package manager entirely
#   ./install.sh --only claude   one component: claude, shell, fastfetch, wezterm, ghostty
#   ./install.sh --dry-run       print what would happen, change nothing
#
# Idempotent: re-running it is safe. Anything it would overwrite gets moved to
# ~/.flava-backup-<timestamp>/ first, so nothing is destroyed silently.

set -euo pipefail

FLAVA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$HOME/.flava-backup-$(date +%Y%m%d-%H%M%S)"

MODE=link
WITH_DEPS=1
DRY_RUN=0
ONLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --copy) MODE=copy ;;
    --no-deps) WITH_DEPS=0 ;;
    --dry-run) DRY_RUN=1 ;;
    --only) ONLY="${2:-}"; shift ;;
    -h|--help) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done

# ------------------------------------------------------------------------- plumbing

BOLD=$'\033[1m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'; OFF=$'\033[0m'

say()  { printf '%s==>%s %s\n' "$BOLD" "$OFF" "$*"; }
ok()   { printf '  %s✓%s %s\n' "$GREEN" "$OFF" "$*"; }
warn() { printf '  %s!%s %s\n' "$YELLOW" "$OFF" "$*"; }
die()  { printf '  %sx%s %s\n' "$RED" "$OFF" "$*" >&2; exit 1; }

run() {
  if [ "$DRY_RUN" = 1 ]; then
    printf '  [dry-run] %s\n' "$*"
  else
    "$@"
  fi
}

wants() {
  [ -z "$ONLY" ] && return 0
  [ "$ONLY" = "$1" ]
}

backup() {
  # Move an existing path out of the way, preserving its position under $HOME.
  local target="$1"
  [ -e "$target" ] || [ -L "$target" ] || return 0
  local rel="${target#"$HOME"/}"
  local dest="$BACKUP_DIR/$rel"
  run mkdir -p "$(dirname "$dest")"
  run mv "$target" "$dest"
  warn "backed up $target -> $dest"
}

install_path() {
  # install_path <source-in-repo> <destination>
  local src="$1" dest="$2"
  [ -e "$src" ] || die "missing in repo: $src"
  if [ "$MODE" = link ] && [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
    ok "already linked: ${dest/#$HOME/\~}"
    return 0
  fi
  backup "$dest"
  run mkdir -p "$(dirname "$dest")"
  if [ "$MODE" = link ]; then
    run ln -s "$src" "$dest"
    ok "linked ${dest/#$HOME/\~}"
  else
    run cp -R "$src" "$dest"
    ok "copied ${dest/#$HOME/\~}"
  fi
}

# ----------------------------------------------------------------- platform + deps

OS="$(uname -s)"
case "$OS" in
  Darwin) PLATFORM=macos ;;
  Linux)  PLATFORM=linux ;;
  *) die "unsupported platform: $OS" ;;
esac
[ -n "${WSL_DISTRO_NAME:-}" ] && PLATFORM=wsl

say "Flava on $PLATFORM, mode=$MODE, repo=$FLAVA_DIR"

# Package names differ; bat is `bat` on brew and `bat` on apt, but apt installs the binary
# as `batcat`. shell/common.sh handles that at runtime, so we only care about the package.
PKGS_COMMON="git python3 fastfetch lsd bat zoxide fzf ripgrep"

install_deps() {
  [ "$WITH_DEPS" = 1 ] || { warn "skipping packages (--no-deps)"; return 0; }
  say "Packages"

  if [ "$PLATFORM" = macos ]; then
    command -v brew >/dev/null 2>&1 || die "Homebrew not found. Install it from https://brew.sh and re-run."
    # shellcheck disable=SC2086
    run brew install $PKGS_COMMON thefuck || warn "some brew packages failed; see output above"
  else
    command -v apt-get >/dev/null 2>&1 || {
      warn "no apt-get here. Install these by hand: $PKGS_COMMON thefuck"
      return 0
    }
    run sudo apt-get update -qq
    # shellcheck disable=SC2086
    run sudo apt-get install -y $PKGS_COMMON python3-pip || warn "some apt packages failed; see output above"
    command -v thefuck >/dev/null 2>&1 || run pipx install thefuck 2>/dev/null || \
      warn "thefuck not installed (try: pipx install thefuck)"
  fi

  for tool in git python3 fastfetch lsd zoxide; do
    command -v "$tool" >/dev/null 2>&1 || warn "$tool still missing after install"
  done
}

POKEMON_DONE=0

install_pokemon() {
  # Called from both the fastfetch and the shell component, so it has to be idempotent
  # within a single run. Testing the symlink path rather than `command -v`, because on a
  # fresh machine ~/.local/bin is not on the installer's own PATH yet and the second call
  # would sail past the guard and "back up" the symlink the first call just made.
  [ "$POKEMON_DONE" = 1 ] && return 0
  POKEMON_DONE=1

  local bin="$HOME/.local/bin/pokemon-colorscripts"
  if [ -e "$bin" ] || command -v pokemon-colorscripts >/dev/null 2>&1; then
    ok "pokemon-colorscripts already installed"
    return 0
  fi

  say "pokemon-colorscripts (about 50MB of sprites)"
  local opt="$HOME/.local/opt/pokemon-colorscripts"
  run mkdir -p "$HOME/.local/opt" "$HOME/.local/bin"
  if [ ! -d "$opt" ]; then
    run git clone --depth 1 https://gitlab.com/phoneybadger/pokemon-colorscripts.git "$opt" \
      || { warn "clone failed; the terminal will just skip the Pokemon"; return 0; }
  fi
  run chmod +x "$opt/pokemon-colorscripts.py"
  run ln -s "$opt/pokemon-colorscripts.py" "$bin"
  ok "pokemon-colorscripts installed"
}

# --------------------------------------------------------------------------- claude

install_claude() {
  say "Claude Code"
  local dst="$HOME/.claude"
  run mkdir -p "$dst"

  install_path "$FLAVA_DIR/claude/CLAUDE.md"             "$dst/CLAUDE.md"
  install_path "$FLAVA_DIR/claude/statusline.py"         "$dst/statusline.py"
  install_path "$FLAVA_DIR/claude/model-thresholds.json" "$dst/model-thresholds.json"
  install_path "$FLAVA_DIR/claude/hooks"                 "$dst/hooks"
  install_path "$FLAVA_DIR/claude/docs"                  "$dst/docs"

  # Skills go one by one, so skills installed from a marketplace on this machine survive.
  run mkdir -p "$dst/skills"
  local skill
  for skill in "$FLAVA_DIR"/claude/skills/*/; do
    install_path "${skill%/}" "$dst/skills/$(basename "$skill")"
  done

  # handoff-frank writes here and expects it to exist.
  run mkdir -p "$dst/handoffs"

  merge_settings
}

merge_settings() {
  local template="$FLAVA_DIR/claude/settings.template.json"
  local target="$HOME/.claude/settings.json"

  if [ "$DRY_RUN" = 1 ]; then
    printf '  [dry-run] merge %s into %s\n' "$template" "$target"
    return 0
  fi

  [ -f "$target" ] && backup "$target"

  # Template keys win. Any key already in settings.json that the template does not mention
  # is preserved, so a machine-local permission list or MCP setting is not lost.
  HOME_DIR="$HOME" TEMPLATE="$template" TARGET="$target" \
  BACKUP="$BACKUP_DIR/.claude/settings.json" python3 - <<'PY'
import json, os

home = os.environ["HOME_DIR"]
template_path = os.environ["TEMPLATE"]
target_path = os.environ["TARGET"]
backup_path = os.environ["BACKUP"]

with open(template_path, encoding="utf-8") as fh:
    template = json.loads(fh.read().replace("__HOME__", home))

existing = {}
if os.path.isfile(backup_path):
    try:
        with open(backup_path, encoding="utf-8") as fh:
            existing = json.load(fh)
    except Exception:
        existing = {}

def merge(base, override):
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = merge(out[key], value)
        else:
            out[key] = value
    return out

result = merge(existing, template)
os.makedirs(os.path.dirname(target_path), exist_ok=True)
with open(target_path, "w", encoding="utf-8") as fh:
    json.dump(result, fh, indent=2)
    fh.write("\n")
print("  \033[32m✓\033[0m settings.json written (hook paths absolute for this machine)")
PY
}

# ------------------------------------------------------------------------ fastfetch

install_fastfetch() {
  say "fastfetch"
  local dst="$HOME/.config/fastfetch"
  run mkdir -p "$dst"
  install_path "$FLAVA_DIR/fastfetch/config.jsonc" "$dst/config.jsonc"
  install_path "$FLAVA_DIR/fastfetch/logos"        "$dst/logos"
}

# ---------------------------------------------------------------------------- shell

install_shell() {
  say "Shell"
  local marker="# >>> flava >>>"
  local line="[ -f \"$FLAVA_DIR/shell/common.sh\" ] && . \"$FLAVA_DIR/shell/common.sh\""
  local rc

  for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    # Only touch an rc file whose shell actually exists on this machine.
    case "$rc" in
      *zshrc) command -v zsh >/dev/null 2>&1 || continue ;;
      *bashrc) command -v bash >/dev/null 2>&1 || continue ;;
    esac

    if [ -f "$rc" ] && grep -qF "$marker" "$rc"; then
      ok "already sourced in ${rc/#$HOME/\~}"
      continue
    fi

    if [ "$DRY_RUN" = 1 ]; then
      printf '  [dry-run] append flava block to %s\n' "$rc"
      continue
    fi

    {
      printf '\n%s\n' "$marker"
      printf '%s\n' "$line"
      printf '%s\n' "# <<< flava <<<"
    } >> "$rc"
    ok "sourced from ${rc/#$HOME/\~}"
  done
}

# -------------------------------------------------------------------------- wezterm

install_wezterm() {
  say "WezTerm"
  if ! command -v wezterm >/dev/null 2>&1 && [ "$PLATFORM" != wsl ]; then
    warn "wezterm not found; installing the config anyway"
  fi
  if [ "$PLATFORM" = wsl ]; then
    warn "on WSL, wezterm.exe reads the config from the WINDOWS home, not this one."
    warn "copy wezterm/wezterm.lua to C:\\Users\\<you>\\.wezterm.lua yourself."
    return 0
  fi
  install_path "$FLAVA_DIR/wezterm/wezterm.lua" "$HOME/.wezterm.lua"
}

# -------------------------------------------------------------------------- ghostty

install_ghostty() {
  say "Ghostty"
  # Ghostty replaces WezTerm on macOS. It reads ~/.config/ghostty/config. No plugin
  # system, so the resurrect keybindings are gone; the config comments say what replaced
  # them. Installed even without the app present, same as the wezterm step.
  if ! command -v ghostty >/dev/null 2>&1 && [ ! -d "/Applications/Ghostty.app" ]; then
    warn "ghostty not found; installing the config anyway"
  fi
  install_path "$FLAVA_DIR/ghostty/config" "$HOME/.config/ghostty/config"
}

# --------------------------------------------------------------------------- verify

verify() {
  say "Verify"

  if [ "$DRY_RUN" = 1 ]; then
    printf '  [dry-run] skipping checks\n'
    return 0
  fi

  if python3 "$HOME/.claude/hooks/tests/test_guards.py" >/tmp/flava-guards.log 2>&1; then
    ok "$(tail -1 /tmp/flava-guards.log)"
  else
    warn "guard suite failed — see /tmp/flava-guards.log"
  fi

  if echo '{}' | python3 "$HOME/.claude/statusline.py" >/dev/null 2>&1; then
    ok "statusline runs and exits 0 on an empty payload"
  else
    warn "statusline failed on an empty payload"
  fi

  command -v fastfetch >/dev/null 2>&1 && ok "fastfetch present" || warn "fastfetch missing"

  # Check the path as well as PATH: ~/.local/bin gets added by shell/common.sh, which the
  # next login shell sources. This process never had it.
  if [ -e "$HOME/.local/bin/pokemon-colorscripts" ] \
     || command -v pokemon-colorscripts >/dev/null 2>&1; then
    ok "pokemon-colorscripts present"
  else
    warn "pokemon-colorscripts missing"
  fi
}

# ----------------------------------------------------------------------------- main

install_deps
wants claude    && install_claude
wants fastfetch && { install_fastfetch; install_pokemon; }
wants shell     && { install_shell; install_pokemon; }
wants wezterm   && install_wezterm
wants ghostty   && install_ghostty
[ -z "$ONLY" ] && verify

echo
say "Done."
[ -d "$BACKUP_DIR" ] && echo "  Replaced files are in $BACKUP_DIR"
echo "  Open a new terminal, or run: exec \$SHELL -l"
echo "  Set your git identity: git config --global user.name / user.email"
exit 0

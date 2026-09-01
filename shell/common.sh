# Flava shared shell config — works under bash and zsh, macOS and Linux/WSL.
#
# Sourced from ~/.bashrc and/or ~/.zshrc by install.sh. Everything here is guarded by a
# `command -v` check, so a machine missing a tool loses that one alias and nothing else.

# Interactive shells only. Sourcing this from a script must be a no-op.
case $- in
  *i*) ;;
  *) return 0 ;;
esac

# ---------------------------------------------------------------- platform detection

FLAVA_OS="$(uname -s)"
FLAVA_IS_WSL=0
[ -n "${WSL_DISTRO_NAME:-}" ] && FLAVA_IS_WSL=1

# ------------------------------------------------------------------------------ PATH

for d in "$HOME/.local/bin" "$HOME/.cargo/bin" "/opt/homebrew/bin" "/usr/local/bin"; do
  case ":$PATH:" in
    *":$d:"*) ;;
    *) [ -d "$d" ] && PATH="$d:$PATH" ;;
  esac
done
export PATH

# --------------------------------------------------------------------------- history

HISTSIZE=10000
if [ -n "${ZSH_VERSION:-}" ]; then
  SAVEHIST=20000
  setopt HIST_IGNORE_ALL_DUPS SHARE_HISTORY APPEND_HISTORY
else
  HISTFILESIZE=20000
  HISTCONTROL=ignoreboth
  shopt -s histappend checkwinsize
fi

# ------------------------------------------------------------------------ bat as cat
# Debian and Ubuntu ship the binary as `batcat` because the name `bat` was taken.

if command -v bat >/dev/null 2>&1; then
  FLAVA_BAT=bat
elif command -v batcat >/dev/null 2>&1; then
  FLAVA_BAT=batcat
else
  FLAVA_BAT=""
fi

if [ -n "$FLAVA_BAT" ]; then
  alias cat="$FLAVA_BAT"
  export MANPAGER="sh -c 'col -bx | $FLAVA_BAT -l man -p'"
fi

# ------------------------------------------------------------------- ls, tree, files

if command -v lsd >/dev/null 2>&1; then
  alias ls='lsd --tree --depth 1'
  alias ll='lsd -l --tree --depth 1'
  alias la='lsd -la --tree --depth 1'
  alias lt='lsd --tree'
else
  # macOS ls wants -G, GNU ls wants --color=auto
  if [ "$FLAVA_OS" = "Darwin" ]; then
    alias ls='ls -G'
  else
    alias ls='ls --color=auto'
  fi
  alias ll='ls -alF'
  alias la='ls -A'
  alias lt='ls -R'
fi

alias grep='grep --color=auto'

# ------------------------------------------------------------------------- navigation

if command -v zoxide >/dev/null 2>&1; then
  if [ -n "${ZSH_VERSION:-}" ]; then
    eval "$(zoxide init zsh)"
  else
    eval "$(zoxide init bash)"
  fi
  alias cd='z'
fi

if command -v fzf >/dev/null 2>&1 && [ -n "$FLAVA_BAT" ]; then
  alias fzf="fzf --preview '$FLAVA_BAT --color=always {}'"
fi

# ----------------------------------------------------------------------- corrections

if command -v thefuck >/dev/null 2>&1; then
  eval "$(thefuck --alias)"
fi

# ---------------------------------------------------------------------------- extras

command -v spotify_player >/dev/null 2>&1 && alias spotify='spotify_player'

# WSL mounts Windows drives world-writable, which paints directories with an unreadable
# green background. Force plain bright blue instead.
if [ "$FLAVA_IS_WSL" = "1" ]; then
  export LS_COLORS="${LS_COLORS}:ow=01;34"
fi

# ----------------------------------------------------------------------------- prompt
# user@host:path (branch)$ — same look in both shells, different syntax to get there.

flava_git_branch() {
  git branch 2>/dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}

if [ -n "${ZSH_VERSION:-}" ]; then
  setopt PROMPT_SUBST
  PROMPT='%F{green}%n@%m%f:%F{blue}%~%f%F{yellow}$(flava_git_branch)%f%# '
else
  PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[01;33m\]$(flava_git_branch)\[\033[00m\]\$ '
fi

# ------------------------------------------------------------------- terminal opener
# A random Pokemon on every new interactive shell. Set FLAVA_NO_POKEMON=1 to silence it.

if [ -z "${FLAVA_NO_POKEMON:-}" ] && command -v pokemon-colorscripts >/dev/null 2>&1; then
  pokemon-colorscripts --no-title -r
fi

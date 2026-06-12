# ZenvX OS default shell configuration (applied to all users via /etc/skel)

# If not running interactively, do nothing
case $- in
	*i*) ;;
	*) return ;;
esac

# --- Environment ---
export TERM=xterm-256color
export PATH="/usr/local/bin:/opt/zenvx:$PATH"
export PYTHONPATH="/opt/zenvx"

# --- History ---
HISTSIZE=2000
HISTFILESIZE=5000
HISTCONTROL=ignoredups:erasedups
shopt -s histappend

# --- Prompt: user@host:dir <cyan-triangle> ---
ZENVX_CYAN='\[\e[38;2;0;255;204m\]'
ZENVX_RESET='\[\e[0m\]'
PS1="\u@\h:\w ${ZENVX_CYAN}\xe2\x96\xb6${ZENVX_RESET} "

# --- Aliases ---
alias ls='ls --color=auto'
alias ll='ls -lh --color=auto'
alias grep='grep --color=auto'
alias agent='zenvx'
alias dashboard='python3 /opt/zenvx/monitoring/dashboard.py'
alias logs='sudo journalctl -u zenvx-agent -f'
alias status='sudo systemctl status zenvx-agent'
alias restart-agent='sudo systemctl restart zenvx-agent'

# --- Message of the day ---
if [ -f /etc/zenvx/motd ]; then
	printf '%b\n' "$(cat /etc/zenvx/motd)"
fi

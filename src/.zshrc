# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Lines configured by zsh-newuser-install
HISTFILE=~/.histfile
# Raised from the zsh-newuser-install default of 1000, which was too short to
# keep even a year of history.
HISTSIZE=50000
SAVEHIST=50000
bindkey -v
# End of lines configured by zsh-newuser-install
# The following lines were added by compinstall
zstyle :compinstall filename '/home/brian/.zshrc'

autoload -Uz compinit
compinit
# End of lines added by compinstall

source /usr/share/zsh-theme-powerlevel10k/powerlevel10k.zsh-theme

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

#
# Plugins!
#
source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
source /usr/share/zsh/plugins/zsh-history-substring-search/zsh-history-substring-search.zsh

#
# autosuggest config
#
ZSH_AUTOSUGGEST_STRATEGY=(history completion)

#
# history-substring-search config
#
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down
# vim mode
bindkey -M vicmd 'k' history-substring-search-up
bindkey -M vicmd 'j' history-substring-search-down

# Custom Aliases
alias la="ls -a"
alias ll="ls -l"
alias lla="ls -la"

# Be Kind Alias
# https://www.explainxkcd.com/wiki/index.php/149:_Sandwich
alias please="sudo"

# Workspace Aliases
alias wg="cd ~/workspace-git/"

# Claude Home Alias
alias ch="cd ~/claude-home && claude"

# Application Aliases
alias vim="nvim"
alias lxappearance="GDK_BACKEND=x11 lxappearance"



# Pip Install Program Location
export PATH="$HOME/.local/bin:$PATH"

# Nvm Source -- lazy loaded.
#
# Sourcing init-nvm.sh directly cost ~520 ms on every single shell start
# (measured 668 ms -> 145 ms with it removed), which was 78% of zsh startup.
# Most of that is nvm.sh plus the bash-style completion script it pulls in.
# Instead, define stubs that load nvm the first time one of its commands is
# actually used.
#
# Consequence: powerlevel10k's `nvm` prompt segment needs nvm's shell functions
# to report a version, so it stays hidden until nvm loads in that shell.
export NVM_DIR="$HOME/.nvm"
_load_nvm() {
    unset -f nvm node npm npx corepack 2>/dev/null
    source /usr/share/nvm/init-nvm.sh
}
nvm()      { _load_nvm; nvm "$@"; }
node()     { _load_nvm; node "$@"; }
npm()      { _load_nvm; npm "$@"; }
npx()      { _load_nvm; npx "$@"; }
corepack() { _load_nvm; corepack "$@"; }

#
# Import pywal bg generated colorscheme
#
# Asynchronously
# &   # Run the process in the background.
# ( ) # Hide shell job control messages.
# Not supported in the "fish" shell.
# (cat ~/.cache/wal/sequences &)
# Syncronously
cat ~/.cache/wal/sequences


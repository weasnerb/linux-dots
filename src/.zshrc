# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Lines configured by zsh-newuser-install
HISTFILE=~/.histfile
HISTSIZE=1000
SAVEHIST=1000
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

# Application Aliases
alias vim="nvim"
alias code="vscodium"
alias lxappearance="GDK_BACKEND=x11 lxappearance"



# Pip Install Program Location
export PATH="$HOME/.local/bin:$PATH"

# Nvm Source
source /usr/share/nvm/init-nvm.sh

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


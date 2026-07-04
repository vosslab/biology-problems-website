# source_me.sh - shell environment for running this repo's Python.
# Usage: source source_me.sh && python3 ...
# This is a bash script sourced into your shell, not run directly.

# Require bash: the checks below and the repo's tab-indented shell style are
# bash-specific. Fail loudly rather than misbehave under another shell.
set | grep -q '^BASH_VERSION=' || echo "use bash for your shell"
set | grep -q '^BASH_VERSION=' || exit 1

# Source ~/.bashrc FIRST, before any repo-specific environment extension below.
# ~/.bashrc applies local shell setup and clears PYTHONPATH, so anything that
# sets PYTHONPATH must run after this line.
source ~/.bashrc

# Python runtime defaults: unbuffered output, no .pyc/__pycache__ files.
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# --- Sibling repositories imported at runtime --------------------------------
# These packages live in adjacent working copies rather than pip installs. Add
# each to PYTHONPATH so `python3 ...` and the bbq_converter.py subprocess can
# import them. Runs after ~/.bashrc, which clears PYTHONPATH.
#   local-llm-wrapper : LLM client (also on PyPI as local-llm-wrapper)
#   qti-package-maker : qti_package_maker package used by bbq_converter.py
prepend_pythonpath() {
	# Prepend a directory to PYTHONPATH when it exists and is not already listed.
	local dir="$1"
	[ -d "$dir" ] || return 0
	case ":${PYTHONPATH:-}:" in
		*":$dir:"*) ;;
		*) export PYTHONPATH="$dir${PYTHONPATH:+:$PYTHONPATH}" ;;
	esac
}

prepend_pythonpath "$HOME/nsh/local-llm-wrapper"
prepend_pythonpath "$HOME/nsh/PROBLEMS/qti-package-maker"
unset -f prepend_pythonpath

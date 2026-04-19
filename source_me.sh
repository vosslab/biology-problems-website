set | grep -q '^BASH_VERSION=' || echo "use bash for your shell"
set | grep -q '^BASH_VERSION=' || exit 1

# Set Python environment optimizations
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

source ~/.bashrc

# Vendored local-llm-wrapper (also on PyPI as local-llm-wrapper).
# Must come after sourcing ~/.bashrc, which clears PYTHONPATH.
# Drop this line once the PyPI install is pinned in pip_requirements.txt.
export PYTHONPATH="$HOME/nsh/local-llm-wrapper:${PYTHONPATH:-}"

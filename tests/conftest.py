"""Pytest config: put the repo root and tools/ on sys.path so tests
can import bioproblems_site.* and tools scripts without requiring
`source source_me.sh`.

Repo root comes from the shared tests/git_file_utils.py helper, which
calls `git rev-parse --show-toplevel` per docs/REPO_STYLE.md. Every
other test file in this repo already uses git_file_utils for the
same job; this conftest follows that convention.
"""

# Standard Library
import os
import sys

# local repo modules
import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)

# tools/ scripts are not a Python package; add the directory so
# tests can import them as top-level modules (e.g. `import dump_topics_csv`).
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
if os.path.isdir(TOOLS_DIR) and TOOLS_DIR not in sys.path:
	sys.path.insert(0, TOOLS_DIR)

"""Pytest config: put the repo root on sys.path so tests can import
bioproblems_site.* without requiring `source source_me.sh`.
"""

# Standard Library
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)

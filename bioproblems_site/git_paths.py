"""Repository-root discovery and display paths."""

import os
import subprocess
import functools


#============================================
@functools.lru_cache(maxsize=1)
def get_repo_root() -> str:
	"""Return the absolute repo root. Falls back to this module's
	directory when not inside a git checkout.
	"""
	result = subprocess.run(
		["git", "rev-parse", "--show-toplevel"],
		capture_output=True,
		text=True,
		check=False,
	)
	if result.returncode == 0:
		repo_root = result.stdout.strip()
		if repo_root:
			return repo_root
	return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#============================================
def display_path(file_path: str | os.PathLike[str]) -> str:
	"""Format a filesystem path relative to the current working directory."""
	path_value = os.fspath(file_path)
	if not path_value:
		return path_value
	absolute_path = os.path.abspath(path_value)
	try:
		return os.path.relpath(absolute_path, start=os.getcwd())
	except ValueError:
		# Paths on a different volume cannot be made relative.
		return absolute_path

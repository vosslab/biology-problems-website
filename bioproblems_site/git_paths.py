"""Git-aware path helpers: repo root discovery, case-canonicalization
against tracked paths, and bbq_converter.py resolution. Extracted from
the former root-level generate_topic_pages.py.
"""

# Standard Library
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
	return os.path.dirname(os.path.abspath(__file__))


@functools.lru_cache(maxsize=1)
def get_git_tracked_paths() -> dict:
	"""Return {lowercase_path: actual_path} for every git-tracked file."""
	tracked = {}
	result = subprocess.run(
		["git", "ls-files"],
		capture_output=True,
		text=True,
		check=False,
	)
	if result.returncode != 0:
		return tracked
	for line in result.stdout.splitlines():
		if not line:
			continue
		lower_path = line.lower()
		if lower_path in tracked and tracked[lower_path] != line:
			# Ambiguous case-only match; keep first seen.
			continue
		tracked[lower_path] = line
	return tracked


#============================================
def canonicalize_git_path(file_path: str) -> str:
	"""Return the path as git sees it (canonical case), else input unchanged."""
	repo_root = get_repo_root()
	relative_path = os.path.relpath(file_path, repo_root)
	tracked = get_git_tracked_paths().get(relative_path.lower())
	if not tracked:
		return file_path
	return os.path.join(repo_root, tracked)


#============================================
def git_rm(path: str) -> None:
	"""Stage the removal of a tracked file with git rm.

	Args:
		path (str): The tracked file to remove.
	"""
	subprocess.run(
		["git", "rm", "--quiet", path],
		capture_output=True,
		text=True,
		check=True,
	)


#============================================
def git_mv(src: str, dst: str) -> None:
	"""Stage a tracked-file move with git mv, preserving history.

	Args:
		src (str): The tracked source path.
		dst (str): The destination path.
	"""
	subprocess.run(
		["git", "mv", src, dst],
		capture_output=True,
		text=True,
		check=True,
	)


#============================================
def tracked_paths_set() -> set:
	"""Return the set of absolute paths git currently tracks.

	Built once per reconcile run and injected into each reconcile_topic
	call so tracked-vs-untracked is decided without repeated git calls.

	Returns:
		set: Absolute paths of every git-tracked file.
	"""
	repo_root = get_repo_root()
	tracked = set()
	result = subprocess.run(
		["git", "ls-files"],
		capture_output=True,
		text=True,
		check=False,
	)
	if result.returncode != 0:
		return tracked
	# Each line is a repo-root-relative path; store the absolute form
	for line in result.stdout.splitlines():
		if not line:
			continue
		tracked.add(os.path.realpath(os.path.join(repo_root, line)))
	return tracked


#============================================
def find_bbq_converter() -> str:
	"""Return an absolute path to bbq_converter.py or empty string."""
	repo_root = get_repo_root()
	candidates = [
		os.path.join(repo_root, "bbq_converter.py"),
		os.path.join(repo_root, "..", "qti_package_maker", "tools", "bbq_converter.py"),
		os.path.join(os.path.expanduser("~"), "nsh", "PROBLEM", "qti_package_maker", "tools", "bbq_converter.py"),
		os.path.join(os.path.expanduser("~"), "nsh", "qti_package_maker", "tools", "bbq_converter.py"),
	]
	for candidate in candidates:
		if os.path.isfile(candidate):
			return os.path.abspath(candidate)
	return ""

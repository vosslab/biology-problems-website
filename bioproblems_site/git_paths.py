"""Repository-root discovery, display paths, and converter resolution."""

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


#============================================
def find_native_bbq_converter() -> str:
	"""Resolve the required sibling Rust release converter, with no fallback."""
	binary = os.path.abspath(os.path.join(
		get_repo_root(), "..", "qti-package-maker-rs", "target", "release", "bbq-converter",
	))
	if not os.path.isfile(binary):
		raise FileNotFoundError(f"Required Rust BBQ converter is missing: {binary}")
	if not os.access(binary, os.X_OK):
		raise PermissionError(f"Rust BBQ converter is not executable: {binary}")
	return binary

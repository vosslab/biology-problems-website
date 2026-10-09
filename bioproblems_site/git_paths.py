"""Repository-root discovery, display paths, and converter resolution."""

import os
import subprocess
import functools
import platform


#============================================
class NativeConverterUnavailableError(RuntimeError):
	"""The vendored native converter is unavailable for this host."""


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
	"""Resolve BPW's vendored executable for the current operating system and CPU.

	Returns:
		The executable in BPW's vendor directory; no source checkout is required.
	"""
	host = f"{platform.system().lower()}-{platform.machine().lower()}"
	vendor_dir = os.path.join(get_repo_root(), "vendor", "qpm-native")
	binary = os.path.join(vendor_dir, host, "bbq-converter")
	if not os.path.isfile(binary):
		available = []
		if os.path.isdir(vendor_dir):
			available = sorted(name for name in os.listdir(vendor_dir)
				if os.path.isfile(os.path.join(vendor_dir, name, "bbq-converter")))
		raise NativeConverterUnavailableError(
			f"No vendored Rust BBQ converter for {host}. "
			f"Available platforms: {', '.join(available) or 'none'}. "
			"Restore the vendor directory from Git or ask a maintainer to refresh a "
			"compatible binary with devel/vendor_qti_wasm.py --native-only. "
			"Existing self-tests are unchanged."
		)
	if not os.access(binary, os.X_OK):
		raise NativeConverterUnavailableError(
			f"Vendored converter is not executable: {binary}. "
			"Restore its executable permission from Git."
		)
	return binary

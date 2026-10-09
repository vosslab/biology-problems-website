"""Repository-root discovery, display paths, and converter resolution."""

import os
import subprocess
import functools
import json
import shutil


#============================================
class NativeConverterUnavailableError(RuntimeError):
	"""Native conversion cannot proceed after dependency recovery."""


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
	"""Prepare the converter from QPM_ROOT or the sibling QPM checkout.

	Returns:
		Executable path supplied by Cargo, independent of target layout.
	"""
	qpm_root = os.environ.get("QPM_ROOT", "").strip() or "../qti-package-maker-rs"
	qpm_root = os.path.abspath(os.path.join(get_repo_root(), os.path.expanduser(qpm_root)))
	manifest = os.path.join(qpm_root, "Cargo.toml")
	if not os.path.isfile(manifest) or not shutil.which("cargo"):
		raise NativeConverterUnavailableError(
			f"Cannot prepare the Rust BBQ converter from {qpm_root}. "
			"Install Cargo and clone QPM beside BPW, or set QPM_ROOT to its checkout. "
			"Existing self-tests are unchanged; mkdocs build can still serve them."
		)
	return _build_native_bbq_converter(manifest)


#============================================
@functools.lru_cache(maxsize=1)
def _build_native_bbq_converter(manifest: str) -> str:
	"""Prepare QPM once before the bank workers start.

	Args:
		manifest: Cargo manifest in the trusted sibling QPM checkout.

	Returns:
		The executable artifact path reported by a successful Cargo build.
	"""
	print("Preparing Rust BBQ converter with Cargo...", flush=True)
	# Run in QPM so Cargo honors its local configuration and target directory.
	command = [
		"cargo", "build", "--locked", "--release", "-p", "qti-cli",
		"--bin", "bbq-converter", "--message-format=json-render-diagnostics",
	]
	completed = subprocess.run(
		command, cwd=os.path.dirname(manifest), stdout=subprocess.PIPE, text=True, check=False,
	)
	if completed.returncode == 0:
		for line in completed.stdout.splitlines():
			message = json.loads(line)
			if message.get("reason") == "compiler-artifact" and message.get("executable"):
				if message["target"]["name"] == "bbq-converter":
					return message["executable"]
	raise NativeConverterUnavailableError(
		"Cargo could not prepare bbq-converter. Resolve the Cargo diagnostics above "
		"and rerun the website build. Existing self-tests are unchanged."
	)

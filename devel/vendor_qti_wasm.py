#!/usr/bin/env python3
"""Refresh BPW's native QPM executable and browser package with provenance."""

# Standard Library
import hashlib
import json
import pathlib
import shutil
import argparse
import os
import platform
import subprocess
import tempfile


#============================================
def vendor_wasm(repo: pathlib.Path, source_repo: pathlib.Path) -> None:
	"""Copy the complete built browser package and record consumed-file hashes.

	Args:
		repo: BPW repository root.
		source_repo: QPM source repository root.
	"""
	dist = source_repo / "packages" / "qti-wasm" / "dist"
	if not (dist / "generated" / "qti_wasm_bg.wasm").is_file():
		raise FileNotFoundError(f"Build the WASM package first: {dist}")
	destination = repo / "site_docs" / "assets" / "qti_wasm"
	if destination.exists():
		shutil.rmtree(destination)
	shutil.copytree(dist, destination)
	# Hash the consumed bytes; the checkout revision does not certify a local build.
	hashes = {}
	for artifact in sorted(destination.rglob("*")):
		if artifact.is_file():
			name = artifact.relative_to(destination).as_posix()
			hashes[name] = hashlib.sha256(artifact.read_bytes()).hexdigest()
	provenance = {
		"sourceCommit": None,
		"sourcePath": "packages/qti-wasm/dist",
		"provenanceNote": (
			"Local built artifacts; no source revision was supplied. "
			"Artifact hashes identify consumed bytes."
		),
		"sha256": hashes,
	}
	(destination / "source.json").write_text(json.dumps(provenance, indent=2) + "\n")
	print(f"Vendored QTI WASM from {dist}; source revision unknown")


#============================================
def vendor_native(repo: pathlib.Path, source_repo: pathlib.Path) -> None:
	"""Build, verify, and atomically install the supported native converter.

	Args:
		repo: BPW repository root.
		source_repo: QPM source repository root used only during refresh.
	"""
	host = f"{platform.system().lower()}-{platform.machine().lower()}"
	if host != "darwin-arm64":
		raise RuntimeError(f"Native refresh supports macOS ARM64; this host is {host}.")
	command = [
		"cargo", "build", "--locked", "--release", "-p", "qti-cli",
		"--bin", "bbq-converter", "--target", "aarch64-apple-darwin",
		"--message-format=json-render-diagnostics",
	]
	print("Building QPM native converter...", flush=True)
	completed = subprocess.run(
		command, cwd=source_repo, stdout=subprocess.PIPE, text=True, check=True,
	)
	binary = None
	for line in completed.stdout.splitlines():
		message = json.loads(line)
		if message.get("reason") == "compiler-artifact" and message.get("executable"):
			if message["target"]["name"] == "bbq-converter":
				binary = pathlib.Path(message["executable"])
	if binary is None:
		raise RuntimeError("Cargo succeeded but reported no bbq-converter executable.")
	subprocess.run([str(binary), "--help"], capture_output=True, text=True, check=True)
	metadata = subprocess.run(
		["cargo", "metadata", "--locked", "--no-deps", "--format-version=1"],
		cwd=source_repo, capture_output=True, text=True, check=True,
	)
	version = next(package["version"] for package in json.loads(metadata.stdout)["packages"]
		if package["name"] == "qti-cli")
	revision = subprocess.run(
		["git", "rev-parse", "HEAD"], cwd=source_repo,
		capture_output=True, text=True, check=True,
	).stdout.strip()
	dirty = subprocess.run(
		["git", "status", "--porcelain", "--untracked-files=normal"], cwd=source_repo,
		capture_output=True, text=True, check=True,
	).stdout.strip()
	provenance = {
		"sourceRepository": "https://github.com/vosslab/qti-package-maker-rs",
		"sourceCommit": revision,
		"sourceDirty": bool(dirty),
		"provenanceNote": "The commit identifies the checkout; SHA256 identifies the built bytes.",
		"target": "aarch64-apple-darwin",
		"version": version,
		"buildCommand": command,
		"sha256": {"bbq-converter": hashlib.sha256(binary.read_bytes()).hexdigest()},
	}
	destination = repo / "vendor" / "qpm-native" / host
	destination.mkdir(parents=True, exist_ok=True)
	# Publish only after compilation and execution succeed; preserve the old binary on failure.
	with tempfile.TemporaryDirectory(prefix=".refresh-", dir=destination) as staging:
		staged = pathlib.Path(staging)
		shutil.copy2(binary, staged / "bbq-converter")
		(staged / "bbq-converter").chmod(0o755)
		(staged / "source.json").write_text(json.dumps(provenance, indent=2) + "\n")
		shutil.copy2(source_repo / "LICENSE.LGPL-3.0", staged / "LICENSE.LGPL-3.0")
		for artifact in staged.iterdir():
			os.replace(artifact, destination / artifact.name)
	print(f"Vendored {version} for {host} from {revision}; source dirty: {bool(dirty)}")


#============================================
def main() -> None:
	"""Refresh both QPM dependencies, or one explicitly selected artifact."""
	parser = argparse.ArgumentParser(description=__doc__)
	selection = parser.add_mutually_exclusive_group()
	selection.add_argument("--native-only", action="store_true", help="Build and vendor only the native converter")
	selection.add_argument("--wasm-only", action="store_true", help="Copy only the prebuilt browser package")
	args = parser.parse_args()
	repo = pathlib.Path(__file__).resolve().parents[1]
	configured = os.environ.get("QPM_ROOT", "").strip() or "../qti-package-maker-rs"
	source_repo = (repo / pathlib.Path(configured).expanduser()).resolve()
	if not args.wasm_only:
		vendor_native(repo, source_repo)
	if not args.native_only:
		vendor_wasm(repo, source_repo)


if __name__ == "__main__":
	main()

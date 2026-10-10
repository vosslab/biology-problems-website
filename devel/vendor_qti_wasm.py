#!/usr/bin/env python3
"""Build Rust QPM's browser package and refresh BPW's vendored copy."""

# Standard Library
import hashlib
import json
import pathlib
import shutil
import argparse
import os
import subprocess


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
def main() -> None:
	"""Build the QPM browser package before replacing BPW's current copy."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.parse_args()
	repo = pathlib.Path(__file__).resolve().parents[1]
	configured = os.environ.get("QPM_ROOT", "").strip() or "../qti-package-maker-rs"
	source_repo = (repo / pathlib.Path(configured).expanduser()).resolve()
	package = source_repo / "packages" / "qti-wasm"
	print(f"Building QTI WASM from {package}", flush=True)
	# ASVS 1.2.5: fixed argument lists, without shell interpolation.
	# check=True stops before vendoring if dependency installation or compilation fails.
	subprocess.run(["npm", "ci"], cwd=package, check=True)
	subprocess.run(["npm", "run", "build"], cwd=package, check=True)
	vendor_wasm(repo, source_repo)


if __name__ == "__main__":
	main()

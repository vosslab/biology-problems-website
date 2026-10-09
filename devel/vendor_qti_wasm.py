#!/usr/bin/env python3
"""Copy the sibling Rust QPM browser package and record artifact provenance."""

# Standard Library
import hashlib
import json
import pathlib
import shutil


#============================================
def main() -> None:
	"""Vendor the complete built distribution without modifying its sources."""
	repo = pathlib.Path(__file__).resolve().parents[1]
	source_repo = repo.parent / "qti-package-maker-rs"
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


if __name__ == "__main__":
	main()

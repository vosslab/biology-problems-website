"""Bind successfully generated question banks to the source actually used."""

import json
from pathlib import Path

import bioproblems_site.file_write as file_write
import bioproblems_site.source_history as source_history


#============================================
def capture(task: dict) -> dict | None:
	"""Capture the authored input before running a generator, including local edits."""
	path = source_history.authored_source(task)
	history = source_history.source_history(path)
	if history is None:
		return None
	revision = history["revisions"][0]
	captured = {
		"source_id": history["id"], "source_path": history["path"],
		"source_fingerprint": history["fingerprint"],
		"source_commit": revision["commit"] if history["clean"] else None,
		"source_updated": revision["date"] if history["clean"] else None,
	}
	return captured


#============================================
def record(task: dict, captured: dict | None, site_docs: Path) -> None:
	"""Publish provenance only for the exact successful output and unchanged input."""
	if captured is None:
		return
	if source_history.fingerprint(source_history.authored_source(task)) != captured["source_fingerprint"]:
		print("WARNING: source changed during generation; provenance was not recorded")
		return
	output = Path(task["output"]).resolve()
	if not output.is_relative_to(site_docs.resolve()) or not output.is_file():
		return
	path = site_docs / "assets/data/question_provenance.json"
	records = json.loads(path.read_text()) if path.exists() else {}
	key = output.relative_to(site_docs.resolve()).as_posix()
	records[key] = {**captured, "output_fingerprint": source_history.fingerprint(output)}
	file_write.write_text(path, json.dumps(records, indent=2, sort_keys=True) + "\n")

"""Protect collection counts, source lineage, and honest activity dates."""

import json
from pathlib import Path

import bioproblems_site.homepage_data as homepage_data
import bioproblems_site.homepage_render as homepage_render
import bioproblems_site.question_index as question_index
import bioproblems_site.question_provenance as provenance
import bioproblems_site.source_history as history


#============================================
def test_lineage_preserves_origin_and_ignores_unchanged_renames() -> None:
	log = (
		"\x1erename\t2026-10-01T12:00:00Z\n\nR100\told.py\tnew.py\n"
		"\x1eedit\t2026-07-12T12:00:00Z\n\nM\told.py\n"
		"\x1emove\t2026-01-04T12:00:00Z\n\nR100\tfirst.py\told.py\n"
		"\x1ecreate\t2024-10-25T12:00:00Z\n\nA\tfirst.py\n"
	)
	lineage = history.parse_lineage(log)
	assert lineage["origin"] == {"commit": "create", "path": "first.py", "date": "2024-10-25"}
	assert lineage["revisions"][0] == {"commit": "edit", "date": "2026-07-12"}
	assert lineage["aliases"] == ["first.py", "new.py", "old.py"]
	assert history.parse_lineage(log.split("\x1ecreate")[0])["origin"] is None


#============================================
def test_statistics_count_owned_placements_and_only_verified_updates(tmp_path: Path) -> None:
	site = tmp_path / "site_docs"
	bank = site / "biology/topic01/bbq-test-questions.txt"
	bank.parent.mkdir(parents=True)
	bank.write_text("MC\tone\n\nMC\ttwo\n")
	(bank.parent / "download.zip").write_bytes(b"not another question")
	entry = question_index.QuestionSetEntry("Biology", "Inheritance", "biology/topic01/index.md",
		"Real <question> (MC)", bank)
	orphan = bank.parent / "bbq-orphan-questions.txt"
	orphan.write_text("MC\torphan\n")
	orphan_entry = question_index.QuestionSetEntry("Biology", "Inheritance", entry.page_path,
		"Orphan", orphan)
	source = tmp_path / "upstream.py"
	sources = {source: {"id": "family", "origin": {"date": "2020-01-01"}}}
	key = bank.relative_to(site).as_posix()
	published = {key: {"source_id": "family", "source_updated": "2026-02-02",
		"output_fingerprint": history.fingerprint(bank)}}
	admissions = {"family": {"date": "2026-03-03", "baseline": False}}
	snapshot = homepage_data.summarize([entry, entry, orphan_entry], site,
		{bank: {source}}, sources, admissions, published)
	assert snapshot["totals"] == {"sets": 1, "subjects": 1, "topics": 1}
	assert snapshot["new"][0]["date"] == "2026-03-03"
	assert snapshot["updated"][0]["date"] == "2026-02-02"
	assert snapshot["diagnostics"]["unowned"] == [orphan.relative_to(site).as_posix()]
	markup = homepage_render.render(snapshot)
	assert "Real &lt;question&gt;" in markup and "Real <question>" not in markup
	bank.write_text("MC\tregenerated outside the pipeline\n")
	rebuilt = homepage_data.summarize([entry], site, {bank: {source}}, sources, admissions, published)
	assert rebuilt["updated"] == []


#============================================
def test_provenance_preserves_other_banks_and_rejects_changing_inputs(tmp_path: Path) -> None:
	site = tmp_path / "site_docs"
	bank = site / "biology/topic01/bbq-bank-questions.txt"
	bank.parent.mkdir(parents=True)
	bank.write_text("MC\tone\n")
	source = tmp_path / "source.py"
	source.write_text("original")
	task = {"script": str(source), "input_path": "", "output": str(bank)}
	captured = {"source_id": "family", "source_fingerprint": history.fingerprint(source),
		"source_updated": "2026-01-01"}
	path = site / "assets/data/question_provenance.json"
	path.parent.mkdir(parents=True)
	path.write_text(json.dumps({"other-bank": {"kept": True}}))
	provenance.record(task, captured, site)
	records = json.loads(path.read_text())
	assert records["other-bank"] == {"kept": True}
	assert records[bank.relative_to(site).as_posix()]["output_fingerprint"] == history.fingerprint(bank)
	source.write_text("changed while generator was running")
	bank.write_text("MC\tdifferent output\n")
	provenance.record(task, captured, site)
	assert json.loads(path.read_text()) == records


#============================================
def test_activity_keeps_all_dated_families_without_duplicate_formats() -> None:
	base = {"name": "Collection", "created": "2020-01-01", "added": "2026-02-01",
		"updated": None, "subject": "Biology", "topic": "Cells", "url": "biology/topic01/"}
	rows = [{**base, "family": str(index), "name": f"Collection {index}",
		"added": f"2026-02-{index + 1:02d}"} for index in range(7)]
	rows.extend([{**rows[0], "name": "Another format"},
		{**base, "family": "unknown", "added": None}])
	additions = homepage_data.recent(rows, "added")
	assert len(additions) == 7
	assert [row["date"] for row in additions] == sorted(
		{row["added"] for row in rows if row["added"]}, reverse=True)
	assert homepage_data.recent(rows, "updated") == []
	rows[0]["updated"] = "2026-03-01"
	rows[1]["updated"] = rows[1]["created"]
	assert [row["date"] for row in homepage_data.recent(rows, "updated")] == ["2026-03-01"]

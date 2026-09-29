"""Protect file identity, scoped catalog generation, and advisory freshness reporting."""

import io
import json
from pathlib import Path

import pytest

import bioproblems_site.build_stages as build_stages
import bioproblems_site.metadata as metadata
import bioproblems_site.question_finder as finder
import bioproblems_site.question_index as question_index
from bioproblems_site.build_contracts import BuildScope


#============================================
def test_catalog_preserves_files_types_qualifiers_and_topic_links(tmp_path: Path) -> None:
	"""Neither repeated names nor shared destinations can collapse source files."""
	sources = []
	for subject, filename, raw_type in (
		("biology", "bbq-gels-questions.txt", "MC"),
		("biology", "bbq-gels_numeric-questions.txt", "NUM"),
		("chemistry", "bbq-gels-questions.txt", "NUM"),
	):
		path = tmp_path / subject / "topic01" / filename
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(f"{raw_type}\tQuestion\n")
		sources.append(question_index.QuestionSetEntry(
			subject, "Gels", f"{subject}/topic01/index.md",
			"Protein <size> (With Ladder, MC/NUM)", path,
		))
	rows = finder.catalog_rows(sources, tmp_path)
	assert len({row["id"] for row in rows}) == len(sources)
	assert [row["type"] for row in rows] == ["MC", "NUM", "NUM"]
	assert all(row["name"] == "Protein <size> (With Ladder)" for row in rows)
	assert [row["url"] for row in rows] == [
		"../biology/topic01/", "../biology/topic01/", "../chemistry/topic01/",
	]


#============================================
def test_scoped_final_index_includes_other_subjects_and_honors_dry_run(
		tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
	) -> None:
	"""A subject-scoped build reports the catalog without restricting its corpus."""
	site_docs = tmp_path / "site_docs"
	topic = metadata.Topic("topic01", "Gels", "", None, True, None)
	hidden = metadata.Topic("topic02", "Hidden", "", None, False, None)
	subjects = {}
	for name in ("biology", "chemistry"):
		subjects[name] = metadata.Subject(name, name.title(), "", (topic, hidden))
		for topic_key in ("topic01", "topic02"):
			folder = site_docs / name / topic_key
			folder.mkdir(parents=True)
			(folder / "bbq-gels-questions.txt").write_text("MC\tQuestion\n")
	monkeypatch.setattr(build_stages, "DEFAULT_SITE_DOCS", site_docs)
	monkeypatch.setattr(metadata, "load_topics_metadata", lambda **kwargs: (subjects, tuple(subjects)))
	monkeypatch.setattr(build_stages.bbq_workflow, "load_task_ownership", lambda: ({}, set()))
	monkeypatch.setattr(build_stages.orphan_prune_module, "reconcile_all", lambda *a, **k: {})
	monkeypatch.setattr(build_stages.mkdocs_nav_module, "update_from_sources", lambda **k: None)
	monkeypatch.setattr(
		build_stages, "_write_subject_index", lambda *a: site_docs / "biology/index.md",
	)
	generated = []
	original_write = finder.write

	def capture_catalog(*args, **kwargs):
		text = original_write(*args, **kwargs)
		generated.extend(json.loads(text))
		return text

	monkeypatch.setattr(finder, "write", capture_catalog)
	outputs = build_stages.run_subject_indexes(BuildScope(subject="biology", dry_run=True))
	path = site_docs / "assets/data/question_finder.json"
	assert path in outputs and not path.exists()
	assert [row["subject"] for row in generated] == ["Biology", "Chemistry"]
	assert all(row["name"] == "Problem set: gels" for row in generated)


#============================================
def test_dependency_freshness_reads_tags_and_warns_without_updates(
		tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
	) -> None:
	"""A newer stable release warns, while equal versions remain current."""
	page = tmp_path / "finder.md"
	markup = (
		'<script src="https://cdn.datatables.net/3.1.2/js/dataTables.min.js"></script>\n'
		'<script src="https://cdn.datatables.net/columncontrol/2.1.2/'
		'js/dataTables.columnControl.min.js"></script>\n'
	)
	page.write_text(markup)
	versions = {"datatables.net": "3.1.10", "datatables.net-columncontrol": "2.1.2"}

	def publisher_response(url, **kwargs):
		package = url.split("/")[-2]
		return io.StringIO(json.dumps({"version": versions[package]}))

	monkeypatch.setattr(finder.urllib.request, "urlopen", publisher_response)
	monkeypatch.setattr(finder.time, "sleep", lambda duration: None)
	finder.check_dependencies(page)
	output = capsys.readouterr().out
	assert "WARNING: newer stable release: datatables.net: using 3.1.2; latest 3.1.10" in output
	assert "Current stable release: datatables.net-columncontrol" in output
	assert page.read_text() == markup

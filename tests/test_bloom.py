"""Protect compact filename identity and safe backend classification boundaries."""

from pathlib import Path
from types import SimpleNamespace

import pytest

import bioproblems_site.bloom as bloom
import bioproblems_site.bloom_evidence as evidence
import bioproblems_site.build_stages as stages
from bioproblems_site.build_contracts import BuildScope, TopicRef


#============================================
def test_compact_mapping_survives_regenerated_instances(tmp_path: Path,
		monkeypatch: pytest.MonkeyPatch) -> None:
	"""A regenerated bank keeps its labels and never needs the API or diagnostics."""
	source = tmp_path / "bbq-example-questions.txt"
	source.write_text("MC\tA newly generated instance\tYes\tCorrect\n")
	(tmp_path / bloom.CACHE_NAME).write_text(f"{source.name}: Apply, Procedural\n")
	monkeypatch.setattr(evidence, "entries", lambda root: [SimpleNamespace(source_path=source)])
	monkeypatch.setattr(bloom, "request", lambda *args: pytest.fail("cached bank contacted API"))
	assert bloom.classify(tmp_path) == set()
	bloom.save(tmp_path, bloom.load(tmp_path))
	assert (tmp_path / bloom.CACHE_NAME).read_text() == f"{source.name}: Apply, Procedural\n"


#============================================
def test_dry_run_and_failed_refresh_preserve_metadata(tmp_path: Path,
		monkeypatch: pytest.MonkeyPatch) -> None:
	"""Planning sends no requests; external failures cannot erase an existing pair."""
	source = tmp_path / "bbq-example-questions.txt"
	source.write_text("NUM\tCalculate a dilution\t10\t0\n")
	cache = tmp_path / bloom.CACHE_NAME
	cache.write_text(f"{source.name}: Apply, Procedural\n")
	monkeypatch.setattr(evidence, "entries", lambda root: [SimpleNamespace(source_path=source)])
	monkeypatch.setattr(evidence, "yaml_sources", lambda root: {})
	monkeypatch.setattr(Path, "home", lambda: tmp_path)
	key = tmp_path / ".config/jev/jev-api-key.txt"
	key.parent.mkdir(parents=True)
	key.write_text("test-credential")
	calls = []

	def fail_request(*args: object) -> tuple:
		calls.append(True)
		raise bloom.ClassificationError("JEV HTTP 503")

	monkeypatch.setattr(bloom, "request", fail_request)
	bloom.classify(tmp_path, refresh={source.name}, dry_run=True)
	assert not calls and not (tmp_path / "LOCAL_ONLY").exists()
	bloom.classify(tmp_path, refresh={source.name})
	assert calls and cache.read_text() == f"{source.name}: Apply, Procedural\n"


#============================================
def test_partial_or_unknown_classification_is_rejected(tmp_path: Path) -> None:
	"""The UI never receives half a pair or model-generated arbitrary labels."""
	for value in ("Apply", "Apply, Invented", "Apply, Procedural, Extra"):
		(tmp_path / bloom.CACHE_NAME).write_text(f"bbq-test-questions.txt: {value}\n")
		with pytest.raises(bloom.ClassificationError):
			bloom.load(tmp_path)
	with pytest.raises(bloom.ClassificationError):
		bloom.validate_response({"answers": {"cognitive": {"choice": "Apply"}}})


#============================================
def test_authored_yaml_and_readable_answer_fields_are_preserved(tmp_path: Path) -> None:
	"""Authored YAML wins only for mapped banks; generated evidence retains answer keys."""
	source = tmp_path / "bbq-WOMC-cells-questions.txt"
	source.write_text("MC\t<p>Identify cell</p>\t<table><tr><td>A</td><td>B</td></tr></table>\tCorrect\n")
	yaml_path = tmp_path / "cells.yml"
	yaml_path.write_text("matching pairs:\n  A: [B]\nreplacement_rules:\n  A: color\n")
	state = evidence.build(source, {source.name: yaml_path})
	assert state["authored_yaml"] == {"matching pairs": {"A": ["B"]}}
	assert "A | B |" in state["examples"][0][2]
	assert state["examples"][0][-1] == "Correct"
	assert evidence.readable("2300.00000000") == "2300.00000000"
	with pytest.raises(ValueError, match="not mapped"):
		evidence.build(source, {})


#============================================
def test_changed_filename_refreshes_all_placements(monkeypatch: pytest.MonkeyPatch) -> None:
	"""A shared bank's new label reaches every subject, including outside build scope."""
	monkeypatch.setattr(bloom, "classify", lambda *args, **kwargs: {"bbq-shared-questions.txt"})
	entries = [SimpleNamespace(source_path=Path("bbq-shared-questions.txt"),
		page_path=f"{subject}/topic01/index.md") for subject in ("genetics", "biochemistry")]
	monkeypatch.setattr(evidence, "entries", lambda root: entries)
	assert stages.run_bloom(BuildScope(subject="genetics")) == {
		TopicRef("genetics", "topic01"), TopicRef("biochemistry", "topic01"),
	}

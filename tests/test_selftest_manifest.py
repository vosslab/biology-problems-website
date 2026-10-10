"""Reachable BBQ declarations define durable self-test progress identities."""

# Standard Library
import json
from pathlib import Path

# PIP3 modules
import pytest

# local repo modules
import bioproblems_site.selftest_manifest as selftest_manifest


#============================================
def _site(tmp_path: Path) -> dict:
	"""Create two reachable topics without standalone HTML."""
	docs = tmp_path / "site_docs"
	for key in ("topic01", "topic02"):
		folder = docs / "biology" / key
		folder.mkdir(parents=True)
		(folder / "index.md").write_text("# Topic\n")
	metadata = tmp_path / "topics_metadata.yml"
	metadata.write_text(
		"biology:\n  title: Biology\n  description: Biology questions.\n  topics:\n"
		"    topic01:\n      title: Cells\n      description: Cell questions.\n"
		"    topic02:\n      title: Genetics\n      description: Genetics questions.\n"
	)
	mkdocs = tmp_path / "mkdocs.yml"
	mkdocs.write_text(
		"nav:\n- Biology:\n  - biology/index.md\n"
		"  - Cells: biology/topic01/index.md\n  - Genetics: biology/topic02/index.md\n"
	)
	return {
		"site_docs_dir": str(docs),
		"mkdocs_path": str(mkdocs),
		"metadata_path": str(metadata),
	}


#============================================
def _declare(site: dict, topic: str, names: list[str]) -> Path:
	"""Declare banks in a rendered page without creating their data."""
	folder = Path(site["site_docs_dir"]) / "biology" / topic
	(folder / "index.md").write_text("".join(
		f'<div data-bbq="{name}" class="qti-selftest">\n'
		'  <div class="selftest-reroll-content"></div>\n</div>\n'
		for name in names
	))
	return folder


#============================================
def _bank(folder: Path, name: str) -> None:
	"""Write a small bank; grading and parsing belong to QPM."""
	(folder / name).write_text("MC\tWhat is a cell?\tA unit of life\tcorrect\tAn atom\tincorrect\n")


#============================================
def test_manifest_uses_only_reachable_declarations(tmp_path: Path) -> None:
	"""Orphan banks and hidden topic declarations cannot inflate the dashboard."""
	site = _site(tmp_path)
	folder = _declare(site, "topic01", ["bbq-cells-questions.txt"])
	_bank(folder, "bbq-cells-questions.txt")
	_bank(folder, "bbq-undeclared-questions.txt")
	hidden = _declare(site, "topic02", ["bbq-hidden-questions.txt"])
	_bank(hidden, "bbq-hidden-questions.txt")
	Path(site["mkdocs_path"]).write_text("nav:\n- Cells: biology/topic01/index.md\n")
	assert selftest_manifest.build_manifest(**site) == {
		"version": 2,
		"source": "reachable-topic-pages",
		"questions": [{
			"questionId": "bbq-cells-questions.txt",
			"pagePath": "biology/topic01/index.md",
			"subjectKey": "biology",
			"topicKey": "topic01",
			"topicTitle": "Cells",
		}],
	}


#============================================
def test_manifest_skips_unrendered_topic(tmp_path: Path) -> None:
	"""Navigation can precede rendering during an index refresh."""
	site = _site(tmp_path)
	(Path(site["site_docs_dir"]) / "biology/topic01/index.md").unlink()
	assert selftest_manifest.build_manifest(**site)["questions"] == []


#============================================
@pytest.mark.parametrize("contents", [None, "", "\n  # comment only\n\t\n"])
def test_manifest_rejects_missing_or_empty_bank(tmp_path: Path, contents: str | None) -> None:
	"""Declared practice must have a bank with question data."""
	site = _site(tmp_path)
	folder = _declare(site, "topic01", ["bbq-cells-questions.txt"])
	if contents is not None:
		(folder / "bbq-cells-questions.txt").write_text(contents)
	error = FileNotFoundError if contents is None else ValueError
	with pytest.raises(error, match="bbq-cells-questions.txt"):
		selftest_manifest.build_manifest(**site)


#============================================
@pytest.mark.parametrize("name", ["", "../outside.txt", "/outside.txt"])
def test_manifest_rejects_nonlocal_declaration(tmp_path: Path, name: str) -> None:
	"""Only a basename is accepted, before any bank is opened."""
	site = _site(tmp_path)
	_declare(site, "topic01", [name])
	with pytest.raises(ValueError, match="basename"):
		selftest_manifest.build_manifest(**site)


#============================================
def test_manifest_requires_bank_attribute(tmp_path: Path) -> None:
	site = _site(tmp_path)
	folder = Path(site["site_docs_dir"]) / "biology/topic01"
	(folder / "index.md").write_text('<div class="qti-selftest"></div>')
	with pytest.raises(ValueError, match="missing data-bbq"):
		selftest_manifest.build_manifest(**site)


#============================================
def test_manifest_rejects_duplicate_placement(tmp_path: Path) -> None:
	site = _site(tmp_path)
	name = "bbq-cells-questions.txt"
	folder = _declare(site, "topic01", [name, name])
	_bank(folder, name)
	with pytest.raises(ValueError, match="Duplicate selftest problem set"):
		selftest_manifest.build_manifest(**site)


#============================================
def test_shared_banks_keep_identity_and_deterministic_order(tmp_path: Path) -> None:
	"""Shared banks count as one achievement even when placed on several pages."""
	site = _site(tmp_path)
	for topic, names in (
		("topic02", ["bbq-shared-questions.txt"]),
		("topic01", ["bbq-shared-questions.txt", "bbq-alpha-questions.txt"]),
	):
		folder = _declare(site, topic, names)
		for name in names:
			_bank(folder, name)
	rows = selftest_manifest.build_manifest(**site)["questions"]
	assert [(row["topicKey"], row["questionId"]) for row in rows] == [
		("topic01", "bbq-alpha-questions.txt"),
		("topic01", "bbq-shared-questions.txt"),
		("topic02", "bbq-shared-questions.txt"),
	]


#============================================
def test_write_and_dry_run_preserve_existing_output(tmp_path: Path) -> None:
	site = _site(tmp_path)
	folder = _declare(site, "topic01", ["bbq-cells-questions.txt"])
	_bank(folder, "bbq-cells-questions.txt")
	output = tmp_path / "data/manifest.json"
	expected = selftest_manifest.write_manifest(**site, output_path=str(output))
	assert json.loads(output.read_text()) == expected
	before = output.read_bytes()
	_declare(site, "topic01", [])
	assert selftest_manifest.write_manifest(
		**site, output_path=str(output), dry_run=True,
	)["questions"] == []
	assert output.read_bytes() == before


#============================================
def test_scoped_refresh_preserves_other_topics(
	tmp_path: Path,
) -> None:
	"""Focused builds replace selected topics without reading other banks."""
	site = _site(tmp_path)
	name = "bbq-cells-questions.txt"
	for topic in ("topic01", "topic02"):
		folder = _declare(site, topic, [name])
		_bank(folder, name)
	output = tmp_path / "manifest.json"
	original = selftest_manifest.write_manifest(**site, output_path=str(output))
	(Path(site["site_docs_dir"]) / "biology/topic02" / name).unlink()
	folder = _declare(site, "topic01", ["bbq-new-questions.txt"])
	_bank(folder, "bbq-new-questions.txt")
	result = selftest_manifest.write_manifest(
		**site, output_path=str(output), topic_scope={("biology", "topic01")},
	)
	assert result["questions"][0]["questionId"] == "bbq-new-questions.txt"
	assert result["questions"][1] == original["questions"][1]
	with pytest.raises(FileNotFoundError):
		selftest_manifest.build_manifest(**site)
	# A missing baseline requires global validation, even for a scoped write.
	output.unlink()
	with pytest.raises(FileNotFoundError):
		selftest_manifest.write_manifest(
			**site, output_path=str(output), topic_scope={("biology", "topic01")},
		)


#============================================
def test_scoped_refresh_drops_unreachable_and_unrendered_topics(tmp_path: Path) -> None:
	site = _site(tmp_path)
	for topic in ("topic01", "topic02"):
		folder = _declare(site, topic, ["bbq-shared-questions.txt"])
		_bank(folder, "bbq-shared-questions.txt")
	output = tmp_path / "manifest.json"
	selftest_manifest.write_manifest(**site, output_path=str(output))
	(Path(site["site_docs_dir"]) / "biology/topic02/index.md").unlink()
	result = selftest_manifest.write_manifest(
		**site, output_path=str(output), topic_scope={("biology", "topic01")},
	)
	assert [row["topicKey"] for row in result["questions"]] == ["topic01"]
	Path(site["mkdocs_path"]).write_text("nav:\n- Biology:\n  - biology/index.md\n")
	assert selftest_manifest.write_manifest(
		**site, output_path=str(output), topic_scope={("biology", "topic02")},
	)["questions"] == []


#============================================
def test_scoped_manifest_rejects_legacy_identity_schema(tmp_path: Path) -> None:
	"""A v1 CRC manifest is not silently treated as problem-set progress."""
	site = _site(tmp_path)
	output = tmp_path / "manifest.json"
	output.write_text(json.dumps({"version": 1, "source": "reachable-topic-pages", "questions": []}))
	with pytest.raises(ValueError, match="invalid self-test manifest"):
		selftest_manifest.write_manifest(
			**site, output_path=str(output), topic_scope={("biology", "topic01")},
		)

"""Tests for the reachable self-test manifest."""

# Standard Library
import os
import json

# PIP3 modules
import pytest

# local repo modules
import bioproblems_site.selftest_manifest as selftest_manifest


#============================================
def _write_metadata(path: object) -> object:
	path.write_text(
		"biology:\n"
		"  title: Biology\n"
		"  description: Biology questions.\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: Cells\n"
		"      description: Cell questions.\n"
		"    topic02:\n"
		"      title: Genetics\n"
		"      description: Genetics questions.\n"
	)


def _write_mkdocs(path: object) -> object:
	path.write_text(
		"nav:\n"
		"- Biology:\n"
		"  - biology/index.md\n"
		"  - \"01: Cells\": biology/topic01/index.md\n"
	)


def _write_selftest(path: object, crc: object, statement: object) -> object:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(
		f"<div id=\"question_html_{crc}\">\n"
		f"<div id='statement_text_{crc}'>{statement}</div>\n"
		"</div>\n",
		encoding="iso8859-1",
	)


def _selftest_container(
	selftest_path: str,
	bbq_basename: str = "bbq-cells-questions.txt",
) -> str:
	"""Return the generated topic-page shell for a standalone self-test."""
	return (
		f'<div class="qti-selftest" data-bbq="{bbq_basename}" '
		f'data-selftest="{selftest_path}">\n'
		'  <div class="selftest-reroll-content"></div>\n'
		'</div>\n'
	)


def test_manifest_uses_reachable_topic_pages(tmp_path: object) -> object:
	site_docs = tmp_path / "site_docs"
	topic_dir = site_docs / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "index.md").write_text(
		"# Cells\n"
		+ _selftest_container("biology/topic01/downloads/selftest-cells.html")
	)
	_write_selftest(
		site_docs / "biology" / "topic01" / "downloads" / "selftest-cells.html",
		"aaaa_0001",
		"What is a cell?",
	)
	# This generated file exists on disk but is not reachable through
	# mkdocs.yml, so it must not affect student dashboard totals.
	_write_selftest(
		site_docs / "biology" / "topic02" / "downloads" / "selftest-hidden.html",
		"bbbb_0002",
		"Hidden question",
	)
	metadata_path = tmp_path / "topics_metadata.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	_write_metadata(metadata_path)
	_write_mkdocs(mkdocs_path)
	manifest = selftest_manifest.build_manifest(
		site_docs_dir=str(site_docs),
		mkdocs_path=str(mkdocs_path),
		metadata_path=str(metadata_path),
	)
	assert manifest["version"] == 2
	assert [row["questionId"] for row in manifest["questions"]] == ["bbq-cells-questions.txt"]
	assert manifest["questions"][0]["crc"] == "aaaa_0001"
	assert "bankId" not in manifest["questions"][0]
	assert manifest["questions"][0]["topicTitle"] == "Cells"


def test_manifest_skips_unrendered_topic_page(tmp_path: object) -> object:
	# Nav lists biology/topic01/index.md, but a fast subject-index-only run
	# may not have rendered that index.md yet. The manifest must skip the
	# unrendered page instead of crashing on the missing file.
	site_docs = tmp_path / "site_docs"
	site_docs.mkdir(parents=True)
	# Intentionally do NOT create site_docs/biology/topic01/index.md.
	metadata_path = tmp_path / "topics_metadata.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	_write_metadata(metadata_path)
	_write_mkdocs(mkdocs_path)
	manifest = selftest_manifest.build_manifest(
		site_docs_dir=str(site_docs),
		mkdocs_path=str(mkdocs_path),
		metadata_path=str(metadata_path),
	)
	assert manifest["questions"] == []


def test_manifest_attribute_order_preserves_ids_and_fingerprints(tmp_path: object) -> None:
	"""Native class-first roots and Python id-first roots describe the same questions."""
	site_docs = tmp_path / "site_docs"
	topic_dir = site_docs / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "index.md").write_text(
		_selftest_container("biology/topic01/downloads/selftest-cells.html")
	)
	selftest_path = topic_dir / "downloads" / "selftest-cells.html"
	selftest_path.parent.mkdir()
	metadata_path = tmp_path / "topics_metadata.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	_write_metadata(metadata_path)
	_write_mkdocs(mkdocs_path)
	manifests = []
	for native in (False, True):
		markup = ""
		if native:
			markup += '<div class="qti-selftest-item" id="question_html_3593_4c9d">'
			markup += "<div class='statement' id = 'statement_text_3593_4c9d'>Match the cells.</div>"
		else:
			markup += "<div id='question_html_3593_4c9d'>"
			markup += '<div id="statement_text_3593_4c9d">Match the cells.</div>'
		markup += "</div>\n"
		selftest_path.write_text(markup, encoding="iso8859-1")
		manifests.append(selftest_manifest.build_manifest(
			site_docs_dir=str(site_docs),
			mkdocs_path=str(mkdocs_path),
			metadata_path=str(metadata_path),
		))
	python_question = manifests[0]["questions"][0]
	native_question = manifests[1]["questions"][0]
	assert python_question["questionId"] == native_question["questionId"] == "bbq-cells-questions.txt"
	assert python_question["crc"] == native_question["crc"] == "3593_4c9d"
	assert python_question["questionFingerprint"] == native_question["questionFingerprint"]


def test_manifest_rejects_missing_question_root(tmp_path: object) -> None:
	"""Attribute flexibility must still fail when the required CRC root is absent."""
	site_docs = tmp_path / "site_docs"
	topic_dir = site_docs / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "index.md").write_text(
		_selftest_container("biology/topic01/downloads/selftest-cells.html")
	)
	selftest_path = topic_dir / "downloads" / "selftest-cells.html"
	selftest_path.parent.mkdir()
	selftest_path.write_text('<div class="qti-selftest-item">Missing id</div>', encoding="iso8859-1")
	metadata_path = tmp_path / "topics_metadata.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	_write_metadata(metadata_path)
	_write_mkdocs(mkdocs_path)
	with pytest.raises(ValueError, match="No question_html_<crc> div"):
		selftest_manifest.build_manifest(
			site_docs_dir=str(site_docs),
			mkdocs_path=str(mkdocs_path),
			metadata_path=str(metadata_path),
		)


def test_manifest_rejects_duplicate_problem_set_placement(tmp_path: object) -> object:
	site_docs = tmp_path / "site_docs"
	topic_dir = site_docs / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "index.md").write_text(
		"# Cells\n"
		+ _selftest_container("biology/topic01/downloads/selftest-a.html")
		+ _selftest_container("biology/topic01/downloads/selftest-b.html")
	)
	_write_selftest(
		site_docs / "biology" / "topic01" / "downloads" / "selftest-a.html",
		"aaaa_0001",
		"First statement",
	)
	_write_selftest(
		site_docs / "biology" / "topic01" / "downloads" / "selftest-b.html",
		"aaaa_0001",
		"Second statement",
	)
	metadata_path = tmp_path / "topics_metadata.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	_write_metadata(metadata_path)
	_write_mkdocs(mkdocs_path)
	try:
		selftest_manifest.build_manifest(
			site_docs_dir=str(site_docs),
			mkdocs_path=str(mkdocs_path),
			metadata_path=str(metadata_path),
		)
	except ValueError as error:
		assert "Duplicate selftest problem set bbq-cells-questions.txt on biology/topic01/index.md" in str(error)
	else:
		raise AssertionError("duplicate problem-set placement did not raise")


def test_manifest_allows_shared_problem_set_on_multiple_topic_pages(tmp_path: object) -> None:
	"""The same BBQ file is one achievement even when several pages use it."""
	site_docs = tmp_path / "site_docs"
	topic01_dir = site_docs / "biology" / "topic01"
	topic02_dir = site_docs / "biology" / "topic02"
	topic01_dir.mkdir(parents=True)
	topic02_dir.mkdir(parents=True)
	bbq_filename = "bbq-shared-questions.txt"
	(topic01_dir / "index.md").write_text(
		_selftest_container("biology/topic01/downloads/selftest-shared.html", bbq_filename)
	)
	(topic02_dir / "index.md").write_text(
		_selftest_container("biology/topic02/downloads/selftest-shared.html", bbq_filename)
	)
	_write_selftest(
		topic01_dir / "downloads" / "selftest-shared.html",
		"aaaa_0001",
		"Shared practice question",
	)
	_write_selftest(
		topic02_dir / "downloads" / "selftest-shared.html",
		"bbbb_0002",
		"Shared practice question",
	)
	metadata_path = tmp_path / "topics_metadata.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	_write_metadata(metadata_path)
	mkdocs_path.write_text(
		"nav:\n"
		"- Biology:\n"
		"  - biology/index.md\n"
		"  - '01: Cells': biology/topic01/index.md\n"
		"  - '02: Genetics': biology/topic02/index.md\n"
	)
	manifest = selftest_manifest.build_manifest(
		site_docs_dir=str(site_docs),
		mkdocs_path=str(mkdocs_path),
		metadata_path=str(metadata_path),
	)
	assert [row["questionId"] for row in manifest["questions"]] == [
		bbq_filename, bbq_filename,
	]
	assert [row["crc"] for row in manifest["questions"]] == [
		"aaaa_0001", "bbbb_0002",
	]


def test_manifest_allows_duplicate_sample_crc_for_distinct_problem_sets(tmp_path: object) -> None:
	"""A generated sample CRC is diagnostic, not the progress identity."""
	site_docs = tmp_path / "site_docs"
	topic_dir = site_docs / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "index.md").write_text(
		_selftest_container("biology/topic01/downloads/selftest-a.html", "bbq-a-questions.txt")
		+ _selftest_container("biology/topic01/downloads/selftest-b.html", "bbq-b-questions.txt")
	)
	for filename in ("selftest-a.html", "selftest-b.html"):
		_write_selftest(
			topic_dir / "downloads" / filename,
			"aaaa_0001",
			"A representative question",
		)
	metadata_path = tmp_path / "topics_metadata.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	_write_metadata(metadata_path)
	_write_mkdocs(mkdocs_path)
	manifest = selftest_manifest.build_manifest(
		site_docs_dir=str(site_docs),
		mkdocs_path=str(mkdocs_path),
		metadata_path=str(metadata_path),
	)
	assert [row["questionId"] for row in manifest["questions"]] == [
		"bbq-a-questions.txt", "bbq-b-questions.txt",
	]


def test_write_manifest_creates_json(tmp_path: object) -> object:
	site_docs = tmp_path / "site_docs"
	topic_dir = site_docs / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "index.md").write_text(
		"# Cells\n"
		+ _selftest_container("biology/topic01/downloads/selftest-cells.html")
	)
	_write_selftest(
		site_docs / "biology" / "topic01" / "downloads" / "selftest-cells.html",
		"aaaa_0001",
		"What is a cell?",
	)
	metadata_path = tmp_path / "topics_metadata.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	output_path = tmp_path / "site_docs" / "assets" / "data" / "manifest.json"
	_write_metadata(metadata_path)
	_write_mkdocs(mkdocs_path)
	selftest_manifest.write_manifest(
		output_path=str(output_path),
		site_docs_dir=str(site_docs),
		mkdocs_path=str(mkdocs_path),
		metadata_path=str(metadata_path),
	)
	with open(output_path, "r") as file_pointer:
		data = json.load(file_pointer)
	assert data["source"] == "reachable-topic-pages"
	assert data["questions"][0]["questionFingerprint"]
	assert os.path.isfile(output_path)


def test_scoped_manifest_refresh_preserves_unselected_topics(tmp_path: object) -> object:
	"""A focused build replaces its topic rows without reading other topics' files."""
	site_docs = tmp_path / "site_docs"
	topic01_dir = site_docs / "biology" / "topic01"
	topic02_dir = site_docs / "biology" / "topic02"
	topic01_dir.mkdir(parents=True)
	topic02_dir.mkdir(parents=True)
	(topic01_dir / "index.md").write_text(
		"# Cells\n" + _selftest_container("biology/topic01/downloads/selftest-cells.html")
	)
	(topic02_dir / "index.md").write_text(
		"# Genetics\n" + _selftest_container("biology/topic02/downloads/selftest-missing.html")
	)
	_write_selftest(
		topic01_dir / "downloads" / "selftest-cells.html",
		"cccc_0003",
		"A current cell question",
	)
	metadata_path = tmp_path / "topics_metadata.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	_write_metadata(metadata_path)
	mkdocs_path.write_text(
		"nav:\n"
		"- Biology:\n"
		"  - biology/index.md\n"
		"  - '01: Cells': biology/topic01/index.md\n"
		"  - '02: Genetics': biology/topic02/index.md\n"
	)
	output_path = site_docs / "assets" / "data" / "manifest.json"
	output_path.parent.mkdir(parents=True)
	output_path.write_text(json.dumps({
		"version": 2,
		"source": "reachable-topic-pages",
		"questions": [
			{
				"questionId": "bbq-old-cells-questions.txt",
				"subjectKey": "biology",
				"topicKey": "topic01",
				"pagePath": "biology/topic01/index.md",
				"selftestPath": "biology/topic01/downloads/selftest-old.html",
			},
			{
				"questionId": "bbq-genetics-questions.txt",
				"subjectKey": "biology",
				"topicKey": "topic02",
				"pagePath": "biology/topic02/index.md",
				"selftestPath": "biology/topic02/downloads/selftest-missing.html",
			},
		],
	}))

	data = selftest_manifest.write_manifest(
		output_path=str(output_path),
		site_docs_dir=str(site_docs),
		mkdocs_path=str(mkdocs_path),
		metadata_path=str(metadata_path),
		topic_scope={("biology", "topic01")},
	)

	assert [row["questionId"] for row in data["questions"]] == [
		"bbq-cells-questions.txt",
		"bbq-genetics-questions.txt",
	]
	try:
		selftest_manifest.build_manifest(
			site_docs_dir=str(site_docs),
			mkdocs_path=str(mkdocs_path),
			metadata_path=str(metadata_path),
		)
	except FileNotFoundError as error:
		assert "selftest-missing.html" in str(error)
	else:
		raise AssertionError("an unrestricted manifest build skipped a missing include")


def test_scoped_manifest_rejects_legacy_identity_schema(tmp_path: object) -> None:
	"""A v1 CRC manifest is not silently treated as problem-set progress."""
	with pytest.raises(ValueError, match="invalid self-test manifest"):
		selftest_manifest._merge_scoped_manifest(
			existing_manifest={
				"version": 1,
				"source": "reachable-topic-pages",
				"questions": [],
			},
			scoped_manifest={"version": 2, "questions": []},
			topic_scope=set(),
			site_docs_dir=str(tmp_path),
			mkdocs_path=str(tmp_path / "mkdocs.yml"),
		)

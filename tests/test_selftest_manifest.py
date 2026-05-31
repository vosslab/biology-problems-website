"""Tests for the reachable self-test manifest."""

# Standard Library
import os
import json

# local repo modules
import bioproblems_site.selftest_manifest as selftest_manifest


#============================================
def _write_metadata(path):
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


def _write_mkdocs(path):
	path.write_text(
		"nav:\n"
		"- Biology:\n"
		"  - biology/index.md\n"
		"  - \"01: Cells\": biology/topic01/index.md\n"
	)


def _write_selftest(path, crc, statement):
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(
		f"<div id=\"question_html_{crc}\">\n"
		f"<div id='statement_text_{crc}'>{statement}</div>\n"
		"</div>\n",
		encoding="iso8859-1",
	)


def test_manifest_uses_reachable_topic_pages(tmp_path):
	site_docs = tmp_path / "site_docs"
	topic_dir = site_docs / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "index.md").write_text(
		"# Cells\n"
		'{% include "biology/topic01/downloads/selftest-cells.html" %}\n'
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
	assert [row["questionId"] for row in manifest["questions"]] == ["aaaa_0001"]
	assert manifest["questions"][0]["topicTitle"] == "Cells"


def test_manifest_skips_unrendered_topic_page(tmp_path):
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


def test_manifest_rejects_duplicate_crc(tmp_path):
	site_docs = tmp_path / "site_docs"
	topic_dir = site_docs / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "index.md").write_text(
		"# Cells\n"
		'{% include "biology/topic01/downloads/selftest-a.html" %}\n'
		'{% include "biology/topic01/downloads/selftest-b.html" %}\n'
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
		assert "Duplicate selftest CRC aaaa_0001" in str(error)
	else:
		raise AssertionError("duplicate CRC did not raise")


def test_write_manifest_creates_json(tmp_path):
	site_docs = tmp_path / "site_docs"
	topic_dir = site_docs / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "index.md").write_text(
		"# Cells\n"
		'{% include "biology/topic01/downloads/selftest-cells.html" %}\n'
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

"""Tests for bioproblems_site.scanner."""

# local repo modules
import bioproblems_site.scanner as scanner


def test_missing_dir_returns_empty_scan(tmp_path):
	"""Absent topic folder scans to zero questions and no formats."""
	result = scanner.scan_topic(str(tmp_path / "does_not_exist"))
	assert result.questions == 0
	assert result.formats == frozenset()


def test_more_bbq_files_yields_higher_count(tmp_path):
	"""Adding a bbq-*-questions.txt file increases the scanned count."""
	topic_dir = tmp_path / "topic01"
	topic_dir.mkdir()
	(topic_dir / "bbq-foo-questions.txt").write_text("Q1\n")
	(topic_dir / "notes.md").write_text("ignore me")
	before = scanner.scan_topic(str(topic_dir)).questions
	(topic_dir / "bbq-bar-questions.txt").write_text("Q1\n")
	after = scanner.scan_topic(str(topic_dir)).questions
	assert after > before
	# bb_text format is detected when bbq-*-questions.txt files exist.
	assert "bb_text" in scanner.scan_topic(str(topic_dir)).formats


def test_scan_subject_skips_missing_topic_folder(tmp_path):
	"""Requested topics absent on disk scan cleanly to zero."""
	site_docs = tmp_path / "site_docs"
	subject = site_docs / "biochemistry"
	subject.mkdir(parents=True)
	(subject / "topic01").mkdir()
	(subject / "topic01" / "bbq-a-questions.txt").write_text("q")
	result = scanner.scan_subject(
		str(site_docs), "biochemistry", ("topic01", "topic02")
	)
	assert result["topic01"].questions > result["topic02"].questions

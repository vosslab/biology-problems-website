"""Minimal pytest: generate_downloads=False must not create artifact files.

Pins the one behavior that actually matters for the --topic-pages
(without --generate-downloads) fast-path workflow.
"""

# Standard Library
import os
import pathlib

# PIP3 modules
import pytest

# local repo modules
import bioproblems_site.topic_page as topic_page


#============================================
def test_generate_downloads_off_creates_no_files(tmp_path: object) -> object:
	# Build a fake topic folder with one bbq-*-questions.txt source
	# file. The bbq file itself is the bb_text "download"; bb_export would
	# live under downloads/ if created.
	downloads_dir = tmp_path / "downloads"
	downloads_dir.mkdir()
	bbq_file = tmp_path / "bbq-xx-questions.txt"
	bbq_file.write_text("MC\tQ1\n*A\tyes\nB\tno\n")
	before = set(os.listdir(downloads_dir))
	stats = {}
	topic_page.generate_download_button_row(
		str(bbq_file),
		["bb_text", "bb_export"],
		force_downloads=False,
		verbose=False,
		stats=stats,
		generate_downloads=False,
	)
	after = set(os.listdir(downloads_dir))
	assert before == after


#============================================
def test_page_links_missing_downloads_without_creating_them(
	tmp_path: pathlib.Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""The page-only mode links its planned artifact without converter writes."""
	bbq_file = tmp_path / "bbq-xx-questions.txt"
	bbq_file.write_text("MC\tQ1\n*A\tyes\nB\tno\n")
	calls: list[tuple[str, str, str]] = []

	def create_must_not_run(bbq_path: str, prefix: str, extension: str) -> str:
		calls.append((bbq_path, prefix, extension))
		raise AssertionError("page rendering created a download")

	monkeypatch.setattr(topic_page, "create_downloadable_format", create_must_not_run)
	button_html = topic_page.generate_download_button_row(
		str(bbq_file),
		["canvas_qti"],
		force_downloads=False,
		verbose=False,
		stats={},
		generate_downloads=False,
		render_missing_download_links=True,
	)

	assert calls == []
	assert "downloads/canvas_qti_v1_2-xx.zip" in button_html


#============================================
def test_expected_output_path_does_not_remove_case_mismatch(
	tmp_path: pathlib.Path,
) -> None:
	"""Stale checks can derive paths without deleting differently cased files."""
	downloads_dir = tmp_path / "downloads"
	downloads_dir.mkdir()
	bbq_file = tmp_path / "bbq-xx-questions.txt"
	bbq_file.write_text("MC\tQ1\n*A\tyes\nB\tno\n")
	case_mismatch = downloads_dir / "Canvas_QTI_v1_2-xx.zip"
	case_mismatch.touch()

	expected = topic_page.get_expected_outfile_name(
		str(bbq_file), "canvas_qti_v1_2", "zip"
	)

	assert expected.endswith("canvas_qti_v1_2-xx.zip")
	assert case_mismatch.is_file()


#============================================
def test_bbq_text_uses_canonical_source_format_label(tmp_path: object) -> object:
	"""The canonical source download does not use retired LMS branding."""
	bbq_file = tmp_path / "bbq-xx-questions.txt"
	bbq_file.write_text("MC\tQ1\n*A\tyes\nB\tno\n")

	button_html = topic_page.generate_download_button_row(
		str(bbq_file),
		["bb_text"],
		force_downloads=False,
		verbose=False,
		stats={},
		generate_downloads=False,
	)

	assert "BBQ Text" in button_html
	assert "Blackboard Learn TXT" not in button_html


#============================================
def test_blackboard_export_uses_pool_format(
	tmp_path: pathlib.Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""The Blackboard button builds the pool-export ZIP through its engine flag."""
	downloads_dir = tmp_path / "downloads"
	downloads_dir.mkdir()
	bbq_file = tmp_path / "bbq-xx-questions.txt"
	bbq_file.write_text("MC\tQ1\n*A\tyes\nB\tno\n")
	calls: list[tuple[str, str, str]] = []

	def fake_create_downloadable_format(
		bbq_path: str,
		prefix: str,
		extension: str,
	) -> str:
		calls.append((bbq_path, prefix, extension))
		outfile = topic_page.get_outfile_name(bbq_path, prefix, extension)
		pathlib.Path(outfile).touch()
		return outfile

	monkeypatch.setattr(
		topic_page,
		"create_downloadable_format",
		fake_create_downloadable_format,
	)
	button_html = topic_page.generate_download_button_row(
		str(bbq_file),
		["bb_export"],
		force_downloads=False,
		verbose=False,
		stats={},
		generate_downloads=True,
	)

	assert calls == [(str(bbq_file), "blackboard_export_zip", "zip")]
	assert "Blackboard Ultra ZIP" in button_html
	assert "Blackboard Ultra pool-export ZIP" in button_html


#============================================
def test_order_question_omits_unsupported_blackboard_export(
	tmp_path: pathlib.Path,
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""ORDER sources do not link an empty Blackboard Ultra pool ZIP."""
	(tmp_path / "downloads").mkdir()
	bbq_file = tmp_path / "bbq-order-questions.txt"
	bbq_file.write_text("ORD\tPut these choices in order.\n")
	calls: list[tuple[str, str, str]] = []

	def fake_create_downloadable_format(
		bbq_path: str,
		prefix: str,
		extension: str,
	) -> str:
		calls.append((bbq_path, prefix, extension))
		return topic_page.get_outfile_name(bbq_path, prefix, extension)

	monkeypatch.setattr(
		topic_page,
		"create_downloadable_format",
		fake_create_downloadable_format,
	)
	button_html = topic_page.generate_download_button_row(
		str(bbq_file),
		["bb_export"],
		force_downloads=False,
		verbose=False,
		stats={},
		generate_downloads=True,
	)

	assert calls == []
	assert "Blackboard Ultra ZIP" not in button_html

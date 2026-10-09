"""Stable source-link and browser-package controls."""
# Standard Library
import pathlib

# PIP3 modules
import pytest
from bs4 import BeautifulSoup

# local repo modules
import bioproblems_site.problem_set_display as problem_set_display
import bioproblems_site.topic_page as topic_page


#============================================
def test_browser_controls_preserve_export_files(
	tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Rendering offers all exports without writing or touching prebuilt files."""
	bbq_file = tmp_path / "bbq-xx-questions.txt"
	bbq_file.write_text("MC\tQ1\n*A\tyes\nB\tno\n")
	downloads = tmp_path / "downloads"
	downloads.mkdir()
	old_export = downloads / "Canvas_QTI_v1_2-xx.zip"
	old_export.write_bytes(b"existing package")
	before = old_export.stat()
	monkeypatch.setattr(
		topic_page, "create_downloadable_format",
		lambda *args, **kwargs: pytest.fail("Page rendering invoked conversion"),
	)
	row = topic_page.generate_download_button_row(
		str(bbq_file), list(topic_page.DOWNLOAD_FORMAT_KEYS), verbose=False, stats={},
	)
	soup = BeautifulSoup(row, "html.parser")
	buttons = soup.select("button.qti-package-download")
	assert [button["data-format"] for button in buttons] == [
		"blackboard_export_zip", "canvas_qti_v1_2", "human_readable",
	]
	assert [button["data-filename"] for button in buttons] == [
		"blackboard_export_zip-xx.zip", "canvas_qti_v1_2-xx.zip", "human_readable-xx.html",
	]
	assert all(button["data-bbq"] == bbq_file.name for button in buttons)
	assert soup.select_one("a.bb_text")["href"] == bbq_file.name
	assert soup.select_one(".qti-package-status")["role"] == "status"
	assert soup.select_one("progress.qti-package-progress").has_attr("hidden")
	assert list(downloads.iterdir()) == [old_export]
	assert old_export.read_bytes() == b"existing package"
	assert old_export.stat().st_mtime_ns == before.st_mtime_ns


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
		verbose=False,
		stats={},
	)

	assert "BBQ Text" in button_html
	assert "Blackboard Learn TXT" not in button_html


#============================================
def test_question_type_badge_starts_download_row(tmp_path: pathlib.Path) -> None:
	"""The generated type label precedes the actions as static metadata."""
	bbq_file = tmp_path / 'bbq-TFMS-dna_structure-questions.txt'
	bbq_file.write_text('MC\tQ1\n*A\tyes\nB\tno\n')
	badge = problem_set_display.render_badges(
		'DNA Structure (TFMS)', source_path=bbq_file,
	)
	row = topic_page.generate_download_button_row(
		str(bbq_file), ['bb_text'],
		verbose=False, stats={}, question_type_badge=badge,
	)
	soup = BeautifulSoup(row, 'html.parser')
	assert soup.div.find_all(recursive=False)[0].name == 'span'
	assert soup.div.find('abbr').get_text() == 'T/F Statements (MC)'
	assert soup.div.find('a').get_text(strip=True) == 'BBQ Text'


#============================================
@pytest.mark.parametrize("item_type", ["ORD", "ORDER"])
def test_order_question_omits_unsupported_packages(
	tmp_path: pathlib.Path, item_type: str,
) -> None:
	"""ORDER banks retain human/source actions and preserve old exports."""
	bbq_file = tmp_path / "bbq-order-questions.txt"
	bbq_file.write_text(f"{item_type}\tPut these choices in order.\n")
	downloads = tmp_path / "downloads"
	downloads.mkdir()
	old_export = downloads / "blackboard_export_zip-order.zip"
	old_export.write_bytes(b"previous export")
	pgml = downloads / "order.pgml"
	pgml.write_text("DOCUMENT();\n")
	row = topic_page.generate_download_button_row(
		str(bbq_file), list(topic_page.DOWNLOAD_FORMAT_KEYS), verbose=False, stats={},
	)
	soup = BeautifulSoup(row, "html.parser")
	assert [b["data-format"] for b in soup.select("button.qti-package-download")] == [
		"human_readable",
	]
	assert soup.select_one("a.bb_text")["href"] == bbq_file.name
	assert soup.select_one("a.webwork_pgml")["href"] == "downloads/order.pgml"
	assert old_export.read_bytes() == b"previous export"


#============================================
def test_topic_page_uses_empty_dynamic_selftest_container(
	tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Topic pages expose a WASM source path without embedding a static question."""
	site_docs = tmp_path / "site_docs"
	topic_dir = site_docs / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	bbq_file = topic_dir / "bbq-cells-questions.txt"
	bbq_file.write_text("MC\tWhat is a cell?\n*A\tA cell\nB\tNot a cell\n")
	downloads_dir = topic_dir / "downloads"
	downloads_dir.mkdir()
	(downloads_dir / "selftest-cells.html").write_text("<div>standalone question</div>\n")
	monkeypatch.setattr(topic_page, "get_topic_title", lambda *args: "Cells")
	monkeypatch.setattr(topic_page, "get_topic_description", lambda *args: "Cell questions.")
	monkeypatch.setattr(topic_page, "get_libretexts_link", lambda *args: None)
	monkeypatch.setattr(topic_page, "get_problem_set_title", lambda *args: "Cell Basics (MC)")
	monkeypatch.setattr(topic_page, "generate_download_button_row", lambda *args, **kwargs: "")

	topic_page.update_index_md(
		str(topic_dir),
		[str(bbq_file)],
		{"count": 0},
		1,
		[],
		False,
		{},
		str(site_docs),
		regenerate_selftests=False,
	)

	page = (topic_dir / "index.md").read_text()
	soup = BeautifulSoup(page, "html.parser")
	container = soup.select_one("div.qti-selftest")
	assert container is not None
	assert container["data-bbq"] == "bbq-cells-questions.txt"
	assert not container.has_attr("data-bank-id")
	assert container["data-selftest"] == "biology/topic01/downloads/selftest-cells.html"
	assert container.select_one(".selftest-reroll-content").get_text() == ""
	assert "standalone question" not in page
	assert "<details>" not in page

"""Stable source-link and browser-package controls."""
# Standard Library
import pathlib

# PIP3 modules
import pytest
import markdown
from bs4 import BeautifulSoup

# local repo modules
import bioproblems_site.topic_page as topic_page


#============================================
def test_browser_controls_preserve_export_files(
	tmp_path: pathlib.Path,
) -> None:
	"""Rendering offers all exports without writing or touching prebuilt files."""
	bbq_file = tmp_path / "bbq-xx-questions.txt"
	bbq_file.write_text("MC\tQ1\n*A\tyes\nB\tno\n")
	downloads = tmp_path / "downloads"
	downloads.mkdir()
	old_export = downloads / "Canvas_QTI_v1_2-xx.zip"
	old_export.write_bytes(b"existing package")
	before = old_export.stat()
	row = topic_page.generate_download_button_row(
		str(bbq_file), list(topic_page.DOWNLOAD_FORMAT_KEYS), verbose=False, stats={},
	)
	soup = BeautifulSoup(row, "html.parser")
	buttons = soup.select("button.qpm-package-download")
	assert [button["data-format"] for button in buttons] == [
		"blackboard_export_zip", "canvas_qti_v1_2", "human_readable",
	]
	assert [button["data-filename"] for button in buttons] == [
		"blackboard_export_zip-xx.zip", "canvas_qti_v1_2-xx.zip", "human_readable-xx.html",
	]
	assert all(button["data-bbq"] == bbq_file.name for button in buttons)
	assert soup.select_one("a.bb_text")["href"] == bbq_file.name
	assert soup.select_one(".qpm-package-status")["role"] == "status"
	assert soup.select_one("progress.qpm-package-progress").has_attr("hidden")
	assert list(downloads.iterdir()) == [old_export]
	assert old_export.read_bytes() == b"existing package"
	assert old_export.stat().st_mtime_ns == before.st_mtime_ns


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
	assert [b["data-format"] for b in soup.select("button.qpm-package-download")] == [
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
	)

	page = (topic_dir / "index.md").read_text()
	soup = BeautifulSoup(page, "html.parser")
	container = soup.select_one("div.qpm-selftest")
	assert container is not None
	assert container["data-bbq"] == "bbq-cells-questions.txt"
	assert not (topic_dir / "downloads").exists()
	assert container.select_one(".selftest-reroll-content").get_text() == ""
	assert "<details>" not in page


#============================================
def test_numbered_banks_keep_legacy_fragments_and_source_association(
	tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Existing chapter and duplicate-title links still reach the intended bank."""
	topic_dir = tmp_path / "site_docs" / "biology" / "topic07"
	topic_dir.mkdir(parents=True)
	bank_names = ["bbq-first-questions.txt", "bbq-second-questions.txt"]
	for bank_name in bank_names:
		(topic_dir / bank_name).write_text("MC\tWhat is a cell?\n", encoding="utf-8")
	monkeypatch.setattr(topic_page, "get_topic_title", lambda *args: "Cells & DNA")
	monkeypatch.setattr(topic_page, "get_topic_description", lambda *args: "Cell questions.")
	monkeypatch.setattr(topic_page, "get_libretexts_link", lambda *args: None)
	monkeypatch.setattr(topic_page, "get_problem_set_title", lambda *args: "Cells & DNA (MC)")
	monkeypatch.setattr(topic_page.bloom, "load", lambda *args: {})
	topic_page.update_index_md(
		str(topic_dir), [str(topic_dir / name) for name in reversed(bank_names)],
		{"count": 0}, len(bank_names), ["bb_text"], False, {},
	)
	page = (topic_dir / "index.md").read_text(encoding="utf-8")
	rendered = markdown.markdown(page, extensions=["toc", "attr_list", "md_in_html"])
	soup = BeautifulSoup(rendered, "html.parser")
	assert soup.find(id="cells-dna").name == "h1"
	for fragment, bank_name, download_id in zip(
		["cells-dna_1", "cells-dna_2"], bank_names,
		["first-button-container", "second-button-container"],
	):
		heading = soup.find(id=fragment)
		assert heading is not None
		bank = heading.find_parent(attrs={"aria-labelledby": fragment})
		assert bank.select_one(".qpm-selftest")["data-bbq"] == bank_name
		assert bank.find(id=download_id).select_one("a.bb_text")["href"] == bank_name

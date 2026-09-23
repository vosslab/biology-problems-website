"""Generated outputs remain usable when a new candidate is invalid."""

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

import bioproblems_site.bbq_runner as bbq_runner
import bioproblems_site.topic_page as topic_page


def test_empty_bbq_candidate_keeps_existing_output(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A successful process with empty output must not erase the prior question bank."""
	workdir = tmp_path / "work"
	workdir.mkdir()
	monkeypatch.chdir(workdir)
	output_path = tmp_path / "site_docs/topic01/bbq-example-questions.txt"
	output_path.parent.mkdir(parents=True)
	output_path.write_text("previous valid questions\n")
	monkeypatch.setattr(bbq_runner, "build_command", lambda task: ["fake-generator"])
	monkeypatch.setattr(bbq_runner, "get_missing_script_message", lambda task: "")
	monkeypatch.setattr(bbq_runner, "get_missing_input_message", lambda task: "")

	def generate_empty(*args: object, **kwargs: object) -> SimpleNamespace:
		Path(output_path.name).write_text("")
		return SimpleNamespace(returncode=0, stdout="", stderr="")

	monkeypatch.setattr(bbq_runner.subprocess, "run", generate_empty)

	assert not bbq_runner.run_task(
		{"script": "generator.py", "args": [], "output": str(output_path)},
		str(tmp_path / "build.log"),
		1,
		1,
	)
	assert output_path.read_text() == "previous valid questions\n"
	assert not Path(output_path.name).exists()


#============================================
def test_empty_direct_output_restores_existing_output(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A generator writing directly to its configured path cannot erase prior content."""
	workdir = tmp_path / "work"
	workdir.mkdir()
	monkeypatch.chdir(workdir)
	output_path = tmp_path / "site_docs/topic01/bbq-example-questions.txt"
	output_path.parent.mkdir(parents=True)
	output_path.write_text("previous valid questions\n")
	monkeypatch.setattr(bbq_runner, "build_command", lambda task: ["fake-generator"])
	monkeypatch.setattr(bbq_runner, "get_missing_script_message", lambda task: "")
	monkeypatch.setattr(bbq_runner, "get_missing_input_message", lambda task: "")

	def write_directly(*args: object, **kwargs: object) -> SimpleNamespace:
		output_path.write_text("")
		return SimpleNamespace(returncode=0, stdout="", stderr="")

	monkeypatch.setattr(bbq_runner.subprocess, "run", write_directly)
	assert not bbq_runner.run_task(
		{"script": "generator.py", "args": [], "output": str(output_path)},
		str(tmp_path / "build.log"),
		1,
		1,
	)
	assert output_path.read_text() == "previous valid questions\n"


#============================================
def test_oversized_candidate_keeps_existing_output(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A candidate above its configured question limit cannot replace valid output."""
	workdir = tmp_path / "work"
	workdir.mkdir()
	monkeypatch.chdir(workdir)
	output_path = tmp_path / "site_docs/topic01/bbq-example-questions.txt"
	output_path.parent.mkdir(parents=True)
	output_path.write_text("previous valid question\n")
	monkeypatch.setattr(bbq_runner, "build_command", lambda task: ["fake-generator"])
	monkeypatch.setattr(bbq_runner, "get_missing_script_message", lambda task: "")
	monkeypatch.setattr(bbq_runner, "get_missing_input_message", lambda task: "")

	def generate_too_many(*args: object, **kwargs: object) -> SimpleNamespace:
		Path(output_path.name).write_text("question one\nquestion two\n")
		return SimpleNamespace(returncode=0, stdout="", stderr="")

	monkeypatch.setattr(bbq_runner.subprocess, "run", generate_too_many)
	assert not bbq_runner.run_task(
		{
			"script": "generator.py",
			"args": [],
			"output": str(output_path),
			"max_questions": 1,
		},
		str(tmp_path / "build.log"),
		1,
		1,
	)
	assert output_path.read_text() == "previous valid question\n"


#============================================
def test_prefers_a_new_direct_output_over_a_recent_stale_basename(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A recent stale workdir file cannot replace a direct output written this run."""
	workdir = tmp_path / "work"
	workdir.mkdir()
	monkeypatch.chdir(workdir)
	output_path = tmp_path / "site_docs/topic01/bbq-example-questions.txt"
	output_path.parent.mkdir(parents=True)
	output_path.write_text("previous valid questions\n")
	stale_candidate_path = workdir / output_path.name
	stale_candidate_path.write_text("stale workdir candidate\n")
	os.utime(stale_candidate_path)
	monkeypatch.setattr(bbq_runner, "build_command", lambda task: ["fake-generator"])
	monkeypatch.setattr(bbq_runner, "get_missing_script_message", lambda task: "")
	monkeypatch.setattr(bbq_runner, "get_missing_input_message", lambda task: "")

	def write_to_configured_path(*args: object, **kwargs: object) -> SimpleNamespace:
		output_path.write_text("new valid questions\n")
		return SimpleNamespace(returncode=0, stdout="", stderr="")

	monkeypatch.setattr(bbq_runner.subprocess, "run", write_to_configured_path)
	assert bbq_runner.run_task(
		{"script": "generator.py", "args": [], "output": str(output_path)},
		str(tmp_path / "build.log"),
		1,
		1,
	)
	assert output_path.read_text() == "new valid questions\n"
	assert stale_candidate_path.read_text() == "stale workdir candidate\n"


def test_empty_converter_result_keeps_existing_html(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A converter that produces no HTML must not erase the prior self-test."""
	source_path = tmp_path / "bbq-example-questions.txt"
	source_path.write_text("question\n")
	output_path = tmp_path / "downloads/selftest-example.html"
	output_path.parent.mkdir()
	output_path.write_text("previous html\n")
	monkeypatch.setattr(topic_page, "get_outfile_name", lambda *args: str(output_path))
	monkeypatch.setattr(topic_page.git_paths, "find_bbq_converter", lambda: "converter.py")

	def write_empty(convert_command: list[str], check: bool) -> SimpleNamespace:
		Path(convert_command[-1]).write_text("")
		return SimpleNamespace(returncode=0)

	monkeypatch.setattr(topic_page.subprocess, "run", write_empty)
	with pytest.raises(RuntimeError, match="produced no output"):
		topic_page.create_downloadable_format(str(source_path), "selftest", "html")
	assert output_path.read_text() == "previous html\n"


#============================================
def test_failed_converter_keeps_existing_html(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A nonzero converter exit must preserve the last valid self-test."""
	source_path = tmp_path / "bbq-example-questions.txt"
	source_path.write_text("question\n")
	output_path = tmp_path / "downloads/selftest-example.html"
	output_path.parent.mkdir()
	output_path.write_text("previous html\n")
	monkeypatch.setattr(topic_page, "get_outfile_name", lambda *args: str(output_path))
	monkeypatch.setattr(topic_page.git_paths, "find_bbq_converter", lambda: "converter.py")

	def fail_conversion(convert_command: list[str], check: bool) -> SimpleNamespace:
		Path(convert_command[-1]).write_text("partial html")
		return SimpleNamespace(returncode=2)

	monkeypatch.setattr(topic_page.subprocess, "run", fail_conversion)
	with pytest.raises(RuntimeError, match="exited with status 2"):
		topic_page.create_downloadable_format(str(source_path), "selftest", "html")
	assert output_path.read_text() == "previous html\n"


#============================================
def test_topic_page_render_failure_preserves_existing_index(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A failed topic title generation cannot replace the last complete page."""
	topic_folder = tmp_path / "site_docs/genetics/topic01"
	topic_folder.mkdir(parents=True)
	source_path = topic_folder / "bbq-example-questions.txt"
	source_path.write_text("question\n")
	index_path = topic_folder / "index.md"
	index_path.write_text("previous complete page\n")
	monkeypatch.setattr(topic_page, "get_topic_title", lambda folder: "1: Example")
	monkeypatch.setattr(topic_page, "get_topic_description", lambda folder: "Description")
	monkeypatch.setattr(topic_page, "get_libretexts_link", lambda folder: None)
	monkeypatch.setattr(
		topic_page,
		"get_outfile_name",
		lambda *args: str(topic_folder / "downloads/selftest-example.html"),
	)
	def fail_title_generation(client: object, source: str) -> str:
		raise RuntimeError("title service failed")

	monkeypatch.setattr(topic_page, "get_problem_set_title", fail_title_generation)

	with pytest.raises(RuntimeError, match="title service failed"):
		topic_page.update_index_md(
			str(topic_folder),
			[str(source_path)],
			{"count": 0},
			1,
			[],
			False,
			False,
			topic_page.init_format_stats(),
			str(tmp_path),
			regenerate_selftests=False,
		)
	assert index_path.read_text() == "previous complete page\n"

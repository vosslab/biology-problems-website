"""Native conversion preserves artifacts and distinguishes optional no-output."""

import pathlib
import subprocess
import json

import pytest

import bioproblems_site.git_paths as git_paths
import bioproblems_site.topic_page as topic_page


#============================================
def test_native_converter_is_required(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
	"""A Python converter never substitutes for the missing native dependency."""
	repo = tmp_path / "website"
	repo.mkdir()
	(repo / "bbq_converter.py").write_text("legacy converter")
	monkeypatch.setattr(git_paths, "get_repo_root", lambda: str(repo))
	monkeypatch.delenv("QPM_ROOT", raising=False)
	with pytest.raises(git_paths.NativeConverterUnavailableError, match="set QPM_ROOT"):
		git_paths.find_native_bbq_converter()


#============================================
def test_native_converter_builds_configured_checkout(
	tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""A missing binary is recovered using Cargo's actual executable location."""
	qpm = tmp_path / "qpm source"
	qpm.mkdir()
	(qpm / "Cargo.toml").write_text("[workspace]\n")
	binary = tmp_path / "custom target" / "bbq-converter"
	monkeypatch.setenv("QPM_ROOT", str(qpm))
	monkeypatch.setattr(git_paths.shutil, "which", lambda name: "/tools/cargo")
	calls = []

	def build(command: list[str], **options: object) -> subprocess.CompletedProcess:
		calls.append((command, options["cwd"]))
		binary.parent.mkdir()
		binary.write_text("built converter")
		message = {"reason": "compiler-artifact", "target": {"name": "bbq-converter"},
			"executable": str(binary)}
		return subprocess.CompletedProcess(command, 0, json.dumps(message) + "\n")

	monkeypatch.setattr(git_paths.subprocess, "run", build)
	monkeypatch.setattr(git_paths, "get_repo_root", lambda: str(tmp_path))
	assert git_paths.find_native_bbq_converter() == str(binary)
	assert git_paths.find_native_bbq_converter() == str(binary)
	assert len(calls) == 1
	assert calls[0][1] == str(qpm)
	git_paths._build_native_bbq_converter.cache_clear()


#============================================
@pytest.mark.parametrize("status, content", [(1, "partial"), (0, "")])
def test_failed_native_export_preserves_existing_artifact(
	tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, status: int, content: str,
) -> None:
	"""Failed or empty conversions cannot replace a previously usable download."""
	source = tmp_path / "bbq-example-questions.txt"
	source.write_text("MC\tQuestion?\tYes\tCorrect\tNo\tIncorrect\n")
	output = pathlib.Path(topic_page.get_outfile_name(str(source), "selftest", "html"))
	output.parent.mkdir()
	output.write_text("valid previous artifact")
	monkeypatch.setattr(git_paths, "find_native_bbq_converter", lambda: "/native converter")

	def convert(command: list[str], **options: object) -> subprocess.CompletedProcess:
		pathlib.Path(command[command.index("--output") + 1]).write_text(content)
		return subprocess.CompletedProcess(command, status, "", "")

	monkeypatch.setattr(topic_page.subprocess, "run", convert)
	with pytest.raises(RuntimeError):
		topic_page.create_downloadable_format(str(source), "selftest", "html", task_log=[])
	assert output.read_text() == "valid previous artifact"


#============================================
def test_native_human_readable_skip_removes_obsolete_output(
	tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Successful unsupported-content skips cannot retain an obsolete HTML download."""
	source = tmp_path / "bbq-example-questions.txt"
	source.write_text("MC\tRDKit canvas\tYes\tCorrect\tNo\tIncorrect\n")
	output = pathlib.Path(topic_page.get_outfile_name(str(source), "human_readable", "html"))
	output.parent.mkdir()
	output.write_text("obsolete artifact")
	monkeypatch.setattr(git_paths, "find_native_bbq_converter", lambda: "/native converter")

	def convert(command: list[str], **options: object) -> subprocess.CompletedProcess:
		return subprocess.CompletedProcess(command, 0, "DONE", "")

	monkeypatch.setattr(topic_page.subprocess, "run", convert)
	assert topic_page.create_downloadable_format(
		str(source), "human_readable", "html", task_log=[],
	) is None
	assert not output.exists()

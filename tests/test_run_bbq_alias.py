"""Integration tests for BBQ CSV topic resolution.

Tests the resolver wiring inside bbq_config.load_tasks_csv via small in-memory
CSVs and a hand-crafted alias map. Real metadata is not required.
"""

# Standard Library
import textwrap
from pathlib import Path

# PIP3 modules
import pytest

# local repo modules
import file_utils
import bioproblems_site.metadata as metadata
import bioproblems_site.bbq_config as bbq_config
import bioproblems_site.bbq_outputs as bbq_outputs


def _bbq_config(tmp_path: object) -> object:
	"""Minimal bbq_config that load_tasks_csv accepts without aliases.

	bp_root is a path-alias root that the resolver uses to expand
	{bp_root} placeholders in CSV cells; these tests do not exercise
	any such expansion, but a non-empty value avoids a special case
	in load_tasks_csv. Passing tmp_path keeps the value isolated to
	the test and avoids the bandit /tmp warning.
	"""
	config = {
		"paths": {"bp_root": str(tmp_path)},
		"defaults": {"input_flag": "-y"},
	}
	return config


def _alias_map_with_amino_acids() -> object:
	"""Alias map: biochemistry topic03 has alias amino_acids; topic14 has none."""
	subjects = {
		"biochemistry": metadata.Subject(
			key="biochemistry", title="B", description="",
			topics=(
				metadata.Topic(
					key="topic03", title="Amino Acids", description="d",
					libretexts=None, visible=True, alias="amino_acids",
				),
				metadata.Topic(
					key="topic14", title="Senses", description="d",
					libretexts=None, visible=True, alias=None,
				),
			),
		),
	}
	return metadata.build_topic_alias_map(subjects)


def _write_csv(tmp_path: object, body: object) -> object:
	"""Write a CSV under tmp_path and return its absolute path."""
	path = tmp_path / "tasks.csv"
	path.write_text(textwrap.dedent(body).lstrip())
	return str(path)


def test_alias_resolves_to_canonical_topicNN(tmp_path: object) -> object:
	body = """
		subject,topic,script,flags,input,notes
		biochemistry,amino_acids,which_macromolecule.py,,,
	"""
	tasks = bbq_config.load_tasks_csv(
		_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
	)
	# Output dir contains canonical topic03 even though the CSV used the alias.
	assert tasks[0]["output_dir"].endswith("/topic03")


@pytest.mark.parametrize("alias, formats", [
	("YORDER", ("ORDER", "SEQUENCEMC")),
	("YMCORDER", ("SEQUENCEMC",)),
])
def test_ordering_aliases_generate_and_resolve_each_format(
	tmp_path: Path, alias: str, formats: tuple[str, ...],
) -> None:
	"""A paired row retains both tasks and discovers only each task's own output."""
	settings = bbq_config.load_bbq_config(str(Path(file_utils.get_repo_root()) / "bbq_settings.yml"))
	settings["paths"]["bp_root"] = str(tmp_path)
	body = (
		"subject,topic,script,flags,input,notes\n"
		f"biochemistry,amino_acids,{alias},-d 5,steps.yml,\n"
	)
	tasks = bbq_config.load_tasks_csv(
		_write_csv(tmp_path, body), settings, _alias_map_with_amino_acids(),
	)
	# Both formats and another bank coexist in the generator's working directory.
	for name in ("ORDER-steps", "SEQUENCEMC-steps", "SEQUENCEMC-other"):
		(tmp_path / f"bbq-{name}-3_items-questions.txt").write_text("question\n")
	outputs = []
	for task in tasks:
		ok, output, _candidate, message = bbq_outputs.resolve_generated_output(task, str(tmp_path), 0)
		assert ok, message
		outputs.append(Path(output).name)
	assert outputs == [f"bbq-{fmt}-steps-3_items-questions.txt" for fmt in formats]


def test_raw_topicNN_for_aliased_topic_raises(tmp_path: object) -> object:
	body = """
		subject,topic,script,flags,input,notes
		biochemistry,topic03,which_macromolecule.py,,,
	"""
	with pytest.raises(metadata.MetadataError):
		bbq_config.load_tasks_csv(
			_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
		)


def test_raw_topicNN_for_non_aliased_topic_accepted(tmp_path: object) -> object:
	body = """
		subject,topic,script,flags,input,notes
		biochemistry,topic14,which_macromolecule.py,,,
	"""
	tasks = bbq_config.load_tasks_csv(
		_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
	)
	assert tasks[0]["output_dir"].endswith("/topic14")


def test_blank_separator_row_skipped(tmp_path: object) -> object:
	# All-blank rows between blocks should be skipped before topic
	# resolution so an empty topic cell does not raise.
	body = """
		subject,topic,script,flags,input,notes
		biochemistry,amino_acids,which_macromolecule.py,,,
		,,,,,
		biochemistry,topic14,which_macromolecule.py,,,
	"""
	tasks = bbq_config.load_tasks_csv(
		_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
	)
	# Both real rows resolved; the blank separator did not produce a
	# phantom task. Asserting on per-row resolved output_dir avoids
	# brittle collection-size assertions.
	# Direct subscript -- output_dir must exist on every task; a
	# missing key is a real bug we want surfaced loudly.
	output_dirs = [t["output_dir"] for t in tasks]
	assert any(d.endswith("/topic03") for d in output_dirs)
	assert any(d.endswith("/topic14") for d in output_dirs)


def test_missing_required_task_column_fails_with_csv_context(tmp_path: object) -> object:
	"""A misspelled required header cannot silently remove task rows from a build."""
	body = """
		subject,topic,scrip,flags,input,notes
		biochemistry,amino_acids,which_macromolecule.py,,,
	"""
	with pytest.raises(ValueError, match="missing required columns"):
		bbq_config.load_tasks_csv(
			_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
		)


#============================================
def test_comment_lines_skipped_with_original_line_numbers(tmp_path: object) -> None:
	"""Notes and disabled rows cannot become tasks or shift active row identities."""
	body = """
		# Tasks for this chapter
		subject,topic,script,flags,input,notes
		#biochemistry,amino_acids,disabled.py,,,,extra
		biochemistry,amino_acids,first.py,,,"Keep # comment in a cell"
		# "Unclosed quotes in comments are ignored
		biochemistry,topic14,second.py,,,
		# comment End of tasks
	"""
	tasks = bbq_config.load_tasks_csv(
		_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
	)
	assert [(task["topic"], task["_csv_row_number"]) for task in tasks] == [
		("topic03", 4), ("topic14", 6),
	]
	assert [task["script"].rsplit("/", 1)[-1] for task in tasks] == ["first.py", "second.py"]


#============================================
def test_invalid_active_row_after_comment_reports_original_line(tmp_path: object) -> None:
	"""Comment support preserves validation and error locations for active rows."""
	body = """
		subject,topic,script
		# comment Ignore this note
		biochemistry,amino_acids,
	"""
	with pytest.raises(ValueError, match=r"tasks\.csv:3 is missing values"):
		bbq_config.load_tasks_csv(
			_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
		)


def test_unknown_subject_raises(tmp_path: object) -> object:
	body = """
		subject,topic,script,flags,input,notes
		physics,whatever,foo.py,,,
	"""
	with pytest.raises(metadata.MetadataError):
		bbq_config.load_tasks_csv(
			_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
		)


def test_unknown_alias_raises(tmp_path: object) -> object:
	body = """
		subject,topic,script,flags,input,notes
		biochemistry,nonexistent_alias,which_macromolecule.py,,,
	"""
	with pytest.raises(metadata.MetadataError):
		bbq_config.load_tasks_csv(
			_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
		)


@pytest.mark.parametrize("flag", ["-x 50", "-x50", "-x=50", "--max-questions 50", "--max-questions=50"])
def test_csv_question_limits_rejected(tmp_path: Path, flag: str) -> None:
	body = f"subject,topic,script,flags,input,notes\nbiochemistry,amino_acids,example.py,{flag},,\n"
	with pytest.raises(ValueError, match=r"tasks\.csv:2 cannot set"):
		bbq_config.load_tasks_csv(
			_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
		)

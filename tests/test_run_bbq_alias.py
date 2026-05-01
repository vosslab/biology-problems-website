"""Integration tests for run_bbq_tasks.py CSV topic resolution.

Tests the resolver wiring inside load_tasks_csv via small in-memory
CSVs and a hand-crafted alias map. Real metadata is not required.
"""

# Standard Library
import textwrap

# PIP3 modules
import pytest

# local repo modules
import bioproblems_site.metadata as metadata
import run_bbq_tasks


def _bbq_config(tmp_path):
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


def _alias_map_with_amino_acids():
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


def _write_csv(tmp_path, body):
	"""Write a CSV under tmp_path and return its absolute path."""
	path = tmp_path / "tasks.csv"
	path.write_text(textwrap.dedent(body).lstrip())
	return str(path)


def test_alias_resolves_to_canonical_topicNN(tmp_path):
	body = """
		subject,topic,script,flags,input,notes
		biochemistry,amino_acids,which_macromolecule.py,,,
	"""
	tasks = run_bbq_tasks.load_tasks_csv(
		_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
	)
	# Output dir contains canonical topic03 even though the CSV used the alias.
	assert tasks[0]["output_dir"].endswith("/topic03")


def test_raw_topicNN_for_aliased_topic_raises(tmp_path):
	body = """
		subject,topic,script,flags,input,notes
		biochemistry,topic03,which_macromolecule.py,,,
	"""
	with pytest.raises(metadata.MetadataError):
		run_bbq_tasks.load_tasks_csv(
			_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
		)


def test_raw_topicNN_for_non_aliased_topic_accepted(tmp_path):
	body = """
		subject,topic,script,flags,input,notes
		biochemistry,topic14,which_macromolecule.py,,,
	"""
	tasks = run_bbq_tasks.load_tasks_csv(
		_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
	)
	assert tasks[0]["output_dir"].endswith("/topic14")


def test_blank_separator_row_skipped(tmp_path):
	# All-blank rows between blocks should be skipped before topic
	# resolution so an empty topic cell does not raise.
	body = """
		subject,topic,script,flags,input,notes
		biochemistry,amino_acids,which_macromolecule.py,,,
		,,,,,
		biochemistry,topic14,which_macromolecule.py,,,
	"""
	tasks = run_bbq_tasks.load_tasks_csv(
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


def test_unknown_subject_raises(tmp_path):
	body = """
		subject,topic,script,flags,input,notes
		physics,whatever,foo.py,,,
	"""
	with pytest.raises(metadata.MetadataError):
		run_bbq_tasks.load_tasks_csv(
			_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
		)


def test_unknown_alias_raises(tmp_path):
	body = """
		subject,topic,script,flags,input,notes
		biochemistry,nonexistent_alias,which_macromolecule.py,,,
	"""
	with pytest.raises(metadata.MetadataError):
		run_bbq_tasks.load_tasks_csv(
			_write_csv(tmp_path, body), _bbq_config(tmp_path), _alias_map_with_amino_acids(),
		)

"""Tests for tools/dump_topics_csv.py CSV export utility."""

# Standard Library
import csv

# local repo modules
# `tools/` is added to sys.path by tests/conftest.py so this is a
# clean absolute import even though tools/ is not a Python package.
import dump_topics_csv


_NAV_TWO_SUBJECTS = (
	"nav:\n"
	"  - Home: index.md\n"
	"  - Biochemistry: biochemistry/index.md\n"
	"  - Genetics: genetics/index.md\n"
)


def _run_dump(tmp_path, yaml_body, nav_body=_NAV_TWO_SUBJECTS):
	"""Write YAML + nav, run dump, return (fieldnames, rows)."""
	metadata_path = tmp_path / "topics.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	output_path = tmp_path / "output.csv"
	metadata_path.write_text(yaml_body)
	mkdocs_path.write_text(nav_body)
	dump_topics_csv.dump_topics_to_csv(
		metadata_path=str(metadata_path),
		mkdocs_path=str(mkdocs_path),
		output_path=str(output_path),
	)
	# Repo policy: ASCII / ISO-8859-1 (see docs/MARKDOWN_STYLE.md);
	# declaring iso8859-1 makes the test independent of the
	# platform locale default.
	with open(output_path, "r", encoding="iso8859-1") as fp:
		reader = csv.DictReader(fp)
		fieldnames = reader.fieldnames
		rows = list(reader)
	return fieldnames, rows


def test_alias_round_trip(tmp_path):
	# Aliased topic: alias column carries the YAML alias verbatim.
	yaml_body = (
		"biochemistry:\n"
		"  title: Biochemistry\n"
		"  description: d\n"
		"  topics:\n"
		"    topic03:\n"
		"      title: Amino Acids\n"
		"      description: d\n"
		"      alias: amino_acids\n"
	)
	nav = "nav:\n  - Home: index.md\n  - B: biochemistry/index.md\n"
	_fieldnames, rows = _run_dump(tmp_path, yaml_body, nav)
	assert rows[0]["alias"] == "amino_acids"


def test_missing_alias_is_empty_string_not_none(tmp_path):
	# Topic without alias: column is "" (must NOT be the literal "None").
	yaml_body = (
		"biochemistry:\n"
		"  title: Biochemistry\n"
		"  description: d\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: Test\n"
		"      description: d\n"
	)
	nav = "nav:\n  - Home: index.md\n  - B: biochemistry/index.md\n"
	_fieldnames, rows = _run_dump(tmp_path, yaml_body, nav)
	assert rows[0]["alias"] == ""


def test_subject_then_topic_ordering(tmp_path):
	# Two subjects out of input order; biochemistry must precede genetics
	# and within biochemistry topic01 must precede topic02.
	yaml_body = (
		"biochemistry:\n"
		"  title: B\n"
		"  description: d\n"
		"  topics:\n"
		"    topic02:\n"
		"      title: T2\n"
		"      description: d\n"
		"    topic01:\n"
		"      title: T1\n"
		"      description: d\n"
		"genetics:\n"
		"  title: G\n"
		"  description: d\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: T1\n"
		"      description: d\n"
	)
	_fieldnames, rows = _run_dump(tmp_path, yaml_body)
	keys = [(r["subject"], r["topic_key"]) for r in rows]
	assert keys == [
		("biochemistry", "topic01"),
		("biochemistry", "topic02"),
		("genetics", "topic01"),
	]


def test_header_contains_expected_columns(tmp_path):
	# Cheap sanity check: the documented columns are present (set
	# semantics; do not pin column order to avoid breaking downstream
	# consumers if a future column is appended).
	yaml_body = (
		"biochemistry:\n"
		"  title: B\n"
		"  description: d\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: T\n"
		"      description: d\n"
	)
	nav = "nav:\n  - Home: index.md\n  - B: biochemistry/index.md\n"
	fieldnames, _rows = _run_dump(tmp_path, yaml_body, nav)
	expected = {"subject", "topic_key", "alias", "title", "description"}
	assert expected.issubset(set(fieldnames))

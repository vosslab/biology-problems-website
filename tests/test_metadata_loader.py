"""Error-detection tests for bioproblems_site.metadata.

Focused on logic that could plausibly be wrong: schema validation and
missing-file handling. Does not assert on shipped YAML contents.
"""

# PIP3 modules
import pytest

# local repo modules
import bioproblems_site.metadata as metadata_module


def test_missing_file_raises(tmp_path):
	with pytest.raises(FileNotFoundError):
		metadata_module.load_metadata_file(str(tmp_path / "missing.yml"))


def test_missing_topic_description_raises(tmp_path):
	yaml_body = (
		"biochemistry:\n"
		"  title: Biochemistry\n"
		"  description: subject intro\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: First\n"
	)
	metadata_path = tmp_path / "topics.yml"
	metadata_path.write_text(yaml_body)
	with pytest.raises(metadata_module.MetadataError):
		metadata_module.load_metadata_file(str(metadata_path))


def test_invalid_topic_key_raises(tmp_path):
	yaml_body = (
		"biochemistry:\n"
		"  title: Biochemistry\n"
		"  description: subject intro\n"
		"  topics:\n"
		"    topicone:\n"
		"      title: Bogus\n"
		"      description: bogus\n"
	)
	metadata_path = tmp_path / "topics.yml"
	metadata_path.write_text(yaml_body)
	with pytest.raises(metadata_module.MetadataError):
		metadata_module.load_metadata_file(str(metadata_path))


def test_libretexts_bad_url_raises(tmp_path):
	yaml_body = (
		"biochemistry:\n"
		"  title: Biochemistry\n"
		"  description: subject intro\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: One\n"
		"      description: one\n"
		"      libretexts:\n"
		"        url: https://example.com/foo\n"
		"        chapter: 1\n"
	)
	metadata_path = tmp_path / "topics.yml"
	metadata_path.write_text(yaml_body)
	with pytest.raises(metadata_module.MetadataError):
		metadata_module.load_metadata_file(str(metadata_path))

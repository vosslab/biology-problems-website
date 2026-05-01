"""Schema tests for the optional Topic.alias field."""

# PIP3 modules
import pytest

# local repo modules
import bioproblems_site.metadata as metadata_module


def _yaml_with_topic(alias_value: str) -> str:
	"""Compose a minimal one-subject one-topic YAML with the given alias line."""
	body = (
		"biochemistry:\n"
		"  title: Biochemistry\n"
		"  description: subject intro\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: First\n"
		"      description: First topic\n"
		f"{alias_value}"
	)
	return body


def test_alias_optional(tmp_path):
	# Topic without an alias still loads.
	metadata_path = tmp_path / "topics.yml"
	metadata_path.write_text(_yaml_with_topic(""))
	subjects = metadata_module.load_metadata_file(str(metadata_path))
	topic = subjects["biochemistry"].topics[0]
	assert topic.alias is None


def test_alias_accepted(tmp_path):
	metadata_path = tmp_path / "topics.yml"
	metadata_path.write_text(_yaml_with_topic("      alias: amino_acids\n"))
	subjects = metadata_module.load_metadata_file(str(metadata_path))
	assert subjects["biochemistry"].topics[0].alias == "amino_acids"


def test_alias_uppercase_rejected(tmp_path):
	metadata_path = tmp_path / "topics.yml"
	metadata_path.write_text(_yaml_with_topic("      alias: Amino_Acids\n"))
	with pytest.raises(metadata_module.MetadataError):
		metadata_module.load_metadata_file(str(metadata_path))


def test_alias_topicNN_collision_rejected(tmp_path):
	# alias 'topic15' would collide with the canonical key form.
	metadata_path = tmp_path / "topics.yml"
	metadata_path.write_text(_yaml_with_topic("      alias: topic15\n"))
	with pytest.raises(metadata_module.MetadataError):
		metadata_module.load_metadata_file(str(metadata_path))


def test_duplicate_alias_within_subject_rejected(tmp_path):
	body = (
		"biochemistry:\n"
		"  title: Biochemistry\n"
		"  description: subject intro\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: First\n"
		"      description: First topic\n"
		"      alias: shared\n"
		"    topic02:\n"
		"      title: Second\n"
		"      description: Second topic\n"
		"      alias: shared\n"
	)
	metadata_path = tmp_path / "topics.yml"
	metadata_path.write_text(body)
	with pytest.raises(metadata_module.MetadataError):
		metadata_module.load_metadata_file(str(metadata_path))


def test_duplicate_alias_across_subjects_allowed(tmp_path):
	# Same alias text can appear in different subjects.
	body = (
		"biochemistry:\n"
		"  title: Biochemistry\n"
		"  description: subject intro\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: DNA structure\n"
		"      description: DNA structure topic\n"
		"      alias: dna_structure\n"
		"genetics:\n"
		"  title: Genetics\n"
		"  description: subject intro\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: DNA structure\n"
		"      description: DNA structure topic\n"
		"      alias: dna_structure\n"
	)
	metadata_path = tmp_path / "topics.yml"
	metadata_path.write_text(body)
	subjects = metadata_module.load_metadata_file(str(metadata_path))
	assert subjects["biochemistry"].topics[0].alias == "dna_structure"
	assert subjects["genetics"].topics[0].alias == "dna_structure"


def test_build_topic_alias_map(tmp_path):
	body = (
		"biochemistry:\n"
		"  title: Biochemistry\n"
		"  description: subject intro\n"
		"  topics:\n"
		"    topic01:\n"
		"      title: First\n"
		"      description: First topic\n"
		"      alias: life_molecules\n"
		"    topic02:\n"
		"      title: Second\n"
		"      description: Second topic\n"
		# topic02 has no alias on purpose.
	)
	metadata_path = tmp_path / "topics.yml"
	metadata_path.write_text(body)
	subjects = metadata_module.load_metadata_file(str(metadata_path))
	alias_map = metadata_module.build_topic_alias_map(subjects)
	assert alias_map == {"biochemistry": {"life_molecules": "topic01"}}

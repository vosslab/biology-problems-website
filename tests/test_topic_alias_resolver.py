"""Resolver tests for bioproblems_site.topic_aliases."""

# PIP3 modules
import pytest

# local repo modules
import bioproblems_site.metadata as metadata
import bioproblems_site.topic_aliases as topic_aliases


# Minimal in-memory fixture: one subject with one aliased topic
# (topic03/amino_acids) and one non-aliased topic (topic14).
_SUBJECT_WITH_MIXED_TOPICS = metadata.Subject(
	key="biochemistry",
	title="Biochemistry",
	description="",
	topics=(
		metadata.Topic(
			key="topic03", title="Amino Acids", description="d",
			libretexts=None, visible=True, alias="amino_acids",
		),
		metadata.Topic(
			key="topic14", title="Human Senses", description="d",
			libretexts=None, visible=True, alias=None,
		),
	),
)
_SUBJECTS_SINGLE = {"biochemistry": _SUBJECT_WITH_MIXED_TOPICS}
_ALIAS_MAP_SINGLE = metadata.build_topic_alias_map(_SUBJECTS_SINGLE)


# ---------------- is_topic_key ----------------

def test_is_topic_key_accepts_two_digit():
	assert topic_aliases.is_topic_key("topic03") is True


def test_is_topic_key_rejects_one_digit():
	assert topic_aliases.is_topic_key("topic3") is False


def test_is_topic_key_rejects_three_digit():
	assert topic_aliases.is_topic_key("topic003") is False


# ---------------- validate_topic_cell ----------------

def test_validate_strips_whitespace():
	assert topic_aliases.validate_topic_cell("  amino_acids  ") == "amino_acids"


def test_validate_rejects_empty():
	with pytest.raises(metadata.MetadataError):
		topic_aliases.validate_topic_cell("   ")


def test_validate_rejects_uppercase():
	with pytest.raises(metadata.MetadataError):
		topic_aliases.validate_topic_cell("Amino_Acids")


def test_validate_rejects_embedded_space():
	with pytest.raises(metadata.MetadataError):
		topic_aliases.validate_topic_cell("amino acids")


def test_validate_rejects_dash():
	with pytest.raises(metadata.MetadataError):
		topic_aliases.validate_topic_cell("amino-acids")


# ---------------- resolve_topic_key ----------------

def test_resolve_alias_hit():
	assert topic_aliases.resolve_topic_key(
		"biochemistry", "amino_acids", _ALIAS_MAP_SINGLE,
		source="t.csv", line_number=2,
	) == "topic03"


def test_resolve_alias_with_whitespace():
	assert topic_aliases.resolve_topic_key(
		"biochemistry", " amino_acids ", _ALIAS_MAP_SINGLE,
		source="t.csv",
	) == "topic03"


def test_resolve_unknown_alias_raises():
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_key(
			"biochemistry", "amino_acid", _ALIAS_MAP_SINGLE,
			source="t.csv", line_number=2,
		)


def test_resolve_topicNN_for_aliased_topic_raises():
	# topic03 has alias 'amino_acids'; raw topicNN must be rejected.
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_key(
			"biochemistry", "topic03", _ALIAS_MAP_SINGLE,
			source="t.csv", line_number=2,
		)


def test_resolve_topicNN_for_non_aliased_topic_accepted():
	# topic14 has no alias, so raw topicNN is allowed.
	assert topic_aliases.resolve_topic_key(
		"biochemistry", "topic14", _ALIAS_MAP_SINGLE,
		source="t.csv",
	) == "topic14"


def test_resolve_unknown_subject_raises():
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_key(
			"physics", "amino_acids", _ALIAS_MAP_SINGLE,
			source="t.csv",
		)


def test_resolve_uppercase_raises():
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_key(
			"biochemistry", "Amino_Acids", _ALIAS_MAP_SINGLE,
			source="t.csv",
		)


# ---------------- resolve_topic_filter ----------------

# Cross-subject fixture: same alias 'dna_structure' in two subjects;
# topic03 exists in both with different alias status.
_GENETICS = metadata.Subject(
	key="genetics",
	title="Genetics",
	description="",
	topics=(
		metadata.Topic(
			key="topic03", title="DNA structure", description="d",
			libretexts=None, visible=True, alias="dna_structure",
		),
	),
)
_BIOCHEM_DNA = metadata.Subject(
	key="biochemistry",
	title="Biochemistry",
	description="",
	topics=(
		metadata.Topic(
			key="topic11", title="DNA structure", description="d",
			libretexts=None, visible=True, alias="dna_structure",
		),
		metadata.Topic(
			key="topic03", title="Amino Acids", description="d",
			libretexts=None, visible=True, alias="amino_acids",
		),
	),
)
_SUBJECTS_MULTI = {"biochemistry": _BIOCHEM_DNA, "genetics": _GENETICS}
_ALIAS_MAP_MULTI = metadata.build_topic_alias_map(_SUBJECTS_MULTI)


def test_filter_subject_alias_form():
	assert topic_aliases.resolve_topic_filter(
		"biochemistry:amino_acids", _ALIAS_MAP_MULTI, _SUBJECTS_MULTI,
	) == ("biochemistry", "topic03")


def test_filter_subject_topicNN_for_unaliased():
	# Add a non-aliased topic to test bare topicNN under subject prefix.
	subjects = {
		"biochemistry": metadata.Subject(
			key="biochemistry", title="B", description="",
			topics=(
				metadata.Topic(
					key="topic14", title="Senses", description="d",
					libretexts=None, visible=True, alias=None,
				),
			),
		),
	}
	alias_map = metadata.build_topic_alias_map(subjects)
	assert topic_aliases.resolve_topic_filter(
		"biochemistry:topic14", alias_map, subjects,
	) == ("biochemistry", "topic14")


def test_filter_subject_topicNN_for_aliased_raises():
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_filter(
			"biochemistry:topic03", _ALIAS_MAP_MULTI, _SUBJECTS_MULTI,
		)


def test_filter_bare_alias_unique():
	assert topic_aliases.resolve_topic_filter(
		"amino_acids", _ALIAS_MAP_MULTI, _SUBJECTS_MULTI,
	) == ("biochemistry", "topic03")


def test_filter_bare_alias_ambiguous_raises():
	# 'dna_structure' exists in both biochemistry and genetics.
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_filter(
			"dna_structure", _ALIAS_MAP_MULTI, _SUBJECTS_MULTI,
		)


def test_filter_bare_topicNN_all_aliased_raises():
	# topic03 exists in both subjects but each has an alias defined.
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_filter(
			"topic03", _ALIAS_MAP_MULTI, _SUBJECTS_MULTI,
		)


def test_filter_unknown_alias_raises():
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_filter(
			"nonexistent", _ALIAS_MAP_MULTI, _SUBJECTS_MULTI,
		)


def test_filter_malformed_subject_alias_raises():
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_filter(
			":amino_acids", _ALIAS_MAP_MULTI, _SUBJECTS_MULTI,
		)

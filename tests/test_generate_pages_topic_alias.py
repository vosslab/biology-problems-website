"""Integration tests for generate_pages.py topic filter resolution.

Tests the wiring of topic alias resolution in generate_pages.py through
bioproblems_site.topic_aliases.resolve_topic_filter.
"""

# PIP3 modules
import pytest

# local repo modules
import bioproblems_site.metadata as metadata
import bioproblems_site.topic_aliases as topic_aliases


# Minimal in-memory fixture: two subjects with mixed aliased/non-aliased topics.
_BIOCHEM = metadata.Subject(
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

_GENETICS = metadata.Subject(
	key="genetics",
	title="Genetics",
	description="",
	topics=(
		metadata.Topic(
			key="topic01", title="DNA Structure", description="d",
			libretexts=None, visible=True, alias="dna_structure",
		),
		metadata.Topic(
			key="topic05", title="Inheritance", description="d",
			libretexts=None, visible=True, alias=None,
		),
	),
)

_SUBJECTS = {"biochemistry": _BIOCHEM, "genetics": _GENETICS}
_ALIAS_MAP = metadata.build_topic_alias_map(_SUBJECTS)


# ========== Test subject:alias preferred form ==========

def test_subject_alias_preferred_form():
	"""subject:alias is always unambiguous and preferred."""
	subject, topic = topic_aliases.resolve_topic_filter(
		"biochemistry:amino_acids", _ALIAS_MAP, _SUBJECTS,
	)
	assert subject == "biochemistry"
	assert topic == "topic03"


# ========== Test subject:topicNN for unaliased topic ==========

def test_subject_unaliased_topicnn():
	"""subject:topicNN accepted for topics with no alias."""
	subject, topic = topic_aliases.resolve_topic_filter(
		"biochemistry:topic14", _ALIAS_MAP, _SUBJECTS,
	)
	assert subject == "biochemistry"
	assert topic == "topic14"


def test_genetics_subject_unaliased_topicnn():
	"""Works across different subjects."""
	subject, topic = topic_aliases.resolve_topic_filter(
		"genetics:topic05", _ALIAS_MAP, _SUBJECTS,
	)
	assert subject == "genetics"
	assert topic == "topic05"


# ========== Test subject:topicNN for aliased topic raises ==========

def test_subject_aliased_topicnn_raises():
	"""subject:topicNN raises when topic has an alias defined."""
	# The error must mention the alias the author should use; that
	# is the actionable contract. Phrasing of the rest of the
	# message is implementation detail, so do not pin it.
	with pytest.raises(metadata.MetadataError, match="amino_acids"):
		topic_aliases.resolve_topic_filter(
			"biochemistry:topic03", _ALIAS_MAP, _SUBJECTS,
		)


# ========== Test bare alias unique ==========

def test_bare_alias_unique():
	"""Bare alias resolves when it exists in only one subject."""
	subject, topic = topic_aliases.resolve_topic_filter(
		"amino_acids", _ALIAS_MAP, _SUBJECTS,
	)
	assert subject == "biochemistry"
	assert topic == "topic03"


def test_genetics_bare_alias_unique():
	"""Bare alias unique in genetics resolves."""
	subject, topic = topic_aliases.resolve_topic_filter(
		"dna_structure", _ALIAS_MAP, _SUBJECTS,
	)
	assert subject == "genetics"
	assert topic == "topic01"


# ========== Test bare alias ambiguous raises ==========

# For this test, we need a fixture where the same alias exists twice.
_BIOCHEM_SHARED = metadata.Subject(
	key="biochemistry",
	title="Biochemistry",
	description="",
	topics=(
		metadata.Topic(
			key="topic11", title="DNA Structure", description="d",
			libretexts=None, visible=True, alias="dna_structure",
		),
	),
)

_SUBJECTS_AMBIGUOUS_ALIAS = {
	"biochemistry": _BIOCHEM_SHARED,
	"genetics": _GENETICS,  # also has dna_structure
}
_ALIAS_MAP_AMBIGUOUS = metadata.build_topic_alias_map(_SUBJECTS_AMBIGUOUS_ALIAS)


def test_bare_alias_ambiguous_raises():
	"""Bare alias raises when it exists in multiple subjects."""
	# Just check the error type; the specific phrasing is allowed
	# to evolve. The integration is covered by resolver tests.
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_filter(
			"dna_structure", _ALIAS_MAP_AMBIGUOUS, _SUBJECTS_AMBIGUOUS_ALIAS,
		)


# ========== Test unknown alias raises ==========

def test_unknown_alias_raises():
	"""Unknown alias raises with helpful message."""
	# The error must name the offending value so the author knows
	# what they typed; the exact phrasing of "unknown alias" is
	# implementation detail and not pinned here.
	with pytest.raises(metadata.MetadataError, match="nonexistent_alias"):
		topic_aliases.resolve_topic_filter(
			"nonexistent_alias", _ALIAS_MAP, _SUBJECTS,
		)


# ========== Test bare topicNN unaliased ==========

def test_bare_topicnn_unaliased_unique():
	"""Bare topicNN accepted if it exists in exactly one subject with no alias."""
	# topic05 exists only in genetics and has no alias.
	subject, topic = topic_aliases.resolve_topic_filter(
		"topic05", _ALIAS_MAP, _SUBJECTS,
	)
	assert subject == "genetics"
	assert topic == "topic05"


# ========== Test bare topicNN all aliased raises ==========

_BIOCHEM_BOTH_ALIASED = metadata.Subject(
	key="biochemistry",
	title="Biochemistry",
	description="",
	topics=(
		metadata.Topic(
			key="topic03", title="Amino Acids", description="d",
			libretexts=None, visible=True, alias="amino_acids",
		),
	),
)

_GENETICS_BOTH_ALIASED = metadata.Subject(
	key="genetics",
	title="Genetics",
	description="",
	topics=(
		metadata.Topic(
			key="topic03", title="Something Else", description="d",
			libretexts=None, visible=True, alias="dna_structure",
		),
	),
)

_SUBJECTS_BOTH_ALIASED = {
	"biochemistry": _BIOCHEM_BOTH_ALIASED,
	"genetics": _GENETICS_BOTH_ALIASED,
}
_ALIAS_MAP_BOTH_ALIASED = metadata.build_topic_alias_map(_SUBJECTS_BOTH_ALIASED)


def test_bare_topicnn_all_aliased_raises():
	"""Bare topicNN raises if all subjects that define it have an alias."""
	# Pin only the offending value (topic03) so the test does not
	# break if the error phrasing is reworded.
	with pytest.raises(metadata.MetadataError, match="topic03"):
		topic_aliases.resolve_topic_filter(
			"topic03", _ALIAS_MAP_BOTH_ALIASED, _SUBJECTS_BOTH_ALIASED,
		)


# ========== Test malformed subject:alias forms ==========

def test_malformed_missing_subject():
	"""Missing subject in subject:alias form."""
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_filter(
			":amino_acids", _ALIAS_MAP, _SUBJECTS,
		)


def test_malformed_missing_topic():
	"""Missing topic in subject:alias form."""
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_filter(
			"biochemistry:", _ALIAS_MAP, _SUBJECTS,
		)


def test_malformed_empty_string():
	"""Empty string raises."""
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_filter(
			"", _ALIAS_MAP, _SUBJECTS,
		)


def test_malformed_whitespace_only():
	"""Whitespace-only string raises."""
	with pytest.raises(metadata.MetadataError):
		topic_aliases.resolve_topic_filter(
			"   ", _ALIAS_MAP, _SUBJECTS,
		)

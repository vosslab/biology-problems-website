"""Behavioral tests for bioproblems_site.subject_index rendering.

Asserts on two durable properties:
- the generated marker appears at the top (required for overwrite safety)
- topics with zero questions are omitted (the UX-review-motivating bug)
"""

# PIP3 modules
import pytest

# local repo modules
import bioproblems_site.metadata as metadata
import bioproblems_site.scanner as scanner
import bioproblems_site.subject_index as subject_index


@pytest.fixture
def subject():
	topic_a = metadata.Topic(
		key="topic01", title="One", description="first",
		libretexts=None, visible=True,
	)
	topic_b = metadata.Topic(
		key="topic02", title="Two", description="second",
		libretexts=None, visible=True,
	)
	return metadata.Subject(
		key="biochemistry",
		title="Biochemistry",
		description="Subject intro.",
		topics=(topic_a, topic_b),
	)


def test_output_begins_with_generated_marker(subject):
	scans = {
		"topic01": scanner.TopicScan(questions=3, formats=frozenset()),
		"topic02": scanner.TopicScan(questions=0, formats=frozenset()),
	}
	out = subject_index.render_subject_index(subject, scans)
	assert out.startswith(subject_index.GENERATED_MARKER)


def test_zero_question_topics_are_omitted(subject):
	scans = {
		"topic01": scanner.TopicScan(questions=3, formats=frozenset()),
		"topic02": scanner.TopicScan(questions=0, formats=frozenset()),
	}
	out = subject_index.render_subject_index(subject, scans)
	assert "topic01/index.md" in out
	assert "topic02/index.md" not in out

"""Tests for the generated, browser-searchable question index."""

from pathlib import Path

import bioproblems_site.metadata as metadata
import bioproblems_site.question_index as question_index


#============================================
def test_question_index_uses_cached_titles_and_fallbacks(tmp_path: Path) -> None:
	"""The public page lists cached titles and remains useful without a cache."""
	topic = metadata.Topic(
		key="topic01", title="Cells", description="Cell questions.",
		libretexts=None, visible=True, alias=None,
	)
	subject = metadata.Subject(
		key="biology", title="Biology", description="Biology questions.",
		topics=(topic,),
	)
	topic_dir = tmp_path / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "bbq-cells-questions.txt").write_text("MC\tQuestion\n")
	(topic_dir / "bbq-missing-title-questions.txt").write_text("MC\tQuestion\n")
	(topic_dir / "problem_set_titles.yml").write_text(
		"bbq-cells-questions.txt: Cell Membranes\n"
	)

	entries = question_index.collect_entries(
		tmp_path, {"biology": subject}, ("biology",),
	)
	text = question_index.render(entries)

	assert "# All Biology Problems" in text
	assert "Cell Membranes" in text
	assert "Problem set: missing title" in text
	assert "../biology/topic01/" in text
	assert question_index.GENERATED_MARKER in text

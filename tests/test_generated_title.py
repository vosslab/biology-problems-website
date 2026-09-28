"""Generated problem-set titles remain valid for the topic page."""

from pathlib import Path

import pytest

import bioproblems_site.topic_page as topic_page


#============================================
def test_generated_dna_prime_marks_are_ascii(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A valid DNA-direction title must not fail the page after repeated retries."""
	cache_path = tmp_path / "titles.yml"
	monkeypatch.setattr(topic_page.title_cache, "path_for_source", lambda path: cache_path)
	monkeypatch.setattr(
		topic_page.bioproblems_site.problem_set_title,
		"get_problem_title_from_file",
		lambda client, path: "mRNA Transcription from 5\u2032/3\u2032 DNA Templates (MC)",
	)
	bbq_path = str(tmp_path / "bbq-rna_transcribe-questions.txt")
	title = topic_page.get_problem_set_title(object(), bbq_path)

	assert title == "mRNA Transcription from 5'/3' DNA Templates (MC)"

"""Tests for the generated, browser-searchable question index."""

from pathlib import Path

from bs4 import BeautifulSoup

import bioproblems_site.metadata as metadata
import bioproblems_site.problem_set_display as problem_set_display
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
	site_docs_dir = tmp_path / "site_docs"
	topic_dir = site_docs_dir / "biology" / "topic01"
	topic_dir.mkdir(parents=True)
	(topic_dir / "bbq-cells-questions.txt").write_text("MC\tQuestion\n")
	(topic_dir / "bbq-missing-title-questions.txt").write_text("MC\tQuestion\n")
	(tmp_path / "problem_set_titles.yml").write_text(
		"bbq-cells-questions.txt: Cell Membranes\n"
	)

	entries = question_index.collect_entries(
		site_docs_dir, {"biology": subject}, ("biology",),
	)
	text = question_index.render(entries)

	assert "# All Biology Problems" in text
	assert "Cell Membranes" in text
	assert "Problem set: missing title" in text
	assert "../biology/topic01/" in text
	assert question_index.GENERATED_MARKER in text


#============================================
def test_format_badges_preserve_qualifiers_and_escape_titles(tmp_path: Path) -> None:
	"""Readable variants survive source-specific badge rendering safely."""
	source = tmp_path / 'bbq-protein_gel_migration-questions.txt'
	source.write_text('MC\tQuestion\n')
	entry = question_index.QuestionSetEntry(
		subject_title='Biochemistry', topic_title='Proteins',
		page_path='biochemistry/topic05/index.md',
		title='Protein <size> & Migration (With Ladder, MC/NUM)',
		source_path=source,
	)
	soup = BeautifulSoup(question_index.render([entry]), 'html.parser')
	link = soup.find('a')
	row = soup.find('span', class_='question-index-entry')
	assert 'Protein <size> & Migration (With Ladder)' in link.get_text()
	assert link.find('size') is None
	assert row.find_all(recursive=False) == [row.find('span', class_='question-type-badges'), link]
	assert [(badge.get_text(), badge['title']) for badge in soup.find_all('abbr')] == [
		('MC', 'Multiple Choice'),
	]
	assert '(With Ladder, MC/NUM)' not in link.get_text()
	assert all(badge.find_parent('a') is None for badge in soup.find_all('abbr'))


#============================================
def test_statement_badge_explains_the_multiple_choice_response() -> None:
	"""The internal TFMS code reads as statement content with an MC response."""
	title = 'DNA Structure (Core Set, TFMS)'
	assert problem_set_display.render_title(title) == 'DNA Structure (Core Set)'
	soup = BeautifulSoup(problem_set_display.render_badges(title), 'html.parser')
	assert soup.get_text() == 'T/F Statements (MC)'
	assert soup.abbr['title'] == 'True/False Statements (Multiple Choice)'


#============================================
def test_same_filename_uses_each_generated_files_response_type(tmp_path: Path) -> None:
	"""Shared cache titles do not turn uniform downloads into mixed-format sets."""
	topics = (
		metadata.Topic(key='topic01', title='Proteins', description='',
			libretexts=None, visible=True, alias=None),
		metadata.Topic(key='topic02', title='Gels', description='',
			libretexts=None, visible=True, alias=None),
	)
	subject = metadata.Subject(
		key='biology', title='Biology', description='', topics=topics,
	)
	filename = 'bbq-protein_gel_migration-questions.txt'
	site_docs = tmp_path / 'site_docs'
	for topic, raw_type in zip(topics, ('MC', 'NUM')):
		topic_dir = site_docs / 'biology' / topic.key
		topic_dir.mkdir(parents=True)
		(topic_dir / filename).write_text(f'{raw_type}\tQuestion\n')
	(tmp_path / 'problem_set_titles.yml').write_text(
		f'{filename}: Protein Molecular Weight (MC/NUM)\n'
	)

	entries = question_index.collect_entries(
		site_docs, {'biology': subject}, ('biology',),
	)
	soup = BeautifulSoup(question_index.render(entries), 'html.parser')
	assert [badge.get_text() for badge in soup.find_all('abbr')] == ['MC', 'NUM']
	assert 'MC/NUM' not in soup.get_text()


#============================================
def test_mc_subtype_uses_filename(tmp_path: Path) -> None:
	"""WOMC and TFMS are distinct MC generator families."""
	womc = tmp_path / 'bbq-WOMC-properties-questions.txt'
	tfms = tmp_path / 'bbq-TFMS-properties-questions.txt'
	regular = tmp_path / 'bbq-properties-questions.txt'
	womc.write_text('MC\tQuestion\n')
	tfms.write_text('MC\tQuestion\n')
	regular.write_text('MC\tQuestion\n')
	assert problem_set_display.question_type_for_source(womc) == 'WOMC'
	assert problem_set_display.question_type_for_source(tfms) == 'TFMS'
	assert problem_set_display.question_type_for_source(regular) == 'MC'


#============================================
def test_multiple_blanks_has_distinct_badge(tmp_path: Path) -> None:
	"""BBQ FIB_PLUS represents MULTI_FIB rather than ordinary FiB."""
	source = tmp_path / 'bbq-multiple_blanks-questions.txt'
	source.write_text('FIB_PLUS\tQuestion\n')
	soup = BeautifulSoup(
		problem_set_display.render_badges('Gene Distances (MULTI_FIB)', source_path=source),
		'html.parser',
	)
	assert soup.get_text() == 'Multi-FiB'
	assert soup.abbr['title'] == 'Multiple Fill in the Blanks'
	assert 'question-type-multi-fib' in soup.abbr['class']

"""Render descriptive titles and their separate question-type badges."""

# Standard Library
import html
from pathlib import Path


QUESTION_TYPES = {
	'MC': ('MC', 'Multiple Choice'),
	'WOMC': ('WOMC', 'Which One Multiple Choice (from matching content)'),
	'TFMS': ('T/F Statements (MC)', 'True/False Statements (Multiple Choice)'),
	'MA': ('MA', 'Multiple Answer'),
	'FiB': ('FiB', 'Fill in the Blank'),
	'MULTI_FIB': ('Multi-FiB', 'Multiple Fill in the Blanks'),
	'NUM': ('NUM', 'Numeric'),
	'Matching': ('Matching', 'Matching'),
	'ORD': ('ORD', 'Ordering'),
}

BBQ_TYPES = {
	'MA': 'MA',
	'MAT': 'Matching',
	'FIB': 'FiB',
	'FIB_PLUS': 'MULTI_FIB',
	'NUM': 'NUM',
	'ORD': 'ORD',
}


#============================================
def split_title(title: str) -> tuple[str, tuple[str, ...]]:
	"""Separate a recognized final format label, preserving content qualifiers."""
	base, opening, suffix = title.rpartition(' (')
	if not opening or not suffix.endswith(')'):
		return title, ()
	qualifiers = suffix[:-1].split(', ')
	question_types = tuple(qualifiers[-1].split('/'))
	if not all(label in QUESTION_TYPES for label in question_types):
		return title, ()
	if len(qualifiers) > 1:
		base += f" ({', '.join(qualifiers[:-1])})"
	return base, question_types


#============================================
def question_type_for_source(source_path: str | Path) -> str:
	"""Read the response type from this generated BBQ file."""
	source_path = Path(source_path)
	with source_path.open(encoding='utf-8') as source:
		# The token before the first tab identifies the BBQ record type.
		raw_type = source.readline().partition('\t')[0].strip().upper()
	if raw_type == 'MC':
		if source_path.name.startswith('bbq-WOMC-'):
			return 'WOMC'
		if source_path.name.startswith('bbq-TFMS-'):
			return 'TFMS'
		return 'MC'
	if raw_type not in BBQ_TYPES:
		raise ValueError(f'Unsupported BBQ question type {raw_type!r}: {source_path}')
	return BBQ_TYPES[raw_type]


#============================================
def render_title(
		title: str,
		href: str | None = None,
) -> str:
	"""Return the escaped descriptive title without its format suffix."""
	base, _question_types = split_title(title)
	# ASVS 1.2.1: encode catalog text at the HTML output boundary.
	text = html.escape(base)
	if href is not None:
		text = f'<a href="{html.escape(href, quote=True)}">{text}</a>'
	return text


#============================================
def render_badges(title: str, source_path: str | Path | None = None) -> str:
	"""Return format metadata for a cached title or a generated BBQ file."""
	_question_base, question_types = split_title(title)
	if source_path is not None:
		question_types = (question_type_for_source(source_path),)
	if not question_types:
		return ''
	badges = []
	for code in question_types:
		label, full_name = QUESTION_TYPES[code]
		css_type = code.lower().replace('_', '-')
		badges.append(
			f'<abbr class="question-type question-type-{css_type}" '
			f'title="{full_name}">{label}</abbr>'
		)
	# Titles without a source may describe more than one generator output.
	return '<span class="question-type-badges">' + '/'.join(badges) + '</span>'

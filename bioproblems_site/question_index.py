"""Render the human-readable all-questions site map."""

import html
from dataclasses import dataclass
from pathlib import Path

import bioproblems_site.file_write as file_write
import bioproblems_site.metadata as metadata_module
import bioproblems_site.problem_set_display as problem_set_display
import bioproblems_site.title_cache as title_cache


GENERATED_MARKER = (
	"<!-- GENERATED FROM BBQ SOURCES BY bioproblems_site.question_index -- "
	"DO NOT EDIT -->"
)


#============================================
@dataclass(frozen=True)
class QuestionSetEntry:
	"""One generated problem set listed on the public question index."""

	subject_title: str
	topic_title: str
	page_path: str
	title: str
	source_path: Path | None = None


#============================================
def _load_titles(cache_path: Path) -> dict[str, str]:
	"""Return cached generated titles keyed by BBQ source basename."""
	payload = title_cache.load(cache_path)
	return {
		key: value.strip()
		for key, value in payload.items()
		if isinstance(key, str)
		and key.startswith("bbq-")
		and isinstance(value, str)
		and value.strip()
	}


#============================================
def _fallback_title(source_name: str) -> str:
	"""Return a readable title when a generated title cache is unavailable."""
	stem = source_name.removeprefix("bbq-").removesuffix("-questions.txt")
	words = stem.replace("_", " ").replace("-", " ").strip()
	return f"Problem set: {words}" if words else "Untitled problem set"


#============================================
def collect_entries(
		site_docs_dir: Path,
		subjects: dict[str, metadata_module.Subject],
		nav_order: tuple[str, ...],
	) -> list[QuestionSetEntry]:
	"""Collect current BBQ problem sets in subject and topic order."""
	entries: list[QuestionSetEntry] = []
	titles = _load_titles(title_cache.path_for_site_docs(site_docs_dir))
	for subject_key in nav_order:
		subject = subjects[subject_key]
		for topic in subject.topics:
			if not topic.visible:
				continue
			topic_dir = site_docs_dir / subject_key / topic.key
			sources = sorted(topic_dir.glob("bbq-*-questions.txt"))
			if not sources:
				continue
			page_path = f"{subject_key}/{topic.key}/index.md"
			for source_path in sources:
				entries.append(QuestionSetEntry(
					subject_title=subject.title,
					topic_title=topic.title,
					page_path=page_path,
					title=titles.get(source_path.name, _fallback_title(source_path.name)),
					source_path=source_path,
				))
	return entries


#============================================
def render(entries: list[QuestionSetEntry]) -> str:
	"""Render the browser-searchable public question index Markdown."""
	lines = [
		GENERATED_MARKER,
		"",
		"# All Biology Problems",
		"",
		"Browse the generated problem sets by subject and topic. Use your browser's "
		"Find command to search all problem-set titles on this page.",
		"",
		f"**{len(entries)} problem sets**",
		"",
	]
	current_subject = ""
	current_topic = ""
	for entry in entries:
		if entry.subject_title != current_subject:
			if current_subject:
				lines.append("")
			current_subject = entry.subject_title
			current_topic = ""
			lines.extend([f"## {html.escape(current_subject)}", ""])
		if entry.topic_title != current_topic:
			if current_topic:
				lines.append("")
			current_topic = entry.topic_title
			lines.extend([f"### {html.escape(current_topic)}", ""])
		page_href = f"../{entry.page_path.removesuffix('/index.md')}/"
		badge = problem_set_display.render_badges(entry.title, source_path=entry.source_path)
		title = problem_set_display.render_title(entry.title, href=page_href)
		lines.append(f'- <span class="question-index-entry">{badge}{title}</span>')
	lines.append("")
	return "\n".join(lines)


#============================================
def write(
		output_path: Path,
		site_docs_dir: Path,
		metadata_path: Path,
		mkdocs_path: Path,
		dry_run: bool = False,
	) -> str:
	"""Render and optionally write the public question index."""
	subjects, nav_order = metadata_module.load_topics_metadata(
		metadata_path=str(metadata_path),
		mkdocs_path=str(mkdocs_path),
	)
	text = render(collect_entries(site_docs_dir, subjects, nav_order))
	if not dry_run:
		file_write.write_text(output_path, text)
	return text

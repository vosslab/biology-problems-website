"""Render site_docs/<subject>/index.md from YAML metadata + scan.

Output carries a generated-file marker, a per-topic question-count chip,
and a LibreTexts icon anchor when a topic has an external chapter.
"""

# Standard Library
import os

# local repo modules
import bioproblems_site.metadata as metadata_module


#============================================
GENERATED_MARKER = (
	"<!-- GENERATED FROM topics_metadata.yml BY "
	"bioproblems_site.subject_index -- DO NOT EDIT -->"
)

LIBRETEXTS_ICON_SRC = "/assets/images/libretexts.png"


def _count_chip(question_count: int) -> str:
	"""Return the inline span for the per-topic question count chip."""
	noun = "question" if question_count == 1 else "questions"
	return (
		f"<span class='topic-count' title='{question_count} {noun}'>"
		f"{question_count} {noun}</span>"
	)


def _libretexts_icon_anchor(link: "metadata_module.LibreTextsLink") -> str:
	"""Return the LibreTexts icon anchor: <a><img class=lt-icon></a>.

	Label ("Unit N, Chapter M" or just "Chapter M") lives in aria-label
	for screen readers; visible glyph is the icon only.
	"""
	if link.unit and link.chapter:
		label = f"Unit {link.unit}, Chapter {link.chapter}"
	else:
		label = f"Chapter {link.chapter}"
	aria = f"LibreTexts {label}"
	return (
		f'<a href="{link.url}" target="_blank" rel="noopener" '
		f'aria-label="{aria}" title="Open LibreTexts chapter">'
		f'<img src="{LIBRETEXTS_ICON_SRC}" alt="" class="lt-icon"></a>'
	)


#============================================
def render_subject_index(
	subject: "metadata_module.Subject",
	scans: dict,
) -> str:
	"""Return the rendered markdown for one subject's index.md.

	Topics with zero questions or visible=False are omitted entirely.
	"""
	lines = [GENERATED_MARKER, "", f"# List of {subject.title} Topics", ""]
	if subject.description:
		for paragraph_line in subject.description.splitlines():
			lines.append(paragraph_line)
		lines.append("")
	lines.append("## Topics")
	lines.append("")
	display_index = 0
	for topic in subject.topics:
		if not topic.visible:
			continue
		scan = scans.get(topic.key)
		if scan is None or scan.questions == 0:
			continue
		display_index += 1
		href = f"{topic.key}/index.md"
		count_markup = _count_chip(scan.questions)
		libretexts_markup = ""
		if topic.libretexts is not None:
			libretexts_markup = " " + _libretexts_icon_anchor(topic.libretexts)
		title_line = (
			f"{display_index}. [{topic.title}]({href}) {count_markup}"
			f"{libretexts_markup}"
		)
		lines.append(title_line)
		if topic.description:
			lines.append(f"    - {topic.description}")
		lines.append("")
	body = "\n".join(lines).rstrip() + "\n"
	return body


#============================================
def has_generated_marker(path: str) -> bool:
	"""True if the file on disk starts with the generated marker."""
	if not os.path.isfile(path):
		return False
	with open(path, "r") as file_pointer:
		first_line = file_pointer.readline().rstrip("\n")
	return first_line == GENERATED_MARKER

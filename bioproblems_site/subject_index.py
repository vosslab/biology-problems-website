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
	"""Return the LibreTexts labeled anchor: logo + short "Chapter X.Y" text.

	Visible label uses the compact "Chapter unit.chapter" form (e.g.,
	"Chapter 1.2") so readers can tell at a glance which LibreTexts
	section a topic references. The longer "LibreTexts Unit N, Chapter M"
	phrasing lives in aria-label and title for screen readers and
	hover tooltips.
	"""
	# Compact visible label: "Chapter unit.chapter" when unit exists,
	# otherwise plain "Chapter M".
	if link.unit and link.chapter:
		visible_label = f"Chapter {link.unit}.{link.chapter}"
		aria_label = f"LibreTexts Unit {link.unit}, Chapter {link.chapter}"
	else:
		visible_label = f"Chapter {link.chapter}"
		aria_label = f"LibreTexts {visible_label}"
	# rel="noopener noreferrer" prevents tabnabbing and opener leaks.
	anchor = (
		f'<a class="lt-link" href="{link.url}" target="_blank" '
		f'rel="noopener noreferrer" aria-label="{aria_label}" '
		f'title="Open on LibreTexts (new tab)">'
		f'<img src="{LIBRETEXTS_ICON_SRC}" alt="" class="lt-icon">'
		f'<span class="lt-label">{visible_label}</span>'
		f'</a>'
	)
	return anchor


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

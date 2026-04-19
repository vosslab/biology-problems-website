"""Update the generated subject nav block inside mkdocs.yml.

Owns exactly one concern: build a YAML fragment that expands each
subject into its topic pages, then replace the text between explicit
BEGIN/END markers in mkdocs.yml. Everything else in mkdocs.yml is
left alone.

Guardrails:
  - both markers must exist exactly once (else RuntimeError)
  - file outside the markers is byte-preserved
  - after writing, the file is re-parsed as YAML to catch mistakes
"""

# PIP3 modules
import yaml

# local repo modules
import bioproblems_site.metadata as metadata_module
import bioproblems_site.scanner as scanner_module


#============================================
BEGIN_MARKER = "# BEGIN GENERATED SUBJECT NAV"
END_MARKER = "# END GENERATED SUBJECT NAV"


class NavMarkerError(RuntimeError):
	"""Raised when the BEGIN/END nav markers are missing or duplicated."""


#============================================
def _subject_display_labels(mkdocs_path: str) -> dict:
	"""Extract the existing subject display label (with icon) from
	mkdocs.yml nav. We preserve the hand-authored emoji/FontAwesome
	prefixes rather than regenerating them from YAML.

	Subjects can appear in two nav shapes:
	  - string value: {"Biochemistry": "biochemistry/index.md"}
	  - list value whose first entry is "<subject>/index.md":
	    {"Biochemistry": ["biochemistry/index.md", ...]}
	Both shapes are walked so icons survive the enable/disable of
	navigation.indexes and other nav-shape tweaks.
	"""
	with open(mkdocs_path, "r") as file_pointer:
		config = yaml.safe_load(file_pointer) or {}
	nav = config.get("nav", [])
	labels = {}
	for entry in nav:
		if not isinstance(entry, dict):
			continue
		for label, value in entry.items():
			# Flat subject: value is the subject index path directly.
			if isinstance(value, str) and value.endswith("/index.md"):
				subject_key = value.split("/", 1)[0]
				labels[subject_key] = label
				continue
			# Expanded subject: value is a list of topic entries whose
			# first item is the subject index path string.
			if isinstance(value, list) and value:
				first = value[0]
				if isinstance(first, str) and first.endswith("/index.md"):
					subject_key = first.split("/", 1)[0]
					labels[subject_key] = label
	return labels


def _render_topic_lines(subject, scans: dict) -> list:
	"""Return the per-topic nav lines for one subject. Skips hidden
	topics and topics with zero questions, mirroring the subject index.
	Topic entries sit at the same indent as the subject index entry.
	"""
	lines = []
	for topic in subject.topics:
		if not topic.visible:
			continue
		scan = scans.get(topic.key)
		if scan is None or scan.questions == 0:
			continue
		numeric = topic.key.replace("topic", "")
		display = f"{numeric}: {topic.title}"
		path = f"{subject.key}/{topic.key}/index.md"
		quoted = _yaml_scalar(display)
		lines.append(f"  - {quoted}: {path}")
	return lines


def _yaml_scalar(text: str) -> str:
	"""Return a single-line YAML scalar safe to use as a mapping key.

	Double-quotes the string; escapes embedded double quotes.
	"""
	escaped = text.replace('\\', '\\\\').replace('"', '\\"')
	return f'"{escaped}"'


def _render_nav_block(
	subjects: dict,
	nav_order: tuple,
	scans_per_subject: dict,
	display_labels: dict,
) -> str:
	"""Build the YAML fragment that goes between the BEGIN/END markers.

	Does not include the markers themselves; replace_nav_block is the
	only writer that knows about markers.
	"""
	lines = []
	for subject_key in nav_order:
		subject = subjects[subject_key]
		label = display_labels.get(subject_key, subject.title)
		lines.append(f"- {_yaml_scalar(label)}:")
		# Subject index comes first so navigation.indexes uses it as
		# the section landing page.
		lines.append(f"  - {subject.key}/index.md")
		lines.extend(_render_topic_lines(
			subject, scans_per_subject[subject_key]
		))
	return "\n".join(lines) + "\n"


#============================================
def replace_nav_block(mkdocs_path: str, new_block: str) -> tuple:
	"""Replace the region between BEGIN/END markers in mkdocs.yml.

	Returns (old_block, new_block) so callers can report a diff.
	Raises NavMarkerError if markers are missing or duplicated.
	"""
	with open(mkdocs_path, "r") as file_pointer:
		original = file_pointer.read()
	begin_count = original.count(BEGIN_MARKER)
	end_count = original.count(END_MARKER)
	if begin_count != 1 or end_count != 1:
		raise NavMarkerError(
			f"{mkdocs_path}: expected exactly one {BEGIN_MARKER} and one "
			f"{END_MARKER}; found {begin_count} and {end_count}"
		)
	begin_idx = original.index(BEGIN_MARKER)
	end_idx = original.index(END_MARKER)
	if end_idx < begin_idx:
		raise NavMarkerError(
			f"{mkdocs_path}: END marker precedes BEGIN marker"
		)
	# Preserve the BEGIN line (including its trailing newline) and the
	# END line. Replace only what sits between them.
	begin_line_end = original.index("\n", begin_idx) + 1
	end_line_start = original.rfind("\n", 0, end_idx) + 1
	old_block = original[begin_line_end:end_line_start]
	updated = original[:begin_line_end] + new_block + original[end_line_start:]
	return old_block, new_block, updated


def write_nav_block(
	mkdocs_path: str,
	subjects: dict,
	nav_order: tuple,
	scans_per_subject: dict,
	*,
	dry_run: bool = False,
) -> "str | None":
	"""Build the generated nav fragment and write it into mkdocs.yml
	between the BEGIN/END markers. Re-parses the file afterwards to
	catch typos. Returns the new block text, or None on dry run.
	"""
	display_labels = _subject_display_labels(mkdocs_path)
	new_block = _render_nav_block(
		subjects, nav_order, scans_per_subject, display_labels
	)
	_old, _new, updated = replace_nav_block(mkdocs_path, new_block)
	if dry_run:
		return new_block
	# Parse the candidate in memory first so we never write a broken file.
	try:
		yaml.safe_load(updated)
	except yaml.YAMLError as error:
		raise NavMarkerError(f"generated nav block broke mkdocs.yml YAML: {error}")
	with open(mkdocs_path, "w") as file_pointer:
		file_pointer.write(updated)
	return new_block


#============================================
def update_from_sources(
	metadata_path: str = "topics_metadata.yml",
	mkdocs_path: str = "mkdocs.yml",
	site_docs_dir: str = "site_docs",
	*,
	dry_run: bool = False,
) -> "str | None":
	"""Convenience: load metadata, scan disk, and rewrite the nav block.

	This is what bioproblems_site.pipeline.run() calls.
	"""
	subjects, nav_order = metadata_module.load_topics_metadata(
		metadata_path=metadata_path, mkdocs_path=mkdocs_path
	)
	scans_per_subject = {}
	for subject_key in nav_order:
		subject = subjects[subject_key]
		topic_keys = tuple(t.key for t in subject.topics)
		scans_per_subject[subject_key] = scanner_module.scan_subject(
			site_docs_dir, subject_key, topic_keys
		)
	return write_nav_block(
		mkdocs_path, subjects, nav_order, scans_per_subject, dry_run=dry_run
	)

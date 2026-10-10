"""Topic-page renderer for bioproblems_site.

Extracted from the former root-level generate_topic_pages.py. Exposes
render_all() for direct topic-page rendering; the unified build uses its
topic-scoped stage through build_site.py.
No argparse here; the public parser lives in build_site.py.
"""

# Standard Library
import html
import os
import re
import glob
import time
import dataclasses

# local repo modules
import bioproblems_site.formats as formats_module
import bioproblems_site.git_paths as git_paths
import bioproblems_site.metadata as bp_metadata
import bioproblems_site.title_cache as title_cache
from bioproblems_site.topic_metadata import (
	get_docs_dir,
	get_libretexts_link,
	get_topic_description,
	get_topic_title,
)
import bioproblems_site.download_buttons as download_buttons
import bioproblems_site.problem_set_title
import bioproblems_site.problem_set_display as problem_set_display

#==============

# ANSI color codes for readable CLI output.
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_MAGENTA = "\033[95m"

# Format keys + labels come from the canonical registries; no local copies.
DOWNLOAD_FORMAT_KEYS = formats_module.FORMAT_KEYS
FORMAT_LABELS = download_buttons.FORMAT_LABELS


def color_text(text: str, color: str) -> str:
	"""Return colored text for CLI readability."""
	return f"{color}{text}{COLOR_RESET}"

#==============

def init_format_stats() -> dict:
	stats = {}
	for format_key in FORMAT_LABELS:
		stats[format_key] = {
			"generated": 0,
			"failed": 0,
			"existing": 0,
			"missing": 0,
			"skipped": 0,
		}
	return stats

#==============

def record_stat(stats: dict, format_key: str, bucket: str) -> None:
	if format_key not in stats:
		stats[format_key] = {
			"generated": 0,
			"failed": 0,
			"existing": 0,
			"missing": 0,
			"skipped": 0,
		}
	stats[format_key][bucket] += 1

#==============

@dataclasses.dataclass
class RenderOptions:
	"""Options consumed by render_all()."""
	download_formats: tuple = DOWNLOAD_FORMAT_KEYS
	verbose: bool = True
	# Optional pre-built client for problem-set title generation.
	llm_client: object = None

#==============
ORDER_ITEM_TYPES = frozenset(("ORD", "ORDER"))
FORMAT_ITEM_TYPE_BLACKLIST = {
	"bb_export": ORDER_ITEM_TYPES,
	"canvas_qti": ORDER_ITEM_TYPES,
}


def find_blacklisted_item_type(bbq_file_name: str, format_key: str) -> str | None:
	if format_key not in FORMAT_ITEM_TYPE_BLACKLIST:
		return None
	blacklist = FORMAT_ITEM_TYPE_BLACKLIST[format_key]
	with open(bbq_file_name, "r") as bbq_file:
		for line in bbq_file:
			item_type = line.partition("\t")[0].strip().upper()
			if item_type in blacklist:
				return item_type
	return None


def supports_blackboard_export(bbq_file_name: str) -> bool:
	"""Return whether every question has a Blackboard Ultra export writer.

	qti-package-maker's Blackboard pool-export engine has no ORDER writer.
	Do not expose an empty pool ZIP when a source contains that item type.
	"""
	return find_blacklisted_item_type(bbq_file_name, "bb_export") is None

#==============
#==============
def find_pgml_file(bbq_file_name: str) -> str:
	"""Search for a PGML file matching a given BBQ file.

	Checks downloads/ first, then the same directory as the BBQ file.
	Returns the path if found, or empty string if not.
	"""
	core_name = extract_core_name(bbq_file_name)
	dir_name = os.path.dirname(bbq_file_name)
	downloads_dir = os.path.join(dir_name, "downloads")

	# Determine expected PGML basename based on BBQ prefix
	# core_name has prefixes like MATCH-, WOMC-, MC-, TFMS-
	pgml_candidates = []
	if core_name.startswith("MATCH-"):
		yaml_base = core_name[len("MATCH-"):]
		pgml_candidates.append(f"{yaml_base}-matching.pgml")
		pgml_candidates.append(f"{yaml_base}-matching.pg")
	elif core_name.startswith("WOMC-") or core_name.startswith("MC-"):
		prefix = "WOMC-" if core_name.startswith("WOMC-") else "MC-"
		yaml_base = core_name[len(prefix):]
		pgml_candidates.append(f"{yaml_base}-which_one.pgml")
		pgml_candidates.append(f"{yaml_base}-which_one.pg")
	elif core_name.startswith("TFMS-"):
		yaml_base = core_name[len("TFMS-"):]
		pgml_candidates.append(f"{yaml_base}.pg")
		pgml_candidates.append(f"{yaml_base}.pgml")
	else:
		# Regular scripts: look for any .pgml or .pg with matching base
		pgml_candidates.append(f"{core_name}.pgml")
		pgml_candidates.append(f"{core_name}.pg")

	# Search downloads/ first, then same directory as bbq file
	search_dirs = []
	if os.path.isdir(downloads_dir):
		search_dirs.append(downloads_dir)
	search_dirs.append(dir_name)

	for search_dir in search_dirs:
		for candidate_name in pgml_candidates:
			candidate_path = os.path.join(search_dir, candidate_name)
			if os.path.isfile(candidate_path):
				return candidate_path
	return ""


#==============
def generate_download_button_row(
	bbq_file_name: str,
	download_formats: list,
	verbose: bool,
	stats: dict,
	*,
	question_type_badge: str = "",
) -> str:
	"""Render source links and browser conversion controls without artifact writes."""
	core_name = html.escape(extract_core_name(bbq_file_name), quote=True)
	bank_name = html.escape(os.path.basename(bbq_file_name), quote=True)
	html_output = f'<div id="{core_name}-button-container" class="button-container">\n'
	if question_type_badge:
		html_output += question_type_badge + "\n"
	browser_controls = False
	for format_key in DOWNLOAD_FORMAT_KEYS:
		if format_key not in download_formats:
			record_stat(stats, format_key, "skipped")
			continue
		if find_blacklisted_item_type(bbq_file_name, format_key) is not None:
			record_stat(stats, format_key, "skipped")
			continue
		label = FORMAT_LABELS[format_key]
		if format_key in download_buttons.BROWSER_FORMATS:
			prefix, extension = download_buttons.BROWSER_FORMATS[format_key]
			output_path = get_expected_outfile_name(bbq_file_name, prefix, extension)
			# ASVS 1.2.1: encode filenames at the HTML attribute boundary.
			filename = html.escape(os.path.basename(output_path), quote=True)
			accessibility_name = label
			if format_key == "bb_export":
				accessibility_name = "Blackboard Ultra pool-export ZIP"
			html_output += (
				f'<button type="button" class="md-button custom-button {format_key} qti-package-download" '
				f'data-bbq="{bank_name}" data-format="{prefix}" data-filename="{filename}" '
				f'aria-label="Generate {accessibility_name}">{label}</button>\n'
			)
			browser_controls = True
			continue
		path = bbq_file_name if format_key == "bb_text" else find_pgml_file(bbq_file_name)
		if path is None or not os.path.isfile(path):
			record_stat(stats, format_key, "missing")
			continue
		record_stat(stats, format_key, "existing")
		relative_path = html.escape(os.path.relpath(path, os.path.dirname(bbq_file_name)), quote=True)
		html_output += (
			f'<a class="md-button custom-button {format_key}" href="{relative_path}" '
			f'download aria-label="Download {label}">{label}</a>\n'
		)
	if browser_controls:
		html_output += '<span class="qti-package-status" role="status" aria-live="polite"></span>\n'
		html_output += (
			'<progress class="qti-package-progress" max="1" value="0" hidden '
			'aria-label="Package generation progress"></progress>\n'
		)
	html_output += "</div>"
	return html_output

#============================================

def is_valid_title(title: object) -> bool:
	"""
	Check whether a problem set title is valid.

	Args:
		title: The title string to validate.

	Returns:
		bool: True if the title passes all checks, False otherwise.
	"""
	if not isinstance(title, str):
		return False
	# Reject titles longer than 140 characters
	if len(title) > 140:
		return False
	# Reject titles containing LLM chain-of-thought leaks
	if 'thinking' in title.lower():
		return False
	# Reject titles containing non-ASCII characters
	if not title.isascii():
		return False
	return True

#============================================

def get_problem_set_title(client: object, bbq_file: str) -> str:
	"""
	Extracts or generates the title for a problem set based on the provided file path.

	Args:
		bbq_file (str): The full path to the problem set file.

	Returns:
		str: The title of the problem set.
	"""
	# Load the one repository-wide map instead of a topic-local cache.
	problem_set_title_yaml = title_cache.path_for_source(bbq_file)
	problem_set_title_data = title_cache.load(problem_set_title_yaml)

	# Extract the base file name from the input path
	bbq_file_basename = os.path.basename(bbq_file)

	# If the file's title is already in the YAML data, validate and return it
	if bbq_file_basename in problem_set_title_data:
		cached_title = problem_set_title_data[bbq_file_basename]
		if is_valid_title(cached_title):
			return cached_title
		# Bad cached title: remove it so we regenerate below
		print(f"WARNING: invalid cached title for {bbq_file_basename}: {cached_title!r}")
		del problem_set_title_data[bbq_file_basename]

	# Generate a new title using an external module function, retry up to 3 times
	max_retries = 3
	problem_set_title = None
	for attempt in range(max_retries):
		candidate = bioproblems_site.problem_set_title.get_problem_title_from_file(
			client, bbq_file,
		)
		# Normalize common typographic prime marks before enforcing ASCII titles.
		candidate = candidate.replace("\u2032", "'").replace("\u2033", "''")
		candidate = candidate.replace("\u2019", "'")
		if is_valid_title(candidate):
			problem_set_title = candidate
			break
		print(f"WARNING: attempt {attempt + 1}/{max_retries} produced invalid title: {candidate!r}")
	if problem_set_title is None:
		raise ValueError(f"Failed to generate valid title after {max_retries} attempts for {bbq_file_basename}: {candidate!r}")

	# Update the YAML data with the newly generated title and a timestamp of the edit
	problem_set_title_data[bbq_file_basename] = problem_set_title
	problem_set_title_data[title_cache.LAST_EDIT_KEY] = time.asctime()

	# Atomically update the shared map so interrupted writes preserve its prior state.
	title_cache.save(problem_set_title_yaml, problem_set_title_data)

	# Return the newly generated problem set title
	return problem_set_title

#==============

def extract_core_name(bbq_file_name: str) -> str:
	# Regular expression to match the core part
	if '/' in bbq_file_name:
		bbq_file_basename = os.path.basename(bbq_file_name)
	else:
		bbq_file_basename = bbq_file_name
	match = re.search(r'^bbq-(.+?)(-questions)?\.txt$', bbq_file_basename)
	if not match:
		raise ValueError
	bbq_core_name = match.group(1)
	return bbq_core_name



#==============
def get_expected_outfile_name(bbq_file_name: str, prefix: str, extension: str) -> str:
	"""Return a generated artifact path without touching the filesystem."""
	dirname = os.path.join(os.path.dirname(bbq_file_name), "downloads")
	outfile = extract_core_name(bbq_file_name)
	if not outfile.startswith(prefix):
		outfile = f'{prefix}-{outfile}'
	# Append the requested extension when it is not already present.
	if not outfile.endswith("." + extension):
		outfile += "." + extension
	outfile = os.path.join(dirname, outfile)
	return outfile


#==============

def update_index_md(
	topic_folder: str,
	bbq_files: list,
	file_counter: dict,
	total_files: int,
	download_formats: list,
	verbose: bool,
	stats: dict,
	client: object = None,
) -> None:
	"""Update or create the topic index page and its configured artifacts.

	Args:
		topic_folder: Path to the topic folder.
		bbq_files: BBQ question files to include on the page.
		file_counter: Mutable counter tracking processed BBQ files.
		total_files: Total number of BBQ files being processed.
		download_formats: Download formats to display.
		verbose: Whether to print per-file progress.
		stats: Mutable generation statistics.
		client: Optional title-generation client.
	"""
	# Normalize the folder path to handle trailing slashes
	normalized_path = os.path.normpath(topic_folder)

	# Extract the last directory name (e.g., "topic09")
	relative_topic_name = os.path.basename(normalized_path)

	topic_number = int(re.search('topic([0-9]+)', relative_topic_name).groups()[0])
	print(f"Topic Number: {topic_number}")

	title = get_topic_title(topic_folder)
	print(color_text(f"Page Title: {title}", COLOR_CYAN))

	description = get_topic_description(topic_folder)
	print(f"Page description: {description}")
	libretexts_link = get_libretexts_link(topic_folder)
	if libretexts_link:
		print(color_text(f"LibreTexts link: {libretexts_link}", COLOR_CYAN))

	index_md_path = os.path.join(topic_folder, "index.md")
	print(f"writing to {git_paths.display_path(index_md_path)}")
	with open(index_md_path, "w", encoding="utf-8") as index_md:
		index_md.write(f"# {title}\n\n")
		index_md.write(f"{description}\n\n")
		if libretexts_link:
			link_title = libretexts_link.get("title") or "LibreTexts chapter"
			# Prepend unit/chapter info to the link title
			link_unit = libretexts_link.get("unit", 0)
			link_chapter = libretexts_link.get("chapter", 0)
			if link_unit and link_chapter:
				link_title = f"Unit {link_unit}, Chapter {link_chapter}: {link_title}"
				aria_label = f"LibreTexts Unit {link_unit}, Chapter {link_chapter}"
			elif link_chapter:
				link_title = f"Chapter {link_chapter}: {link_title}"
				aria_label = f"LibreTexts Chapter {link_chapter}"
			else:
				aria_label = "LibreTexts chapter"
			libretexts_url = libretexts_link["url"]
			# Icon anchor matches the subject index convention (.lt-icon).
			icon_anchor = (
				f'<a href="{libretexts_url}" target="_blank" rel="noopener" '
				f'aria-label="{aria_label}" title="Open LibreTexts chapter">'
				f'<img src="/assets/images/libretexts.png" alt="LibreTexts" class="lt-icon"></a>'
			)
			reference_line = (
				f"**LibreTexts reference:** [{link_title}]({libretexts_url}) "
				f"{icon_anchor}"
			)
			index_md.write(f"{reference_line}\n\n")

		bbq_files.sort()
		for bbq_file in bbq_files:
			file_counter["count"] += 1
			file_progress = ""
			if total_files:
				file_progress = f"[{file_counter['count']}/{total_files}] "
			print('-' * 50)
			print(color_text(
				f"  {file_progress}BBQ file {git_paths.display_path(bbq_file)}",
				COLOR_CYAN,
			))

			# Generate the problem set title using the LLM
			problem_set_title = get_problem_set_title(client, bbq_file)
			print(color_text(f"  Problem set title: {problem_set_title}", COLOR_CYAN))

			# Add content to the index.md file
			index_md.write(f"## {problem_set_display.render_title(problem_set_title)}\n\n")
			question_type_badge = problem_set_display.render_badges(
				problem_set_title, source_path=bbq_file,
			)
			download_button_row = generate_download_button_row(
				bbq_file,
				download_formats,
				verbose,
				stats,
				question_type_badge=question_type_badge,
			)
			index_md.write(download_button_row)
			bank_name = os.path.basename(bbq_file)
			bank_url = html.escape(bank_name, quote=True)
			index_md.write(
				f'<div class="qti-selftest" data-bbq="{bank_url}">\n'
			)
			index_md.write('  <div class="selftest-reroll-content"></div>\n')
			index_md.write("</div>\n\n\n")


#==============

def enumerate_topic_jobs(
	base_dir: str,
	subject_filter: "str | None" = None,
	topic_filter: "str | None" = None,
) -> list:
	"""Discover topic folders and their BBQ source files.

	Traverses site_docs/<subject>/topic??/ folders, honoring the same
	subject/topic filters as render_all. Returns a list of
	(topic_folder, bbq_files) tuples for folders that contain at least
	one bbq-*-questions.txt source.
	"""
	all_topic_folders = glob.glob(os.path.join(base_dir, "*/topic??/"))
	all_topic_folders.sort()
	topic_jobs = []
	for topic_folder in all_topic_folders:
		norm_topic = os.path.normpath(topic_folder)
		if norm_topic == base_dir or "topic" not in norm_topic:
			continue
		# Extract subject and topic from the path (format: .../subject_key/topic_key/...).
		path_parts = norm_topic.split(os.sep)
		# Find the index of the last path component that matches topic??
		topic_key = None
		subject_key = None
		for i, part in enumerate(path_parts):
			# Match the canonical topicNN form via the shared regex,
			# not a hardcoded length check, so changes to the key
			# contract (e.g. moving to three digits) only need to be
			# made in one place.
			if bp_metadata.TOPIC_KEY_RE.match(part):
				topic_key = part
				if i > 0:
					subject_key = path_parts[i - 1]
				break
		# Apply filters: if subject_filter is set, skip other subjects.
		# If topic_filter is set, skip other topics.
		if subject_filter and subject_key != subject_filter:
			continue
		if topic_filter and topic_key != topic_filter:
			continue
		bbq_files = glob.glob(os.path.join(norm_topic, "bbq-*-questions.txt"))
		if not bbq_files:
			continue
		bbq_files.sort()
		topic_jobs.append((norm_topic, bbq_files))
	return topic_jobs

#==============

def render_all(
	options: "RenderOptions | None" = None,
	subject_filter: "str | None" = None,
	topic_filter: "str | None" = None,
	base_dir: "str | None" = None,
) -> None:
	"""Traverse topic folders and (re)generate their index.md files.

	Metadata is sourced from topics_metadata.yml exclusively.

	Args:
		options: RenderOptions object (or None for defaults).
		subject_filter: if set, only render topics under this subject key.
		topic_filter: if set, only render this topic key (within the
			filtered subject, if subject_filter is also set).
		base_dir: absolute site_docs directory supplied by a coordinator.
	"""
	if options is None:
		options = RenderOptions()
	stats = init_format_stats()
	if base_dir is None:
		base_dir = get_docs_dir()
	if not os.path.exists(base_dir):
		raise FileNotFoundError(
			f"Base directory '{git_paths.display_path(base_dir)}' not found."
		)
	if options.verbose:
		joined_formats = ", ".join(options.download_formats) or "none"
		print(color_text(f"Download formats: {joined_formats}", COLOR_CYAN))

	topic_jobs = enumerate_topic_jobs(base_dir, subject_filter, topic_filter)
	if options.verbose:
		print(color_text(
			f"Found {len(topic_jobs)} topic folders to parse", COLOR_CYAN
		))

	total_jobs = len(topic_jobs)
	total_bbq_files = sum(len(files) for _, files in topic_jobs)
	if options.verbose:
		print(color_text(
			f"Processing {total_jobs} topic folders with "
			f"{total_bbq_files} BBQ files",
			COLOR_CYAN,
		))

	file_counter = {"count": 0}
	for idx, (topic_folder, bbq_files) in enumerate(topic_jobs, start=1):
		if options.verbose:
			print("\n\n\n################################")
			progress = f"[{idx}/{total_jobs}]"
			file_progress = ""
			if total_bbq_files:
				file_progress = (
					f" ({file_counter['count'] + len(bbq_files)}/"
					f"{total_bbq_files} files)"
				)
			print(color_text(
				f"{progress} Current folder: {git_paths.display_path(topic_folder)}"
				f"{file_progress}",
				COLOR_MAGENTA,
			))
		update_index_md(
			topic_folder,
			bbq_files,
			file_counter,
			total_bbq_files,
			list(options.download_formats),
			options.verbose,
			stats,
			client=options.llm_client,
		)
	if options.verbose:
		print("\n\nSummary:")
		format_order = (
			"bb_text", "bb_export", "canvas_qti",
			"human_read", "webwork_pgml",
		)
		for format_key in format_order:
			label = FORMAT_LABELS.get(format_key, format_key)
			counts = stats.get(format_key, {})
			generated = counts.get("generated", 0)
			failed = counts.get("failed", 0)
			existing = counts.get("existing", 0)
			missing = counts.get("missing", 0)
			skipped = counts.get("skipped", 0)
			print(
				f"- {label}: generated {generated}, failed {failed}, "
				f"existing {existing}, missing {missing}, skipped {skipped}"
			)
		print(color_text("PROGRAM HAS COMPLETED!!!", COLOR_GREEN))

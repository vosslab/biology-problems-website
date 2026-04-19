"""Topic-page renderer for bioproblems_site.

Extracted from the former root-level generate_topic_pages.py. Exposes
render_all() as the callable entrypoint for bioproblems_site.pipeline.
No argparse here -- that lives in generate_pages.py at the repo root.
"""

# Standard Library
import os
import re
import glob
import time
import functools
import subprocess
import urllib.parse
import dataclasses

# PIP3 modules
import yaml

# local repo modules
import bioproblems_site.formats as formats_module
import bioproblems_site.git_paths as git_paths
import bioproblems_site.metadata as bp_metadata
import bioproblems_site.download_buttons as download_buttons
import bioproblems_site.problem_set_title

#==============

MKDOCS_CONFIG: str = "mkdocs.yml"

# ANSI color codes for readable CLI output.
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
COLOR_MAGENTA = "\033[95m"

# Format keys + labels come from the canonical registries; no local copies.
DOWNLOAD_FORMAT_KEYS = formats_module.FORMAT_KEYS
FORMAT_LABELS = download_buttons.FORMAT_LABELS


def color_text(text: str, color: str) -> str:
	"""Return colored text for CLI readability."""
	return f"{color}{text}{COLOR_RESET}"

#==============

def remove_case_mismatched_files(expected_path: str) -> None:
	dir_name = os.path.dirname(expected_path)
	base_name = os.path.basename(expected_path)
	if not os.path.isdir(dir_name):
		return
	lower_name = base_name.lower()
	for entry in os.listdir(dir_name):
		if entry == base_name:
			continue
		if entry.lower() != lower_name:
			continue
		entry_path = os.path.join(dir_name, entry)
		if not os.path.isfile(entry_path):
			continue
		os.remove(entry_path)
		print(color_text(f"  REMOVED CASE MISMATCH: {entry_path}", COLOR_YELLOW))

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
	"""Options consumed by render_all(). Populated by the pipeline."""
	download_formats: tuple = DOWNLOAD_FORMAT_KEYS
	no_downloads: bool = False
	force_downloads: bool = False
	verbose: bool = True
	# Pre-built LLMClient for problem-set title generation. The pipeline
	# constructs one client at startup based on --ollama / --model flags.
	llm_client: object = None

#==============

def get_docs_dir() -> str:
	if not os.path.isfile(MKDOCS_CONFIG):
		raise FileNotFoundError(f"Config file '{MKDOCS_CONFIG}' not found.")
	with open(MKDOCS_CONFIG, "r") as file_pointer:
		config = yaml.safe_load(file_pointer) or {}
	docs_dir = config["docs_dir"]
	return docs_dir

#==============

def _derive_libretexts_title(url: str) -> str:
	"""Recover a human-readable chapter title from a LibreTexts URL slug."""
	# Take the last path segment and URL-decode it (e.g. '1.01%3A_Molecules_of_Life').
	last_segment = url.rstrip("/").rsplit("/", 1)[-1]
	decoded = urllib.parse.unquote(last_segment)
	# Drop any leading 'N.NN: ' or 'NN: ' numeric prefix if present.
	if ":" in decoded:
		decoded = decoded.split(":", 1)[1]
	# Convert underscores to spaces and tidy whitespace.
	return decoded.replace("_", " ").strip()


@functools.lru_cache(maxsize=None)
def _topic_entry(subject_folder: str, relative_topic_name: str) -> dict:
	"""Return the metadata entry for one topic.

	Reads topics_metadata.yml via bioproblems_site.metadata and returns
	the dict shape consumed by get_topic_title/get_libretexts_link/
	get_topic_description. Cached per (subject, topic) tuple.
	"""
	subjects, _order = bp_metadata.load_topics_metadata()
	subject = subjects.get(subject_folder)
	if subject is None:
		raise FileNotFoundError(
			f"Subject {subject_folder!r} missing from topics_metadata.yml"
		)
	matching = [t for t in subject.topics if t.key == relative_topic_name]
	if not matching:
		raise ValueError(
			f"No entry for {subject_folder}/{relative_topic_name} in "
			f"topics_metadata.yml"
		)
	topic = matching[0]
	libretexts_payload = None
	if topic.libretexts is not None:
		libretexts_payload = {
			"url": topic.libretexts.url,
			"title": _derive_libretexts_title(topic.libretexts.url),
			"unit": topic.libretexts.unit,
			"chapter": topic.libretexts.chapter,
		}
	return {
		"title": topic.title,
		"description": topic.description,
		"libretexts": libretexts_payload,
	}


def _get_topic_entry(topic_folder: str) -> dict:
	"""Path-based entry lookup retained for existing call sites."""
	subject_folder = os.path.basename(os.path.dirname(topic_folder))
	relative_topic_name = os.path.basename(os.path.normpath(topic_folder))
	return _topic_entry(subject_folder, relative_topic_name)

#==============

def get_topic_title(folder_path: str) -> str:
	"""Return the topic title parsed from site_docs/<subject>/index.md."""
	entry = _get_topic_entry(folder_path)
	title = entry.get("title")
	if not title:
		raise ValueError(f"No topic title found for folder path: {folder_path}")
	# Prefix the numeric label so existing page output stays identical.
	relative_topic_name = os.path.basename(os.path.normpath(folder_path))
	topic_int = int(re.search(r'topic(\d+)', relative_topic_name).group(1))
	return f"{topic_int}: {title}"

#==============

def get_libretexts_link(topic_folder: str):
	"""Return the LibreTexts mapping for a topic, or None if not linked."""
	entry = _get_topic_entry(topic_folder)
	return entry.get("libretexts")

#==============

def get_topic_description(topic_folder: str) -> str:
	"""Return the description parsed from site_docs/<subject>/index.md."""
	entry = _get_topic_entry(topic_folder)
	description = entry.get("description")
	if not description:
		relative_topic_name = os.path.basename(os.path.normpath(topic_folder))
		raise ValueError(f"No description found for topic: {relative_topic_name}")
	return description

#==============
def create_downloadable_format(bbq_file: str, prefix: str, extension: str):
	if prefix == "bbq":
		raise ValueError
	file_path = get_outfile_name(bbq_file, prefix, extension)
	if os.path.exists(file_path):
		os.remove(file_path)
	converter_path = git_paths.find_bbq_converter()
	if not converter_path:
		print(color_text("cannot find bbq_converter.py", COLOR_YELLOW))
		print("Expected in repo root or qti_package_maker/tools.")
		print("Example: ln -sv ~/nsh/PROBLEM/qti_package_maker/tools/bbq_converter.py .")
		raise FileNotFoundError
	convert_cmd = [
		"python3",
		converter_path,
		"--quiet",
		f"--{prefix}",
		"--input",
		bbq_file,
		"--output",
		file_path,
	]
	cmd_display = " ".join(convert_cmd)
	print(color_text(cmd_display, COLOR_CYAN))
	subprocess.run(convert_cmd, check=False)
	if not os.path.isfile(file_path):
		print("\n" + cmd_display + "\n")
		print(color_text(f"WARNING: {prefix}, {extension}, {bbq_file}", COLOR_YELLOW))
	return file_path

#==============
def get_download_js_string():
	download_js = (
		'<script>\n'
		'	function downloadFile(filePath) {\n'
		'		const link = document.createElement(\'a\');\n'
		'		link.href = filePath;\n'
		'		link.download = filePath.split(\'/\').pop()\n'
		'		document.body.appendChild(link);\n'
		'		link.click();\n'
		'		document.body.removeChild(link);\n'
		'	}\n'
		'</script>\n\n'
	)
	return download_js

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
	force_downloads: bool,
	verbose: bool,
	stats: dict,
) -> str:
	"""
	Generates a row of HTML buttons for downloading various file types.
	"""
	if not download_formats:
		if verbose:
			print(color_text("  Downloads disabled for this page.", COLOR_YELLOW))
		for format_key in DOWNLOAD_FORMAT_KEYS:
			record_stat(stats, format_key, "skipped")
		return ""

	# Define file types with their prefixes, suffixes, and button classes
	file_types = {
		"bb_text": {
			"prefix": "bbq",
			"extension": "txt",
			"button_class": "bb_text",
			"display_name": "Blackboard Learn TXT"
		},
		"bb_qti": {
			"prefix": "blackboard_qti_v2_1",
			"extension": "zip",
			"button_class": "bb_qti",
			"display_name": "Blackboard Ultra QTI v2.1"
		},
		"canvas_qti": {
			"prefix": "canvas_qti_v1_2",
			"extension": "zip",
			"button_class": "canvas_qti",
			"display_name": "Canvas/ADAPT QTI v1.2"
		},
		"human_read": {
			"prefix": "human_readable",
			"extension": "html",
			"button_class": "human_read",
			"display_name": "Human-Readable TXT"
		},
		"webwork_pgml": {
			"prefix": "webwork_pgml",
			"extension": "pgml",
			"button_class": "webwork_pgml",
			"display_name": "WeBWorK PGML"
		}
	}

	bbq_core_name = extract_core_name(bbq_file_name)
	#bbq_base_name = os.path.basename(bbq_file_name)
	dir_name = os.path.dirname(bbq_file_name)

	# Initialize the HTML output string
	html_output = f'<div id="{bbq_core_name}-button-container" class="button-container">\n'

	# Generate a button for each file type
	for type_key, file_type in file_types.items():
		if type_key not in download_formats:
			if verbose:
				print(color_text(f"  SKIP {file_type['display_name']} (disabled)", COLOR_YELLOW))
			record_stat(stats, type_key, "skipped")
			continue
		# Special handling for WeBWorK PGML: search for existing file only
		if type_key == "webwork_pgml":
			pgml_path = find_pgml_file(bbq_file_name)
			if not pgml_path:
				if verbose:
					print(color_text(f"  MISSING {file_type['display_name']}", COLOR_YELLOW))
				record_stat(stats, type_key, "missing")
				continue
			if verbose:
				print(color_text(f"  FOUND {file_type['display_name']}: {pgml_path}", COLOR_GREEN))
			record_stat(stats, type_key, "existing")
			pgml_basename = os.path.basename(pgml_path)
			pgml_relative_path = os.path.relpath(pgml_path, start=dir_name)
			button_html = (
				f'<a class="md-button custom-button {file_type["button_class"]}" '
				f'href="{pgml_relative_path}" '
				f'download '
				f'title="Download {pgml_basename}" '
				f'aria-label="Click to download the {file_type["display_name"]} file ({pgml_basename})">\n'
				f'    <i class="fa fa-code"></i>{file_type["display_name"]}\n'
				f'</a>'
			)
			html_output += button_html + '\n'
			continue
		# Construct the filename using the base name and file type details
		if type_key == "bb_text":
			out_file_path = bbq_file_name
		else:
			out_file_path = get_outfile_name(
				bbq_file_name,
				file_type['prefix'],
				file_type['extension'],
			)
		exists_before = os.path.isfile(out_file_path)
		# Check if the source file is newer than the existing download file
		source_is_newer = False
		if exists_before:
			source_mtime = os.path.getmtime(bbq_file_name)
			download_mtime = os.path.getmtime(out_file_path)
			source_is_newer = source_mtime > download_mtime
		if exists_before and not force_downloads and not source_is_newer:
			if verbose:
				print(color_text(f"  FOUND {file_type['display_name']}: {out_file_path}", COLOR_GREEN))
			record_stat(stats, type_key, "existing")
		elif source_is_newer:
			if verbose:
				print(color_text(f"  STALE {file_type['display_name']}: source newer, rebuilding", COLOR_CYAN))
			out_file_path = create_downloadable_format(
				bbq_file_name,
				file_type['prefix'],
				file_type['extension'],
			)
			if not os.path.isfile(out_file_path):
				if verbose:
					print(color_text(f"  MISSING {file_type['display_name']}: {out_file_path}", COLOR_YELLOW))
				record_stat(stats, type_key, "failed")
				continue
			record_stat(stats, type_key, "generated")
		elif type_key == "bb_text":
			if verbose:
				print(color_text(f"  MISSING {file_type['display_name']}: {out_file_path}", COLOR_YELLOW))
			record_stat(stats, type_key, "missing")
		else:
			if verbose:
				print(color_text(f"  BUILD {file_type['display_name']}: {out_file_path}", COLOR_CYAN))
			out_file_path = create_downloadable_format(
				bbq_file_name,
				file_type['prefix'],
				file_type['extension'],
			)
		if not os.path.isfile(out_file_path):
			if verbose:
				print(color_text(f"  MISSING {file_type['display_name']}: {out_file_path}", COLOR_YELLOW))
			if type_key != "bb_text":
				record_stat(stats, type_key, "failed")
			continue
		if type_key != "bb_text" and not (exists_before and not force_downloads):
			record_stat(stats, type_key, "generated")
		out_file_basename = os.path.basename(out_file_path)
		out_relative_path = os.path.relpath(out_file_path, start=dir_name)
		out_file_basename = os.path.basename(out_file_path)
		# Create HTML button element with corresponding attributes
		if type_key == "human_read":
			button_html = (
				f'<button class="md-button custom-button {file_type["button_class"]}" '
				f'onclick="window.open(\'{out_relative_path}\', \'_blank\')" '
				f'title="View {out_file_basename}" '
				f'aria-label="Click to view the {file_type["display_name"]} file ({out_file_basename})">\n'
				f'    <i class="fa fa-eye"></i> {file_type["display_name"]}\n'
				f'</button>'
			)
		else:
			button_html = (
				f'<a class="md-button custom-button {file_type["button_class"]}" '
				f'href="{out_relative_path}" '
				f'download '
				f'title="Download {out_file_basename}" '
				f'aria-label="Click to download the {file_type["display_name"]} file ({out_file_basename})">\n'
				f'    <i class="fa fa-download"></i>{file_type["display_name"]}\n'
				f'</a>'
			)
		# Add the button to the HTML output
		html_output += button_html + '\n'

	# Close the container div
	html_output += '</div>'

	return html_output

#============================================

def is_valid_title(title: str) -> bool:
	"""
	Check whether a problem set title is valid.

	Args:
		title: The title string to validate.

	Returns:
		bool: True if the title passes all checks, False otherwise.
	"""
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

def get_problem_set_title(client, bbq_file: str) -> str:
	"""
	Extracts or generates the title for a problem set based on the provided file path.

	Args:
		bbq_file (str): The full path to the problem set file.

	Returns:
		str: The title of the problem set.
	"""
	# Normalize and obtain the directory path of the file
	bbq_file_path = os.path.normpath(bbq_file)
	dir_path = os.path.dirname(bbq_file_path)

	# Define the path for the YAML file containing problem set titles
	problem_set_title_yaml = os.path.join(dir_path, 'problem_set_titles.yml')

	# Check if the YAML file exists
	if os.path.isfile(problem_set_title_yaml):
		# Load the YAML data if the file exists
		with open(problem_set_title_yaml, 'r') as problem_set_title_file_pointer:
			problem_set_title_data = yaml.safe_load(problem_set_title_file_pointer)
	else:
		# Initialize an empty dictionary if the file doesn't exist
		problem_set_title_data = {}

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
		if is_valid_title(candidate):
			problem_set_title = candidate
			break
		print(f"WARNING: attempt {attempt + 1}/{max_retries} produced invalid title: {candidate!r}")
	if problem_set_title is None:
		raise ValueError(f"Failed to generate valid title after {max_retries} attempts for {bbq_file_basename}: {candidate!r}")

	# Update the YAML data with the newly generated title and a timestamp of the edit
	problem_set_title_data[bbq_file_basename] = problem_set_title
	problem_set_title_data['last edit'] = time.asctime()

	# Write the updated data back to the YAML file
	with open(problem_set_title_yaml, "w") as problem_set_title_file_pointer:
		yaml.dump(problem_set_title_data, problem_set_title_file_pointer)

	# Return the newly generated problem set title
	return problem_set_title

#==============

def extract_core_name(bbq_file_name):
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
def get_outfile_name(bbq_file_name: str, prefix: str, extension: str):
	dirname = os.path.join(os.path.dirname(bbq_file_name), "downloads")
	outfile = extract_core_name(bbq_file_name)
	if not outfile.startswith(prefix):
		outfile = f'{prefix}-{outfile}'
	# Ensure the extension is '.txt'
	if not outfile.endswith("." + extension):
		outfile += "." + extension
	outfile = os.path.join(dirname, outfile)
	remove_case_mismatched_files(outfile)
	return outfile

#==============

def update_index_md(
	topic_folder: str,
	bbq_files: list,
	file_counter: dict,
	total_files: int,
	download_formats: list,
	force_downloads: bool,
	verbose: bool,
	stats: dict,
	base_dir: str,
	client=None,
) -> None:
	"""Update or create the index.md file for the topic.

	Args:
		topic_folder (str): The path to the topic folder.
		subtitle (str): The subtitle for the topic.
		bbq_files (list[str]): List of BBQ file paths to process.
		file_counter (dict): Mutable counter tracking processed BBQ files.
		total_files (int): Total number of BBQ files being processed.
	"""
	# Get subtitle from the parent folder's index.md
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
	print(f'writing to {index_md_path}')
	with open(index_md_path, "w") as index_md:
		downloads_folder = os.path.join(topic_folder, "downloads")
		if not os.path.isdir(downloads_folder):
			os.makedirs(downloads_folder)

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
				f'<img src="/assets/images/libretexts.png" alt="" class="lt-icon"></a>'
			)
			reference_line = (
				f"**LibreTexts reference:** [{link_title}]({libretexts_url}) "
				f"{icon_anchor}"
			)
			index_md.write(f"{reference_line}\n\n")

		bbq_files.sort()
		for bbq_file in bbq_files:
			bbq_file = git_paths.canonicalize_git_path(bbq_file)
			file_counter["count"] += 1
			file_progress = ""
			if total_files:
				file_progress = f"[{file_counter['count']}/{total_files}] "
			print('-' * 50)
			# Extract the base file name from the input path
			#bbq_file_basename = os.path.basename(bbq_file)
			# Convert the text file to HTML
			print(color_text(f'  {file_progress}BBQ file {bbq_file}', COLOR_CYAN))

			html_file_path = get_outfile_name(bbq_file, 'selftest', 'html')
			if os.path.exists(html_file_path):
				os.remove(html_file_path)
			html_file_path = create_downloadable_format(bbq_file, 'selftest', 'html')
			if not os.path.isfile(html_file_path):
				print("\n\n\n!! unfortunately, the script requires a selftest for each problem !!")
				record_stat(stats, "selftest", "failed")
				raise FileNotFoundError(html_file_path)
			record_stat(stats, "selftest", "generated")

			# Generate the problem set title using the LLM
			problem_set_title = get_problem_set_title(client, bbq_file)
			print(color_text(f"  Problem set title: {problem_set_title}", COLOR_CYAN))

			# Add content to the index.md file
			index_md.write(f"## {problem_set_title}\n\n")
			#print("bbq_file_basename=", bbq_file_basename)
			download_button_row = generate_download_button_row(
				bbq_file,
				download_formats,
				force_downloads,
				verbose,
				stats,
			)
			index_md.write(download_button_row)
			index_md.write("<details>\n")
			index_md.write("  <summary>Click\n")
			index_md.write("    <span style='font-weight: normal;'>\n")
			index_md.write("       to show\n")
			index_md.write("    </span>\n")
			index_md.write("    <span style='font-size: 1.1em; color: var(--md-primary-fg-color--dark)'>\n")
			index_md.write(f"      {problem_set_title}\n")
			index_md.write("    </span>\n")
			index_md.write("    <span style='font-weight: normal;'>\n")
			index_md.write("      example problem\n")
			index_md.write("    </span>\n")
			index_md.write("  </summary>\n")
			index_md.write(f"  {{% include \"{os.path.relpath(html_file_path, base_dir)}\" %}}\n\n")
			index_md.write("</details>\n\n\n")

#==============

def render_all(options: "RenderOptions | None" = None) -> None:
	"""Traverse topic folders and (re)generate their index.md files.

	Called by bioproblems_site.pipeline.run. Metadata is sourced from
	topics_metadata.yml exclusively (the legacy markdown parser was
	removed in M3).
	"""
	if options is None:
		options = RenderOptions()
	stats = init_format_stats()
	base_dir = get_docs_dir()
	if not os.path.exists(base_dir):
		raise FileNotFoundError(f"Base directory '{base_dir}' not found.")
	if options.verbose:
		joined_formats = ", ".join(options.download_formats) or "none"
		print(color_text(f"Download formats: {joined_formats}", COLOR_CYAN))
		print(color_text(f"Force downloads: {options.force_downloads}", COLOR_CYAN))

	all_topic_folders = glob.glob(os.path.join(base_dir, "*/topic??/"))
	all_topic_folders.sort()
	if options.verbose:
		print(color_text(
			f"Found {len(all_topic_folders)} topic folders to parse", COLOR_CYAN
		))

	topic_jobs = []
	for topic_folder in all_topic_folders:
		norm_topic = os.path.normpath(topic_folder)
		if norm_topic == base_dir or "topic" not in norm_topic:
			continue
		bbq_files = glob.glob(os.path.join(norm_topic, "bbq-*-questions.txt"))
		if not bbq_files:
			continue
		topic_jobs.append((norm_topic, bbq_files))

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
				f"{progress} Current folder: {topic_folder}{file_progress}",
				COLOR_MAGENTA,
			))
		update_index_md(
			topic_folder,
			bbq_files,
			file_counter,
			total_bbq_files,
			list(options.download_formats),
			options.force_downloads,
			options.verbose,
			stats,
			base_dir,
			client=options.llm_client,
		)
	if options.verbose:
		print("\n\nSummary:")
		format_order = (
			"selftest", "bb_text", "bb_qti", "canvas_qti",
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
			if format_key == "selftest":
				print(f"- {label}: generated {generated}, failed {failed}")
				continue
			print(
				f"- {label}: generated {generated}, failed {failed}, "
				f"existing {existing}, missing {missing}, skipped {skipped}"
			)
		print(color_text("PROGRAM HAS COMPLETED!!!", COLOR_GREEN))

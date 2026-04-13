#!/usr/bin/env python3

# Standard Library
import os
import re
import glob
import time
import argparse
import subprocess
import urllib.parse

# PIP3 modules
import yaml

# Local
import llm_generate_problem_set_title

#==============

BASE_DIR: str = ""
MKDOCS_CONFIG: str = "mkdocs.yml"
SUBJECT_TOPIC_CACHE: dict = {}
GIT_TRACKED_PATHS = None

# ANSI color codes for readable CLI output
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
COLOR_MAGENTA = "\033[95m"

DOWNLOAD_FORMAT_KEYS = (
	"bb_text",
	"bb_qti",
	"canvas_qti",
	"human_read",
	"webwork_pgml",
)

FORMAT_LABELS = {
	"selftest": "Selftest HTML",
	"bb_text": "Blackboard Learn TXT",
	"bb_qti": "Blackboard Ultra QTI v2.1",
	"canvas_qti": "Canvas/ADAPT QTI v1.2",
	"human_read": "Human-Readable TXT",
	"webwork_pgml": "WeBWorK PGML",
}


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

def get_git_tracked_paths() -> dict:
	global GIT_TRACKED_PATHS
	if GIT_TRACKED_PATHS is not None:
		return GIT_TRACKED_PATHS
	GIT_TRACKED_PATHS = {}
	result = subprocess.run(
		["git", "ls-files"],
		capture_output=True,
		text=True,
		check=False,
	)
	if result.returncode != 0:
		return GIT_TRACKED_PATHS
	for line in result.stdout.splitlines():
		if not line:
			continue
		lower_path = line.lower()
		if lower_path in GIT_TRACKED_PATHS and GIT_TRACKED_PATHS[lower_path] != line:
			print(color_text(f"  MULTIPLE GIT CASE MATCHES: {line}", COLOR_YELLOW))
			continue
		GIT_TRACKED_PATHS[lower_path] = line
	return GIT_TRACKED_PATHS

#==============

def canonicalize_git_path(file_path: str) -> str:
	repo_root = get_repo_root()
	relative_path = os.path.relpath(file_path, repo_root)
	tracked = get_git_tracked_paths().get(relative_path.lower())
	if not tracked:
		return file_path
	canonical_path = os.path.join(repo_root, tracked)
	if canonical_path != file_path and canonical_path.lower() == file_path.lower():
		print(color_text(f"  CASE MISMATCH: {file_path} -> {canonical_path}", COLOR_YELLOW))
	return canonical_path

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

def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Generate topic pages and optional download formats."
	)
	parser.add_argument(
		"-f",
		"--formats",
		dest="download_formats",
		action="append",
		choices=DOWNLOAD_FORMAT_KEYS,
		help="Download formats to include (default: all).",
	)
	parser.add_argument(
		"--no-downloads",
		dest="no_downloads",
		action="store_true",
		help="Skip download button generation.",
	)
	parser.add_argument(
		"--force-downloads",
		dest="force_downloads",
		action="store_true",
		help="Regenerate download formats even if files exist.",
	)
	verbosity_group = parser.add_mutually_exclusive_group()
	verbosity_group.add_argument(
		"-q",
		"--quiet",
		dest="verbose",
		action="store_false",
		help="Reduce console output.",
	)
	verbosity_group.add_argument(
		"-v",
		"--verbose",
		dest="verbose",
		action="store_true",
		help="Enable detailed console output.",
	)
	verbosity_group.set_defaults(verbose=True)
	args = parser.parse_args()

	if args.no_downloads:
		args.download_formats = []
	elif not args.download_formats:
		args.download_formats = list(DOWNLOAD_FORMAT_KEYS)
	else:
		seen = set()
		ordered = []
		for item in args.download_formats:
			if item in seen:
				continue
			ordered.append(item)
			seen.add(item)
		args.download_formats = ordered
	return args

#==============

def get_docs_dir() -> str:
	if not os.path.isfile(MKDOCS_CONFIG):
		raise FileNotFoundError(f"Config file '{MKDOCS_CONFIG}' not found.")
	with open(MKDOCS_CONFIG, "r") as file_pointer:
		config = yaml.safe_load(file_pointer) or {}
	docs_dir = config.get("docs_dir")
	if not docs_dir:
		docs_dir = "docs"
	return docs_dir

#==============

def get_repo_root() -> str:
	result = subprocess.run(
		["git", "rev-parse", "--show-toplevel"],
		capture_output=True,
		text=True,
		check=False,
	)
	if result.returncode == 0:
		repo_root = result.stdout.strip()
		if repo_root:
			return repo_root
	return os.path.dirname(os.path.abspath(__file__))

#==============

def find_bbq_converter() -> str:
	repo_root = get_repo_root()
	candidates = [
		os.path.join(repo_root, "bbq_converter.py"),
		os.path.join(repo_root, "..", "qti_package_maker", "tools", "bbq_converter.py"),
		os.path.join(os.path.expanduser("~"), "nsh", "PROBLEM", "qti_package_maker", "tools", "bbq_converter.py"),
		os.path.join(os.path.expanduser("~"), "nsh", "qti_package_maker", "tools", "bbq_converter.py"),
	]
	for candidate in candidates:
		if os.path.isfile(candidate):
			return os.path.abspath(candidate)
	return ""

#==============

# Matches a numbered topic list line in site_docs/<subject>/index.md, e.g.:
#   1. [Life Molecules](topic01/index.md) &mdash; <a href="..." ...>(LibreTexts Unit 1, Chapter 1 ...)</a>
# The trailing HTML block is optional.
_TOPIC_HEADING_RE = re.compile(
	r'^\s*(\d+)\.\s+\[([^\]]+)\]\((topic\d+)/index\.md\)(.*)$'
)

# Matches the optional LibreTexts anchor, capturing URL, unit (optional), and chapter.
_LIBRETEXTS_RE = re.compile(
	r'href="([^"]+)"[^>]*>.*?\(LibreTexts(?:\s+Unit\s+(\d+),)?\s+Chapter\s+(\d+)'
)

# Matches the indented description bullet that follows a topic heading line.
_DESCRIPTION_RE = re.compile(r'^\s*-\s+(.*\S)\s*$')

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

def load_subject_topics(subject_folder: str) -> dict:
	"""Parse site_docs/<subject>/index.md and return a topic metadata dict.

	Returns a mapping like:
		{
			'topic01': {
				'title': 'Life Molecules',
				'description': 'Students categorize biomolecules ...',
				'libretexts': {'url': ..., 'title': ..., 'unit': 1, 'chapter': 1} or None,
			},
			...
		}
	Results are cached per subject.
	"""
	# Return cached result if we have already parsed this subject.
	if subject_folder in SUBJECT_TOPIC_CACHE:
		return SUBJECT_TOPIC_CACHE[subject_folder]
	index_path = os.path.join(BASE_DIR or "site_docs", subject_folder, "index.md")
	if not os.path.isfile(index_path):
		raise FileNotFoundError(f"Subject index not found: {index_path}")
	with open(index_path, "r") as file_pointer:
		lines = file_pointer.readlines()
	topics: dict = {}
	current_key = None
	# Walk the file line by line, assigning each description bullet to the most recent heading.
	for raw_line in lines:
		heading_match = _TOPIC_HEADING_RE.match(raw_line)
		if heading_match:
			_topic_number, title, topic_key, trailing = heading_match.groups()
			libretexts = None
			libre_match = _LIBRETEXTS_RE.search(trailing)
			if libre_match:
				url, unit_str, chapter_str = libre_match.groups()
				libretexts = {
					"url": url,
					"title": _derive_libretexts_title(url),
					"unit": int(unit_str) if unit_str else 0,
					"chapter": int(chapter_str) if chapter_str else 0,
				}
			topics[topic_key] = {
				"title": title.strip(),
				"description": "",
				"libretexts": libretexts,
			}
			current_key = topic_key
			continue
		# Only treat the first indented bullet after a heading as that topic's description.
		if current_key is not None and not topics[current_key]["description"]:
			desc_match = _DESCRIPTION_RE.match(raw_line)
			if desc_match:
				topics[current_key]["description"] = desc_match.group(1)
	SUBJECT_TOPIC_CACHE[subject_folder] = topics
	return topics

def _get_topic_entry(topic_folder: str) -> dict:
	"""Look up the parsed entry for a topic folder, raising if absent."""
	subject_folder = os.path.basename(os.path.dirname(topic_folder))
	relative_topic_name = os.path.basename(os.path.normpath(topic_folder))
	topics = load_subject_topics(subject_folder)
	entry = topics.get(relative_topic_name)
	if entry is None:
		raise ValueError(
			f"No entry for {subject_folder}/{relative_topic_name} in "
			f"site_docs/{subject_folder}/index.md"
		)
	return entry

#==============

def get_topic_title(folder_path: str, topic_number: int) -> str:
	"""Return the topic title parsed from site_docs/<subject>/index.md."""
	# topic_number is accepted for backwards-compatible call sites but unused.
	del topic_number
	entry = _get_topic_entry(folder_path)
	title = entry.get("title")
	if not title:
		raise ValueError(f"No topic title found for folder path: {folder_path}")
	# Prefix the numeric label so existing page output stays identical.
	relative_topic_name = os.path.basename(os.path.normpath(folder_path))
	topic_int = int(re.search(r'topic(\d+)', relative_topic_name).group(1))
	return f"{topic_int}: {title}"

#==============

def get_libretexts_link(topic_folder: str, relative_topic_name: str):
	"""Return the LibreTexts mapping for a topic, or None if not linked."""
	del relative_topic_name
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
	converter_path = find_bbq_converter()
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
		if not prefix.startswith("human"):
			#raise FileNotFoundError(file_path)
			#return None
			pass
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

def get_problem_set_title(bbq_file: str) -> str:
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
		candidate = llm_generate_problem_set_title.get_problem_title_from_file(bbq_file)
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
	#relative_path = os.path.relpath(normalized_path, BASE_DIR)

	topic_number = int(re.search('topic([0-9]+)', relative_topic_name).groups()[0])
	print(f"Topic Number: {topic_number}")

	title = get_topic_title(topic_folder, topic_number)
	print(color_text(f"Page Title: {title}", COLOR_CYAN))

	description = get_topic_description(topic_folder)
	print(f"Page description: {description}")
	libretexts_link = get_libretexts_link(topic_folder, relative_topic_name)
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
			elif link_chapter:
				link_title = f"Chapter {link_chapter}: {link_title}"
			index_md.write(f"**LibreTexts reference:** [{link_title}]({libretexts_link['url']})\n\n")

		bbq_files.sort()
		for bbq_file in bbq_files:
			bbq_file = canonicalize_git_path(bbq_file)
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
			problem_set_title = get_problem_set_title(bbq_file)
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
			"""
			download_msg = f"Download the {bbq_file_basename} file for Blackboard Upload"
			markdown_link = f"[{download_msg}]({bbq_file_basename})\n\n"
			a_href = f"<a id='raw-url' href='{bbq_file_basename}' download>{download_msg}</a>\n\n"
			index_md.write(a_href)
			"""
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
			index_md.write(f"  {{% include \"{os.path.relpath(html_file_path, BASE_DIR)}\" %}}\n\n")
			index_md.write("</details>\n\n\n")
		#index_md.write(get_download_js_string())

#==============

def main():
	"""Traverse the topic folders and generate pages.

	Raises:
		FileNotFoundError: If the base directory does not exist.
	"""
	global BASE_DIR
	args = parse_args()
	stats = init_format_stats()
	BASE_DIR = get_docs_dir()
	if not os.path.exists(BASE_DIR):
		raise FileNotFoundError(f"Base directory '{BASE_DIR}' not found.")
	if args.verbose:
		if not args.download_formats:
			print(color_text("Download formats: none", COLOR_YELLOW))
		else:
			joined_formats = ", ".join(args.download_formats)
			print(color_text(f"Download formats: {joined_formats}", COLOR_CYAN))
		print(color_text(f"Force downloads: {args.force_downloads}", COLOR_CYAN))

	search_text = os.path.join(BASE_DIR, "*/topic??")
	print(color_text(f"Search text: {search_text}", COLOR_CYAN))
	all_topic_folders = glob.glob(os.path.join(BASE_DIR, "*/topic??/"))
	all_topic_folders.sort()
	print(color_text(f"Found {len(all_topic_folders)} topic folders to parse", COLOR_CYAN))

	# Pre-filter only topics that actually have bbq files so progress counts are accurate
	topic_jobs = []
	for topic_folder in all_topic_folders:
		norm_topic = os.path.normpath(topic_folder)
		if norm_topic == BASE_DIR or "topic" not in norm_topic:
			continue
		bbq_files = glob.glob(os.path.join(norm_topic, "bbq-*-questions.txt"))
		if not bbq_files:
			continue
		topic_jobs.append((norm_topic, bbq_files))

	total_jobs = len(topic_jobs)
	total_bbq_files = sum(len(files) for _, files in topic_jobs)
	print(color_text(f"Processing {total_jobs} topic folders with {total_bbq_files} BBQ files", COLOR_CYAN))

	file_counter = {"count": 0}
	for idx, (topic_folder, bbq_files) in enumerate(topic_jobs, start=1):
		print("\n\n\n################################")
		progress = f"[{idx}/{total_jobs}]"
		file_progress = ""
		if total_bbq_files:
			file_progress = f" ({file_counter['count'] + len(bbq_files)}/{total_bbq_files} files)"
		print(color_text(f"{progress} Current folder: {topic_folder}{file_progress}", COLOR_MAGENTA))
		print(color_text(f"{progress} Found {len(bbq_files)} bbq files in topic folder: {topic_folder}", COLOR_CYAN))

		# Update the index.md file for the topic
		update_index_md(
			topic_folder,
			bbq_files,
			file_counter,
			total_bbq_files,
			args.download_formats,
			args.force_downloads,
			args.verbose,
			stats,
		)
		#sys.exit(1)
	print("\n\n\n")
	print("Summary:")
	format_order = ("selftest", "bb_text", "bb_qti", "canvas_qti", "human_read", "webwork_pgml")
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

#==============

if __name__ == "__main__":
	main()

"""Topic-page renderer for bioproblems_site.

Extracted from the former root-level generate_topic_pages.py. Exposes
render_all() for direct topic-page rendering; the unified build uses its
topic-scoped stage through build_site.py.
No argparse here; the public parser lives in build_site.py.
"""

# Standard Library
import os
import re
import glob
import time
import subprocess
import dataclasses

# PIP3 modules
import yaml
from qti_package_maker import package_interface

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

#==============

# ANSI color codes for readable CLI output.
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_COMMAND = "\033[36m"
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
		print(color_text(
			f"  REMOVED CASE MISMATCH: {git_paths.display_path(entry_path)}",
			COLOR_YELLOW,
		))

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
	# When False, do not create missing artifact files. Buttons still
	# render for files that already exist on disk; buttons for missing
	# formats are omitted.
	generate_downloads: bool = False
	force_downloads: bool = False
	# Rotate (regenerate) the per-BBQ self-test HTML on every build; each
	# build draws a fresh random question from the bbq-*.txt source.
	# Intentional -- do not re-gate for speed.
	regenerate_selftests: bool = True
	# A page can render expected missing links while the download stage owns
	# every artifact write.
	render_missing_download_links: bool = False
	verbose: bool = True
	# Optional pre-built client for problem-set title generation.
	llm_client: object = None

#==============

#==============
def _create_human_readable_download(
		bbq_file: str,
		output_path: str,
) -> str | None:
	qti_packer = package_interface.QTIPackageInterface(
		package_name=extract_core_name(bbq_file),
		verbose=False,
	)
	qti_packer.read_package(bbq_file, "bbq_text")
	saved_path = qti_packer.save_package(
		"human_readable", outfile=output_path)
	if saved_path is None:
		if len(qti_packer.item_bank) == 0:
			raise RuntimeError(
				f"human_readable could not read any questions from "
				f"{git_paths.display_path(bbq_file)}"
			)
		if os.path.lexists(output_path):
			if not os.path.isfile(output_path):
				raise RuntimeError(
					f"cannot remove non-file human_readable output at "
					f"{git_paths.display_path(output_path)}"
				)
			os.remove(output_path)
		print(color_text(
			f"  SKIP Human-Readable: no supported text questions in "
			f"{git_paths.display_path(bbq_file)}",
			COLOR_YELLOW,
		))
		return None
	if not os.path.isfile(saved_path) or os.path.getsize(saved_path) == 0:
		raise RuntimeError(
			f"human_readable engine reported output but wrote no file for "
			f"{git_paths.display_path(bbq_file)}"
		)
	remove_case_mismatched_files(output_path)
	return output_path

#==============
def create_downloadable_format(bbq_file: str, prefix: str, extension: str) -> str | None:
	if prefix == "bbq":
		raise ValueError
	file_path = get_outfile_name(bbq_file, prefix, extension)
	converter_path = git_paths.find_bbq_converter()
	if not converter_path:
		print(color_text("cannot find bbq_converter.py", COLOR_YELLOW))
		print("Expected in repo root or qti_package_maker/tools.")
		print("Example: ln -sv ~/nsh/PROBLEM/qti_package_maker/tools/bbq_converter.py .")
		raise FileNotFoundError
	output_directory = os.path.dirname(file_path) or "."
	os.makedirs(output_directory, exist_ok=True)
	if prefix == "human_readable":
		return _create_human_readable_download(bbq_file, file_path)
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
	display_cmd = list(convert_cmd)
	display_cmd[1] = git_paths.display_path(converter_path)
	for path_flag in ("--input", "--output"):
		flag_index = display_cmd.index(path_flag)
		display_cmd[flag_index + 1] = git_paths.display_path(
			display_cmd[flag_index + 1]
		)
	cmd_display = " ".join(display_cmd)
	print(color_text(cmd_display, COLOR_COMMAND))
	completed_process = subprocess.run(convert_cmd, check=False)
	if completed_process.returncode != 0:
		raise RuntimeError(
			f"{prefix} converter exited with status {completed_process.returncode} "
			f"for {git_paths.display_path(bbq_file)}."
		)
	if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
		print("\n" + color_text(cmd_display, COLOR_COMMAND) + "\n")
		print(color_text(
			f"WARNING: {prefix}, {extension}, {git_paths.display_path(bbq_file)}",
			COLOR_YELLOW,
		))
		raise RuntimeError(
			f"{prefix} converter produced no output for "
			f"{git_paths.display_path(bbq_file)}."
		)
	remove_case_mismatched_files(file_path)
	return file_path


#==============
def _create_optional_download(
		bbq_file: str,
		prefix: str,
		extension: str,
		display_name: str,
) -> str | None:
	"""Skip a failed optional download without stopping the task build."""
	try:
		return create_downloadable_format(bbq_file, prefix, extension)
	except Exception as error:
		output_path = get_outfile_name(bbq_file, prefix, extension)
		if os.path.isfile(output_path):
			os.remove(output_path)
		print(color_text(
			f"  SKIP {display_name}: {type(error).__name__}: {error}",
			COLOR_YELLOW,
		))
		return None


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
def get_download_js_string() -> str:
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
	*,
	generate_downloads: bool = False,
	render_missing_download_links: bool = False,
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
			"display_name": "BBQ Text"
		},
		"bb_export": {
			"prefix": "blackboard_export_zip",
			"extension": "zip",
			"button_class": "bb_export",
			"display_name": "Blackboard Ultra ZIP",
			"accessibility_name": "Blackboard Ultra pool-export ZIP",
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
		blacklisted_item_type = find_blacklisted_item_type(
			bbq_file_name,
			type_key,
		)
		if blacklisted_item_type is not None:
			if verbose:
				print(color_text(
					f"  SKIP {file_type['display_name']}: blacklisted item type "
					f"{blacklisted_item_type}",
					COLOR_YELLOW,
				))
			output_path = get_outfile_name(
				bbq_file_name,
				file_type['prefix'],
				file_type['extension'],
			)
			if os.path.isfile(output_path):
				os.remove(output_path)
			record_stat(stats, type_key, "skipped")
			continue
		# Special handling for WeBWorK PGML: search for existing file only
		if type_key == "webwork_pgml":
			pgml_path = find_pgml_file(bbq_file_name)
			if not pgml_path:
				if verbose:
					print(color_text(
						f"  NOT FOUND (this stage only links existing files): "
						f"{file_type['display_name']}",
						COLOR_YELLOW,
					))
				record_stat(stats, type_key, "missing")
				continue
			if verbose:
				print(color_text(
					f"  FOUND {file_type['display_name']}: "
					f"{git_paths.display_path(pgml_path)}",
					COLOR_GREEN,
				))
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
		# When generate_downloads is off, never create missing artifact
		# files. Skip the button entirely for formats that do not yet
		# exist on disk.
		planned_missing_artifact = False
		if not generate_downloads and not exists_before:
			if verbose:
				print(color_text(
					f"  NOT PRESENT (this page-render stage does not generate downloads): "
					f"{file_type['display_name']}: "
					f"{git_paths.display_path(out_file_path)}",
					COLOR_YELLOW,
				))
			record_stat(stats, type_key, "missing")
			if not render_missing_download_links:
				continue
			planned_missing_artifact = True
		# Check if the source file is newer than the existing download file
		source_is_newer = False
		if exists_before:
			source_mtime = os.path.getmtime(bbq_file_name)
			download_mtime = os.path.getmtime(out_file_path)
			source_is_newer = source_mtime > download_mtime
		# Honor generate_downloads for the stale-rebuild path too:
		# render the button pointing at the stale file rather than
		# rebuilding.
		if source_is_newer and not generate_downloads:
			source_is_newer = False
		if exists_before and not force_downloads and not source_is_newer:
			if verbose:
				print(color_text(
					f"  FOUND {file_type['display_name']}: "
					f"{git_paths.display_path(out_file_path)}",
					COLOR_GREEN,
				))
			record_stat(stats, type_key, "existing")
		elif source_is_newer:
			if verbose:
				print(color_text(f"  STALE {file_type['display_name']}: source newer, rebuilding", COLOR_CYAN))
			out_file_path = _create_optional_download(
				bbq_file_name,
				file_type['prefix'],
				file_type['extension'],
				file_type['display_name'],
			)
			if out_file_path is None:
				record_stat(stats, type_key, "skipped")
				continue
			if not os.path.isfile(out_file_path):
				if verbose:
					print(color_text(
						f"  SKIP {file_type['display_name']}: output was not created",
						COLOR_YELLOW,
					))
				record_stat(stats, type_key, "skipped")
				continue
			record_stat(stats, type_key, "generated")
		elif type_key == "bb_text":
			if verbose:
				print(color_text(
					f"  MISSING {file_type['display_name']}: "
					f"{git_paths.display_path(out_file_path)}",
					COLOR_YELLOW,
				))
			record_stat(stats, type_key, "missing")
		elif not planned_missing_artifact:
			if verbose:
				print(color_text(
					f"  BUILD {file_type['display_name']}: "
					f"{git_paths.display_path(out_file_path)}",
					COLOR_CYAN,
				))
			out_file_path = _create_optional_download(
				bbq_file_name,
				file_type['prefix'],
				file_type['extension'],
				file_type['display_name'],
			)
		if out_file_path is None:
			record_stat(stats, type_key, "skipped")
			continue
		if not planned_missing_artifact and not os.path.isfile(out_file_path):
			if verbose:
				print(color_text(
					f"  SKIP {file_type['display_name']}: output was not created",
					COLOR_YELLOW,
				))
			if type_key != "bb_text":
				record_stat(stats, type_key, "skipped")
			continue
		if (
			type_key != "bb_text"
			and not planned_missing_artifact
			and not (exists_before and not force_downloads)
		):
			record_stat(stats, type_key, "generated")
		out_file_basename = os.path.basename(out_file_path)
		out_relative_path = os.path.relpath(out_file_path, start=dir_name)
		accessibility_name = file_type.get(
			"accessibility_name", file_type["display_name"]
		)
		# Create HTML button element with corresponding attributes
		if type_key == "human_read":
			button_html = (
				f'<button class="md-button custom-button {file_type["button_class"]}" '
				f'onclick="window.open(\'{out_relative_path}\', \'_blank\')" '
				f'title="View {out_file_basename}" '
				f'aria-label="Click to view the {accessibility_name} file ({out_file_basename})">\n'
				f'    <i class="fa fa-eye"></i> {file_type["display_name"]}\n'
				f'</button>'
			)
		else:
			button_html = (
				f'<a class="md-button custom-button {file_type["button_class"]}" '
				f'href="{out_relative_path}" '
				f'download '
				f'title="Download {out_file_basename}" '
				f'aria-label="Click to download the {accessibility_name} file ({out_file_basename})">\n'
				f'    <i class="fa fa-download"></i>{file_type["display_name"]}\n'
				f'</a>'
			)
		# Add the button to the HTML output
		html_output += button_html + '\n'

	# Close the container div
	html_output += '</div>'

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


#============================================
def get_outfile_name(bbq_file_name: str, prefix: str, extension: str) -> str:
	"""Return the expected artifact path for compatibility with existing callers."""
	return get_expected_outfile_name(bbq_file_name, prefix, extension)

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
	client: object = None,
	*,
	generate_downloads: bool = False,
	regenerate_selftests: bool = True,
	render_missing_download_links: bool = False,
) -> None:
	"""Update or create the topic index page and its configured artifacts.

	Args:
		topic_folder: Path to the topic folder.
		bbq_files: BBQ question files to include on the page.
		file_counter: Mutable counter tracking processed BBQ files.
		total_files: Total number of BBQ files being processed.
		download_formats: Download formats to display or generate.
		force_downloads: Whether to replace existing download files.
		verbose: Whether to print per-file progress.
		stats: Mutable generation statistics.
		base_dir: Base directory used to form include paths.
		client: Optional title-generation client.
		generate_downloads: Whether to create download files.
		regenerate_selftests: Whether to regenerate self-test HTML.
		render_missing_download_links: Whether to show links for missing files.
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
			bbq_file = git_paths.canonicalize_git_path(bbq_file)
			file_counter["count"] += 1
			file_progress = ""
			if total_files:
				file_progress = f"[{file_counter['count']}/{total_files}] "
			print('-' * 50)
			# Convert the text file to HTML
			print(color_text(
				f"  {file_progress}BBQ file {git_paths.display_path(bbq_file)}",
				COLOR_CYAN,
			))

			html_file_path = get_outfile_name(bbq_file, 'selftest', 'html')
			# The self-test HTML draws a fresh random question when explicitly
			# regenerated. Stage its replacement before publishing over the current file.
			if regenerate_selftests:
				html_file_path = create_downloadable_format(bbq_file, 'selftest', 'html')
				if not os.path.isfile(html_file_path):
					print("\n\n\n!! unfortunately, the script requires a selftest for each problem !!")
					record_stat(stats, "selftest", "failed")
					raise FileNotFoundError(git_paths.display_path(html_file_path))
				record_stat(stats, "selftest", "generated")
			elif os.path.isfile(html_file_path):
				record_stat(stats, "selftest", "existing")
			else:
				record_stat(stats, "selftest", "missing")

			# Generate the problem set title using the LLM
			problem_set_title = get_problem_set_title(client, bbq_file)
			print(color_text(f"  Problem set title: {problem_set_title}", COLOR_CYAN))

			# Add content to the index.md file
			index_md.write(f"## {problem_set_title}\n\n")
			download_button_row = generate_download_button_row(
				bbq_file,
				download_formats,
				force_downloads,
				verbose,
				stats,
				generate_downloads=generate_downloads,
				render_missing_download_links=render_missing_download_links,
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
def generate_download_artifacts(bbq_file_name: str, verbose: bool = True) -> None:
	"""Create converter-owned downloads without rendering a topic page."""
	stats = init_format_stats()
	generate_download_button_row(
		bbq_file_name,
		list(DOWNLOAD_FORMAT_KEYS),
		force_downloads=False,
		verbose=verbose,
		stats=stats,
		generate_downloads=True,
	)

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
	one bbq-*-questions.txt source. Shared by render_all and
	regenerate_all_selftests so the discovery logic lives in one place.
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

def regenerate_all_selftests(
	subject_filter: "str | None" = None,
	topic_filter: "str | None" = None,
	site_docs_dir: "str | None" = None,
	verbose: bool = True,
	stats: "dict | None" = None,
) -> None:
	"""Force-regenerate every self-test HTML from its BBQ source.

	Standalone self-test regeneration pass: enumerates every BBQ source
	file in scope (honoring subject_filter/topic_filter) and rebuilds its
	self-test HTML via create_downloadable_format. That helper stages and
	validates the replacement before publishing through qti-package-maker. Every
	self-test is treated as stale, so a fresh random question is drawn.

	This pass does NOT write index.md, does NOT construct an LLMClient,
	and does NOT call get_problem_set_title. When a stats dict is passed,
	per-file generated/failed counts are recorded under the "selftest" key.

	Args:
		subject_filter: if set, only regenerate self-tests for this subject.
		topic_filter: if set, only regenerate self-tests for this topic.
		site_docs_dir: docs root; falls back to mkdocs.yml docs_dir when None.
		verbose: print a concise per-file line for each regenerated self-test.
		stats: optional stats dict; when provided, records selftest counts.
	"""
	# Resolve the docs root. When the caller does not supply one, read the
	# canonical docs_dir from mkdocs.yml so this matches render_all.
	base_dir = site_docs_dir
	if base_dir is None:
		base_dir = get_docs_dir()
	if not os.path.exists(base_dir):
		raise FileNotFoundError(
			f"Base directory '{git_paths.display_path(base_dir)}' not found."
		)
	topic_jobs = enumerate_topic_jobs(base_dir, subject_filter, topic_filter)
	total_bbq_files = sum(len(files) for _, files in topic_jobs)
	if verbose:
		print(color_text(
			f"Regenerating self-tests for {len(topic_jobs)} topic folders "
			f"with {total_bbq_files} BBQ files",
			COLOR_CYAN,
		))
	file_count = 0
	for topic_folder, bbq_files in topic_jobs:
		for bbq_file in bbq_files:
			# Canonicalize so the path is stable regardless of how glob
			# returned it (matches update_index_md's handling).
			bbq_file = git_paths.canonicalize_git_path(bbq_file)
			file_count += 1
			# create_downloadable_format preserves the current file until the
			# replacement passes its converter output checks.
			html_file_path = create_downloadable_format(bbq_file, "selftest", "html")
			if not os.path.isfile(html_file_path):
				if verbose:
					print(color_text(
						f"  [{file_count}/{total_bbq_files}] FAILED selftest: "
						f"{git_paths.display_path(bbq_file)}",
						COLOR_YELLOW,
					))
				if stats is not None:
					record_stat(stats, "selftest", "failed")
				raise FileNotFoundError(git_paths.display_path(html_file_path))
			if verbose:
				print(color_text(
					f"  [{file_count}/{total_bbq_files}] regenerated "
					f"{git_paths.display_path(html_file_path)}",
					COLOR_GREEN,
				))
			if stats is not None:
				record_stat(stats, "selftest", "generated")

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
		print(color_text(f"Force downloads: {options.force_downloads}", COLOR_CYAN))

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
			options.force_downloads,
			options.verbose,
			stats,
			base_dir,
			client=options.llm_client,
			generate_downloads=options.generate_downloads,
			regenerate_selftests=options.regenerate_selftests,
			render_missing_download_links=options.render_missing_download_links,
		)
	if options.verbose:
		print("\n\nSummary:")
		format_order = (
			"selftest", "bb_text", "bb_export", "canvas_qti",
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

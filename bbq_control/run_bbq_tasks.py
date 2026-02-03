#!/usr/bin/env python3

"""
Batch runner for BBQ-related scripts (CSV only).

Config format (CSV):
chapter,topic,script,flags,input,notes
genetics,topic05,unique_gametes.py,"-n 5",,
"""

import argparse
import csv
import datetime
import math
import random
import os
import shlex
import shutil
import subprocess
import sys
import time

import yaml

try:
	# PIP3 modules
	from rich.text import Text
	from textual.app import App, ComposeResult
	from textual.containers import Horizontal, Vertical
	from textual.widgets import DataTable, RichLog, Static
	TEXTUAL_AVAILABLE = True
except ImportError:
	TEXTUAL_AVAILABLE = False

# ANSI colors for concise CLI feedback
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
INPUT_SCRIPT_BASENAMES = {
	"yaml_match_to_bbq.py",
	"yaml_which_one_mc_to_bbq.py",
	"yaml_make_which_one_multiple_choice.py",
	"yaml_mc_statements_to_bbq.py",
	"yaml_make_match_sets.py",
}


def color(text: str, code: str) -> str:
	return f"{code}{text}{COLOR_RESET}"


def get_repo_root() -> str:
	"""Get git repo root, falling back to script's parent directory."""
	script_dir = os.path.dirname(os.path.abspath(__file__))
	try:
		result = subprocess.check_output(
			['git', 'rev-parse', '--show-toplevel'],
			cwd=script_dir,
			stderr=subprocess.DEVNULL,
			universal_newlines=True
		)
		return result.strip()
	except (subprocess.CalledProcessError, FileNotFoundError):
		# Fallback: assume script is one level below repo root
		return os.path.dirname(script_dir)


#============================================
def parse_args():
	"""
	Parse command-line arguments.

	Returns:
		argparse.Namespace: Parsed arguments.
	"""
	parser = argparse.ArgumentParser(description="Run BBQ generation tasks from CSV.")
	parser.add_argument(
		"-t", "--tasks", dest="tasks_csv", default="bbq_tasks.csv",
		help="Path to tasks CSV (default: bbq_tasks.csv)",
	)
	parser.add_argument(
		"-s", "--settings", dest="settings_yaml", default="",
		help="Path to settings YAML (searches CWD, repo root, script dir).",
	)
	parser.add_argument(
		"-n", "--dry-run", dest="dry_run", action="store_true",
		help="Run commands but do not move outputs.",
	)
	parser.add_argument(
		"-F", "--flat", "--no-tui", dest="no_tui", action="store_true",
		help="Disable the Textual TUI interface.",
	)
	parser.add_argument(
		"-x", "--max-questions", dest="max_questions", type=int, default=None,
		help="Append -x N to all scripts.",
	)
	parser.add_argument(
		"-l", "--limit", dest="limit", type=int, default=None,
		help="Maximum number of tasks to run (for testing).",
	)
	parser.add_argument(
		"-R", "--shuffle", dest="shuffle_tasks", action="store_true",
		help="Shuffle task order before applying --limit (for testing).",
	)
	args = parser.parse_args()
	return args


#============================================
def find_settings_yaml(settings_arg: str) -> str:
	"""
	Find bbq_settings.yml in order: CWD, repo root, script directory.

	Args:
		settings_arg: the --settings argument value (may be empty)

	Returns:
		Resolved path to settings file, or empty string if not found.
	"""
	# If user provided an absolute path, use it directly
	if settings_arg and os.path.isabs(settings_arg):
		if os.path.isfile(settings_arg):
			return settings_arg
		return ""
	# Determine the basename to search for
	settings_basename = os.path.basename(settings_arg) if settings_arg else "bbq_settings.yml"
	# Search locations in priority order
	script_dir = os.path.dirname(os.path.abspath(__file__))
	repo_root = get_repo_root()
	search_paths = [
		os.path.join(os.getcwd(), settings_basename),
		os.path.join(repo_root, settings_basename),
		os.path.join(repo_root, "bbq_control", settings_basename),
		os.path.join(script_dir, settings_basename),
	]
	for candidate in search_paths:
		if os.path.isfile(candidate):
			return candidate
	return ""


def load_bbq_config(config_path: str) -> dict:
	if not config_path:
		return {}
	if not os.path.isfile(config_path):
		return {}
	with open(config_path, "r") as config_handle:
		config_data = yaml.safe_load(config_handle)
	if not isinstance(config_data, dict):
		return {}
	return config_data


def apply_aliases(text: str, aliases: dict) -> str:
	if not text:
		return ""
	result = text
	for key, value in aliases.items():
		if not isinstance(value, str):
			continue
		result = result.replace(f"{{{key}}}", value)
	return result


def resolve_alias_map(raw_aliases: dict) -> dict:
	if not isinstance(raw_aliases, dict):
		return {}
	resolved = dict(raw_aliases)
	for _ in range(3):
		for key, value in resolved.items():
			if not isinstance(value, str):
				continue
			resolved[key] = apply_aliases(value, resolved)
	for key, value in resolved.items():
		if isinstance(value, str):
			resolved[key] = os.path.expanduser(value)
	return resolved


def resolve_script_alias(script_value: str, script_aliases: dict):
	if not script_value:
		return ""
	if script_value.startswith("@"):
		alias_key = script_value[1:]
		return script_aliases.get(alias_key, script_value)
	if script_value in script_aliases:
		return script_aliases[script_value]
	return script_value


def get_env_bp_root() -> str:
	for key in ("bp_root", "BP_ROOT"):
		value = os.environ.get(key, "").strip()
		if value:
			return os.path.expanduser(value)
	return ""


def apply_env_overrides(path_aliases: dict) -> dict:
	if not isinstance(path_aliases, dict):
		return {}
	updated = dict(path_aliases)
	env_bp_root = get_env_bp_root()
	if env_bp_root:
		updated["bp_root"] = env_bp_root
	return updated


def check_pythonpath(bbq_config: dict) -> tuple:
	pythonpath_value = os.environ.get("PYTHONPATH", "").strip()
	if not pythonpath_value:
		return False, "ERROR: PYTHONPATH is not set. Run: source bbq_control/source_me.sh"
	paths_config = bbq_config.get("paths", {}) if isinstance(bbq_config, dict) else {}
	path_aliases = resolve_alias_map(paths_config)
	path_aliases = apply_env_overrides(path_aliases)
	bp_root = (path_aliases.get("bp_root") or "").strip()
	expected = ""
	if bp_root:
		if os.path.basename(bp_root) == "problems":
			expected = os.path.dirname(bp_root)
		else:
			expected = bp_root
	if expected:
		python_parts = pythonpath_value.split(os.pathsep)
		if expected not in python_parts:
			message = (
				"ERROR: PYTHONPATH does not include "
				f"{expected}. Run: source bbq_control/source_me.sh"
			)
			return False, message
	return True, ""


def build_pythonpath(bbq_config: dict) -> str:
	paths_config = bbq_config.get("paths", {}) if isinstance(bbq_config, dict) else {}
	path_aliases = resolve_alias_map(paths_config)
	path_aliases = apply_env_overrides(path_aliases)
	python_parts = []

	def add_path(path_value: str):
		if not path_value:
			return
		normalized = os.path.abspath(os.path.expanduser(path_value))
		if normalized not in python_parts:
			python_parts.append(normalized)

	bp_root = (path_aliases.get("bp_root") or "").strip()
	if bp_root:
		if os.path.basename(bp_root) == "problems":
			bp_root = os.path.dirname(bp_root)
		add_path(bp_root)
	qti_root = (path_aliases.get("qti_package_maker") or "").strip()
	if qti_root:
		add_path(qti_root)
	existing = os.environ.get("PYTHONPATH", "")
	if existing:
		for part in existing.split(os.pathsep):
			add_path(part)
	return os.pathsep.join(python_parts)


def expand_text(text: str, aliases: dict) -> str:
	if not text:
		return ""
	expanded = apply_aliases(text, aliases)
	return os.path.expanduser(expanded)


def normalize_path(path_value: str, repo_root: str, base_root: str, aliases: dict) -> str:
	if not path_value:
		return ""
	path_value = expand_text(path_value, aliases)
	if not os.path.isabs(path_value):
		root = base_root if base_root else repo_root
		path_value = os.path.join(root, path_value)
	return os.path.abspath(path_value)


def add_input_args(args: list, input_flag: str, input_path: str) -> list:
	if not input_path:
		return args
	updated = list(args)
	if input_flag:
		if input_flag not in updated:
			updated.extend([input_flag, input_path])
		elif input_path not in updated:
			updated.append(input_path)
	elif input_path not in updated:
		updated.append(input_path)
	return updated


def get_missing_input_message(task: dict) -> str:
	input_path = task.get("input_path") or ""
	if not input_path:
		return ""
	if os.path.isfile(input_path):
		return ""
	return f"Missing input file: {input_path}"


def get_missing_script_message(task: dict) -> str:
	script_path = task.get("script") or ""
	if not script_path:
		return ""
	if os.path.isfile(script_path):
		return ""
	return f"Missing script file: {script_path}"


def load_tasks(config_path: str, bbq_config: dict) -> list:
	return load_tasks_csv(config_path, bbq_config)


def load_tasks_csv(config_path: str, bbq_config: dict) -> list:
	tasks = []
	repo_root = get_repo_root()
	paths_config = bbq_config.get("paths", {}) if isinstance(bbq_config, dict) else {}
	path_aliases = resolve_alias_map(paths_config)
	path_aliases = apply_env_overrides(path_aliases)
	path_aliases["repo_root"] = repo_root
	script_aliases_raw = bbq_config.get("script_aliases", {}) if isinstance(bbq_config, dict) else {}
	script_aliases = {}
	if isinstance(script_aliases_raw, dict):
		for alias_key, alias_value in script_aliases_raw.items():
			if isinstance(alias_value, str):
				script_aliases[alias_key] = expand_text(alias_value, path_aliases)
				continue
			if isinstance(alias_value, list):
				expanded_list = []
				for item in alias_value:
					if not isinstance(item, str):
						continue
					expanded_list.append(expand_text(item, path_aliases))
				if expanded_list:
					script_aliases[alias_key] = expanded_list
	defaults = bbq_config.get("defaults", {}) if isinstance(bbq_config, dict) else {}
	default_input_flag = ""
	if isinstance(defaults, dict):
		default_input_flag = (defaults.get("input_flag") or "").strip()
	if not default_input_flag:
		default_input_flag = "-y"
	base_root = (path_aliases.get("bp_root") or "").strip()
	if not os.path.isfile(config_path):
		raise FileNotFoundError(f"Config file not found: {config_path}")
	with open(config_path, newline="") as fp:
		reader = csv.DictReader(fp)
		for row in reader:
			program = (row.get("program") or "python3").strip()
			script = (row.get("script") or "").strip()
			flags = (row.get("flags") or "").strip()
			input_value = (row.get("input") or "").strip()
			output = (row.get("output") or "").strip()
			chapter = (row.get("chapter") or "").strip()
			topic = (row.get("topic") or "").strip()
			output_file = (row.get("output_file") or "").strip()
			if not script and not flags:
				continue
			script_value = resolve_script_alias(script, script_aliases)
			script_values = []
			if isinstance(script_value, list):
				for item in script_value:
					if not isinstance(item, str):
						continue
					if item.strip():
						script_values.append(item.strip())
			elif isinstance(script_value, str):
				if script_value:
					script_values.append(script_value)
			if not script_values and script:
				script_values = [script]
			output_dir_parts = [repo_root, "site_docs"]
			if chapter:
				output_dir_parts.append(chapter)
			if topic:
				output_dir_parts.append(topic)
			output_dir = os.path.join(*output_dir_parts)
			if not output and output_file:
				output = os.path.join(output_dir, output_file)
			output = normalize_path(output, repo_root, "", path_aliases)
			flags = expand_text(flags, path_aliases)
			base_args = shlex.split(flags) if flags else []
			for script_entry in script_values:
				script_path = normalize_path(script_entry, repo_root, base_root, path_aliases)
				args = list(base_args)
				input_path = ""
				if input_value:
					input_flag = default_input_flag
					input_value_expanded = input_value
					if os.path.basename(input_value_expanded) == input_value_expanded:
						script_basename = os.path.basename(script_path)
						if script_basename in INPUT_SCRIPT_BASENAMES:
							input_value_expanded = os.path.join(
								os.path.dirname(script_path),
								input_value_expanded,
							)
					input_path = normalize_path(input_value_expanded, repo_root, base_root, path_aliases)
					args = add_input_args(args, input_flag, input_path)
				task = {
					"program": program or "python3",
					"script": script_path,
					"args": args,
					"output": output,
					"output_dir": output_dir,
					"input_path": input_path,
				}
				tasks.append(task)
	return tasks


def ensure_parent_dir(path: str):
	parent = os.path.dirname(path)
	if parent and not os.path.isdir(parent):
		os.makedirs(parent, exist_ok=True)


def move_output_if_needed(output_path: str, workdir: str = ".") -> bool:
	"""If output_path does not exist, but the basename exists in workdir, move it."""
	if not output_path:
		return True
	base = os.path.basename(output_path)
	if not base:
		return False
	candidate = os.path.join(workdir, base)
	if os.path.isfile(candidate):
		ensure_parent_dir(output_path)
		if os.path.abspath(candidate) == os.path.abspath(output_path):
			return True
		if os.path.isfile(output_path):
			os.remove(output_path)
		shutil.move(candidate, output_path)
		return True
	return os.path.isfile(output_path)


def output_exists(output_path: str, workdir: str = ".") -> bool:
	if not output_path:
		return True
	if os.path.isfile(output_path):
		return True
	base = os.path.basename(output_path)
	if not base:
		return False
	candidate = os.path.join(workdir, base)
	return os.path.isfile(candidate)


def resolve_output_candidate(output_path: str, workdir: str = ".") -> str:
	if not output_path:
		return ""
	if os.path.isfile(output_path):
		return output_path
	base = os.path.basename(output_path)
	if not base:
		return ""
	candidate = os.path.join(workdir, base)
	if os.path.isfile(candidate):
		return candidate
	return ""


def resolve_output_workdir(output_path: str, workdir: str = ".") -> str:
	if not output_path:
		return ""
	base = os.path.basename(output_path)
	if not base:
		return ""
	candidate = os.path.join(workdir, base)
	if os.path.isfile(candidate):
		return candidate
	return ""


def resolve_output_workdir_recent(output_path: str, workdir: str, start_time: float) -> str:
	candidate = resolve_output_workdir(output_path, workdir)
	if not candidate:
		return ""
	mtime = os.path.getmtime(candidate)
	if mtime >= (start_time - 2.0):
		return candidate
	return ""


def build_output_patterns(task: dict) -> tuple:
	script_path = task.get("script", "") if isinstance(task, dict) else ""
	script_basename = os.path.splitext(os.path.basename(script_path))[0]
	if not script_basename:
		return [], ("-problems.txt",)
	prefixes = [f"bbq-{script_basename}"]
	input_path = task.get("input_path", "") if isinstance(task, dict) else ""
	input_basename = os.path.splitext(os.path.basename(input_path))[0] if input_path else ""
	if input_basename:
		if script_basename == "yaml_match_to_bbq":
			prefixes.append(f"bbq-MATCH-{input_basename}")
		elif script_basename == "yaml_which_one_mc_to_bbq":
			prefixes.append(f"bbq-MC-{input_basename}")
		elif script_basename == "yaml_mc_statements_to_bbq":
			prefixes.append(f"bbq-TFMS-{input_basename}")
	suffixes = ("-problems.txt", "-questions.txt")
	return prefixes, suffixes


def find_recent_outputs(workdir: str, start_time: float, prefixes: list, suffixes: tuple) -> list:
	candidates = []
	if not workdir or not os.path.isdir(workdir):
		return candidates
	if not prefixes:
		return candidates
	for entry in os.scandir(workdir):
		if not entry.is_file():
			continue
		name = entry.name
		if not any(name.startswith(prefix) for prefix in prefixes):
			continue
		if suffixes and not any(name.endswith(suffix) for suffix in suffixes):
			continue
		try:
			mtime = entry.stat().st_mtime
		except OSError:
			continue
		if mtime >= (start_time - 2.0):
			candidates.append((mtime, entry.path))
	candidates.sort(key=lambda item: item[0], reverse=True)
	return [path for _, path in candidates]


def resolve_generated_output(task: dict, workdir: str, start_time: float) -> tuple:
	output_dir = (task.get("output_dir") or "").strip()
	script_path = task.get("script", "")
	if not script_path:
		return False, "", "", "Missing script path for output detection."
	prefixes, suffixes = build_output_patterns(task)
	if not prefixes:
		return False, "", "", "Missing script basename for output detection."
	candidates = find_recent_outputs(workdir, start_time, prefixes, suffixes)
	if not candidates:
		return False, "", "", "Expected output not found in workdir."
	if len(candidates) > 1:
		names = ", ".join(os.path.basename(path) for path in candidates)
		return False, "", "", f"Multiple outputs found in {workdir}: {names}"
	candidate = candidates[0]
	if output_dir:
		output_path = os.path.join(output_dir, os.path.basename(candidate))
	else:
		output_path = candidate
	return True, output_path, candidate, ""


def move_output_candidate(candidate: str, output_path: str) -> bool:
	if not candidate or not output_path:
		return False
	ensure_parent_dir(output_path)
	if os.path.abspath(candidate) == os.path.abspath(output_path):
		return True
	if os.path.isfile(output_path):
		os.remove(output_path)
	shutil.move(candidate, output_path)
	return True


def count_output_lines(output_path: str, workdir: str = ".") -> int:
	candidate = resolve_output_candidate(output_path, workdir)
	return count_output_lines_path(candidate)


def count_output_lines_path(path: str) -> int:
	if not path:
		return 0
	with open(path, "r") as file_handle:
		return sum(1 for _ in file_handle)


def cleanup_dry_run_output(path: str, log_path: str):
	if not path:
		return
	base = os.path.basename(path)
	if not base.startswith("bbq") or not base.endswith(".txt"):
		return
	if os.path.isfile(path):
		os.remove(path)
		log_line(log_path, f"CLEANUP removed {path}")


def log_line(log_path: str, message: str):
	ensure_parent_dir(log_path)
	timestamp = datetime.datetime.now().isoformat()
	with open(log_path, "a") as fp:
		fp.write(f"[{timestamp}] {message}\n")


def log_error(
	log_path: str,
	label: str,
	message: str,
	stdout_text: str = "",
	stderr_text: str = "",
	cmd_list: list = None,
):
	if not log_path:
		return
	ensure_parent_dir(log_path)
	timestamp = datetime.datetime.now().isoformat()
	with open(log_path, "a") as fp:
		fp.write(f"[{timestamp}] {label}: {message}\n")
		if cmd_list:
			fp.write(f"CMD: {' '.join(str(part) for part in cmd_list)}\n")
		if stdout_text:
			fp.write("STDOUT:\n")
			fp.write(stdout_text.rstrip() + "\n")
		if stderr_text:
			fp.write("STDERR:\n")
			fp.write(stderr_text.rstrip() + "\n")
		fp.write("\n")


def rotate_log(log_path: str, max_backups: int = 5) -> bool:
	"""
	Rotate log file with numbered backups (.1, .2, ... .N).

	Shifts existing backups up by one number and moves current log to .1.
	Returns True if an existing log was rotated, False otherwise.
	"""
	if not log_path:
		return False
	rotated = False
	# Shift existing backups: .4 -> .5, .3 -> .4, .2 -> .3, .1 -> .2
	for i in range(max_backups - 1, 0, -1):
		old_backup = f"{log_path}.{i}"
		new_backup = f"{log_path}.{i + 1}"
		if os.path.isfile(old_backup):
			shutil.move(old_backup, new_backup)
	# Move current log to .1
	if os.path.isfile(log_path):
		shutil.move(log_path, f"{log_path}.1")
		rotated = True
	# Create empty log file
	with open(log_path, "w") as fp:
		fp.write("")
	return rotated


def build_command(task: dict) -> list:
	# Simplest form: a single command string
	if "cmd" in task:
		cmd_value = task.get("cmd")
		if isinstance(cmd_value, str):
			parts = shlex.split(cmd_value)
		elif isinstance(cmd_value, list):
			parts = [str(x) for x in cmd_value]
		else:
			parts = []
		extra_args = task.get("extra_args", [])
		if extra_args:
			parts.extend(str(a) for a in extra_args)
		if parts and parts[0].endswith(".py"):
			parts.insert(0, "python3")
		return parts
	program = task.get("program")
	if not program:
		program = "python3"
	script = task.get("script")
	args = task.get("args", [])
	cmd = [str(program)]
	if script:
		cmd.append(str(script))
	cmd.extend(str(a) for a in args)
	extra_args = task.get("extra_args", [])
	if extra_args:
		cmd.extend(str(a) for a in extra_args)
	return cmd


def task_label(task: dict, index: int, output_path: str, cmd_list: list) -> str:
	if task.get("name"):
		return task.get("name")
	script_path = task.get("script", "")
	if script_path:
		script_base = os.path.basename(script_path)
		if script_base in (
			"yaml_match_to_bbq.py",
			"yaml_which_one_mc_to_bbq.py",
			"yaml_mc_statements_to_bbq.py",
		):
			input_path = task.get("input_path", "")
			input_base = os.path.splitext(os.path.basename(input_path))[0] if input_path else ""
			if input_base:
				return f"{script_base} ({input_base})"
		return script_base
	if output_path:
		return os.path.basename(output_path)
	if "cmd" in task and isinstance(task["cmd"], str):
		return task["cmd"].split()[0]
	if cmd_list:
		return cmd_list[0]
	return f"Task {index}"


def shorten_text(text: str, max_len: int) -> str:
	if len(text) <= max_len:
		return text
	if max_len <= 3:
		return text[:max_len]
	return text[:max_len - 3] + "..."


#============================================
class RunContext:
	def __init__(
		self,
		log_path: str,
		error_log_path: str,
		allow_cleanup: bool,
		pythonpath_value: str,
	):
		self.log_path = log_path
		self.error_log_path = error_log_path
		self.allow_cleanup = allow_cleanup
		self.pythonpath_value = pythonpath_value


#============================================
def run_task_capture(
	task: dict,
	log_path: str,
	move_output: bool,
	allow_cleanup: bool = True,
	pythonpath_value: str = "",
	error_log_path: str = "",
) -> tuple:
	output_path = task.get("output", "")
	workdir = "."
	cmd = build_command(task)
	label = task_label(task, 0, output_path, cmd)
	max_questions = task.get("max_questions")
	start_time = time.time()
	candidate_path = ""

	missing_script = get_missing_script_message(task)
	if missing_script:
		log_line(log_path, missing_script)
		log_error(error_log_path, label, missing_script, cmd_list=cmd)
		return False, "", missing_script, 0
	missing_input = get_missing_input_message(task)
	if missing_input:
		log_line(log_path, missing_input)
		log_error(error_log_path, label, missing_input, cmd_list=cmd)
		return False, "", missing_input, 0

	log_line(log_path, f"CMD   {' '.join(cmd)} (cwd={workdir})")
	env_override = None
	if pythonpath_value:
		env_override = os.environ.copy()
		env_override["PYTHONPATH"] = pythonpath_value
	try:
		proc = subprocess.run(
			cmd,
			cwd=workdir,
			env=env_override,
			text=True,
			capture_output=True,
			check=False,
		)
	except Exception as exc:
		log_line(log_path, f"LAUNCH ERROR {exc}")
		log_error(error_log_path, label, f"Launch error: {exc}", cmd_list=cmd)
		return False, "", str(exc), 0

	if proc.stdout:
		log_line(log_path, f"STDOUT:\n{proc.stdout.rstrip()}")
	if proc.stderr:
		log_line(log_path, f"STDERR:\n{proc.stderr.rstrip()}")

	if proc.returncode != 0:
		log_line(log_path, f"EXIT -> {proc.returncode}")
		log_error(
			error_log_path,
			label,
			f"Exit {proc.returncode}",
			stdout_text=proc.stdout,
			stderr_text=proc.stderr,
			cmd_list=cmd,
		)
		return False, proc.stdout, proc.stderr, 0

	if output_path:
		if move_output:
			moved_ok = move_output_if_needed(output_path, workdir)
			if not moved_ok:
				log_line(log_path, f"ERROR expected output not found: {output_path}")
				return False, proc.stdout, proc.stderr, 0
		else:
			candidate_path = resolve_output_workdir_recent(output_path, workdir, start_time)
			if not candidate_path:
				log_line(log_path, f"ERROR expected output not found: {output_path}")
				log_error(error_log_path, label, f"Output not found: {output_path}", cmd_list=cmd)
				return False, proc.stdout, proc.stderr, 0
	else:
		ok, resolved_output, detected_path, error_message = resolve_generated_output(
			task,
			workdir,
			start_time,
		)
		if not ok:
			log_line(log_path, f"ERROR {error_message}")
			log_error(
				error_log_path,
				label,
				error_message,
				stdout_text=proc.stdout,
				stderr_text=proc.stderr,
				cmd_list=cmd,
			)
			return False, proc.stdout, proc.stderr, 0
		output_path = resolved_output
		candidate_path = detected_path
		log_line(log_path, f"DETECTED output -> {output_path}")
		if move_output:
			moved_ok = move_output_candidate(candidate_path, output_path)
			if not moved_ok:
				log_line(log_path, f"ERROR expected output not found: {output_path}")
				log_error(error_log_path, label, f"Output not found: {output_path}", cmd_list=cmd)
				return False, proc.stdout, proc.stderr, 0
		else:
			if not os.path.isfile(candidate_path):
				log_line(log_path, f"ERROR expected output not found: {candidate_path}")
				log_error(error_log_path, label, f"Output not found: {candidate_path}", cmd_list=cmd)
				return False, proc.stdout, proc.stderr, 0

	if move_output:
		line_count = count_output_lines_path(output_path)
	else:
		if not candidate_path:
			candidate_path = resolve_output_workdir_recent(output_path, workdir, start_time)
		line_count = count_output_lines_path(candidate_path)
	if max_questions and line_count > max_questions:
		msg = f"Output has {line_count} lines; expected <= {max_questions}."
		log_line(log_path, msg)
		log_error(error_log_path, label, msg, cmd_list=cmd)
		if proc.stderr:
			return False, proc.stdout, proc.stderr + "\n" + msg, line_count
		return False, proc.stdout, msg, line_count
	if not move_output:
		if allow_cleanup:
			if candidate_path:
				cleanup_dry_run_output(candidate_path, log_path)
			else:
				cleanup_dry_run_output(resolve_output_workdir(output_path, workdir), log_path)
		else:
			log_line(log_path, "SKIP CLEANUP (PYTHONPATH not set)")
	return True, proc.stdout, proc.stderr, line_count


def run_task(
	task: dict,
	log_path: str,
	index: int,
	total: int,
	move_output: bool = True,
	allow_cleanup: bool = True,
	pythonpath_value: str = "",
	error_log_path: str = "",
):
	output_path = task.get("output", "")
	workdir = "."
	max_questions = task.get("max_questions")
	start_time = time.time()

	cmd = build_command(task)
	label = task_label(task, index, output_path, cmd)
	summary = f"[{index}/{total}] {label}"
	print(color(summary, COLOR_CYAN))
	log_line(log_path, f"START {summary} -> {output_path or 'N/A'}")
	missing_script = get_missing_script_message(task)
	if missing_script:
		print(color(f"FAILED {label}: {missing_script}", COLOR_RED))
		log_line(log_path, missing_script)
		log_error(error_log_path, label, missing_script, cmd_list=cmd)
		return False
	missing_input = get_missing_input_message(task)
	if missing_input:
		print(color(f"FAILED {label}: {missing_input}", COLOR_RED))
		log_line(log_path, missing_input)
		log_error(error_log_path, label, missing_input, cmd_list=cmd)
		return False
	log_line(log_path, f"CMD   {' '.join(cmd)} (cwd={workdir})")

	env_override = None
	if pythonpath_value:
		env_override = os.environ.copy()
		env_override["PYTHONPATH"] = pythonpath_value
	try:
		proc = subprocess.run(
			cmd,
			cwd=workdir,
			env=env_override,
			text=True,
			capture_output=True,
			check=False,
		)
	except Exception as exc:  # subprocess failure before execution
		print(color(f"FAILED to launch {label}: {exc}", COLOR_RED))
		log_line(log_path, f"LAUNCH ERROR {label}: {exc}")
		log_error(error_log_path, label, f"Launch error: {exc}", cmd_list=cmd)
		return False

	if proc.stdout:
		log_line(log_path, f"STDOUT {label}:\n{proc.stdout.rstrip()}")
	if proc.stderr:
		log_line(log_path, f"STDERR {label}:\n{proc.stderr.rstrip()}")

	if proc.returncode != 0:
		print(color(f"FAILED {label} (exit {proc.returncode})", COLOR_RED))
		log_line(log_path, f"EXIT {label} -> {proc.returncode}")
		log_error(
			error_log_path,
			label,
			f"Exit {proc.returncode}",
			stdout_text=proc.stdout,
			stderr_text=proc.stderr,
			cmd_list=cmd,
		)
		return False

	# If the task specifies an output path and the script wrote to CWD, move it.
	line_count = 0
	candidate_path = ""
	if output_path:
		if move_output:
			moved_ok = move_output_if_needed(output_path, workdir)
			if moved_ok:
				if os.path.isfile(output_path):
					log_line(log_path, f"MOVED output to {output_path}")
			else:
				print(color(f"FAILED: expected output not found: {output_path}", COLOR_RED))
				log_line(log_path, f"ERROR: expected output not found: {output_path}")
				log_error(error_log_path, label, f"Output not found: {output_path}", cmd_list=cmd)
				return False
		else:
			candidate_path = resolve_output_workdir_recent(output_path, workdir, start_time)
			if not candidate_path:
				print(color(f"FAILED: expected output not found: {output_path}", COLOR_RED))
				log_line(log_path, f"ERROR: expected output not found: {output_path}")
				log_error(error_log_path, label, f"Output not found: {output_path}", cmd_list=cmd)
				return False
			log_line(log_path, f"SKIP MOVE {label} -> {output_path}")
	else:
		ok, resolved_output, detected_path, error_message = resolve_generated_output(
			task,
			workdir,
			start_time,
		)
		if not ok:
			print(color(f"FAILED: {error_message}", COLOR_RED))
			log_line(log_path, f"ERROR: {error_message}")
			log_error(
				error_log_path,
				label,
				error_message,
				stdout_text=proc.stdout,
				stderr_text=proc.stderr,
				cmd_list=cmd,
			)
			return False
		output_path = resolved_output
		task["output"] = output_path
		candidate_path = detected_path
		log_line(log_path, f"DETECTED output -> {output_path}")
		if move_output:
			moved_ok = move_output_candidate(candidate_path, output_path)
			if not moved_ok:
				print(color(f"FAILED: expected output not found: {output_path}", COLOR_RED))
				log_line(log_path, f"ERROR: expected output not found: {output_path}")
				log_error(error_log_path, label, f"Output not found: {output_path}", cmd_list=cmd)
				return False
			log_line(log_path, f"MOVED output to {output_path}")
		else:
			if not os.path.isfile(candidate_path):
				print(color(f"FAILED: expected output not found: {candidate_path}", COLOR_RED))
				log_line(log_path, f"ERROR: expected output not found: {candidate_path}")
				log_error(error_log_path, label, f"Output not found: {candidate_path}", cmd_list=cmd)
				return False
			log_line(log_path, f"SKIP MOVE {label} -> {candidate_path}")
	# Count output lines
	if move_output:
		line_count = count_output_lines_path(output_path)
	else:
		if not candidate_path:
			candidate_path = resolve_output_workdir_recent(output_path, workdir, start_time)
		line_count = count_output_lines_path(candidate_path)
	# Check against max_questions limit
	if max_questions and line_count > max_questions:
		msg = f"Output has {line_count} lines; expected <= {max_questions}."
		print(color(f"FAILED {label}: {msg}", COLOR_RED))
		log_line(log_path, msg)
		log_error(error_log_path, label, msg, cmd_list=cmd)
		return False
	if not move_output:
		if allow_cleanup:
			if candidate_path:
				cleanup_dry_run_output(candidate_path, log_path)
			else:
				cleanup_dry_run_output(resolve_output_workdir(output_path, workdir), log_path)
		else:
			log_line(log_path, "SKIP CLEANUP (PYTHONPATH not set)")

	# Show line count in output
	if line_count > 0:
		print(color(f"DONE  {label} ({line_count} lines)", COLOR_GREEN))
	else:
		print(color(f"DONE  {label}", COLOR_GREEN))
	log_line(log_path, f"EXIT {label} -> 0")
	return True


if TEXTUAL_AVAILABLE:
	class BBQTaskApp(App):
		STATUS_STYLES = {
			"pending": "yellow",
			"running": "cyan",
			"ok": "green",
			"failed": "red",
		}

		def format_status(self, status: str) -> Text:
			style = self.STATUS_STYLES.get(status, "")
			if style:
				return Text(status, style=style)
			return Text(status)

		def __init__(self, tasks: list, args: argparse.Namespace, run_context: RunContext) -> None:
			super().__init__()
			self.tasks = tasks
			self.args = args
			self.run_context = run_context
			self.total = len(tasks)
			self.start_time = time.time()
			self.completed = 0
			self.durations = []
			self.log_lines = []
			self.task_rows = []
			self.column_keys = {}

		CSS = (
			"#root { height: 1fr; }\n"
			"#top_row { height: 40%; min-height: 10; }\n"
			"#metrics_box { width: 30%; height: 1fr; border: solid gray; }\n"
			"#metrics_title { height: 1; }\n"
			"#metrics { height: 1fr; }\n"
			"#footer_note { height: 1; }\n"
			"#messages { width: 70%; height: 1fr; border: solid gray; }\n"
			"#task_table { height: 1fr; border: solid gray; }\n"
		)

		def compose(self) -> ComposeResult:
			with Vertical(id="root"):
				with Horizontal(id="top_row"):
					with Vertical(id="metrics_box"):
						yield Static("BBQ Task Dashboard", id="metrics_title")
						yield Static("Ready", id="metrics")
						yield Static("Press q to quit", id="footer_note")
					yield RichLog(id="messages", wrap=True, highlight=False)
				table = DataTable(id="task_table", zebra_stripes=True)
				table.cursor_type = "row"
				self.task_rows = []
				self.column_keys = {
					"index": table.add_column("#"),
					"script": table.add_column("script"),
					"status": table.add_column("status"),
					"sec": table.add_column("sec"),
					"lines": table.add_column("lines"),
				}
				for idx, task in enumerate(self.tasks, start=1):
					script_path = task.get("script", "")
					label = os.path.basename(script_path) if script_path else task_label(
						task, idx, task.get("output", ""), build_command(task)
					)
					label = shorten_text(label, 120)
					row_key = table.add_row(
						str(idx),
						label,
						self.format_status("pending"),
						"",
						"",
					)
					self.task_rows.append(row_key)
				yield table

		def on_mount(self) -> None:
			self.run_worker(self.run_tasks, exclusive=True)

		def append_log(self, message: str) -> None:
			self.log_lines.append(message)
			if len(self.log_lines) > 200:
				self.log_lines = self.log_lines[-200:]
			log_widget = self.query_one(RichLog)
			log_widget.write(message)

		def update_metrics(self) -> None:
			elapsed = time.time() - self.start_time
			if self.completed > 0:
				avg = sum(self.durations) / self.completed
				eta = avg * (self.total - self.completed)
			else:
				eta = 0.0
			metrics = (
				f"Completed: {self.completed}/{self.total}\n"
				f"Elapsed: {elapsed:.1f}s\n"
				f"ETA: {eta:.1f}s"
			)
			self.query_one("#metrics", Static).update(metrics)

		async def run_tasks(self) -> None:
			for idx, task in enumerate(self.tasks, start=1):
				script_path = task.get("script", "")
				label = os.path.basename(script_path) if script_path else task_label(
					task, idx, task.get("output", ""), build_command(task)
				)
				label = shorten_text(label, 44)
				table = self.query_one(DataTable)
				row_key = self.task_rows[idx - 1]
				table.update_cell(row_key, self.column_keys["status"], self.format_status("running"))
				start = time.time()

				ok, stdout, stderr, line_count = await self.run_in_thread(task)
				duration = time.time() - start
				self.durations.append(duration)
				self.completed += 1

				status = "ok" if ok else "failed"
				table.update_cell(row_key, self.column_keys["status"], self.format_status(status))
				table.update_cell(row_key, self.column_keys["sec"], f"{duration:.1f}")
				table.update_cell(row_key, self.column_keys["lines"], str(line_count))
				self.append_log(f"{status.upper()} {label} ({duration:.1f}s, {line_count} lines)")
				if stdout:
					self.append_log(stdout.rstrip()[:2000])
				if stderr:
					self.append_log(stderr.rstrip()[:2000])
				self.update_metrics()

			self.append_log("All tasks completed.")

		async def run_in_thread(self, task: dict) -> tuple:
			worker = self.run_worker(
				lambda: run_task_capture(
					task,
					self.run_context.log_path,
					not self.args.dry_run,
					self.run_context.allow_cleanup,
					self.run_context.pythonpath_value,
					self.run_context.error_log_path,
				),
				thread=True,
				exclusive=False
			)
			return await worker.wait()

		def on_key(self, event) -> None:
			if event.key == "q":
				self.exit()


#============================================
def main():
	args = parse_args()
	# Hardcoded settings
	log_path = os.path.join(os.getcwd(), "bbq_generation.log")
	error_log_path = os.path.join(os.getcwd(), "bbq_generation_errors.log")
	if os.path.isfile(error_log_path):
		os.remove(error_log_path)
	# Duplicates: 1.1x max-questions when set, otherwise 99
	if args.max_questions is not None:
		duplicates_count = math.ceil(args.max_questions * 1.1)
	else:
		duplicates_count = 99

	# Find settings file
	settings_path = find_settings_yaml(args.settings_yaml)
	if not settings_path:
		print(color("Warning: bbq_settings.yml not found, aliases will not expand.", COLOR_YELLOW))
	settings = load_bbq_config(settings_path)
	pythonpath_ok, pythonpath_message = check_pythonpath(settings)
	if not pythonpath_ok:
		if pythonpath_message:
			print(color(pythonpath_message, COLOR_RED))
		return 1
	pythonpath_value = build_pythonpath(settings)
	tasks = load_tasks(args.tasks_csv, settings)
	if args.shuffle_tasks:
		random.shuffle(tasks)
	if args.limit is not None:
		if args.limit <= 0:
			print(color("Limit must be a positive integer.", COLOR_RED))
			return 1
		tasks = tasks[:args.limit]
	if args.max_questions is not None:
		if args.max_questions <= 0:
			print(color("Max questions must be a positive integer.", COLOR_RED))
			return 1
		for task in tasks:
			task_args = task.get("args", [])
			if "-x" in task_args or "--max-questions" in task_args:
				continue
			task.setdefault("extra_args", [])
			task["extra_args"].extend(["-x", str(args.max_questions)])
			task["max_questions"] = args.max_questions
	if args.max_questions is not None:
		for task in tasks:
			task.setdefault("max_questions", args.max_questions)
	# Always add duplicates flag
	for task in tasks:
		task_args = task.get("args", [])
		if "-d" in task_args or "--duplicates" in task_args:
			continue
		task.setdefault("extra_args", [])
		task["extra_args"].extend(["-d", str(duplicates_count)])

	total = len(tasks)
	if total == 0:
		print(color("No tasks found in config.", COLOR_YELLOW))
		return 0
	if rotate_log(log_path):
		print(f"Rotated previous log to {log_path}.1")
	if not pythonpath_ok and pythonpath_message:
		log_line(log_path, pythonpath_message)
	run_context = RunContext(
		log_path,
		error_log_path,
		pythonpath_ok,
		pythonpath_value,
	)

	use_tui = TEXTUAL_AVAILABLE and not args.no_tui and sys.stdout.isatty()
	if use_tui:
		app = BBQTaskApp(tasks, args, run_context)
		app.run()
		return 0
	if not TEXTUAL_AVAILABLE and not args.no_tui:
		print(color("Textual is not installed; running in plain mode.", COLOR_YELLOW))

	log_line(log_path, f"=== RUN START ({total} tasks) ===")
	failures = 0

	for idx, task in enumerate(tasks, start=1):
		cmd = build_command(task)
		if args.dry_run:
			print(color(f"[{idx}/{total}] DRY-RUN {' '.join(cmd)}", COLOR_CYAN))
			ok = run_task(
				task,
				log_path,
				idx,
				total,
				move_output=False,
				allow_cleanup=run_context.allow_cleanup,
				pythonpath_value=run_context.pythonpath_value,
				error_log_path=run_context.error_log_path,
			)
		else:
			ok = run_task(
				task,
				log_path,
				idx,
				total,
				allow_cleanup=run_context.allow_cleanup,
				pythonpath_value=run_context.pythonpath_value,
				error_log_path=run_context.error_log_path,
			)
		if not ok:
			failures += 1

	log_line(log_path, f"=== RUN END (failures={failures}) ===")
	if failures:
		print(color(
			f"Completed with {failures} failure(s). See {log_path} and {error_log_path}",
			COLOR_RED,
		))
		return 1
	print(color("All tasks completed successfully.", COLOR_GREEN))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

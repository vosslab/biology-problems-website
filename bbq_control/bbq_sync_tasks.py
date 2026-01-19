#!/usr/bin/env python3

"""
Sync BBQ output files with biology-problems generators.
"""

# Standard Library
import argparse
import csv
import datetime
import os
import shlex
import shutil
import subprocess

import yaml

#============================================
# Known scripts where input lives in the same directory.
INPUT_SCRIPT_BASENAMES = {
	"yaml_make_which_one_multiple_choice.py",
	"yaml_multiple_choice_statements.py",
	"yaml_make_match_sets.py",
}


#============================================
def parse_args():
	"""
	Parse command-line arguments.

	Returns:
		argparse.Namespace: Parsed arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Sync BBQ outputs from biology-problems generators."
	)

	config_group = parser.add_argument_group("config")
	config_group.add_argument(
		"-c",
		"--config",
		dest="config_path",
		default="bbq_control/bbq_tasks.csv",
		help="Path to task CSV mapping.",
	)
	config_group.add_argument(
		"-s",
		"--state",
		dest="state_path",
		default="bbq_control/bbq_task_state.csv",
		help="Path to task state CSV.",
	)
	config_group.add_argument(
		"-l",
		"--log",
		dest="log_path",
		default="logs/bbq_sync.log",
		help="Path to append run logs.",
	)
	config_group.add_argument(
		"--bbq-config",
		dest="bbq_config",
		default="bbq_control/bbq_settings.yml",
		help="Path to BBQ settings YAML.",
	)

	run_group = parser.add_argument_group("run")
	run_group.add_argument(
		"-f",
		"--force",
		dest="force",
		action="store_true",
		help="Regenerate all outputs.",
	)
	run_group.add_argument(
		"-o",
		"--only-changed",
		dest="force",
		action="store_false",
		help="Only regenerate when inputs change.",
	)
	run_group.add_argument(
		"-n",
		"--dry-run",
		dest="dry_run",
		action="store_true",
		help="Print actions without running commands.",
	)
	run_group.add_argument(
		"-r",
		"--run",
		dest="dry_run",
		action="store_false",
		help="Execute commands (default).",
	)
	run_group.add_argument(
		"-v",
		"--verbose",
		dest="verbose",
		action="store_true",
		help="Show skip reasons.",
	)
	run_group.add_argument(
		"-q",
		"--quiet",
		dest="verbose",
		action="store_false",
		help="Hide skip reasons.",
	)

	parser.set_defaults(force=False, dry_run=False, verbose=True)
	args = parser.parse_args()
	return args


#============================================
def expand_path(path_value: str) -> str:
	"""
	Expand user and return absolute path.

	Args:
		path_value (str): Path from config.

	Returns:
		str: Absolute path or empty string.
	"""
	if not path_value:
		cleaned_path = ""
		return cleaned_path
	expanded_path = os.path.expanduser(path_value)
	absolute_path = os.path.abspath(expanded_path)
	return absolute_path


#============================================
def build_pythonpath(path_aliases: dict) -> str:
	"""
	Build a PYTHONPATH from BBQ settings and existing environment.

	Args:
		path_aliases (dict): Resolved path aliases.

	Returns:
		str: PYTHONPATH value.
	"""
	python_parts = []

	def add_path(path_value: str):
		if not path_value:
			return
		normalized = os.path.abspath(os.path.expanduser(path_value))
		if normalized not in python_parts:
			python_parts.append(normalized)

	if isinstance(path_aliases, dict):
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


#============================================
def load_bbq_config(config_path: str) -> dict:
	"""
	Load BBQ YAML config for path aliases and script aliases.

	Args:
		config_path (str): Path to config YAML.

	Returns:
		dict: Config dictionary (empty if missing or invalid).
	"""
	if not config_path:
		return {}
	if not os.path.isfile(config_path):
		return {}
	with open(config_path, "r") as config_handle:
		config_data = yaml.safe_load(config_handle)
	if not isinstance(config_data, dict):
		return {}
	return config_data


#============================================
def apply_aliases(text: str, aliases: dict) -> str:
	"""
	Apply {alias} replacements to a string.

	Args:
		text (str): Input string.
		aliases (dict): Alias mapping.

	Returns:
		str: Expanded string.
	"""
	if not text:
		return ""
	result = text
	for key, value in aliases.items():
		if not isinstance(value, str):
			continue
		result = result.replace(f"{{{key}}}", value)
	return result


#============================================
def resolve_alias_map(raw_aliases: dict) -> dict:
	"""
	Resolve nested aliases and expand user paths.

	Args:
		raw_aliases (dict): Alias mapping.

	Returns:
		dict: Resolved aliases.
	"""
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


#============================================
def resolve_script_alias(script_value: str, script_aliases: dict) -> str:
	"""
	Resolve a script alias to a path.

	Args:
		script_value (str): Script alias or path.
		script_aliases (dict): Script alias mapping.

	Returns:
		str: Resolved script path or alias.
	"""
	if not script_value:
		return ""
	if script_value.startswith("@"):
		alias_key = script_value[1:]
		return script_aliases.get(alias_key, script_value)
	if script_value in script_aliases:
		return script_aliases[script_value]
	return script_value


#============================================
def expand_text(text: str, aliases: dict) -> str:
	"""
	Expand aliases and user paths in text.

	Args:
		text (str): Input text.
		aliases (dict): Alias mapping.

	Returns:
		str: Expanded text.
	"""
	if not text:
		return ""
	expanded = apply_aliases(text, aliases)
	return os.path.expanduser(expanded)


#============================================
def normalize_path(path_value: str, repo_root: str, base_root: str, aliases: dict) -> str:
	"""
	Normalize a path with alias expansion and base roots.

	Args:
		path_value (str): Input path.
		repo_root (str): Repository root for relative paths.
		base_root (str): Base root for external scripts.
		aliases (dict): Alias mapping.

	Returns:
		str: Absolute path.
	"""
	if not path_value:
		return ""
	path_value = expand_text(path_value, aliases)
	if not os.path.isabs(path_value):
		root = base_root if base_root else repo_root
		path_value = os.path.join(root, path_value)
	return os.path.abspath(path_value)


#============================================
def add_input_args(args: list, input_flag: str, input_path: str) -> list:
	"""
	Append input arguments if provided.

	Args:
		args (list): Existing arguments.
		input_flag (str): Input flag (example: -y).
		input_path (str): Input path.

	Returns:
		list: Updated arguments.
	"""
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


#============================================
def ensure_parent_dir(path_value: str):
	"""
	Ensure the parent directory exists.

	Args:
		path_value (str): File path to ensure parent for.
	"""
	parent_dir = os.path.dirname(path_value)
	if parent_dir and not os.path.isdir(parent_dir):
		os.makedirs(parent_dir, exist_ok=True)


#============================================
def log_line(log_path: str, message: str):
	"""
	Append a log line with a timestamp.

	Args:
		log_path (str): Path to the log file.
		message (str): Log message.
	"""
	if not log_path:
		return
	ensure_parent_dir(log_path)
	timestamp = datetime.datetime.now().isoformat()
	with open(log_path, "a") as log_handle:
		log_handle.write(f"[{timestamp}] {message}\n")


#============================================
def load_tasks(config_path: str, bbq_config: dict) -> list:
	"""
	Load tasks from CSV config.

	Args:
		config_path (str): Path to CSV config.
		bbq_config (dict): BBQ config with aliases.

	Returns:
		list: List of task dictionaries.
	"""
	if not os.path.isfile(config_path):
		raise FileNotFoundError(f"Config file not found: {config_path}")

	repo_root = os.getcwd()
	paths_config = bbq_config.get("paths", {}) if isinstance(bbq_config, dict) else {}
	path_aliases = resolve_alias_map(paths_config)
	path_aliases["repo_root"] = repo_root
	script_aliases_raw = bbq_config.get("script_aliases", {}) if isinstance(bbq_config, dict) else {}
	script_aliases = {}
	if isinstance(script_aliases_raw, dict):
		for alias_key, alias_value in script_aliases_raw.items():
			if not isinstance(alias_value, str):
				continue
			script_aliases[alias_key] = expand_text(alias_value, path_aliases)
	defaults = bbq_config.get("defaults", {}) if isinstance(bbq_config, dict) else {}
	default_input_flag = ""
	if isinstance(defaults, dict):
		default_input_flag = (defaults.get("input_flag") or "").strip()
	if not default_input_flag:
		default_input_flag = "-y"
	base_root = (path_aliases.get("bp_root") or "").strip()

	tasks = []
	with open(config_path, newline="") as csv_handle:
		reader = csv.DictReader(csv_handle)
		for row in reader:
			script_raw = (row.get("script") or "").strip()
			flags_raw = (row.get("flags") or "").strip()
			input_raw = (row.get("input") or "").strip()
			output_raw = (row.get("output") or "").strip()
			chapter_raw = (row.get("chapter") or "").strip()
			topic_raw = (row.get("topic") or "").strip()
			output_file_raw = (row.get("output_file") or "").strip()
			program_raw = (row.get("program") or "").strip()

			if not script_raw:
				continue

			script_raw = resolve_script_alias(script_raw, script_aliases)
			script_path = normalize_path(script_raw, repo_root, base_root, path_aliases)
			if not output_raw and output_file_raw:
				output_parts = ["site_docs"]
				if chapter_raw:
					output_parts.append(chapter_raw)
				if topic_raw:
					output_parts.append(topic_raw)
				output_parts.append(output_file_raw)
				output_raw = os.path.join(*output_parts)
			output_path = normalize_path(output_raw, repo_root, "", path_aliases)
			program_value = program_raw if program_raw else "python3"
			flags_raw = expand_text(flags_raw, path_aliases)
			args_list = shlex.split(flags_raw) if flags_raw else []
			if input_raw:
				input_flag = default_input_flag
				if os.path.basename(input_raw) == input_raw:
					script_basename = os.path.basename(script_path)
					if script_basename in INPUT_SCRIPT_BASENAMES:
						input_raw = os.path.join(os.path.dirname(script_path), input_raw)
				input_path = normalize_path(input_raw, repo_root, base_root, path_aliases)
				args_list = add_input_args(args_list, input_flag, input_path)
			flags_raw = shlex.join(args_list) if args_list else ""

			workdir_path = os.getcwd()

			task = {
				"script": script_path,
				"flags_raw": flags_raw,
				"args": args_list,
				"output": output_path,
				"output_raw": output_raw,
				"program": program_value,
				"workdir": workdir_path,
			}
			tasks.append(task)

	return tasks


#============================================
def load_state(state_path: str) -> dict:
	"""
	Load state CSV into a dict keyed by output path.

	Args:
		state_path (str): Path to state CSV.

	Returns:
		dict: State entries keyed by output path.
	"""
	state = {}
	if not os.path.isfile(state_path):
		return state

	with open(state_path, newline="") as csv_handle:
		reader = csv.DictReader(csv_handle)
		for row in reader:
			output_raw = (row.get("output") or "").strip()
			output_key = expand_path(output_raw)
			if not output_key:
				continue
			state[output_key] = row

	return state


#============================================
def write_state(state_path: str, entries: list):
	"""
	Write state CSV entries.

	Args:
		state_path (str): Path to state CSV.
		entries (list): List of state entry dicts.
	"""
	if not state_path:
		return

	fieldnames = [
		"output",
		"script",
		"flags",
		"program",
		"signature",
		"git_commit",
		"git_dirty",
		"script_mtime",
		"output_mtime",
		"last_run",
		"status",
		"notes",
	]

	ensure_parent_dir(state_path)
	with open(state_path, "w", newline="") as csv_handle:
		writer = csv.DictWriter(csv_handle, fieldnames=fieldnames)
		writer.writeheader()
		for entry in entries:
			writer.writerow(entry)


#============================================
def build_signature(task: dict) -> str:
	"""
	Build a signature string for a task.

	Args:
		task (dict): Task dictionary.

	Returns:
		str: Signature string.
	"""
	parts = [
		task.get("program", ""),
		task.get("script", ""),
		task.get("flags_raw", ""),
		task.get("output", ""),
	]
	signature_value = "||".join(parts)
	return signature_value


#============================================
def get_file_mtime(path_value: str) -> float:
	"""
	Get a file modification time.

	Args:
		path_value (str): File path.

	Returns:
		float: Modification time or 0.0.
	"""
	if not path_value:
		return 0.0
	if not os.path.isfile(path_value):
		return 0.0
	mtime_value = os.path.getmtime(path_value)
	return mtime_value


#============================================
def run_command(cmd_list: list, cwd: str, env_override: dict = None) -> subprocess.CompletedProcess:
	"""
	Run a subprocess command.

	Args:
		cmd_list (list): Command list.
		cwd (str): Working directory.

	Returns:
		subprocess.CompletedProcess: Completed process.
	"""
	env = None
	if env_override is not None:
		env = os.environ.copy()
		env.update(env_override)
	elif "PYTHONPATH" in os.environ:
		env = os.environ.copy()
	proc = subprocess.run(
		cmd_list,
		cwd=cwd,
		env=env,
		text=True,
		capture_output=True,
		check=False,
	)
	return proc


#============================================
def get_repo_root(script_path: str, git_available: bool) -> str:
	"""
	Get git repository root for a script.

	Args:
		script_path (str): Script path.
		git_available (bool): True if git is available.

	Returns:
		str: Repository root path or empty string.
	"""
	if not git_available:
		return ""
	script_dir = os.path.dirname(script_path)
	cmd_list = ["git", "-C", script_dir, "rev-parse", "--show-toplevel"]
	proc = run_command(cmd_list, script_dir)
	if proc.returncode != 0:
		return ""
	repo_root = proc.stdout.strip()
	return repo_root


#============================================
def get_git_commit(repo_root: str, script_path: str, git_available: bool) -> str:
	"""
	Get latest git commit hash for a script.

	Args:
		repo_root (str): Repository root path.
		script_path (str): Script path.
		git_available (bool): True if git is available.

	Returns:
		str: Commit hash or empty string.
	"""
	if not git_available or not repo_root:
		return ""
	relative_path = os.path.relpath(script_path, repo_root)
	cmd_list = [
		"git",
		"-C",
		repo_root,
		"log",
		"-1",
		"--format=%H",
		"--",
		relative_path,
	]
	proc = run_command(cmd_list, repo_root)
	if proc.returncode != 0:
		return ""
	commit_hash = proc.stdout.strip()
	return commit_hash


#============================================
def get_git_dirty(repo_root: str, script_path: str, git_available: bool) -> bool:
	"""
	Check if a script has uncommitted changes.

	Args:
		repo_root (str): Repository root path.
		script_path (str): Script path.
		git_available (bool): True if git is available.

	Returns:
		bool: True if dirty.
	"""
	if not git_available or not repo_root:
		return False
	relative_path = os.path.relpath(script_path, repo_root)
	cmd_list = [
		"git",
		"-C",
		repo_root,
		"status",
		"--porcelain",
		"--",
		relative_path,
	]
	proc = run_command(cmd_list, repo_root)
	if proc.returncode != 0:
		return False
	is_dirty = bool(proc.stdout.strip())
	return is_dirty


#============================================
def build_command(task: dict) -> list:
	"""
	Build the command list for a task.

	Args:
		task (dict): Task dictionary.

	Returns:
		list: Command list.
	"""
	program_value = task.get("program")
	if not program_value:
		program_value = "python3"
	script_path = task.get("script")
	args_list = task.get("args", [])
	cmd_list = [program_value]
	if script_path:
		cmd_list.append(script_path)
	cmd_list.extend(args_list)
	return cmd_list


#============================================
def task_label(task: dict, output_path: str, cmd_list: list) -> str:
	"""
	Build a display label for a task.

	Args:
		task (dict): Task dictionary.
		output_path (str): Output path.
		cmd_list (list): Command list.

	Returns:
		str: Label string.
	"""
	if output_path:
		label_value = os.path.basename(output_path)
		return label_value
	if task.get("script"):
		label_value = os.path.basename(task["script"])
		return label_value
	if cmd_list:
		label_value = cmd_list[0]
		return label_value
	label_value = "task"
	return label_value


#============================================
def move_output_if_needed(output_path: str, workdir: str) -> bool:
	"""
	Move output file into place if it exists in workdir.

	Args:
		output_path (str): Expected output path.
		workdir (str): Working directory.

	Returns:
		bool: True if output exists or was moved.
	"""
	if not output_path:
		return True
	if os.path.isfile(output_path):
		return True
	base_name = os.path.basename(output_path)
	if not base_name:
		return False
	candidate = os.path.join(workdir, base_name)
	if os.path.isfile(candidate):
		ensure_parent_dir(output_path)
		shutil.move(candidate, output_path)
		return True
	return False


#============================================
#============================================
def should_run_task(
	task: dict,
	state_entry: dict,
	force: bool,
	output_exists: bool,
	output_mtime: float,
	git_commit: str,
	git_dirty: bool,
	script_mtime: float,
	signature_value: str,
) -> tuple:
	"""
	Decide whether a task should run.

	Args:
		task (dict): Task dictionary.
		state_entry (dict): State entry for task.
		force (bool): Force rebuild.
		output_exists (bool): Output existence.
		output_mtime (float): Output mtime.
		git_commit (str): Git commit hash.
		git_dirty (bool): Git dirty flag.
		script_mtime (float): Script mtime.
		signature_value (str): Task signature.

	Returns:
		tuple: (should_run, reasons list)
	"""
	reasons = []
	should_run = False

	if force:
		reasons.append("forced")

	if not output_exists:
		reasons.append("output missing")

	if not reasons:
		if not state_entry:
			reasons.append("state missing")
		else:
			stored_signature = (state_entry.get("signature") or "").strip()
			stored_commit = (state_entry.get("git_commit") or "").strip()
			stored_mtime_raw = (state_entry.get("script_mtime") or "").strip()
			stored_mtime = float(stored_mtime_raw) if stored_mtime_raw else 0.0

			if stored_signature != signature_value:
				reasons.append("task changed")
			if git_commit and stored_commit != git_commit:
				reasons.append("git updated")
			if git_dirty:
				reasons.append("git dirty")
			if not git_commit and script_mtime > stored_mtime:
				reasons.append("script mtime updated")
			if output_exists and script_mtime > output_mtime:
				reasons.append("output older than script")

	if reasons:
		should_run = True

	result = (should_run, reasons)
	return result


#============================================
def run_task(task: dict, log_path: str, pythonpath_value: str) -> bool:
	"""
	Run a task command and move output if needed.

	Args:
		task (dict): Task dictionary.
		log_path (str): Log path.

	Returns:
		bool: True on success.
	"""
	output_path = task.get("output", "")
	workdir = task.get("workdir") or os.getcwd()
	cmd_list = build_command(task)
	label_value = task_label(task, output_path, cmd_list)
	env_override = None
	if pythonpath_value:
		env_override = {"PYTHONPATH": pythonpath_value}

	log_line(log_path, f"START {label_value} -> {output_path or 'N/A'}")
	log_line(log_path, f"CMD   {' '.join(cmd_list)} (cwd={workdir})")

	try:
		proc = run_command(cmd_list, workdir, env_override=env_override)
	except FileNotFoundError as exc:
		log_line(log_path, f"LAUNCH ERROR {label_value}: {exc}")
		return False

	if proc.stdout:
		log_line(log_path, f"STDOUT {label_value}:\n{proc.stdout.rstrip()}")
	if proc.stderr:
		log_line(log_path, f"STDERR {label_value}:\n{proc.stderr.rstrip()}")

	if proc.returncode != 0:
		log_line(log_path, f"EXIT {label_value} -> {proc.returncode}")
		return False

	if output_path:
		moved_ok = move_output_if_needed(output_path, workdir)
		if not moved_ok:
			log_line(log_path, f"ERROR expected output not found: {output_path}")
			return False

	log_line(log_path, f"EXIT {label_value} -> 0")
	return True


#============================================
def format_skip_message(label_value: str, reasons: list) -> str:
	"""
	Format skip message with reasons.

	Args:
		label_value (str): Task label.
		reasons (list): Skip reasons.

	Returns:
		str: Formatted message.
	"""
	reason_text = ", ".join(reasons)
	message = f"SKIP  {label_value} ({reason_text})"
	return message


#============================================
def main():
	args = parse_args()
	bbq_config = load_bbq_config(args.bbq_config)
	if args.bbq_config and not os.path.isfile(args.bbq_config):
		print(f"Config not found: {args.bbq_config}")
	paths_config = bbq_config.get("paths", {}) if isinstance(bbq_config, dict) else {}
	path_aliases = resolve_alias_map(paths_config)
	pythonpath_value = build_pythonpath(path_aliases)
	tasks = load_tasks(args.config_path, bbq_config)
	if not tasks:
		print("No tasks found in config.")
		return

	git_available = bool(shutil.which("git"))
	state = load_state(args.state_path)
	state_entries = []
	failures = 0

	for task in tasks:
		script_path = task.get("script", "")
		output_path = task.get("output", "")
		signature_value = build_signature(task)
		label_value = task_label(task, output_path, build_command(task))

		output_exists = os.path.isfile(output_path) if output_path else False
		output_mtime = get_file_mtime(output_path)
		output_mtime_after = output_mtime

		if not script_path or not os.path.isfile(script_path):
			print(f"ERROR missing script: {script_path}")
			entry = {
				"output": output_path,
				"script": script_path,
				"flags": task.get("flags_raw", ""),
				"program": task.get("program", ""),
				"signature": signature_value,
				"git_commit": "",
				"git_dirty": "0",
				"script_mtime": "0",
				"output_mtime": str(output_mtime),
				"last_run": datetime.datetime.now().isoformat(),
				"status": "missing",
				"notes": "script missing",
			}
			state_entries.append(entry)
			failures += 1
			continue

		script_mtime = get_file_mtime(script_path)

		repo_root = get_repo_root(script_path, git_available)
		git_commit = get_git_commit(repo_root, script_path, git_available)
		git_dirty = get_git_dirty(repo_root, script_path, git_available)

		state_entry = state.get(output_path, {})
		should_run, reasons = should_run_task(
			task,
			state_entry,
			args.force,
			output_exists,
			output_mtime,
			git_commit,
			git_dirty,
			script_mtime,
			signature_value,
		)

		status_value = "skipped"
		notes_value = ""
		if should_run:
			notes_value = ", ".join(reasons)
			if args.dry_run:
				cmd_text = " ".join(build_command(task))
				print(f"DRY-RUN {label_value}: {cmd_text}")
				status_value = "dry-run"
			else:
				print(f"RUN   {label_value}")
				ok = run_task(task, args.log_path, pythonpath_value)
				if ok:
					status_value = "updated"
					output_mtime_after = get_file_mtime(output_path)
				else:
					status_value = "failed"
					failures += 1
		else:
			if args.verbose:
				message = format_skip_message(label_value, ["up to date"])
				print(message)

		entry = {
			"output": output_path,
			"script": script_path,
			"flags": task.get("flags_raw", ""),
			"program": task.get("program", ""),
			"signature": signature_value,
			"git_commit": git_commit,
			"git_dirty": "1" if git_dirty else "0",
			"script_mtime": str(script_mtime),
			"output_mtime": str(output_mtime_after),
			"last_run": datetime.datetime.now().isoformat(),
			"status": status_value,
			"notes": notes_value,
		}
		state_entries.append(entry)

	write_state(args.state_path, state_entries)

	if failures:
		print(f"Completed with {failures} failure(s).")
		return
	print("All tasks completed successfully.")


#============================================
if __name__ == "__main__":
	main()

"""Execution and timing behavior for configured BBQ tasks."""

import argparse
from collections.abc import Callable
import os
import shlex
import shutil
import subprocess
import time

from bioproblems_site.bbq_config import (
	get_missing_input_message,
	get_missing_script_message,
)
from bioproblems_site.bbq_outputs import (
	cleanup_dry_run_output,
	count_output_lines_path,
	log_error,
	log_line,
	move_output_candidate,
	resolve_generated_output,
	resolve_output_workdir_recent,
)
from bioproblems_site.git_paths import display_path

# ANSI colors for concise CLI feedback
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"
def color(text: str, code: str) -> str:
	return f"{code}{text}{COLOR_RESET}"


#============================================
def format_elapsed_time(elapsed_seconds: float) -> str:
	"""Format one task duration for concise terminal output."""
	if elapsed_seconds < 60:
		return f"{elapsed_seconds:.2f}s"
	minutes = int(elapsed_seconds // 60)
	seconds = elapsed_seconds % 60
	return f"{minutes}m {seconds:05.2f}s"


#============================================
def get_slowest_task_timings(timing_records: list[dict], limit: int = 10) -> list[dict]:
	"""Return task timing records from slowest to fastest."""
	sorted_records = sorted(
		timing_records,
		key=lambda record: record["elapsed_seconds"],
		reverse=True,
	)
	return sorted_records[:limit]


#============================================
#============================================
def print_slowest_task_timings(timing_records: list[dict]) -> None:
	"""Print up to ten slowest tasks from one CSV run."""
	slowest_records = get_slowest_task_timings(timing_records)
	if not slowest_records:
		return
	print(color(f"Slowest {len(slowest_records)} tasks:", COLOR_CYAN))
	for timing_record in slowest_records:
		duration = format_elapsed_time(timing_record["elapsed_seconds"])
		print(
			f"  {duration:>10}  {timing_record['label']} "
			f"({timing_record['status']})"
		)


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


#============================================
def output_file_signature(output_path: str) -> tuple[int, int, int] | None:
	"""Return the modification identity needed to detect a direct task output."""
	if not output_path or not os.path.isfile(output_path):
		return None
	output_stat = os.stat(output_path)
	return output_stat.st_mtime_ns, output_stat.st_size, output_stat.st_ino


#============================================
def recent_task_output_candidate(
	output_path: str,
	workdir: str,
	start_time: float,
	original_signature: tuple[int, int, int] | None,
) -> str:
	"""Prefer a destination changed by this run over a recent stale basename."""
	current_signature = output_file_signature(output_path)
	if current_signature is not None and current_signature != original_signature:
		return output_path
	candidate_path = resolve_output_workdir_recent(output_path, workdir, start_time)
	if candidate_path and os.path.abspath(candidate_path) != os.path.abspath(output_path):
		return candidate_path
	return ""


#============================================
def validate_task_output(
	candidate_path: str,
	output_path: str,
	max_questions: int | None,
) -> tuple[int, str]:
	"""Reject missing, empty, or oversized outputs before replacing prior files."""
	if not candidate_path or not os.path.isfile(candidate_path):
		return 0, (
			"Generated output not found: "
			f"{display_path(candidate_path or output_path)}"
		)
	line_count = count_output_lines_path(candidate_path)
	if line_count == 0:
		return 0, (
			"Generated BBQ output is empty; refusing to publish "
			f"{display_path(output_path)}."
		)
	if max_questions and line_count > max_questions:
		return line_count, (
			f"Output has {line_count} lines; expected <= {max_questions}. "
			f"Refusing to publish {display_path(output_path)}."
		)
	return line_count, ""


#============================================
def discard_unpublished_task_output(candidate_path: str, output_path: str, log_path: str) -> None:
	"""Remove a rejected working copy while leaving the configured output alone."""
	if not candidate_path or os.path.abspath(candidate_path) == os.path.abspath(output_path):
		return
	cleanup_dry_run_output(candidate_path, log_path)


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
	) -> None:
		self.log_path = log_path
		self.error_log_path = error_log_path
		self.allow_cleanup = allow_cleanup
		self.pythonpath_value = pythonpath_value


def run_pgml_generation(task: dict, log_path: str, pythonpath_value: str = "") -> bool:
	pgml_info = task.get("pgml_info")
	if not pgml_info:
		return True
	pgml_script = pgml_info.get("script", "")
	input_path = pgml_info.get("input_path", "")
	pgml_suffix = pgml_info.get("suffix", "")
	pgml_extension = pgml_info.get("extension", "pgml")
	pgml_output_dir = pgml_info.get("output_dir", "")
	if not pgml_script or not os.path.isfile(pgml_script):
		log_line(log_path, f"PGML ERROR: configured script not found: {pgml_script}")
		return False
	if not input_path or not os.path.isfile(input_path):
		log_line(log_path, f"PGML ERROR: configured input not found: {input_path}")
		return False
	if not isinstance(pgml_output_dir, str) or not pgml_output_dir:
		log_line(log_path, "PGML ERROR: configured output directory is missing")
		return False
	yaml_basename = os.path.splitext(os.path.basename(input_path))[0]
	output_filename = f"{yaml_basename}{pgml_suffix}.{pgml_extension}"
	output_path = os.path.join(pgml_output_dir, output_filename)
	try:
		os.makedirs(pgml_output_dir, exist_ok=True)
	except OSError as exc:
		log_line(log_path, f"PGML ERROR: could not create output directory: {exc}")
		return False
	cmd = ["python3", pgml_script, "-y", input_path, "-o", output_path]
	log_line(log_path, f"PGML CMD  {' '.join(cmd)}")
	env_override = None
	if pythonpath_value:
		env_override = os.environ.copy()
		env_override["PYTHONPATH"] = pythonpath_value
	try:
		proc = subprocess.run(
			cmd,
			text=True,
			capture_output=True,
			check=False,
			env=env_override,
		)
	except OSError as exc:
		log_line(log_path, f"PGML ERROR: launch failed: {exc}")
		return False
	if proc.returncode != 0:
		log_line(log_path, f"PGML FAILED (exit {proc.returncode}): {output_filename}")
		if proc.stderr:
			log_line(log_path, f"PGML STDERR:\n{proc.stderr.rstrip()}")
		return False
	if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
		log_line(log_path, f"PGML ERROR: generator produced no output: {output_filename}")
		return False
	log_line(log_path, f"PGML OK: {output_path}")
	print(color(f"  PGML {output_filename}", COLOR_GREEN))
	return True


#============================================
def copy_sister_pgml(task: dict, log_path: str) -> bool:
	"""Copy a sister PGML/PG file from the source script directory to downloads.

	Looks for a .pgml or .pg file in the same directory as the task's source
	script whose basename matches the script (exact or normalized). Copies the
	first match to {output_dir}/downloads/.

	Args:
		task: Task dictionary with 'script', 'output_dir', and optionally 'pgml_info'.
		log_path: Path to the run log file.

	Returns:
		True on success or benign skip, False on copy failure.
	"""
	# skip if task already has pgml_info (handled by run_pgml_generation)
	if task.get("pgml_info"):
		return True
	script_path = task.get("script", "")
	if not script_path or not os.path.isfile(script_path):
		return True
	source_dir = os.path.dirname(script_path)
	script_stem = os.path.splitext(os.path.basename(script_path))[0]
	# gather all .pgml and .pg files in the source directory
	sister_candidates = []
	for filename in os.listdir(source_dir):
		if filename.endswith(".pgml") or filename.endswith(".pg"):
			sister_candidates.append(filename)
	if not sister_candidates:
		return True
	# try exact match first (.pgml before .pg)
	matched_file = None
	for ext in (".pgml", ".pg"):
		candidate = script_stem + ext
		if candidate in sister_candidates:
			matched_file = candidate
			break
	# try normalized match: lowercase and replace hyphens with underscores
	if matched_file is None:
		normalized_stem = script_stem.lower().replace("-", "_")
		for candidate in sister_candidates:
			candidate_stem = os.path.splitext(candidate)[0]
			normalized_candidate = candidate_stem.lower().replace("-", "_")
			if normalized_candidate == normalized_stem:
				matched_file = candidate
				break
	# no match found
	if matched_file is None:
		log_line(log_path, f"PGML COPY SKIP: no sister file for {os.path.basename(script_path)}")
		return True
	# build source and destination paths
	source_pgml = os.path.join(source_dir, matched_file)
	output_dir = task.get("output_dir", "")
	if not output_dir:
		log_line(log_path, f"PGML COPY SKIP: no output_dir for {os.path.basename(script_path)}")
		return True
	downloads_dir = os.path.join(output_dir, "downloads")
	try:
		os.makedirs(downloads_dir, exist_ok=True)
	except OSError as exc:
		log_line(log_path, f"PGML COPY ERROR: cannot create {downloads_dir}: {exc}")
		return False
	dest_pgml = os.path.join(downloads_dir, matched_file)
	try:
		shutil.copy2(source_pgml, dest_pgml)
		if os.path.getsize(dest_pgml) == 0:
			log_line(log_path, f"PGML COPY ERROR: sister file is empty: {source_pgml}")
			return False
	except OSError as exc:
		log_line(log_path, f"PGML COPY ERROR: {exc}")
		print(color(f"  PGML COPY FAIL {matched_file}", COLOR_RED))
		return False
	log_line(log_path, f"PGML COPY OK: {dest_pgml}")
	print(color(f"  PGML COPY {matched_file}", COLOR_GREEN))
	return True


#============================================
def _complete_pgml_outputs(task: dict, log_path: str, pythonpath_value: str) -> None:
	"""Attempt optional PGML generation and copying."""
	run_pgml_generation(task, log_path, pythonpath_value)
	copy_sister_pgml(task, log_path)


#============================================
def _run_task_capture(
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
	original_output_signature = output_file_signature(output_path)
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
	except OSError as exc:
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

	explicit_output = bool(output_path)
	if explicit_output:
		candidate_path = recent_task_output_candidate(
			output_path,
			workdir,
			start_time,
			original_output_signature,
		)
		if not candidate_path:
			message = f"Generated output not found: {output_path}"
			log_line(log_path, f"ERROR {message}")
			log_error(error_log_path, label, message, cmd_list=cmd)
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

	line_count, output_error = validate_task_output(
		candidate_path,
		output_path,
		max_questions,
	)
	if output_error:
		discard_unpublished_task_output(candidate_path, output_path, log_path)
		log_line(log_path, f"ERROR {output_error}")
		log_error(
			error_log_path,
			label,
			output_error,
			stdout_text=proc.stdout,
			stderr_text=proc.stderr,
			cmd_list=cmd,
		)
		return False, proc.stdout, output_error, line_count

	if move_output:
		moved_ok = move_output_candidate(candidate_path, output_path)
		if not moved_ok:
			message = f"Could not publish generated output: {output_path}"
			log_line(log_path, f"ERROR {message}")
			log_error(error_log_path, label, message, cmd_list=cmd)
			return False, proc.stdout, proc.stderr, line_count
	if not move_output:
		if allow_cleanup:
			discard_unpublished_task_output(candidate_path, output_path, log_path)
		else:
			log_line(log_path, "SKIP CLEANUP (PYTHONPATH not set)")
	if move_output:
		_complete_pgml_outputs(task, log_path, pythonpath_value)
	return True, proc.stdout, proc.stderr, line_count


#============================================
def run_task_capture(
	task: dict,
	log_path: str,
	move_output: bool,
	allow_cleanup: bool = True,
	pythonpath_value: str = "",
	error_log_path: str = "",
) -> tuple:
	"""Run a captured task and return its result."""
	return _run_task_capture(
		task,
		log_path,
		move_output,
		allow_cleanup,
		pythonpath_value,
		error_log_path,
	)


#============================================
def _run_task(
	task: dict,
	log_path: str,
	index: int,
	total: int,
	move_output: bool = True,
	allow_cleanup: bool = True,
	pythonpath_value: str = "",
	error_log_path: str = "",
	output_callback: Callable[[str, str], None] | None = None,
) -> bool:
	output_path = task.get("output", "")
	workdir = "."
	max_questions = task.get("max_questions")
	start_time = time.time()
	original_output_signature = output_file_signature(output_path)

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
	except OSError as exc:  # subprocess launch failure
		print(color(f"FAILED to launch {label}: {exc}", COLOR_RED))
		log_line(log_path, f"LAUNCH ERROR {label}: {exc}")
		log_error(error_log_path, label, f"Launch error: {exc}", cmd_list=cmd)
		return False
	if output_callback:
		if proc.stdout:
			output_callback("stdout", proc.stdout)
		if proc.stderr:
			output_callback("stderr", proc.stderr)

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

	# Validate the generated candidate before it can replace an existing output.
	explicit_output = bool(output_path)
	candidate_path = ""
	if explicit_output:
		candidate_path = recent_task_output_candidate(
			output_path,
			workdir,
			start_time,
			original_output_signature,
		)
		if not candidate_path:
			message = f"Generated output not found: {output_path}"
			print(color(f"FAILED {label}: {message}", COLOR_RED))
			log_line(log_path, f"ERROR: {message}")
			log_error(
				error_log_path,
				label,
				message,
				stdout_text=proc.stdout,
				stderr_text=proc.stderr,
				cmd_list=cmd,
			)
			return False
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

	line_count, output_error = validate_task_output(
		candidate_path,
		output_path,
		max_questions,
	)
	if output_error:
		discard_unpublished_task_output(candidate_path, output_path, log_path)
		print(color(f"FAILED {label}: {output_error}", COLOR_RED))
		log_line(log_path, f"ERROR: {output_error}")
		log_error(
			error_log_path,
			label,
			output_error,
			stdout_text=proc.stdout,
			stderr_text=proc.stderr,
			cmd_list=cmd,
		)
		return False

	if move_output:
		moved_ok = move_output_candidate(candidate_path, output_path)
		if not moved_ok:
			message = f"Could not publish generated output: {output_path}"
			print(color(f"FAILED {label}: {message}", COLOR_RED))
			log_line(log_path, f"ERROR: {message}")
			log_error(error_log_path, label, message, cmd_list=cmd)
			return False
		log_line(log_path, f"MOVED output to {output_path}")
	else:
		log_line(log_path, f"SKIP MOVE {label} -> {candidate_path}")
	if not move_output:
		if allow_cleanup:
			discard_unpublished_task_output(candidate_path, output_path, log_path)
		else:
			log_line(log_path, "SKIP CLEANUP (PYTHONPATH not set)")

	if move_output:
		_complete_pgml_outputs(task, log_path, pythonpath_value)

	# Show line count in output
	if line_count > 0:
		print(color(f"DONE  {label} ({line_count} lines)", COLOR_GREEN))
	else:
		print(color(f"DONE  {label}", COLOR_GREEN))
	log_line(log_path, f"EXIT {label} -> 0")
	return True


#============================================
def run_task(
	task: dict,
	log_path: str,
	index: int,
	total: int,
	move_output: bool = True,
	allow_cleanup: bool = True,
	pythonpath_value: str = "",
	error_log_path: str = "",
	output_callback: Callable[[str, str], None] | None = None,
) -> bool:
	"""Run one task and return its success status."""
	return _run_task(
		task,
		log_path,
		index,
		total,
		move_output,
		allow_cleanup,
		pythonpath_value,
		error_log_path,
		output_callback,
	)


#============================================
def run_tasks_plain(
	tasks: list[dict[str, object]],
	args: argparse.Namespace,
	run_context: RunContext,
) -> int:
	"""Run prepared tasks without the Textual interface."""
	total = len(tasks)
	log_line(run_context.log_path, f"=== RUN START ({total} tasks) ===")
	failures = 0
	timing_records: list[dict[str, object]] = []
	for index, task in enumerate(tasks, start=1):
		command = build_command(task)
		label = task_label(task, index, task.get("output", ""), command)
		task_start = time.perf_counter()
		if args.dry_run:
			print(color(f"[{index}/{total}] DRY-RUN {' '.join(command)}", COLOR_CYAN))
			ok = run_task(
				task,
				run_context.log_path,
				index,
				total,
				move_output=False,
				allow_cleanup=run_context.allow_cleanup,
				pythonpath_value=run_context.pythonpath_value,
				error_log_path=run_context.error_log_path,
			)
		else:
			ok = run_task(
				task,
				run_context.log_path,
				index,
				total,
				allow_cleanup=run_context.allow_cleanup,
				pythonpath_value=run_context.pythonpath_value,
				error_log_path=run_context.error_log_path,
			)
		elapsed_seconds = time.perf_counter() - task_start
		timing_record = {
			"label": label,
			"elapsed_seconds": elapsed_seconds,
			"status": "DONE" if ok else "FAILED",
		}
		timing_records.append(timing_record)
		log_line(
			run_context.log_path,
			f"TIME {label} -> {elapsed_seconds:.3f}s",
		)
		print(color(f"  TIME  {format_elapsed_time(elapsed_seconds)}", COLOR_CYAN))
		if not ok:
			failures += 1
	log_line(run_context.log_path, f"=== RUN END (failures={failures}) ===")
	print_slowest_task_timings(timing_records)
	if failures:
		log_paths = list(dict.fromkeys(
			path for path in (run_context.log_path, run_context.error_log_path) if path
		))
		log_details = f" See {' and '.join(log_paths)}." if log_paths else ""
		print(color(
			f"Completed with {failures} failure(s).{log_details}",
			COLOR_RED,
		))
		return 1
	print(color("All tasks completed successfully.", COLOR_GREEN))
	return 0

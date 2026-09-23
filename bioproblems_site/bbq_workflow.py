"""Configured BBQ selection, local stale checks, and change reporting."""

import dataclasses
import os
from pathlib import Path
import random
import time
from collections.abc import Iterator
from functools import partial

import bioproblems_site.bbq_config as bbq_config
import bioproblems_site.bbq_outputs as bbq_outputs
import bioproblems_site.bbq_runner as bbq_runner
import bioproblems_site.metadata as metadata_module
import bioproblems_site.git_paths as git_paths
from bioproblems_site.build_contracts import BuildChanges, BuildScope, TaskBuildResult, TopicRef
from bioproblems_site.build_progress import BuildProgress


REPO_ROOT = Path(git_paths.get_repo_root())
DEFAULT_SETTINGS_PATH = REPO_ROOT / "bbq_settings.yml"
DEFAULT_TASK_DIR = REPO_ROOT / "task_files"


#============================================
class TaskOwnershipError(RuntimeError):
	"""Raised when repository task files cannot establish safe cleanup ownership."""


#============================================
def load_task_owned_patterns() -> dict[str, list[tuple[set[str], tuple[str, ...], set[str]]]]:
	"""Load every current CSV task as topic-local BBQ source ownership patterns.

	Returns:
		dict: Real topic directory paths mapped to automatic prefix/suffix and
			explicit-basename ownership patterns.
	"""
	if not DEFAULT_TASK_DIR.is_dir():
		raise TaskOwnershipError(
			f"Task inventory directory not found: {git_paths.display_path(DEFAULT_TASK_DIR)}"
		)
	task_files = sorted(DEFAULT_TASK_DIR.glob("*.csv"))
	if not task_files:
		raise TaskOwnershipError(
			f"No task CSV files found in {git_paths.display_path(DEFAULT_TASK_DIR)}"
		)
	try:
		settings = bbq_config.load_bbq_config(str(DEFAULT_SETTINGS_PATH))
		subjects, _nav_order = metadata_module.load_topics_metadata()
		alias_map = metadata_module.build_topic_alias_map(subjects)
	except (OSError, TypeError, ValueError) as exc:
		raise TaskOwnershipError(f"Cannot establish task ownership: {exc}") from exc
	topic_patterns: dict[str, list[tuple[set[str], tuple[str, ...], set[str]]]] = {}
	for task_file in task_files:
		try:
			loaded_tasks = bbq_config.load_tasks_csv(str(task_file), settings, alias_map)
		except (OSError, TypeError, ValueError) as exc:
			raise TaskOwnershipError(
				f"Cannot establish task ownership from "
				f"{git_paths.display_path(task_file)}: {exc}"
			) from exc
		for task in loaded_tasks:
			script_path = task.get("script", "")
			if not isinstance(script_path, str) or not script_path or not os.path.isfile(script_path):
				displayed_script = (
					git_paths.display_path(script_path)
					if isinstance(script_path, str)
					else repr(script_path)
				)
				raise TaskOwnershipError(
					f"Cannot establish task ownership from "
					f"{git_paths.display_path(task_file)}: generator script is missing "
					f"({displayed_script!r})"
				)
			input_path = task.get("input_path", "")
			if isinstance(input_path, str) and input_path and not os.path.isfile(input_path):
				raise TaskOwnershipError(
					f"Cannot establish task ownership from "
					f"{git_paths.display_path(task_file)}: task input is missing "
					f"({git_paths.display_path(input_path)})"
				)
			output_dir = task["output_dir"]
			if not isinstance(output_dir, str):
				raise TaskOwnershipError(
					"BBQ task output directory must be a string in "
					f"{git_paths.display_path(task_file)}"
				)
			output_value = task["output"]
			if not isinstance(output_value, str):
				raise TaskOwnershipError(
					"BBQ task output path must be a string in "
					f"{git_paths.display_path(task_file)}"
				)
			prefixes: list[str] = []
			suffixes: tuple[str, ...] = ()
			explicit_basenames = {os.path.basename(output_value)} if output_value else set()
			if not explicit_basenames:
				prefixes, suffixes = bbq_outputs.build_output_patterns(task)
			if not explicit_basenames and not prefixes:
				row_number = task.get("_csv_row_number", "?")
				raise TaskOwnershipError(
					f"Cannot derive BBQ ownership for "
					f"{git_paths.display_path(task_file)}:{row_number}"
				)
			pattern = (set(prefixes), suffixes, explicit_basenames)
			topic_path = os.path.realpath(output_dir)
			topic_patterns.setdefault(topic_path, []).append(pattern)
	if not topic_patterns:
		raise TaskOwnershipError(
			f"Task inventory owns no BBQ outputs: {git_paths.display_path(DEFAULT_TASK_DIR)}"
		)
	return topic_patterns


#============================================
def _task_paths(task: dict[str, object]) -> set[Path]:
	"""Return known direct inputs and expected outputs for one configured task."""
	paths: set[Path] = set()
	for key in ("script", "input_path", "task_file", "settings_path", "output"):
		value = task.get(key, "")
		if isinstance(value, str) and value:
			paths.add(Path(value))
	return paths


#============================================
def expected_output_paths(task: dict[str, object]) -> set[Path]:
	"""Return explicit or currently discoverable configured task outputs."""
	output_value = task.get("output", "")
	if isinstance(output_value, str) and output_value:
		return {Path(output_value)}
	output_dir = task.get("output_dir", "")
	if not isinstance(output_dir, str) or not output_dir:
		return set()
	prefixes, suffixes = bbq_outputs.build_output_patterns(task)
	output_paths: set[Path] = set()
	for candidate_path in Path(output_dir).glob("bbq-*.txt"):
		if not any(candidate_path.name.startswith(prefix) for prefix in prefixes):
			continue
		if suffixes and not any(candidate_path.name.endswith(suffix) for suffix in suffixes):
			continue
		output_paths.add(candidate_path)
	return output_paths


#============================================
def _task_source_files(task: dict[str, object]) -> set[Path]:
	"""Return the BBQ question files produced or owned by one task row."""
	return {
		output_path
		for output_path in expected_output_paths(task)
		if output_path.name.startswith("bbq-") and output_path.name.endswith("-questions.txt")
	}


#============================================
def task_needs_run(task: dict[str, object], scope: BuildScope) -> bool:
	"""Check only the direct task configuration, source inputs, and outputs."""
	if scope.full:
		return True
	outputs = expected_output_paths(task)
	if not outputs:
		return True
	if any(not output_path.is_file() for output_path in outputs):
		return True
	input_mtimes = [path.stat().st_mtime for path in _task_paths(task) if path.is_file()]
	if not input_mtimes:
		return False
	newest_input = max(input_mtimes)
	stale = any(output_path.stat().st_mtime < newest_input for output_path in outputs)
	return stale


#============================================
def _task_ref(task: dict[str, object]) -> TopicRef:
	"""Build a subject-qualified topic reference from CSV-owned canonical data."""
	subject = task["subject"]
	topic = task["topic"]
	if not isinstance(subject, str) or not isinstance(topic, str):
		raise TypeError("BBQ task subject and topic must be canonical strings")
	return TopicRef(subject, topic)


#============================================
def _apply_task_selection(
		task_rows: list[list[dict[str, object]]],
		scope: BuildScope,
	) -> list[list[dict[str, object]]]:
	"""Shuffle and limit complete CSV rows before running their generators."""
	if scope.shuffle:
		random.shuffle(task_rows)
	if scope.limit is not None:
		return task_rows[:scope.limit]
	return task_rows


#============================================
def _load_scoped_task_rows(scope: BuildScope) -> list[list[dict[str, object]]]:
	"""Load canonical CSV rows, preserving tasks expanded from one source row."""
	settings = bbq_config.load_bbq_config(str(DEFAULT_SETTINGS_PATH))
	subjects, _nav_order = metadata_module.load_topics_metadata()
	if scope.subject is not None and scope.subject not in subjects:
		raise ValueError(f"Unknown subject {scope.subject!r}; expected one of {sorted(subjects)}")
	if scope.topic is not None:
		if scope.subject is None:
			raise ValueError("A topic filter requires a subject filter")
		valid_topics = {topic.key for topic in subjects[scope.subject].topics}
		if scope.topic not in valid_topics:
			raise ValueError(
				f"Unknown topic {scope.topic!r} for subject {scope.subject!r}; "
				f"expected one of {sorted(valid_topics)}"
			)
	alias_map = metadata_module.build_topic_alias_map(subjects)
	if scope.tasks_csv:
		task_files = [scope.tasks_csv]
	else:
		if not DEFAULT_TASK_DIR.is_dir():
			raise FileNotFoundError(
				"Task inventory directory not found: "
				f"{git_paths.display_path(DEFAULT_TASK_DIR)}"
			)
		task_files = sorted(DEFAULT_TASK_DIR.glob("*.csv"))
		if not task_files:
			raise ValueError(
				f"No task CSV files found in {git_paths.display_path(DEFAULT_TASK_DIR)}"
			)
	task_rows: list[list[dict[str, object]]] = []
	for task_file in task_files:
		if task_file is None:
			continue
		loaded_tasks = bbq_config.load_tasks_csv(str(task_file), settings, alias_map)
		current_row_number: int | None = None
		current_task_row: list[dict[str, object]] = []
		for task in loaded_tasks:
			task["task_file"] = str(task_file)
			task["settings_path"] = str(DEFAULT_SETTINGS_PATH)
			if scope.subject is not None and task["subject"] != scope.subject:
				continue
			if scope.topic is not None and task["topic"] != scope.topic:
				continue
			row_number = task["_csv_row_number"]
			if not isinstance(row_number, int):
				raise TypeError("CSV task row number must be an integer")
			if current_task_row and row_number != current_row_number:
				task_rows.append(current_task_row)
				current_task_row = []
			current_row_number = row_number
			current_task_row.append(task)
		if current_task_row:
			task_rows.append(current_task_row)
	return _apply_task_selection(task_rows, scope)


#============================================
def _load_scoped_tasks(scope: BuildScope) -> list[dict[str, object]]:
	"""Load selected task dictionaries in CSV row and generator order."""
	return [task for task_row in _load_scoped_task_rows(scope) for task in task_row]


#============================================
def _prepare_task(task: dict[str, object], scope: BuildScope) -> None:
	"""Apply the shared single-task max-question override when requested."""
	if scope.max_questions is None:
		return
	task_args = task["args"]
	if not isinstance(task_args, list):
		raise TypeError("BBQ task args must be a list")
	if "-x" not in task_args and "--max-questions" not in task_args:
		task.setdefault("extra_args", []).extend(["-x", str(scope.max_questions)])
	task["max_questions"] = scope.max_questions


#============================================
def configured_topics(scope: BuildScope) -> set[TopicRef]:
	"""Return canonical topics configured by the current task-file selection."""
	topics = {_task_ref(task) for task in _load_scoped_tasks(scope)}
	return topics


#============================================
def _task_row_label(task_row: list[dict[str, object]], topic_ref: TopicRef) -> str:
	"""Return a compact label for one selected CSV task row."""
	task = task_row[0]
	task_file = Path(str(task["task_file"])).name
	row_number = task["_csv_row_number"]
	label = f"{topic_ref.subject}/{topic_ref.topic} ({task_file}:{row_number})"
	return label


#============================================
def _report_command_output(
	progress: BuildProgress,
	row_index: int,
	task: dict[str, object],
	stream_name: str,
	output: str,
) -> None:
	"""Forward captured generator output to an optional build observer."""
	label = bbq_runner.task_label(
		task,
		row_index,
		task.get("output", ""),
		bbq_runner.build_command(task),
	)
	message = f"{stream_name.upper()} {label}:\n{output.rstrip()}"
	progress.emit("log", message=message)


#============================================
def iter_task_results(
	scope: BuildScope,
	progress: BuildProgress | None = None,
) -> Iterator[TaskBuildResult]:
	"""Run configured CSV rows lazily and yield each row before starting the next."""
	task_rows = _load_scoped_task_rows(scope)
	tasks = [task for task_row in task_rows for task in task_row]
	row_total = len(task_rows)
	if progress:
		selected_topics = {_task_ref(task_row[0]) for task_row in task_rows}
		row_labels = [
			_task_row_label(task_row, _task_ref(task_row[0]))
			for task_row in task_rows
		]
		progress.emit(
			"plan",
			task_rows=row_total,
			topics=len(selected_topics),
			row_labels=row_labels,
		)
	pending_task_ids = {
		id(task)
		for task in tasks
		if task_needs_run(task, scope)
	}
	pending_count = len(pending_task_ids)
	if scope.dry_run:
		for row_index, task_row in enumerate(task_rows, start=1):
			if progress:
				progress.check_cancelled()
			topic_ref = _task_ref(task_row[0])
			row_label = _task_row_label(task_row, topic_ref) if progress else ""
			row_needs_run = any(id(task) in pending_task_ids for task in task_row)
			source_files: set[Path] = set()
			changed_files: set[Path] = set()
			for task in task_row:
				source_files.update(_task_source_files(task))
				if id(task) in pending_task_ids:
					changed_files.update(expected_output_paths(task))
			if row_needs_run:
				print(f"[dry-run] BBQ {topic_ref.subject}/{topic_ref.topic}")
			if progress:
				progress.emit(
					"row_started",
					row=row_index,
					total=row_total,
					label=row_label,
				)
				if row_needs_run:
					progress.emit(
						"stage_started", phase="bbq", row=row_index, label=row_label,
					)
					progress.emit(
						"stage_completed", phase="bbq", row=row_index,
						label=row_label, duration=0.0, executed=False, planned=True,
					)
				else:
					progress.emit(
						"stage_skipped", phase="bbq", row=row_index, label=row_label,
						detail="up to date",
					)
			yield TaskBuildResult(
				topic_ref=topic_ref,
				source_files=source_files,
				changed_files=changed_files,
				needs_run=row_needs_run,
			)
		return
	if pending_count == 0:
		for row_index, task_row in enumerate(task_rows, start=1):
			if progress:
				progress.check_cancelled()
			topic_ref = _task_ref(task_row[0])
			row_label = _task_row_label(task_row, topic_ref) if progress else ""
			if progress:
				progress.emit(
					"row_started",
					row=row_index,
					total=row_total,
					label=row_label,
				)
				progress.emit(
					"stage_skipped", phase="bbq", row=row_index, label=row_label,
					detail="up to date",
				)
			yield TaskBuildResult(
				topic_ref=topic_ref,
				source_files=set().union(*(_task_source_files(task) for task in task_row)),
			)
		return
	settings = bbq_config.load_bbq_config(str(DEFAULT_SETTINGS_PATH))
	pythonpath_ok, pythonpath_message = bbq_config.check_pythonpath(settings)
	if not pythonpath_ok:
		raise RuntimeError(pythonpath_message)
	pythonpath_value = bbq_config.build_pythonpath(settings)
	log_path = "bbq_generation.log"
	error_log_path = log_path
	bbq_outputs.start_run_log(log_path)
	legacy_error_log_path = "bbq_generation_errors.log"
	if os.path.isfile(legacy_error_log_path):
		try:
			os.remove(legacy_error_log_path)
		except OSError as exc:
			print(f"WARNING: could not remove old error log {legacy_error_log_path}: {exc}")
	context = bbq_runner.RunContext(log_path, error_log_path, True, pythonpath_value)
	total = pending_count
	# The historical 199-question default belongs to an all-task batch.
	# A single selected CSV retains its generator-defined default.
	runner_scope = scope
	if (
		scope.subject is None
		and scope.tasks_csv is None
		and scope.limit is None
		and scope.max_questions is None
	):
		runner_scope = dataclasses.replace(scope, max_questions=199)
	pending_index = 0
	task_elapsed_total = 0.0
	for row_index, task_row in enumerate(task_rows, start=1):
		if progress:
			progress.check_cancelled()
		topic_ref = _task_ref(task_row[0])
		row_label = _task_row_label(task_row, topic_ref) if progress else ""
		if progress:
			progress.emit(
				"row_started",
				row=row_index,
				total=row_total,
				label=row_label,
			)
		row_needs_run = any(id(task) in pending_task_ids for task in task_row)
		changed_files: set[Path] = set()
		row_start = time.perf_counter()
		if progress:
			if row_needs_run:
				progress.emit(
					"stage_started", phase="bbq", row=row_index, label=row_label,
				)
			else:
				progress.emit(
					"stage_skipped", phase="bbq", row=row_index, label=row_label,
					detail="up to date",
				)
		for task in task_row:
			if id(task) not in pending_task_ids:
				continue
			if progress:
				progress.check_cancelled()
			pending_index += 1
			_prepare_task(task, runner_scope)
			before_outputs = expected_output_paths(task)
			if progress:
				progress.check_cancelled()
			task_start = time.perf_counter()
			try:
				ok = bbq_runner.run_task(
					task,
					log_path,
					pending_index,
					total,
					pythonpath_value=context.pythonpath_value,
					error_log_path=context.error_log_path,
					output_callback=(
						partial(_report_command_output, progress, row_index, task)
						if progress else None
					),
				)
			except Exception as error:
				if progress:
					progress.emit(
						"stage_failed",
						phase="bbq",
						row=row_index,
						label=row_label,
						duration=time.perf_counter() - row_start,
						detail=str(error),
					)
				raise
			elapsed_seconds = time.perf_counter() - task_start
			task_elapsed_total += elapsed_seconds
			average_task_seconds = task_elapsed_total / pending_index
			eta_seconds = average_task_seconds * (total - pending_index)
			print(
				f"  task time: {bbq_runner.format_elapsed_time(elapsed_seconds)}; "
				f"elapsed: {bbq_runner.format_elapsed_time(task_elapsed_total)}; "
				f"ETA: {bbq_runner.format_elapsed_time(eta_seconds)}"
			)
			bbq_outputs.log_line(
				log_path,
				f"TIME [{pending_index}/{total}] {topic_ref.subject}/{topic_ref.topic} "
				f"-> {elapsed_seconds:.3f}s",
			)
			if not ok:
				if progress:
					elapsed_seconds = time.perf_counter() - row_start
					progress.emit(
						"stage_failed", phase="bbq", row=row_index,
						label=row_label, duration=elapsed_seconds,
						detail="BBQ command failed",
					)
				raise RuntimeError(f"BBQ task failed for {topic_ref.subject}/{topic_ref.topic}")
			after_outputs = expected_output_paths(task)
			changed_files.update(before_outputs | after_outputs)
		source_files = set().union(*(_task_source_files(task) for task in task_row))
		if progress and row_needs_run:
			progress.emit(
				"stage_completed",
				phase="bbq",
				row=row_index,
				label=row_label,
				duration=time.perf_counter() - row_start,
				executed=True,
			)
		yield TaskBuildResult(
			topic_ref=topic_ref,
			source_files=source_files,
			changed_files=changed_files,
			needs_run=row_needs_run,
		)


#============================================
def run_if_needed(scope: BuildScope) -> BuildChanges:
	"""Run selected rows and aggregate their task-level build changes."""
	changed_topics: set[TopicRef] = set()
	changed_subjects: set[str] = set()
	changed_files: set[Path] = set()
	selected_topics: set[TopicRef] = set()
	for task_result in iter_task_results(scope):
		selected_topics.add(task_result.topic_ref)
		if not task_result.needs_run:
			continue
		changed_topics.add(task_result.topic_ref)
		changed_subjects.add(task_result.topic_ref.subject)
		changed_files.update(task_result.changed_files)
	return BuildChanges(changed_topics, changed_subjects, changed_files, selected_topics)

"""Configured BBQ selection, local stale checks, and change reporting."""

import dataclasses
import os
from pathlib import Path
import random

import bioproblems_site.bbq_config as bbq_config
import bioproblems_site.bbq_outputs as bbq_outputs
import bioproblems_site.bbq_runner as bbq_runner
import bioproblems_site.metadata as metadata_module
import bioproblems_site.git_paths as git_paths
from bioproblems_site.build_contracts import BuildChanges, BuildScope, TopicRef


REPO_ROOT = Path(git_paths.get_repo_root())
DEFAULT_SETTINGS_PATH = REPO_ROOT / "bbq_settings.yml"
DEFAULT_TASK_DIR = REPO_ROOT / "task_files"


#============================================
def load_task_owned_patterns() -> dict[str, list[tuple[set[str], tuple[str, ...], set[str]]]]:
	"""Load every current CSV task as topic-local BBQ source ownership patterns.

	Returns:
		dict: Real topic directory paths mapped to automatic prefix/suffix and
			explicit-basename ownership patterns.
	"""
	settings = bbq_config.load_bbq_config(str(DEFAULT_SETTINGS_PATH))
	subjects, _nav_order = metadata_module.load_topics_metadata()
	alias_map = metadata_module.build_topic_alias_map(subjects)
	topic_patterns: dict[str, list[tuple[set[str], tuple[str, ...], set[str]]]] = {}
	for task_file in sorted(DEFAULT_TASK_DIR.glob("*.csv")):
		loaded_tasks = bbq_config.load_tasks_csv(str(task_file), settings, alias_map)
		for task in loaded_tasks:
			output_dir = task["output_dir"]
			if not isinstance(output_dir, str):
				raise TypeError("BBQ task output directory must be a string")
			output_value = task["output"]
			if not isinstance(output_value, str):
				raise TypeError("BBQ task output path must be a string")
			prefixes: list[str] = []
			suffixes: tuple[str, ...] = ()
			explicit_basenames = {os.path.basename(output_value)} if output_value else set()
			if not explicit_basenames:
				prefixes, suffixes = bbq_outputs.build_output_patterns(task)
			pattern = (set(prefixes), suffixes, explicit_basenames)
			topic_path = os.path.realpath(output_dir)
			topic_patterns.setdefault(topic_path, []).append(pattern)
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
		tasks: list[dict[str, object]],
		scope: BuildScope,
	) -> list[dict[str, object]]:
	"""Apply optional randomization before the development task limit."""
	if scope.shuffle:
		random.shuffle(tasks)
	if scope.limit is not None:
		return tasks[:scope.limit]
	return tasks


#============================================
def _load_scoped_tasks(scope: BuildScope) -> list[dict[str, object]]:
	"""Load canonical task dictionaries inside the requested public scope."""
	settings = bbq_config.load_bbq_config(str(DEFAULT_SETTINGS_PATH))
	subjects, _nav_order = metadata_module.load_topics_metadata()
	if scope.subject is not None and scope.subject not in subjects:
		raise ValueError(f"Unknown subject {scope.subject!r}; expected one of {sorted(subjects)}")
	alias_map = metadata_module.build_topic_alias_map(subjects)
	task_files = [scope.tasks_csv] if scope.tasks_csv else sorted(DEFAULT_TASK_DIR.glob("*.csv"))
	tasks: list[dict[str, object]] = []
	for task_file in task_files:
		if task_file is None:
			continue
		loaded_tasks = bbq_config.load_tasks_csv(str(task_file), settings, alias_map)
		for task in loaded_tasks:
			task["task_file"] = str(task_file)
			task["settings_path"] = str(DEFAULT_SETTINGS_PATH)
			if scope.subject is None or task["subject"] == scope.subject:
				tasks.append(task)
	return _apply_task_selection(tasks, scope)


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
def run_if_needed(scope: BuildScope) -> BuildChanges:
	"""Run stale BBQ tasks or report their planned subject-qualified scope."""
	tasks = _load_scoped_tasks(scope)
	selected_topics = {_task_ref(task) for task in tasks}
	pending_tasks = [task for task in tasks if task_needs_run(task, scope)]
	if scope.dry_run:
		planned_topics = {_task_ref(task) for task in pending_tasks}
		planned_subjects = {topic_ref.subject for topic_ref in planned_topics}
		planned_files = set().union(*(expected_output_paths(task) for task in pending_tasks))
		for task in pending_tasks:
			print(f"[dry-run] BBQ {_task_ref(task).subject}/{_task_ref(task).topic}")
		return BuildChanges(planned_topics, planned_subjects, planned_files, selected_topics)
	if not pending_tasks:
		return BuildChanges(selected_topics=selected_topics)
	settings = bbq_config.load_bbq_config(str(DEFAULT_SETTINGS_PATH))
	pythonpath_ok, pythonpath_message = bbq_config.check_pythonpath(settings)
	if not pythonpath_ok:
		raise RuntimeError(pythonpath_message)
	pythonpath_value = bbq_config.build_pythonpath(settings)
	log_path = "bbq_generation.log"
	error_log_path = "bbq_generation_errors.log"
	if os.path.isfile(error_log_path):
		os.remove(error_log_path)
	bbq_outputs.rotate_log(log_path)
	context = bbq_runner.RunContext(log_path, error_log_path, True, pythonpath_value)
	changed_topics: set[TopicRef] = set()
	changed_subjects: set[str] = set()
	changed_files: set[Path] = set()
	total = len(pending_tasks)
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
	for index, task in enumerate(pending_tasks, start=1):
		_prepare_task(task, runner_scope)
		before_outputs = expected_output_paths(task)
		ok = bbq_runner.run_task(
			task, log_path, index, total, pythonpath_value=context.pythonpath_value,
			error_log_path=context.error_log_path,
		)
		if not ok:
			raise RuntimeError(f"BBQ task failed for {_task_ref(task).subject}/{_task_ref(task).topic}")
		topic_ref = _task_ref(task)
		changed_topics.add(topic_ref)
		changed_subjects.add(topic_ref.subject)
		after_outputs = expected_output_paths(task)
		changed_files.update(before_outputs)
		changed_files.update(after_outputs)
	return BuildChanges(changed_topics, changed_subjects, changed_files, selected_topics)

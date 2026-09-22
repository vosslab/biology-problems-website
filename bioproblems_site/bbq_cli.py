"""Application-facing CLI for single-file and batch BBQ generation."""

import argparse
import math
import os
import random
import sys

import bioproblems_site.bbq_batch as bbq_batch
import bioproblems_site.bbq_tui as bbq_tui
from bioproblems_site.bbq_config import (
	build_pythonpath,
	check_pythonpath,
	find_settings_yaml,
	load_bbq_config,
	load_tasks_csv,
)
from bioproblems_site.bbq_outputs import log_line, rotate_log
from bioproblems_site.bbq_runner import RunContext, run_tasks_plain
from bioproblems_site import metadata


def add_arguments(subparsers: argparse._SubParsersAction) -> None:
	"""Add the ``bbq`` subcommand to the application parser."""
	parser = subparsers.add_parser(
		"bbq",
		description="Run configured biology problem generators from CSV.",
	)
	task_group = parser.add_mutually_exclusive_group(required=True)
	task_group.add_argument(
		"-t", "--tasks", dest="tasks_csv",
		help="Path to one task CSV file.",
	)
	task_group.add_argument(
		"-a", "--all-tasks", action="store_true",
		help="Run every task CSV in task_files/.",
	)
	task_group.add_argument(
		"--list-tasks", action="store_true",
		help="List task CSV files without running generators.",
	)
	parser.add_argument(
		"-s", "--settings", dest="settings_yaml", default="",
		help="Path to settings YAML (default: repository bbq_settings.yml).",
	)
	parser.add_argument(
		"-n", "--dry-run", dest="dry_run", action="store_true",
		help="Run commands but do not move generated outputs.",
	)
	parser.add_argument(
		"-F", "--flat", "--no-tui", dest="no_tui", action="store_true",
		help="Disable the Textual TUI interface.",
	)
	parser.add_argument(
		"-x", "--max-questions", dest="max_questions", type=int, default=None,
		help="Append -x N to all scripts; batch mode defaults to 199.",
	)
	parser.add_argument(
		"-l", "--limit", dest="limit", type=int,
		help="Maximum number of tasks to run.",
	)
	parser.add_argument(
		"-R", "--shuffle", dest="shuffle_tasks", action="store_true",
		help="Shuffle task order before applying --limit.",
	)


def _parser_error(args: argparse.Namespace, message: str) -> None:
	parser = getattr(args, "_root_parser", None)
	if parser is not None:
		parser.error(message)
	raise ValueError(message)


def run(args: argparse.Namespace) -> int:
	"""Run the selected BBQ workflow."""
	if args.list_tasks:
		return bbq_batch.list_task_files()
	if args.all_tasks:
		return bbq_batch.run_all_task_files(args)
	if args.max_questions is not None and args.max_questions <= 0:
		_parser_error(args, "--max-questions must be positive")
	if args.limit is not None and args.limit <= 0:
		_parser_error(args, "--limit must be positive")

	log_path = os.path.join(os.getcwd(), "bbq_generation.log")
	error_log_path = os.path.join(os.getcwd(), "bbq_generation_errors.log")
	if os.path.isfile(error_log_path):
		os.remove(error_log_path)
	duplicates_count = math.ceil(args.max_questions * 1.1) if args.max_questions else 99
	settings_path = find_settings_yaml(args.settings_yaml)
	if not settings_path:
		print("Warning: bbq_settings.yml not found, aliases will not expand.")
	settings = load_bbq_config(settings_path)
	pythonpath_ok, pythonpath_message = check_pythonpath(settings)
	if not pythonpath_ok:
		if pythonpath_message:
			print(pythonpath_message)
		return 1
	pythonpath_value = build_pythonpath(settings)
	topic_subjects, _topic_nav_order = metadata.load_topics_metadata()
	topic_alias_map = metadata.build_topic_alias_map(topic_subjects)
	tasks = load_tasks_csv(args.tasks_csv, settings, topic_alias_map)
	if args.shuffle_tasks:
		random.shuffle(tasks)
	if args.limit is not None:
		tasks = tasks[:args.limit]
	if args.max_questions is not None:
		for task in tasks:
			task_args = task.get("args", [])
			if "-x" not in task_args and "--max-questions" not in task_args:
				task.setdefault("extra_args", []).extend(["-x", str(args.max_questions)])
			task["max_questions"] = args.max_questions
	for task in tasks:
		task_args = task.get("args", [])
		if "-d" not in task_args and "--duplicates" not in task_args:
			task.setdefault("extra_args", []).extend(["-d", str(duplicates_count)])
	if not tasks:
		print("No tasks found in config.")
		return 0
	if rotate_log(log_path):
		print(f"Rotated previous log to {log_path}.1")
	if pythonpath_message:
		log_line(log_path, pythonpath_message)
	run_context = RunContext(
		log_path,
		error_log_path,
		pythonpath_ok,
		pythonpath_value,
	)
	if not args.no_tui and sys.stdout.isatty():
		return bbq_tui.run_app(tasks, args, run_context)
	return run_tasks_plain(tasks, args, run_context)

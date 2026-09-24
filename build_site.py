#!/usr/bin/env python3
"""Build and update the Biology Problems website content."""

import argparse
from pathlib import Path
import sys

import bioproblems_site.build_contracts as build_contracts
import bioproblems_site.build_coordinator as build_coordinator
import bioproblems_site.bbq_runner as bbq_runner
import bioproblems_site.git_paths as git_paths
import bioproblems_site.llm_helpers as llm_helpers
import bioproblems_site.metadata as metadata


#============================================
def build_parser() -> argparse.ArgumentParser:
	"""Build the compact public parser for the unified workflow."""
	parser = argparse.ArgumentParser(
		description="Build and update the Biology Problems website content.",
		add_help=False,
		epilog=(
			"This command generates BBQ content and updates self-tests, topic pages,\n"
			"downloads, indexes, and navigation. Then run MkDocs to build the final\n"
			"static site.\n\n"
			"Examples:\n"
			"  ./build_site.py\n"
			"  ./build_site.py -S genetics\n"
			"  ./build_site.py -S genetics -T topic01\n"
			"  ./build_site.py -S genetics -T 'Genetic Disorders'\n"
			"  ./build_site.py --task task_files/genetics_tasks1.csv\n"
			"  ./build_site.py -x 99\n"
			"  ./build_site.py -R -l 1\n"
			"  ./build_site.py -b codex\n"
			"  ./build_site.py -n\n"
			"  ./build_site.py -S genetics -T topic01 --rebuild"
		),
		formatter_class=argparse.RawDescriptionHelpFormatter,
	)
	parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
	parser.add_argument(
		"-S", "--subject", dest="subject", metavar="SUBJECT",
		help="Build only one subject, for example genetics.",
	)
	parser.add_argument(
		"-T", "--topic", dest="topic", metavar="TOPIC",
		help="Build one topic by key, alias, or title within --subject.",
	)
	# Remove the previous plural spelling after 2026-12-31.
	parser.add_argument(
		"-t", "--task", "--tasks", dest="task_file", metavar="TASK_FILE",
		help="Use one task CSV from task_files/ instead of all task files.",
	)
	parser.add_argument(
		"-l", "--limit", dest="limit", metavar="N", type=int,
		help="Run at most N CSV task rows.",
	)
	parser.add_argument(
		"-R", "--shuffle", dest="shuffle", action="store_true",
		help="Shuffle CSV task rows before applying --limit.",
	)
	parser.add_argument(
		"-n", "--dry-run", dest="dry_run", action="store_true",
		help="Show what would be rebuilt without changing files.",
	)
	output_group = parser.add_mutually_exclusive_group()
	output_group.add_argument(
		"--cli", dest="cli", action="store_true",
		help="Use plain output, even when stdin and stdout are interactive terminals.",
	)
	output_group.add_argument(
		"--tui", dest="tui", action="store_true",
		help="Open the Textual dashboard; requires interactive stdin and stdout.",
	)
	parser.add_argument(
		"-F", "--rebuild", dest="full", action="store_true",
		help=(
			"Force regeneration within the selected scope; without filters, "
			"rebuild all configured tasks and topics."
		),
	)
	parser.add_argument(
		"--full", dest="full", action="store_true", help=argparse.SUPPRESS,
	)
	parser.add_argument(
		"-b", "--backend", dest="backend",
		choices=llm_helpers.LLM_BACKENDS,
		default=llm_helpers.DEFAULT_LLM_BACKEND,
		metavar="BACKEND",
		help="Use Ollama, Codex, or Claude for generated page titles (default: ollama).",
	)
	parser.add_argument(
		"-m", "--model", dest="model",
		metavar="MODEL",
		help="Use a specific model with the selected title-generation backend.",
	)
	parser.add_argument(
		"-x", "--max-questions", dest="max_questions", metavar="N", type=int,
		help="Set the common per-task maximum where rows do not define -x (default: 50).",
	)
	return parser


#============================================
def _normalize_topic_title(title: str) -> str:
	"""Normalize display-title whitespace and casing for CLI matching."""
	return " ".join(title.split()).casefold()


#============================================
def _resolve_topic_filter(subject: metadata.Subject, topic_reference: str) -> str:
	"""Resolve a topic key, metadata alias, or display title to its canonical key."""
	cleaned_reference = " ".join(topic_reference.split())
	for topic in subject.topics:
		if topic.key == cleaned_reference:
			return topic.key
	for topic in subject.topics:
		if topic.alias == cleaned_reference:
			return topic.key
	title_matches = [
		topic
		for topic in subject.topics
		if _normalize_topic_title(topic.title) == _normalize_topic_title(cleaned_reference)
	]
	if len(title_matches) == 1:
		return title_matches[0].key
	if len(title_matches) > 1:
		keys = sorted(topic.key for topic in title_matches)
		raise ValueError(
			f"Topic title {topic_reference!r} is ambiguous for {subject.key!r}; "
			f"use one of {keys}"
		)
	raise ValueError(
			f"Unknown topic {topic_reference!r} for subject {subject.key!r}; "
			"use a canonical topic key, its metadata alias, or its title"
	)


#============================================
def _scope_from_args(args: argparse.Namespace) -> build_contracts.BuildScope:
	"""Validate parsed arguments and construct the repository-local build scope."""
	if args.limit is not None and args.limit <= 0:
		raise ValueError("--limit must be positive")
	if args.max_questions is not None and args.max_questions <= 0:
		raise ValueError("--max-questions must be positive")
	if args.topic is not None:
		if args.subject is None:
			raise ValueError("--topic requires --subject")
		subjects, _nav_order = metadata.load_topics_metadata()
		if args.subject not in subjects:
			raise ValueError(
				f"Unknown subject {args.subject!r}; expected one of {sorted(subjects)}"
			)
		topic = _resolve_topic_filter(subjects[args.subject], args.topic)
	else:
		topic = None
	tasks_csv = None
	if args.task_file:
		repo_root = Path(git_paths.get_repo_root())
		task_dir = repo_root / "task_files"
		tasks_csv = Path(args.task_file)
		if not tasks_csv.is_absolute():
			tasks_csv = repo_root / tasks_csv
		tasks_csv = tasks_csv.resolve()
		if task_dir not in tasks_csv.parents or tasks_csv.suffix != ".csv":
			raise ValueError("--task must name a CSV inside task_files/")
		if not tasks_csv.is_file():
			raise FileNotFoundError(
				f"Task CSV not found: {git_paths.display_path(tasks_csv)}"
			)
	scope = build_contracts.BuildScope(
		subject=args.subject,
		topic=topic,
		tasks_csv=tasks_csv,
		limit=args.limit,
		shuffle=args.shuffle,
		dry_run=args.dry_run,
		full=args.full,
		max_questions=args.max_questions,
		backend=args.backend,
		model=args.model,
	)
	return scope


#============================================
def parse_scope(arguments: list[str] | None = None) -> build_contracts.BuildScope:
	"""Parse public arguments and validate their repository-local scope."""
	args = build_parser().parse_args(arguments)
	return _scope_from_args(args)


#============================================
def main(arguments: list[str] | None = None) -> int:
	"""Run the selected unified build and return its process status."""
	args = build_parser().parse_args(arguments)
	try:
		scope = _scope_from_args(args)
	except (FileNotFoundError, ValueError) as error:
		build_parser().error(str(error))
	interactive = sys.stdin.isatty() and sys.stdout.isatty()
	if args.tui and not interactive:
		build_parser().error("--tui requires interactive stdin and stdout.")
	if args.tui or (not args.cli and interactive):
		import bioproblems_site.bbq_tui as bbq_tui

		return bbq_tui.run_app(scope)
	report = build_coordinator.build_site(scope)
	for stage_name, stage_seconds in report.stage_seconds.items():
		stage_files = report.stage_files.get(stage_name, set())
		stage_duration = bbq_runner.format_elapsed_time(stage_seconds)
		print(f"{stage_name}: {len(stage_files)} file(s) in {stage_duration}")
	total_duration = bbq_runner.format_elapsed_time(report.elapsed_seconds)
	print(f"total: {total_duration}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

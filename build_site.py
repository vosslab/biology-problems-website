#!/usr/bin/env python3
"""Build and update the Biology Problems website content."""

import argparse
from pathlib import Path

import bioproblems_site.build_contracts as build_contracts
import bioproblems_site.build_coordinator as build_coordinator
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
			"  ./build_site.py --task task_files/genetics_tasks1.csv\n"
			"  ./build_site.py -R -l 1\n"
			"  ./build_site.py -b codex\n"
			"  ./build_site.py -n\n"
			"  ./build_site.py -F"
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
		help="Build one canonical topic within --subject, for example topic01.",
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
	parser.add_argument(
		"-F", "--full", dest="full", action="store_true",
		help="Rebuild everything in the selected scope, even if up to date.",
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
	parser.add_argument("--max-questions", type=int, help=argparse.SUPPRESS)
	return parser


#============================================
def parse_scope(arguments: list[str] | None = None) -> build_contracts.BuildScope:
	"""Parse public arguments and validate their repository-local scope."""
	args = build_parser().parse_args(arguments)
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
		valid_topics = {topic.key for topic in subjects[args.subject].topics}
		if args.topic not in valid_topics:
			raise ValueError(
				f"Unknown topic {args.topic!r} for subject {args.subject!r}; "
				f"expected one of {sorted(valid_topics)}"
			)
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
			raise FileNotFoundError(f"Task CSV not found: {tasks_csv}")
	scope = build_contracts.BuildScope(
		subject=args.subject,
		topic=args.topic,
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
def main(arguments: list[str] | None = None) -> int:
	"""Run the selected unified build and return its process status."""
	try:
		scope = parse_scope(arguments)
	except (FileNotFoundError, ValueError) as error:
		build_parser().error(str(error))
	report = build_coordinator.build_site(scope)
	for stage_name, stage_files in report.stage_files.items():
		print(f"{stage_name}: {len(stage_files)} file(s)")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

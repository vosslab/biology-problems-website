"""Argument handling and orchestration for the site-generation command."""

# Short form used for argparse -h (the module docstring is used for
# in-editor help and is fine being longer; argparse gets this block).
_CLI_DESCRIPTION = (
	"Regenerate subject indexes, topic pages, and the mkdocs.yml nav block. "
	"Default: fast subject-indexes + nav run. "
	"Use -T to rebuild topic pages; self-tests rotate by default on -T "
	"(use --no-selftests to skip). "
	"Use -H to force-regenerate every self-test from its BBQ source "
	"(standalone, no index.md rewrite or LLM). "
	"Use -G with -T to also create missing download artifact files."
)

import argparse

# local repo modules
import bioproblems_site.pipeline as pipeline
import bioproblems_site.llm_helpers as llm_helpers
import bioproblems_site.metadata as metadata
import bioproblems_site.topic_aliases as topic_aliases


def add_arguments(subparsers: argparse._SubParsersAction) -> None:
	"""Add the ``pages`` subcommand to the application parser."""
	parser = subparsers.add_parser("pages", description=_CLI_DESCRIPTION)
	# Value-taking filters (lowercase short flags).
	parser.add_argument(
		"-s", "--subject", dest="subject_filter",
		help="Limit generation to one subject.",
	)
	parser.add_argument(
		"-t", "--topic", dest="topic_filter",
		help="Limit generation to one topic.",
	)
	# Build-axis flags (uppercase short flags to avoid filter collision).
	parser.add_argument(
		"-S", "--subject-indexes", dest="subject_indexes", action="store_true",
		help="Regenerate subject index.md pages and the mkdocs.yml nav block.",
	)
	parser.add_argument(
		"-T", "--topic-pages", dest="topic_pages", action="store_true",
		help="Regenerate topic??/index.md pages.",
	)
	parser.add_argument(
		"-G", "--generate-downloads", dest="generate_downloads",
		action="store_true",
		help="Also create missing download artifact files while "
			"rebuilding topic pages. Requires --topic-pages (-T).",
	)
	parser.add_argument(
		"-H", "--selftests", dest="run_selftests", action="store_true",
		help="Regenerate every self-test HTML from its bbq-*.txt source via "
			"qti-package-maker (treats all as stale). Standalone pass: does "
			"not rewrite index.md or use the LLM. Honors -s/--subject and "
			"-t/--topic filters.",
	)
	parser.add_argument(
		"--no-selftests", dest="regenerate_selftests", action="store_false",
		help="Reuse existing self-test HTML for fast -T iteration "
			"(a missing self-test file is still built).",
	)
	parser.add_argument(
		"--full", dest="full", action="store_true",
		help="Convenience alias for subject indexes, topic pages, and "
			"download generation.",
	)
	# Run-mode toggles.
	parser.add_argument(
		"-n", "--dry-run", dest="dry_run", action="store_true",
		help="Print what would be written without touching any files.",
	)
	parser.add_argument(
		"-q", "--quiet", dest="verbose", action="store_false",
		help="Suppress per-file progress output.",
	)
	parser.add_argument(
		"-m", "--model", dest="model", type=str, default=None,
		help="Use this exact local Ollama model instead of gemma4:e4b.",
	)
	parser.set_defaults(verbose=True)
	parser.set_defaults(regenerate_selftests=True)


def run(args: argparse.Namespace) -> int:
	"""Run the selected page-generation workflow."""
	parser = getattr(args, "_root_parser", None)
	if args.full and (
		args.subject_indexes or args.topic_pages or args.generate_downloads
	):
		message = (
			"--full cannot be combined with --subject-indexes, "
			"--topic-pages, or --generate-downloads"
		)
		if parser is not None:
			parser.error(message)
		raise ValueError(message)
	if args.generate_downloads and not args.topic_pages:
		message = "--generate-downloads requires --topic-pages"
		if parser is not None:
			parser.error(message)
		raise ValueError(message)
	# Resolve the three normalized build bools. --full expands to all
	# three; a bare invocation defaults to the fast subject-index path.
	if args.full:
		subject_indexes = True
		topic_pages = True
		generate_downloads = True
	elif args.run_selftests and not args.subject_indexes and not args.topic_pages:
		# A bare -H runs only the standalone self-test pass; no
		# subject-index or topic-page work is implied.
		subject_indexes = False
		topic_pages = False
		generate_downloads = False
	elif not args.subject_indexes and not args.topic_pages:
		# Fast default: subject indexes + nav, no topic work.
		subject_indexes = True
		topic_pages = False
		generate_downloads = False
	else:
		subject_indexes = args.subject_indexes
		topic_pages = args.topic_pages
		generate_downloads = args.generate_downloads
	# Pre-flight: fail fast if the selected Ollama model is not installed.
	ollama_model = args.model if args.model else llm_helpers.DEFAULT_OLLAMA_MODEL
	if topic_pages:
		llm_helpers.validate_ollama_model(ollama_model)

	# Resolve topic filter if provided. Load metadata once to get the
	# alias map and subjects dict.
	subject_filter = args.subject_filter
	topic_filter = args.topic_filter
	if topic_filter:
		subjects, _ = metadata.load_topics_metadata()
		alias_map = metadata.build_topic_alias_map(subjects)
		subject_filter, topic_filter = topic_aliases.resolve_topic_filter(
			topic_filter, alias_map, subjects
		)

	pipeline.run(
		subject_filter=subject_filter,
		topic_filter=topic_filter,
		subject_indexes=subject_indexes,
		topic_pages=topic_pages,
		generate_downloads=generate_downloads,
		regenerate_selftests=args.regenerate_selftests,
		run_selftests=args.run_selftests,
		dry_run=args.dry_run,
		verbose=args.verbose,
		model=args.model,
	)
	return 0

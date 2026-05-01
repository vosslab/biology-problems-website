#!/usr/bin/env python3

"""Single page-generation entrypoint for biology-problems-website.

Real logic lives in bioproblems_site.pipeline.
"""

# Short form used for argparse -h (the module docstring is used for
# in-editor help and is fine being longer; argparse gets this block).
_CLI_DESCRIPTION = (
	"Regenerate subject indexes, topic pages, and the mkdocs.yml nav block. "
	"Default: fast subject-indexes + nav run. "
	"Use -T to rebuild topic pages. "
	"Use -G with -T to also create missing download artifact files."
)

# Standard Library
import argparse

# local repo modules
import bioproblems_site.pipeline as pipeline
import bioproblems_site.llm_helpers as llm_helpers
import bioproblems_site.metadata as metadata
import bioproblems_site.topic_aliases as topic_aliases


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description=_CLI_DESCRIPTION)
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
		"-O", "--ollama", dest="use_ollama", action="store_true",
		help="Use Ollama instead of Apple Intelligence (auto-selects model by RAM).",
	)
	parser.add_argument(
		"-m", "--model", dest="model", type=str, default=None,
		help="Use Ollama with this exact local model (implies --ollama).",
	)
	parser.set_defaults(verbose=True)
	args = parser.parse_args()
	# --full is a convenience alias; combining it with the lower-level
	# build flags is ambiguous, so reject.
	if args.full and (
		args.subject_indexes or args.topic_pages or args.generate_downloads
	):
		parser.error(
			"--full cannot be combined with --subject-indexes, "
			"--topic-pages, or --generate-downloads"
		)
	# Download generation has no meaning without topic-page rendering.
	if args.generate_downloads and not args.topic_pages:
		parser.error("--generate-downloads requires --topic-pages")
	return args


def main() -> None:
	args = parse_args()
	# Resolve the three normalized build bools. --full expands to all
	# three; a bare invocation defaults to the fast subject-index path.
	if args.full:
		subject_indexes = True
		topic_pages = True
		generate_downloads = True
	elif not args.subject_indexes and not args.topic_pages:
		# Fast default: subject indexes + nav, no topic work.
		subject_indexes = True
		topic_pages = False
		generate_downloads = False
	else:
		subject_indexes = args.subject_indexes
		topic_pages = args.topic_pages
		generate_downloads = args.generate_downloads
	# --model implies --ollama; collapse to a single boolean for downstream callers.
	use_ollama = args.use_ollama or (args.model is not None)
	# Pre-flight: fail fast if the requested Ollama model is not installed.
	if args.model:
		llm_helpers.validate_ollama_model(args.model)

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
		dry_run=args.dry_run,
		verbose=args.verbose,
		model=args.model,
		use_ollama=use_ollama,
	)


if __name__ == "__main__":
	main()

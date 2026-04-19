#!/usr/bin/env python3

"""Single page-generation entrypoint for biology-problems-website.

Regenerates subject indexes, topic pages, and the mkdocs.yml nav block
from topics_metadata.yml + on-disk topic folders. Real logic lives in
bioproblems_site.pipeline.
"""

# Standard Library
import argparse

# local repo modules
import bioproblems_site.pipeline as pipeline
import bioproblems_site.llm_helpers as llm_helpers


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("-s", "--subject", dest="subject_filter")
	parser.add_argument("-t", "--topic", dest="topic_filter")
	scope = parser.add_mutually_exclusive_group()
	scope.add_argument("--indexes-only", dest="indexes_only", action="store_true")
	scope.add_argument("--topics-only", dest="topics_only", action="store_true")
	parser.add_argument(
		"--adopt-existing", dest="adopt_existing", action="store_true",
		help="Allow first-write overwrite of hand-authored subject index.md.",
	)
	parser.add_argument("-n", "--dry-run", dest="dry_run", action="store_true")
	parser.add_argument("-q", "--quiet", dest="verbose", action="store_false")
	parser.add_argument(
		"-O", "--ollama", dest="use_ollama", action="store_true",
		help="Use Ollama instead of Apple Intelligence (auto-selects model by RAM).",
	)
	parser.add_argument(
		"-m", "--model", dest="model", type=str, default=None,
		help="Use Ollama with this exact local model (implies --ollama).",
	)
	parser.set_defaults(verbose=True)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	# --model implies --ollama; collapse to a single boolean for downstream callers.
	use_ollama = args.use_ollama or (args.model is not None)
	# Pre-flight: fail fast if the requested Ollama model is not installed.
	if args.model:
		llm_helpers.validate_ollama_model(args.model)
	pipeline.run(
		subject_filter=args.subject_filter,
		topic_filter=args.topic_filter,
		indexes_only=args.indexes_only,
		topics_only=args.topics_only,
		adopt_existing=args.adopt_existing,
		dry_run=args.dry_run,
		verbose=args.verbose,
		model=args.model,
		use_ollama=use_ollama,
	)


if __name__ == "__main__":
	main()

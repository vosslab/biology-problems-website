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
	parser.set_defaults(verbose=True)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	pipeline.run(**vars(args))


if __name__ == "__main__":
	main()

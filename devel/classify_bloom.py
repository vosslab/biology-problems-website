#!/usr/bin/env python3
"""Developer maintenance: refresh Bloom labels or regenerate the coverage report.

Normal build_site.py runs already classify missing filenames.
Run from the repository root with python3 -m devel.classify_bloom.
"""

import argparse
from pathlib import Path

import bioproblems_site.bloom as bloom
import bioproblems_site.bloom_evidence as evidence
import bioproblems_site.bloom_report as report
import bioproblems_site.git_paths as git_paths


#============================================
def main() -> None:
	"""Keep exploratory maintenance explicit while ordinary builds classify new filenames."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("-a", "--action", dest="action",
		choices=("classify", "refresh", "report"), default="classify")
	parser.add_argument("-f", "--filenames", dest="filenames", nargs="+",
		help="Restrict refresh to exact BBQ basenames; default refreshes every visible bank")
	mode = parser.add_mutually_exclusive_group()
	mode.add_argument("-n", "--dry-run", dest="dry_run", action="store_true")
	mode.add_argument("-w", "--write", dest="dry_run", action="store_false")
	parser.set_defaults(dry_run=False)
	args = parser.parse_args()
	root = Path(git_paths.get_repo_root())
	names = {entry.source_path.name for entry in evidence.entries(root)}
	if args.filenames and (args.action != "refresh" or not set(args.filenames) <= names):
		parser.error("--filenames requires refresh and exact filenames in the current catalog")
	refresh = set(args.filenames) if args.filenames else names
	if args.action != "report":
		bloom.classify(root, refresh=refresh if args.action == "refresh" else None,
			dry_run=args.dry_run)
	if not args.dry_run:
		report.write(root)
		print("Coverage: docs/BLOOM_COVERAGE.md; run build_site.py -I to render site metadata.")


if __name__ == "__main__":
	main()

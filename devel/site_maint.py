#!/usr/bin/env python3
"""Maintainer command surface for repository-owned site utilities."""

import argparse
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
	sys.path.insert(0, str(REPO_ROOT))

from bioproblems_site import biomacromolecule_data, deletion_wordbank, scanner, topics_csv
from bioproblems_site.git_paths import get_repo_root


def _repo_path(repo_root: Path, value: str) -> Path:
	path = Path(value)
	return path if path.is_absolute() else repo_root / path


def run_topics_csv(args: argparse.Namespace) -> int:
	repo_root = Path(get_repo_root())
	output = Path(args.output)
	if not output.is_absolute():
		output = Path.cwd() / output
	topics_csv.dump_topics_to_csv(
		_repo_path(repo_root, args.metadata),
		_repo_path(repo_root, args.mkdocs),
		output,
	)
	print(f"Wrote {output}")
	return 0


def run_count_questions(_args: argparse.Namespace) -> int:
	repo_root = Path(get_repo_root())
	for line_count, path in scanner.count_bbq_lines(repo_root / "site_docs"):
		print(f"{line_count:>6} {path}")
	return 0


def run_build_biomacromolecule_data(_args: argparse.Namespace) -> int:
	return biomacromolecule_data.write_js(Path(get_repo_root()))


def run_build_deletion_wordbank(args: argparse.Namespace) -> int:
	repo_root = Path(get_repo_root())
	source = _repo_path(repo_root, args.source) if args.source else None
	return deletion_wordbank.write_js(repo_root, source_path=source, word_len=args.length)


def run_reset_generated(_args: argparse.Namespace) -> int:
	repo_root = Path(get_repo_root())
	pathspecs = [
		":(glob)site_docs/**/downloads/*",
		":(glob)site_docs/*/topic*/index.md",
		":(glob)site_docs/**/bbq-*-questions.txt",
		"site_docs/assets/data/selftest_question_manifest.json",
		"site_docs/sitemap.md",
	]
	subprocess.run(["git", "checkout", "--", *pathspecs], cwd=repo_root, check=True)
	subprocess.run(
		["git", "clean", "-f", "--", ":(glob)site_docs/**/downloads/*", ":(glob)site_docs/**/bbq-*-questions.txt"],
		cwd=repo_root,
		check=True,
	)
	print("Reset generated site content.")
	return 0


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description=__doc__)
	subparsers = parser.add_subparsers(dest="command", required=True)
	topics_parser = subparsers.add_parser("topics-csv", help="Export topic metadata to CSV.")
	topics_parser.add_argument("-o", "--output", default="topics_reference.csv")
	topics_parser.add_argument("-m", "--metadata", default="topics_metadata.yml")
	topics_parser.add_argument("-k", "--mkdocs", default="mkdocs.yml")
	subparsers.add_parser("count-questions", help="Count lines in generated BBQ text files.")
	subparsers.add_parser(
		"build-biomacromolecule-data",
		help="Build the biomacromolecule puzzle data JavaScript.",
	)
	wordbank_parser = subparsers.add_parser(
		"build-deletion-wordbank",
		help="Build the deletion-mutants word bank JavaScript.",
	)
	wordbank_parser.add_argument("--length", type=int, default=5)
	wordbank_parser.add_argument("--source", default="")
	subparsers.add_parser("reset-generated", help="Restore generated site content from Git.")
	return parser


def main() -> None:
	args = build_parser().parse_args()
	dispatch = {
		"topics-csv": run_topics_csv,
		"count-questions": run_count_questions,
		"build-biomacromolecule-data": run_build_biomacromolecule_data,
		"build-deletion-wordbank": run_build_deletion_wordbank,
		"reset-generated": run_reset_generated,
	}
	exit_code = dispatch[args.command](args)
	if exit_code:
		raise SystemExit(exit_code)


if __name__ == "__main__":
	main()

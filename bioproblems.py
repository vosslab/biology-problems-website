#!/usr/bin/env python3
"""Primary application CLI for site pages and BBQ question generation."""

import argparse

from bioproblems_site import bbq_cli, pages_cli


def build_parser() -> argparse.ArgumentParser:
	"""Build the application parser and its two workflow subcommands."""
	parser = argparse.ArgumentParser(description=__doc__)
	subparsers = parser.add_subparsers(dest="command", required=True)
	pages_cli.add_arguments(subparsers)
	bbq_cli.add_arguments(subparsers)
	return parser


def main() -> None:
	"""Parse the selected workflow and return its exit status."""
	parser = build_parser()
	args = parser.parse_args()
	args._root_parser = parser
	dispatch = {"pages": pages_cli.run, "bbq": bbq_cli.run}
	exit_code = dispatch[args.command](args)
	if exit_code:
		raise SystemExit(exit_code)


if __name__ == "__main__":
	main()

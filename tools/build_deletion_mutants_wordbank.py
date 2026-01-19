#!/usr/bin/env python3
"""
Generate the embedded deletion-mutants word bank JS.

This script reads the Wordle answer list and writes a filtered, embedded
word list for the deletion mutants daily puzzle:
- exact length (default: 5)
- ASCII a-z only
- all unique letters

By default, this updates the generated word bank block inside:
  site_docs/assets/scripts/deletion_mutants_words.js
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re


_RE_WORD = re.compile(r"^[a-z]+$")


def _has_all_unique_letters(word: str) -> bool:
	seen: set[str] = set()
	for ch in word:
		if ch in seen:
			return False
		seen.add(ch)
	return True


def _iter_filtered_words(src: Path, word_len: int) -> list[str]:
	words: list[str] = []
	seen: set[str] = set()
	for raw in src.read_text(encoding="ascii").splitlines():
		line = raw.strip()
		if not line or line.startswith("#"):
			continue
		if len(line) != word_len:
			continue
		if not _RE_WORD.fullmatch(line):
			continue
		word = line.upper()
		if word in seen:
			continue
		if not _has_all_unique_letters(word):
			continue
		seen.add(word)
		words.append(word)
	return words


def _format_js_array(words: list[str]) -> str:
	per_line = 12
	lines: list[str] = []
	for i in range(0, len(words), per_line):
		chunk = words[i : i + per_line]
		lines.append("\t\t" + ", ".join([f"'{w}'" for w in chunk]) + ",")
	return "\n".join(lines) + "\n"


def _find_default_source(repo_root: Path) -> Path:
	candidates = [
		repo_root / "data" / "wordlists" / "real_wordles.txt",
		repo_root / "devel" / "real_wordles.txt",
		repo_root / "site_docs" / "daily_puzzles" / "deletetions_source" / "real_wordles.txt",
	]
	for path in candidates:
		if path.exists():
			return path
	return candidates[0]


def _parse_args(repo_root: Path) -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Generate deletion mutants embedded word bank JS.",
	)
	parser.add_argument(
		"--src",
		type=Path,
		default=_find_default_source(repo_root),
		help="Path to the source word list (default: auto-detected).",
	)
	parser.add_argument(
		"--target",
		type=Path,
		default=repo_root / "site_docs" / "assets" / "scripts" / "deletion_mutants_words.js",
		help="Path to the JS file containing the generated word bank block.",
	)
	parser.add_argument(
		"--word-len",
		type=int,
		default=5,
		help="Word length to filter (default: 5).",
	)
	return parser.parse_args()


def _replace_between_markers(text: str, marker_name: str, replacement: str) -> str:
	begin = f"// BEGIN {marker_name}\n"
	end = f"// END {marker_name}\n"

	start = text.find(begin)
	if start < 0:
		raise ValueError(f"Missing begin marker: {begin.strip()}")
	stop = text.find(end)
	if stop < 0:
		raise ValueError(f"Missing end marker: {end.strip()}")
	if stop < start:
		raise ValueError("End marker appears before begin marker")

	before = text[: start + len(begin)]
	after = text[stop:]
	return before + replacement + after


def main() -> None:
	repo_root = Path(__file__).resolve().parent
	args = _parse_args(repo_root)
	src = args.src
	target = args.target
	word_len = args.word_len
	if not src.exists():
		raise FileNotFoundError(f"Missing source word list: {src}")
	if not target.exists():
		raise FileNotFoundError(f"Missing target JS file: {target}")

	words = _iter_filtered_words(src, word_len)
	if not words:
		raise RuntimeError("No words found after filtering")

	replacement = (
		"\tvar EMBEDDED_WORD_BANK_V1 = {\n"
		f"\t\t{word_len}: [\n"
		f"{_format_js_array(words)}"
		"\t\t]\n"
		"\t};\n"
	)

	current = target.read_text(encoding="ascii")
	updated = _replace_between_markers(current, "GENERATED WORD BANK V1", replacement)
	target.write_text(updated, encoding="ascii")

	print(f"Updated {target} ({len(words)} words)")


if __name__ == "__main__":
	main()

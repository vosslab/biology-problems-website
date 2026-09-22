"""Generate the embedded deletion-mutants word bank."""

from pathlib import Path
import re
from collections.abc import Iterable


_RE_WORD = re.compile(r"^[a-z]+$")


def _has_all_unique_letters(word: str) -> bool:
	return len(set(word)) == len(word)


def filter_words(words: Iterable[str], length: int) -> list[str]:
	"""Return unique-letter ASCII words of the requested length."""
	filtered: list[str] = []
	seen: set[str] = set()
	for raw_word in words:
		word = raw_word.strip()
		if not word or word.startswith("#") or len(word) != length:
			continue
		if not _RE_WORD.fullmatch(word) or not _has_all_unique_letters(word):
			continue
		upper_word = word.upper()
		if upper_word not in seen:
			seen.add(upper_word)
			filtered.append(upper_word)
	return filtered


def _format_js_array(words: list[str]) -> str:
	lines: list[str] = []
	for index in range(0, len(words), 12):
		chunk = words[index:index + 12]
		lines.append("\t\t" + ", ".join(f"'{word}'" for word in chunk) + ",")
	return "\n".join(lines) + "\n"


def update_wordbank_block(js_path: str | Path, words: list[str], word_len: int = 5) -> None:
	"""Replace the generated word-bank block in a JavaScript file."""
	target_path = Path(js_path)
	text = target_path.read_text(encoding="ascii")
	begin_marker = "// BEGIN GENERATED WORD BANK V1\n"
	end_marker = "// END GENERATED WORD BANK V1\n"
	start = text.find(begin_marker)
	stop = text.find(end_marker)
	if start < 0:
		raise ValueError("Missing begin marker: // BEGIN GENERATED WORD BANK V1")
	if stop < 0:
		raise ValueError("Missing end marker: // END GENERATED WORD BANK V1")
	if stop < start:
		raise ValueError("End marker appears before begin marker")
	replacement = (
		"\tvar EMBEDDED_WORD_BANK_V1 = {\n"
		f"\t\t{word_len}: [\n"
		f"{_format_js_array(words)}"
		"\t\t]\n"
		"\t};\n"
	)
	target_path.write_text(
		text[:start + len(begin_marker)] + replacement + text[stop:],
		encoding="ascii",
	)


def _find_default_source(repo_root: Path) -> Path:
	candidates = (
		repo_root / "data" / "wordlists" / "real_wordles.txt",
		repo_root / "devel" / "real_wordles.txt",
		repo_root / "site_docs" / "daily_puzzles" / "deletetions_source" / "real_wordles.txt",
	)
	return next((path for path in candidates if path.exists()), candidates[0])


def write_js(
	repo_root: str | Path,
	source_path: str | Path | None = None,
	target_path: str | Path | None = None,
	word_len: int = 5,
) -> int:
	"""Filter the configured word list and update the generated JavaScript."""
	root = Path(repo_root)
	source = Path(source_path) if source_path else _find_default_source(root)
	target = (
		Path(target_path)
		if target_path
		else root / "site_docs" / "assets" / "scripts" / "deletion_mutants_words.js"
	)
	if not source.exists():
		raise FileNotFoundError(f"Missing source word list: {source}")
	if not target.exists():
		raise FileNotFoundError(f"Missing target JS file: {target}")
	words = filter_words(source.read_text(encoding="ascii").splitlines(), word_len)
	if not words:
		raise RuntimeError("No words found after filtering")
	update_wordbank_block(target, words, word_len)
	print(f"Updated {target} ({len(words)} words)")
	return len(words)

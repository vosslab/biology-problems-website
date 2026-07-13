#!/usr/bin/env python3
"""Sort BBQ task CSV rows into the topic order from topics_metadata.yml.

The sorter is deliberately independent of run_bbq_tasks.py and the site
package. It reads topics_metadata.yml directly, keeps every nonblank CSV row
unchanged, and writes only standardized blank separator rows between topic
groups.
"""

# Standard Library
import os
import re
import csv
import stat
import pathlib
import argparse
import tempfile
import subprocess

# PIP3 modules
import yaml


TOPIC_KEY_RE = re.compile(r"^topic\d{2}$")


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse the command line arguments."""
	parser = argparse.ArgumentParser(
		description="Sort a BBQ task CSV by the topics_metadata.yml topic order.",
	)
	parser.add_argument(
		"-i", "--input", dest="input_file", required=True, type=pathlib.Path,
		help="Task CSV to sort in place.",
	)
	args = parser.parse_args()
	return args


#============================================
def get_repo_root() -> pathlib.Path:
	"""Return the Git repository root for the current working directory."""
	output = subprocess.check_output(
		["git", "rev-parse", "--show-toplevel"], text=True,
	)
	repo_root = output.strip()
	return pathlib.Path(repo_root)


#============================================
def load_topic_order(
	metadata_path: pathlib.Path,
) -> tuple[dict[str, int], dict[str, dict[str, int]], dict[str, dict[str, str]]]:
	"""Read metadata and return subject, topic, and alias ordering maps.

	Args:
		metadata_path: Repository topics_metadata.yml source of truth.

	Returns:
		Three maps: subject position, canonical topic position per subject,
		and author-facing aliases mapped to canonical topic keys per subject.
	"""
	with metadata_path.open("r", encoding="utf-8") as file_pointer:
		metadata = yaml.safe_load(file_pointer)
	if not isinstance(metadata, dict):
		raise ValueError(f"{metadata_path}: top-level metadata must be a mapping")

	subject_positions = {}
	topic_positions = {}
	aliases = {}
	for subject_position, subject_key in enumerate(sorted(metadata)):
		subject_data = metadata[subject_key]
		if not isinstance(subject_data, dict):
			raise ValueError(f"{metadata_path}: {subject_key!r} must be a mapping")
		topics_data = subject_data.get("topics")
		if not isinstance(topics_data, dict):
			raise ValueError(f"{metadata_path}: {subject_key!r}.topics must be a mapping")
		for topic_key in topics_data:
			if not isinstance(topic_key, str) or not TOPIC_KEY_RE.fullmatch(topic_key):
				raise ValueError(f"{metadata_path}: invalid topic key {topic_key!r}")
		subject_positions[subject_key] = subject_position
		topic_positions[subject_key] = {}
		aliases[subject_key] = {}
		for topic_position, topic_key in enumerate(sorted(topics_data)):
			topic_data = topics_data[topic_key]
			if not isinstance(topic_data, dict):
				raise ValueError(
					f"{metadata_path}: {subject_key}.{topic_key} must be a mapping"
				)
			topic_positions[subject_key][topic_key] = topic_position
			alias = topic_data.get("alias")
			if alias is None:
				continue
			if not isinstance(alias, str) or not alias.strip():
				raise ValueError(
					f"{metadata_path}: {subject_key}.{topic_key}.alias must be a string"
				)
			if alias in aliases[subject_key]:
				raise ValueError(
					f"{metadata_path}: duplicate alias {alias!r} for {subject_key!r}"
				)
			aliases[subject_key][alias] = topic_key
	return subject_positions, topic_positions, aliases


#============================================
def get_column_index(header: list[str], column_name: str) -> int:
	"""Return one required CSV column index or raise a clear error."""
	matching_indices = [
		index for index, field_name in enumerate(header) if field_name == column_name
	]
	if len(matching_indices) != 1:
		raise ValueError(
			f"CSV header must contain exactly one {column_name!r} column"
		)
	column_index = matching_indices[0]
	return column_index


#============================================
def row_has_data(row: list[str]) -> bool:
	"""Return whether a CSV row contains task data rather than a separator."""
	has_data = any(cell.strip() for cell in row)
	return has_data


#============================================
def resolve_topic_key(
	subject: str,
	topic_text: str,
	subject_positions: dict[str, int],
	topic_positions: dict[str, dict[str, int]],
	aliases: dict[str, dict[str, str]],
	source_path: str,
	line_number: int,
) -> str:
	"""Resolve an author-facing topic cell to its canonical topicNN key."""
	if subject not in subject_positions:
		raise ValueError(f"{source_path}: line {line_number}: unknown subject {subject!r}")
	if topic_text in aliases[subject]:
		canonical_topic = aliases[subject][topic_text]
		return canonical_topic
	if topic_text not in topic_positions[subject]:
		raise ValueError(
			f"{source_path}: line {line_number}: unknown topic {topic_text!r} "
			f"for subject {subject!r}"
		)
	aliased_topics = set(aliases[subject].values())
	if topic_text in aliased_topics:
		alias = next(
			name for name, canonical in aliases[subject].items() if canonical == topic_text
		)
		raise ValueError(
			f"{source_path}: line {line_number}: topic {topic_text!r} has "
			f"alias {alias!r}; use the alias in task CSVs"
		)
	return topic_text


#============================================
def sort_task_rows(
	header: list[str],
	rows: list[list[str]],
	subject_positions: dict[str, int],
	topic_positions: dict[str, dict[str, int]],
	aliases: dict[str, dict[str, str]],
	source_path: str,
) -> tuple[list[list[str]], int, int]:
	"""Sort rows by metadata order and add one blank row between topic groups.

	Nonblank task rows are kept as their original lists, so their fields and
	their relative order within each subject/topic group are unchanged.
	"""
	subject_index = get_column_index(header, "subject")
	topic_index = get_column_index(header, "topic")
	required_index = max(subject_index, topic_index)
	indexed_rows = []
	for row_offset, row in enumerate(rows, start=2):
		if not row_has_data(row):
			continue
		if len(row) <= required_index:
			raise ValueError(
				f"{source_path}: line {row_offset}: missing subject or topic cell"
			)
		subject = row[subject_index].strip()
		topic_text = row[topic_index].strip()
		canonical_topic = resolve_topic_key(
			subject, topic_text, subject_positions, topic_positions, aliases,
			source_path, row_offset,
		)
		sort_key = (
			subject_positions[subject],
			topic_positions[subject][canonical_topic],
			row_offset,
		)
		indexed_rows.append((sort_key, row))

	indexed_rows.sort(key=lambda item: item[0])
	separator_row = [""] * len(header)
	sorted_rows = []
	previous_group = None
	for sort_key, row in indexed_rows:
		group = sort_key[:2]
		if previous_group is not None and group != previous_group:
			sorted_rows.append(separator_row.copy())
		sorted_rows.append(row)
		previous_group = group
	task_count = len(indexed_rows)
	topic_group_count = len({sort_key[:2] for sort_key, _row in indexed_rows})
	return sorted_rows, task_count, topic_group_count


#============================================
def write_csv_in_place(
	input_path: pathlib.Path,
	header: list[str],
	rows: list[list[str]],
) -> None:
	"""Atomically replace a CSV with sorted rows while preserving file mode."""
	file_mode = stat.S_IMODE(input_path.stat().st_mode)
	file_descriptor, temporary_path = tempfile.mkstemp(
		prefix=f".{input_path.name}.", suffix=".tmp", dir=input_path.parent,
	)
	with os.fdopen(file_descriptor, "w", newline="", encoding="utf-8") as file_pointer:
		writer = csv.writer(file_pointer, lineterminator="\n")
		writer.writerow(header)
		writer.writerows(rows)
	os.chmod(temporary_path, file_mode)
	os.replace(temporary_path, input_path)


#============================================
def sort_csv_file(input_path: pathlib.Path, metadata_path: pathlib.Path) -> tuple[int, int]:
	"""Sort one task CSV in place using the repository metadata order."""
	with input_path.open("r", newline="", encoding="utf-8") as file_pointer:
		reader = csv.reader(file_pointer)
		header = next(reader, None)
		if header is None:
			raise ValueError(f"{input_path}: CSV is empty")
		rows = list(reader)
	subject_positions, topic_positions, aliases = load_topic_order(metadata_path)
	sorted_rows, task_count, topic_group_count = sort_task_rows(
		header, rows, subject_positions, topic_positions, aliases, str(input_path),
	)
	write_csv_in_place(input_path, header, sorted_rows)
	return task_count, topic_group_count


#============================================
def main() -> None:
	"""Sort the requested task CSV using topics_metadata.yml at the Git root."""
	args = parse_args()
	input_path = args.input_file.resolve()
	if not input_path.is_file():
		raise FileNotFoundError(f"Task CSV not found: {input_path}")
	repo_root = get_repo_root()
	metadata_path = repo_root / "topics_metadata.yml"
	task_count, topic_group_count = sort_csv_file(input_path, metadata_path)
	print(
		f"Sorted {input_path} ({task_count} task rows, "
		f"{topic_group_count} topic groups)."
	)


if __name__ == "__main__":
	main()

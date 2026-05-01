#!/usr/bin/env python3
"""Export topics metadata to CSV for offline cross-reference.

Reads topics_metadata.yml and writes a CSV with columns:
subject, topic_key, alias, title, description

One row per topic across all subjects, ordered by subject then topic_key.
The output file is generated; manual editing is discouraged.
"""

# Standard Library
import os
import sys
import csv
import argparse

# local repo modules
import bioproblems_site.metadata as metadata_module
import bioproblems_site.git_paths as git_paths


#============================================
def parse_args():
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Export topics metadata to CSV"
	)
	parser.add_argument(
		'-o', '--output', dest='output_file',
		default='topics_reference.csv',
		help="Output CSV path (default: topics_reference.csv in CWD)"
	)
	parser.add_argument(
		'-m', '--metadata', dest='metadata_path', default='topics_metadata.yml',
		help="Input metadata YAML path (default: topics_metadata.yml)"
	)
	parser.add_argument(
		'-k', '--mkdocs', dest='mkdocs_path', default='mkdocs.yml',
		help="Input mkdocs.yml path (default: mkdocs.yml)"
	)
	args = parser.parse_args()
	return args


#============================================
def dump_topics_to_csv(metadata_path: str, mkdocs_path: str, output_path: str) -> None:
	"""Write topics metadata to CSV.

	Args:
		metadata_path: Path to topics_metadata.yml
		mkdocs_path: Path to mkdocs.yml
		output_path: Path to write output CSV
	"""
	subjects, _nav_order = metadata_module.load_topics_metadata(
		metadata_path=metadata_path,
		mkdocs_path=mkdocs_path,
	)

	with open(output_path, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		# Write header row with exact column order
		writer.writerow(['subject', 'topic_key', 'alias', 'title', 'description'])

		# Iterate subjects in alphabetical order (they are already sorted)
		for subject_key in sorted(subjects.keys()):
			subject = subjects[subject_key]
			# Topics are already ordered by topic_key within each subject
			for topic in subject.topics:
				alias = topic.alias if topic.alias is not None else ''
				writer.writerow([
					subject_key,
					topic.key,
					alias,
					topic.title,
					topic.description,
				])


#============================================
def main():
	"""Main entry point."""
	args = parse_args()

	# If paths are relative, make them absolute from the repo root.
	repo_root = git_paths.get_repo_root()
	metadata_path = args.metadata_path
	mkdocs_path = args.mkdocs_path
	output_path = args.output_file

	if not os.path.isabs(metadata_path):
		metadata_path = os.path.join(repo_root, metadata_path)
	if not os.path.isabs(mkdocs_path):
		mkdocs_path = os.path.join(repo_root, mkdocs_path)
	# Output: relative paths resolve against the current working
	# directory, not the repo root. Do not auto-create directories;
	# the user must pass -o explicitly to write under a subdirectory.

	print(
		f"Exporting topics from {metadata_path} to {output_path}",
		file=sys.stderr,
	)
	dump_topics_to_csv(metadata_path, mkdocs_path, output_path)
	print(f"Written to {output_path}", file=sys.stderr)


if __name__ == '__main__':
	main()

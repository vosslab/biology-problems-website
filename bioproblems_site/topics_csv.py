"""Export topics metadata to a compact CSV reference."""

import csv
from pathlib import Path

from bioproblems_site import metadata


def dump_topics_to_csv(
	metadata_path: str | Path,
	mkdocs_path: str | Path,
	output_path: str | Path,
) -> None:
	"""Write one subject/topic row for each topic in the metadata source."""
	subjects, _nav_order = metadata.load_topics_metadata(
		metadata_path=str(metadata_path),
		mkdocs_path=str(mkdocs_path),
	)
	with Path(output_path).open("w", newline="") as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(["subject", "topic_key", "alias", "title", "description"])
		for subject_key in sorted(subjects):
			for topic in subjects[subject_key].topics:
				writer.writerow([
					subject_key,
					topic.key,
					topic.alias if topic.alias is not None else "",
					topic.title,
					topic.description,
				])

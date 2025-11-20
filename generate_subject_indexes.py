#!/usr/bin/env python3

# Standard Library
import re
import os
import sys

# Third Party
import yaml

BASE_DIR = "./docs"
MKDOCS_CONFIG = "mkdocs.yml"
TOPICS_METADATA_FILE = "topics_metadata.yml"

SUBJECT_METADATA = {
	"biochemistry": {
		"title": "List of Biochemistry Topics",
		"intro": "Explore the foundational concepts and techniques in Biochemistry. Click on a topic to dive deeper.",
		"index_path": os.path.join(BASE_DIR, "biochemistry", "index.md"),
	},
	"genetics": {
		"title": "List of Genetics Topics",
		"intro": "Explore the main topics in genetics. Click on a topic to dive deeper.",
		"index_path": os.path.join(BASE_DIR, "genetics", "index.md"),
	},
}


def load_yaml_file(path: str) -> dict:
	if not os.path.isfile(path):
		raise FileNotFoundError(f"Required YAML file missing: {path}")
	with open(path, "r") as file_pointer:
		content = yaml.safe_load(file_pointer) or {}
		if not isinstance(content, dict):
			raise ValueError(f"Expected a mapping at root of {path}")
		return content


def load_mkdocs_config() -> list:
	if not os.path.isfile(MKDOCS_CONFIG):
		raise FileNotFoundError(f"Could not find {MKDOCS_CONFIG}")
	with open(MKDOCS_CONFIG, "r") as file_pointer:
		config = yaml.safe_load(file_pointer) or {}
	return config.get("nav", [])


def find_subject_entries(nav_config: list, subject_key: str):
	"""Return nav entries list for a given subject (biochemistry/genetics)."""
	for section in nav_config:
		if not isinstance(section, dict):
			continue
		for _, entries in section.items():
			if not isinstance(entries, list):
				continue
			for item in entries:
				if not isinstance(item, dict):
					continue
				path = list(item.values())[0]
				if isinstance(path, str) and path.startswith(f"{subject_key}/"):
					return entries
	return None


def extract_topics(entries: list, subject_key: str):
	"""Yield topic entries preserving nav order."""
	topics = []
	for item in entries:
		if not isinstance(item, dict):
			continue
		title, path = list(item.items())[0]
		if not isinstance(path, str):
			continue
		if path == f"{subject_key}/index.md":
			continue
		if f"{subject_key}/topic" not in path:
			continue
		# Make link relative to subject index.md
		relative_path = path
		prefix = f"{subject_key}/"
		if relative_path.startswith(prefix):
			relative_path = relative_path[len(prefix):]
		# Strip leading number prefix in nav title (e.g., "1: Title")
		clean_title = re.sub(r"^\s*\d+\s*:\s*", "", title).strip()
		relative_topic = os.path.basename(os.path.dirname(path))
		topics.append(
			{
				"title": clean_title or title,
				"path": relative_path,
				"topic": relative_topic,
			}
		)
	return topics


def build_link_markup(url: str) -> str:
	return (
		f' &mdash; '
		f'<a href="{url}" target="_blank" rel="noopener" title="Open LibreTexts chapter">'
		f'<span style="font-size: 0.8em;">(LibreTexts Chapter '
		f'<i class="fa fa-external-link-alt"></i>)</span></a>'
	)


def write_subject_index(
	subject_key: str,
	metadata_map: dict,
	nav_topics: list,
):
	meta = SUBJECT_METADATA[subject_key]
	lines = []
	lines.append(f"# {meta['title']}")
	lines.append("")
	lines.append(meta["intro"])
	lines.append("")
	lines.append("## Topics")
	lines.append("")

	subject_metadata = metadata_map.get(subject_key, {})

	for idx, topic in enumerate(nav_topics, start=1):
		topic_key = topic["topic"]
		topic_entry = subject_metadata.get(topic_key, {}) if isinstance(subject_metadata, dict) else {}
		topic_desc = topic_entry.get("description", "")
		libre_entry = topic_entry.get("libretexts", {}) if isinstance(topic_entry, dict) else {}
		libre_url = libre_entry.get("url") if isinstance(libre_entry, dict) else None

		line = f"{idx}. [{topic['title']}]({topic['path']})"
		if libre_url:
			line += build_link_markup(libre_url)
		lines.append(line)
		if topic_desc:
			lines.append(f"    - {topic_desc}")
		lines.append("")

	output_path = meta["index_path"]
	with open(output_path, "w") as file_pointer:
		file_pointer.write("\n".join(lines).rstrip() + "\n")
	print(f"Wrote {output_path}")


def main():
	nav_config = load_mkdocs_config()
	topic_metadata = load_yaml_file(TOPICS_METADATA_FILE)

	for subject_key in SUBJECT_METADATA.keys():
		entries = find_subject_entries(nav_config, subject_key)
		if entries is None:
			raise ValueError(f"Could not find nav section for subject {subject_key}")
		topics = extract_topics(entries, subject_key)
		if not topics:
			print(f"Warning: no topics found for {subject_key}")
			continue
		write_subject_index(subject_key, topic_metadata, topics)


if __name__ == "__main__":
	sys.exit(main())
import re

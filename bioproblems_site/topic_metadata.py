"""Resolve page titles and descriptions from canonical topic metadata."""

from functools import lru_cache
import os
import re
import urllib.parse

import yaml

import bioproblems_site.git_paths as git_paths
import bioproblems_site.metadata as metadata


MKDOCS_CONFIG = os.path.join(git_paths.get_repo_root(), "mkdocs.yml")


def get_docs_dir() -> str:
	"""Return the MkDocs source directory from its configuration."""
	if not os.path.isfile(MKDOCS_CONFIG):
		raise FileNotFoundError(f"Config file '{MKDOCS_CONFIG}' not found.")
	with open(MKDOCS_CONFIG, "r", encoding="utf-8") as file_pointer:
		config = yaml.safe_load(file_pointer) or {}
	return config["docs_dir"]


def _derive_libretexts_title(url: str) -> str:
	"""Recover a human-readable chapter title from a LibreTexts URL slug."""
	last_segment = url.rstrip("/").rsplit("/", 1)[-1]
	decoded = urllib.parse.unquote(last_segment)
	if ":" in decoded:
		decoded = decoded.split(":", 1)[1]
	return decoded.replace("_", " ").strip()


@lru_cache(maxsize=None)
def _topic_entry(subject_folder: str, relative_topic_name: str) -> dict:
	"""Return cached title, description, and LibreTexts data for a topic."""
	subjects, _order = metadata.load_topics_metadata()
	subject = subjects.get(subject_folder)
	if subject is None:
		raise FileNotFoundError(
			f"Subject {subject_folder!r} missing from topics_metadata.yml"
		)
	matching = [topic for topic in subject.topics if topic.key == relative_topic_name]
	if not matching:
		raise ValueError(
			f"No entry for {subject_folder}/{relative_topic_name} in "
			f"topics_metadata.yml"
		)
	topic = matching[0]
	libretexts = None
	if topic.libretexts is not None:
		libretexts = {
			"url": topic.libretexts.url,
			"title": _derive_libretexts_title(topic.libretexts.url),
			"unit": topic.libretexts.unit,
			"chapter": topic.libretexts.chapter,
		}
	return {
		"title": topic.title,
		"description": topic.description,
		"libretexts": libretexts,
	}


def _get_topic_entry(topic_folder: str) -> dict:
	"""Look up topic metadata using its site_docs folder path."""
	subject_folder = os.path.basename(os.path.dirname(topic_folder))
	topic_name = os.path.basename(os.path.normpath(topic_folder))
	return _topic_entry(subject_folder, topic_name)


def get_topic_title(topic_folder: str) -> str:
	"""Return the metadata title prefixed with the topic number."""
	entry = _get_topic_entry(topic_folder)
	title = entry.get("title")
	if not title:
		raise ValueError(f"No topic title found for folder path: {topic_folder}")
	topic_name = os.path.basename(os.path.normpath(topic_folder))
	topic_number = int(re.search(r"topic(\d+)", topic_name).group(1))
	return f"{topic_number}: {title}"


def get_libretexts_link(topic_folder: str) -> dict | None:
	"""Return a topic's LibreTexts mapping, or None when it has no link."""
	return _get_topic_entry(topic_folder).get("libretexts")


def get_topic_description(topic_folder: str) -> str:
	"""Return the description from canonical topic metadata."""
	entry = _get_topic_entry(topic_folder)
	description = entry.get("description")
	if not description:
		topic_name = os.path.basename(os.path.normpath(topic_folder))
		raise ValueError(f"No description found for topic: {topic_name}")
	return description

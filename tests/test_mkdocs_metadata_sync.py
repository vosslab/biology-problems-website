"""Sync gate: topics_metadata.yml subject keys match mkdocs.yml nav.

Regressions here are the class of drift that created the biotechnology
orphan, so the invariant is worth a pytest. Keep it to one behavioral
error test and one live-repo sync check.
"""

# Standard Library
import os
from pathlib import Path
import re

# PIP3 modules
import pytest
import yaml

# local repo modules
import bioproblems_site.metadata as metadata_module
import file_utils


def test_repo_yaml_and_mkdocs_nav_are_in_sync() -> object:
	"""Live invariant: the repo's YAML and mkdocs.yml name the same subjects."""
	repo_root = file_utils.get_repo_root()
	metadata_path = os.path.join(repo_root, "topics_metadata.yml")
	mkdocs_path = os.path.join(repo_root, "mkdocs.yml")
	metadata_module.load_topics_metadata(
		metadata_path=metadata_path,
		mkdocs_path=mkdocs_path,
	)


def test_navigation_topics_have_index_pages() -> None:
	"""Every topic linked from the live navigation has a publishable page."""
	repo_root = Path(file_utils.get_repo_root())
	config = yaml.safe_load((repo_root / "mkdocs.yml").read_text())

	def navigation_paths(entries: list[object]) -> list[str]:
		paths: list[str] = []
		for entry in entries:
			if isinstance(entry, str):
				paths.append(entry)
			elif isinstance(entry, dict):
				for value in entry.values():
					if isinstance(value, list):
						paths.extend(navigation_paths(value))
					elif isinstance(value, str):
						paths.append(value)
		return paths

	topic_paths = [
		Path(path) for path in navigation_paths(config["nav"])
		if re.fullmatch(r"topic\d+", Path(path).parent.name)
	]
	assert topic_paths, "mkdocs.yml has no navigation topics"
	missing = [
		str(path) for path in topic_paths
		if path.name != "index.md" or not (repo_root / config["docs_dir"] / path).is_file()
	]
	assert not missing, f"Navigation topics without index.md: {missing}"


def test_mismatch_raises_clear_error(tmp_path: object) -> object:
	metadata_path = tmp_path / "topics.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	metadata_path.write_text(
		"foo:\n  title: Foo\n  description: intro\n  topics:\n"
		"    topic01:\n      title: One\n      description: one\n"
	)
	mkdocs_path.write_text("nav:\n- Bar: bar/index.md\n")
	with pytest.raises(metadata_module.MetadataMkdocsMismatchError):
		metadata_module.load_topics_metadata(
			metadata_path=str(metadata_path),
			mkdocs_path=str(mkdocs_path),
		)


def test_progress_nav_is_not_treated_as_subject(tmp_path: object) -> object:
	metadata_path = tmp_path / "topics.yml"
	mkdocs_path = tmp_path / "mkdocs.yml"
	metadata_path.write_text(
		"biology:\n  title: Biology\n  description: intro\n  topics:\n"
		"    topic01:\n      title: One\n      description: one\n"
	)
	mkdocs_path.write_text(
		"nav:\n"
		"- Home: index.md\n"
		"- Progress: progress/index.md\n"
		"- Biology:\n"
		"  - biology/index.md\n"
		"  - \"01: One\": biology/topic01/index.md\n"
	)
	subjects, nav_order = metadata_module.load_topics_metadata(
		metadata_path=str(metadata_path),
		mkdocs_path=str(mkdocs_path),
	)
	assert set(subjects) == {"biology"}
	assert nav_order == ("biology",)

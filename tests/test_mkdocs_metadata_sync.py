"""Sync gate: topics_metadata.yml subject keys match mkdocs.yml nav.

Regressions here are the class of drift that created the biotechnology
orphan, so the invariant is worth a pytest. Keep it to one behavioral
error test and one live-repo sync check.
"""

# Standard Library
import os

# PIP3 modules
import pytest

# local repo modules
import bioproblems_site.metadata as metadata_module
import git_file_utils


def test_repo_yaml_and_mkdocs_nav_are_in_sync():
	"""Live invariant: the repo's YAML and mkdocs.yml name the same subjects."""
	repo_root = git_file_utils.get_repo_root()
	metadata_path = os.path.join(repo_root, "topics_metadata.yml")
	mkdocs_path = os.path.join(repo_root, "mkdocs.yml")
	metadata_module.load_topics_metadata(
		metadata_path=metadata_path,
		mkdocs_path=mkdocs_path,
	)


def test_mismatch_raises_clear_error(tmp_path):
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

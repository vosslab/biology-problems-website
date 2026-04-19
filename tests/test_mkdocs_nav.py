"""Guardrail tests for bioproblems_site.mkdocs_nav."""

# PIP3 modules
import pytest
import yaml

# local repo modules
import bioproblems_site.mkdocs_nav as mkdocs_nav


def test_missing_markers_raises(tmp_path):
	mkdocs_path = tmp_path / "mkdocs.yml"
	mkdocs_path.write_text("nav:\n- Home: index.md\n")
	with pytest.raises(mkdocs_nav.NavMarkerError):
		mkdocs_nav.replace_nav_block(str(mkdocs_path), "payload")


def test_replacement_preserves_surrounding_lines(tmp_path):
	mkdocs_path = tmp_path / "mkdocs.yml"
	mkdocs_path.write_text(
		"nav:\n"
		"- Home: index.md\n"
		"# BEGIN GENERATED SUBJECT NAV\n"
		"- Old: old/index.md\n"
		"# END GENERATED SUBJECT NAV\n"
		"- Author: author.md\n"
	)
	_old, _new, updated = mkdocs_nav.replace_nav_block(
		str(mkdocs_path), '- "New": new/index.md\n'
	)
	assert "- Home: index.md" in updated
	assert "- Author: author.md" in updated
	assert '- "New": new/index.md' in updated
	assert "- Old: old/index.md" not in updated
	# File must still parse as YAML after the swap.
	yaml.safe_load(updated)

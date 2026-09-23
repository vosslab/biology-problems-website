"""Stable behavior of generated text-file publication."""

from pathlib import Path

import pytest

import bioproblems_site.atomic_write as atomic_write


#============================================
def test_failed_publication_preserves_previous_text_file(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""An interrupted replacement leaves the last complete content available."""
	output_path = tmp_path / "generated.md"
	output_path.write_text("previous complete content\n")

	def fail_replace(source: str, destination: str | Path) -> None:
		raise OSError("simulated publication interruption")

	monkeypatch.setattr(atomic_write.os, "replace", fail_replace)
	with pytest.raises(OSError, match="simulated publication interruption"):
		atomic_write.atomic_write_text(output_path, "replacement content\n")

	assert output_path.read_text() == "previous complete content\n"
	assert list(tmp_path.glob(".generated.md.*")) == []

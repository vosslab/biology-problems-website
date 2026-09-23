"""Atomic text-file publication for generated site content and configuration."""

import os
from pathlib import Path
import stat
import tempfile


#============================================
def atomic_write_text(path: str | Path, text: str) -> None:
	"""Publish complete text while preserving the prior file on write failure."""
	output_path = Path(path)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	try:
		mode = stat.S_IMODE(output_path.stat().st_mode)
	except FileNotFoundError:
		mode = 0o644
	file_descriptor, temporary_path = tempfile.mkstemp(
		prefix=f".{output_path.name}.",
		dir=output_path.parent,
	)
	try:
		with os.fdopen(file_descriptor, "w", encoding="utf-8") as output_file:
			output_file.write(text)
			output_file.flush()
			os.fsync(output_file.fileno())
		os.chmod(temporary_path, mode)
		os.replace(temporary_path, output_path)
	finally:
		if os.path.exists(temporary_path):
			try:
				os.remove(temporary_path)
			except OSError:
				pass

"""Write generated text files."""

from pathlib import Path


#============================================
def write_text(path: str | Path, text: str) -> None:
	"""Write text directly to its destination, creating its parent directory."""
	output_path = Path(path)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	output_path.write_text(text, encoding="utf-8")

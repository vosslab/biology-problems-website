"""Numbered Bloom badges and a readable scale key from shared display definitions."""

import html
import json
import functools
from pathlib import Path

import bioproblems_site.git_paths as git_paths


#============================================
@functools.cache
def definitions() -> dict:
	"""Read the authored JSON also consumed by Question Finder in the browser."""
	path = Path(git_paths.get_repo_root()) / "site_docs/assets/data/bloom_taxonomy.json"
	data = json.loads(path.read_text(encoding="utf-8"))
	return data


#============================================
def badge(label: str, dimension: str) -> str:
	"""Render a canonical label with its scale position and native tooltip."""
	for number, entry in enumerate(definitions()[dimension]["levels"], start=1):
		if entry["label"] == label:
			# ASVS 1.2.1: escape text at the HTML element and attribute boundary.
			name = html.escape(label, quote=True)
			description = html.escape(entry["description"], quote=True)
			markup = (
				f'<span class="bloom-badge" data-bloom="{name}" title="{description}">'
				f'{name} ({number})</span>'
			)
			return markup
	raise ValueError(f"Unknown {dimension} Bloom label: {label}")


#============================================
def guide() -> str:
	"""Expose both scales in native details for keyboard and touch access."""
	lines = ['<details class="bloom-scales"><summary>Bloom\'s scales</summary>',
		'<p>Two dimensions describe the assessed task. Numbers identify categories, '
		'not difficulty ratings.</p><div class="bloom-scales-grid">']
	for dimension, data in definitions().items():
		lines.append(f'<section><h3>{html.escape(data["title"])}</h3><dl>')
		for entry in data["levels"]:
			lines.append(f'<dt>{badge(entry["label"], dimension)}</dt>'
				f'<dd>{html.escape(entry["description"])}</dd>')
		lines.append('</dl></section>')
	lines.append('</div><p>Based on Anderson and Krathwohl (2001), chapters 4-5. '
		'<a href="https://celt.iastate.edu/prepare-and-teach/design-your-course/blooms-taxonomy/">'
		'Iowa State Bloom\'s taxonomy guide</a>.</p></details>')
	markup = "\n".join(lines)
	return markup

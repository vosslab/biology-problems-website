"""Generate the file-based metadata catalog for the instructor Question Finder."""

import json
from pathlib import Path
import random
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser

import bioproblems_site.file_write as file_write
import bioproblems_site.metadata as metadata
import bioproblems_site.problem_set_display as problem_set_display
import bioproblems_site.question_index as question_index


#============================================
def catalog_rows(
		entries: list[question_index.QuestionSetEntry], site_docs_dir: Path,
	) -> list[dict[str, str]]:
	"""Keep each source placement, using the canonical title and type authorities."""
	rows = []
	for entry in entries:
		if entry.source_path is None:
			raise ValueError("Finder rows require a BBQ source path")
		name, _cached_types = problem_set_display.split_title(entry.title)
		code = problem_set_display.question_type_for_source(entry.source_path)
		label, description = problem_set_display.QUESTION_TYPES[code]
		# Relative routes also work when the site is hosted below a project prefix.
		url = "../" + urllib.parse.quote(entry.page_path.removesuffix("/index.md")) + "/"
		rows.append({
			"id": entry.source_path.relative_to(site_docs_dir).as_posix(),
			"name": name,
			"subject": entry.subject_title,
			"topic": entry.topic_title,
			"type": label,
			"type_code": code,
			"type_description": description,
			"url": url,
		})
	return rows


#============================================
def write(
		output_path: Path,
		site_docs_dir: Path,
		metadata_path: Path,
		mkdocs_path: Path,
		dry_run: bool = False,
	) -> str:
	"""Refresh the complete visible corpus even when generation was scoped."""
	subjects, nav_order = metadata.load_topics_metadata(
		metadata_path=str(metadata_path), mkdocs_path=str(mkdocs_path),
	)
	entries = question_index.collect_entries(site_docs_dir, subjects, nav_order)
	text = json.dumps(catalog_rows(entries, site_docs_dir), separators=(",", ":")) + "\n"
	if not dry_run:
		file_write.write_text(output_path, text)
	return text


#============================================
class _LibraryTags(HTMLParser):
	"""Read actual script URLs, rather than maintaining a second version list."""

	def __init__(self) -> None:
		super().__init__()
		self.versions: dict[str, str] = {}

	def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
		if tag != "script":
			return
		source = dict(attrs).get("src", "")
		patterns = {
			"datatables.net": r"https://cdn\.datatables\.net/(\d+\.\d+\.\d+)/js/dataTables\.min\.js",
			"datatables.net-columncontrol": (
				r"https://cdn\.datatables\.net/columncontrol/(\d+\.\d+\.\d+)/"
				r"js/dataTables\.columnControl\.min\.js"
			),
		}
		for package, pattern in patterns.items():
			match = re.fullmatch(pattern, source or "")
			if match:
				self.versions[package] = match[1]


#============================================
def stable_version(version: str) -> tuple[int, ...]:
	"""Compare the publisher's stable major/minor/patch release numbers."""
	if not re.fullmatch(r"\d+\.\d+\.\d+", version):
		raise ValueError(f"Expected a stable semantic version: {version}")
	parts = tuple(int(part) for part in version.split("."))
	return parts


#============================================
def check_dependencies(page_path: Path) -> None:
	"""Report CDN pins versus official npm latest releases without changing files."""
	parser = _LibraryTags()
	parser.feed(page_path.read_text(encoding="utf-8"))
	packages = ("datatables.net", "datatables.net-columncontrol")
	if set(parser.versions) != set(packages):
		raise ValueError("Question Finder must declare both versioned CDN library scripts")
	for package in packages:
		url = f"https://registry.npmjs.org/{package}/latest"
		time.sleep(random.random())
		with urllib.request.urlopen(url, timeout=30) as response:
			latest = json.load(response)["version"]
		current = parser.versions[package]
		newer = stable_version(latest) > stable_version(current)
		prefix = "WARNING: newer stable release" if newer else "Current stable release"
		print(f"{prefix}: {package}: using {current}; latest {latest}")

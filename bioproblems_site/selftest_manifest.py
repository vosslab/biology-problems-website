"""Build the browser self-test completion manifest.

The student-facing dashboard must count only questions reachable from
rendered topic pages. Generated-but-orphaned selftest files under
downloads/ are intentionally ignored.
"""

# Standard Library
import os
import re
import json
import hashlib

# PIP3 modules
import yaml

# local repo modules
import bioproblems_site.metadata as metadata_module


#============================================
DEFAULT_OUTPUT_PATH = os.path.join(
	"site_docs", "assets", "data", "selftest_question_manifest.json"
)

TOPIC_PAGE_RE = re.compile(r"^([a-z_]+)/((?:topic)\d{2})/index\.md$")
INCLUDE_RE = re.compile(r'{%\s*include\s+"([^"]*selftest[^"]*\.html)"\s*%}')
QUESTION_DIV_RE = re.compile(
	r"<div\s+id=[\"']question_html_([0-9a-f]{4}_[0-9a-f]{4})[\"']",
	re.IGNORECASE,
)


#============================================
def _iter_nav_paths(nav_entries: list) -> list:
	"""Return every string path found in a MkDocs nav tree."""
	paths = []
	for entry in nav_entries:
		if isinstance(entry, str):
			paths.append(entry)
			continue
		if isinstance(entry, dict):
			for value in entry.values():
				if isinstance(value, str):
					paths.append(value)
				elif isinstance(value, list):
					paths.extend(_iter_nav_paths(value))
	return paths


def reachable_topic_pages(mkdocs_path: str) -> list:
	"""Return topic page paths reachable through mkdocs.yml nav."""
	with open(mkdocs_path, "r") as file_pointer:
		config = yaml.safe_load(file_pointer) or {}
	nav_paths = _iter_nav_paths(config["nav"])
	topic_pages = []
	for path in nav_paths:
		match = TOPIC_PAGE_RE.match(path)
		if match:
			topic_pages.append(path)
	topic_pages.sort()
	return topic_pages


def _extract_include_paths(page_text: str) -> list:
	"""Return included selftest HTML paths from a rendered topic page."""
	paths = INCLUDE_RE.findall(page_text)
	paths.sort()
	return paths


def _statement_fingerprint(html_text: str, crc: str) -> str:
	"""Return a stable fingerprint for the question statement."""
	pattern = re.compile(
		rf"<div\s+id=[\"']statement_text_{re.escape(crc)}[\"'][^>]*>"
		r"(.*?)"
		r"</div>",
		re.IGNORECASE | re.DOTALL,
	)
	match = pattern.search(html_text)
	if match:
		payload = match.group(1)
	else:
		payload = html_text
	normalized = re.sub(r"\s+", " ", payload).strip()
	digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
	return digest[:16]


def _topic_title(subjects: dict, subject_key: str, topic_key: str) -> str:
	"""Return the topic title from topics_metadata.yml."""
	subject = subjects[subject_key]
	matching = [topic for topic in subject.topics if topic.key == topic_key]
	if not matching:
		raise ValueError(f"No metadata entry for {subject_key}/{topic_key}")
	return matching[0].title


def build_manifest(
	*,
	site_docs_dir: str = "site_docs",
	mkdocs_path: str = "mkdocs.yml",
	metadata_path: str = "topics_metadata.yml",
) -> dict:
	"""Build the self-test manifest from reachable topic pages."""
	subjects, _nav_order = metadata_module.load_topics_metadata(
		metadata_path=metadata_path, mkdocs_path=mkdocs_path
	)
	rows = []
	seen_ids = {}
	for page_path in reachable_topic_pages(mkdocs_path):
		page_match = TOPIC_PAGE_RE.match(page_path)
		subject_key = page_match.group(1)
		topic_key = page_match.group(2)
		full_page_path = os.path.join(site_docs_dir, page_path)
		# A topic page can be listed in nav (questions exist on disk) before
		# its index.md is rendered: fast subject-index-only runs skip topic
		# pages. An unrendered page exposes no reachable questions, so skip it.
		if not os.path.isfile(full_page_path):
			continue
		with open(full_page_path, "r") as file_pointer:
			page_text = file_pointer.read()
		for include_path in _extract_include_paths(page_text):
			full_selftest_path = os.path.join(site_docs_dir, include_path)
			if not os.path.isfile(full_selftest_path):
				raise FileNotFoundError(full_selftest_path)
			with open(full_selftest_path, "r", encoding="iso8859-1") as file_pointer:
				selftest_html = file_pointer.read()
			crcs = QUESTION_DIV_RE.findall(selftest_html)
			if not crcs:
				raise ValueError(f"No question_html_<crc> div in {include_path}")
			for crc in crcs:
				fingerprint = _statement_fingerprint(selftest_html, crc)
				row = {
					"questionId": crc,
					"crc": crc,
					"subjectKey": subject_key,
					"topicKey": topic_key,
					"topicTitle": _topic_title(subjects, subject_key, topic_key),
					"pagePath": page_path,
					"selftestPath": include_path,
					"questionFingerprint": fingerprint,
				}
				if crc in seen_ids:
					previous = seen_ids[crc]
					raise ValueError(
						f"Duplicate selftest CRC {crc}: "
						f"{previous['selftestPath']} and {include_path}"
					)
				seen_ids[crc] = row
				rows.append(row)
	rows.sort(key=lambda row: (
		row["subjectKey"],
		row["topicKey"],
		row["selftestPath"],
		row["questionId"],
	))
	manifest = {
		"version": 1,
		"source": "reachable-topic-pages",
		"questions": rows,
	}
	return manifest


def write_manifest(
	*,
	output_path: str = DEFAULT_OUTPUT_PATH,
	site_docs_dir: str = "site_docs",
	mkdocs_path: str = "mkdocs.yml",
	metadata_path: str = "topics_metadata.yml",
	dry_run: bool = False,
) -> dict:
	"""Build and optionally write the self-test manifest."""
	manifest = build_manifest(
		site_docs_dir=site_docs_dir,
		mkdocs_path=mkdocs_path,
		metadata_path=metadata_path,
	)
	if dry_run:
		return manifest
	output_dir = os.path.dirname(output_path)
	os.makedirs(output_dir, exist_ok=True)
	with open(output_path, "w") as file_pointer:
		json.dump(manifest, file_pointer, indent=2, sort_keys=True)
		file_pointer.write("\n")
	return manifest

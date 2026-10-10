"""Build the browser self-test completion manifest.

The student-facing dashboard must count only questions reachable from
rendered topic pages. Each declaration identifies a BBQ bank in the
topic directory; standalone HTML is not part of this contract.
"""

# Standard Library
import html
import json
import os
import re

# PIP3 modules
import yaml

# local repo modules
import bioproblems_site.metadata as metadata_module
import bioproblems_site.git_paths as git_paths


#============================================
DEFAULT_OUTPUT_PATH = os.path.join(
	"site_docs", "assets", "data", "selftest_question_manifest.json"
)

TOPIC_PAGE_RE = re.compile(r"^([a-z_]+)/((?:topic)\d{2})/index\.md$")
OPENING_DIV_RE = re.compile(
	r"<div\b(?P<attributes>(?:[^>\"']|\"[^\"]*\"|'[^']*')*)>",
	re.IGNORECASE,
)
CLASS_ATTRIBUTE_RE = re.compile(r"\bclass\s*=\s*([\"'])(.*?)\1", re.IGNORECASE)
BBQ_ATTRIBUTE_RE = re.compile(r"\bdata-bbq\s*=\s*([\"'])(.*?)\1", re.IGNORECASE)


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


def _extract_selftest_sources(page_text: str) -> list:
	"""Return BBQ basenames declared by self-test containers."""
	sources = []
	for match in OPENING_DIV_RE.finditer(page_text):
		attributes = match.group("attributes")
		class_match = CLASS_ATTRIBUTE_RE.search(attributes)
		if class_match is None:
			continue
		classes = class_match.group(2).split()
		if "qti-selftest" not in classes:
			continue
		bbq_match = BBQ_ATTRIBUTE_RE.search(attributes)
		if bbq_match is None:
			raise ValueError("Self-test container is missing data-bbq")
		bbq_basename = html.unescape(bbq_match.group(2))
		if not bbq_basename or os.path.basename(bbq_basename) != bbq_basename:
			raise ValueError(f"Self-test data-bbq must be a basename: {bbq_basename}")
		sources.append(bbq_basename)
	return sources


#============================================
def _validate_bank(topic_dir: str, bbq_basename: str) -> None:
	"""Require a local bank with question data without interpreting QPM records."""
	bank_path = os.path.join(topic_dir, bbq_basename)
	with open(bank_path, "rb") as source:
		if not any(line.strip() and not line.lstrip().startswith(b"#") for line in source):
			raise ValueError(f"No questions in {git_paths.display_path(bank_path)}")


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
	topic_scope: set[tuple[str, str]] | None = None,
) -> dict:
	"""Build the self-test manifest from reachable topic pages.

	When topic_scope is provided, validate only those subject/topic pairs.
	"""
	subjects, _nav_order = metadata_module.load_topics_metadata(
		metadata_path=metadata_path, mkdocs_path=mkdocs_path
	)
	rows = []
	seen_placements = set()
	for page_path in reachable_topic_pages(mkdocs_path):
		page_match = TOPIC_PAGE_RE.match(page_path)
		subject_key = page_match.group(1)
		topic_key = page_match.group(2)
		if topic_scope is not None and (subject_key, topic_key) not in topic_scope:
			continue
		full_page_path = os.path.join(site_docs_dir, page_path)
		# A topic page can be listed in nav (questions exist on disk) before
		# its index.md is rendered: fast subject-index-only runs skip topic
		# pages. An unrendered page exposes no reachable questions, so skip it.
		if not os.path.isfile(full_page_path):
			continue
		with open(full_page_path, "r") as file_pointer:
			page_text = file_pointer.read()
		for bbq_basename in _extract_selftest_sources(page_text):
			_validate_bank(os.path.dirname(full_page_path), bbq_basename)
			row = {
				"questionId": bbq_basename,
				"subjectKey": subject_key,
				"topicKey": topic_key,
				"topicTitle": _topic_title(subjects, subject_key, topic_key),
				"pagePath": page_path,
			}
			placement_key = (page_path, bbq_basename)
			if placement_key in seen_placements:
				raise ValueError(
					f"Duplicate selftest problem set {bbq_basename} on {page_path}"
				)
			seen_placements.add(placement_key)
			rows.append(row)
	rows.sort(key=lambda row: (
		row["subjectKey"],
		row["topicKey"],
		row["questionId"],
	))
	manifest = {
		"version": 2,
		"source": "reachable-topic-pages",
		"questions": rows,
	}
	return manifest


def _merge_scoped_manifest(
	*,
	existing_manifest: dict,
	scoped_manifest: dict,
	topic_scope: set[tuple[str, str]],
	site_docs_dir: str,
	mkdocs_path: str,
) -> dict:
	"""Replace selected topic rows and retain currently reachable rows elsewhere."""
	if (
		existing_manifest.get("version") != 2
		or existing_manifest.get("source") != "reachable-topic-pages"
		or not isinstance(existing_manifest.get("questions"), list)
	):
		raise ValueError("Cannot merge a scoped build into an invalid self-test manifest")
	reachable_topics = set()
	for page_path in reachable_topic_pages(mkdocs_path):
		match = TOPIC_PAGE_RE.match(page_path)
		reachable_topics.add((match.group(1), match.group(2)))
	rows = [
		row
		for row in existing_manifest["questions"]
		if (row.get("subjectKey"), row.get("topicKey")) in reachable_topics
		and (row.get("subjectKey"), row.get("topicKey")) not in topic_scope
		and os.path.isfile(os.path.join(site_docs_dir, row.get("pagePath", "")))
	]
	rows.extend(scoped_manifest["questions"])
	rows.sort(key=lambda row: (
		row["subjectKey"],
		row["topicKey"],
		row["questionId"],
	))
	seen_placements = set()
	for row in rows:
		placement_key = (row["pagePath"], row["questionId"])
		if placement_key in seen_placements:
			raise ValueError(
				f"Duplicate selftest problem set {placement_key[1]} on {placement_key[0]} "
				"in merged manifest"
			)
		seen_placements.add(placement_key)
	return {
		"version": 2,
		"source": "reachable-topic-pages",
		"questions": rows,
	}


def write_manifest(
	*,
	output_path: str = DEFAULT_OUTPUT_PATH,
	site_docs_dir: str = "site_docs",
	mkdocs_path: str = "mkdocs.yml",
	metadata_path: str = "topics_metadata.yml",
	dry_run: bool = False,
	topic_scope: set[tuple[str, str]] | None = None,
) -> dict:
	"""Build and optionally write the self-test manifest."""
	manifest = build_manifest(
		site_docs_dir=site_docs_dir,
		mkdocs_path=mkdocs_path,
		metadata_path=metadata_path,
		topic_scope=topic_scope,
	)
	if topic_scope is not None:
		if not os.path.isfile(output_path):
			# A focused build cannot establish a complete site-wide manifest from
			# scratch, so initialize it through the same strict global contract.
			manifest = build_manifest(
				site_docs_dir=site_docs_dir,
				mkdocs_path=mkdocs_path,
				metadata_path=metadata_path,
			)
		else:
			with open(output_path, "r") as file_pointer:
				existing_manifest = json.load(file_pointer)
			manifest = _merge_scoped_manifest(
				existing_manifest=existing_manifest,
				scoped_manifest=manifest,
				topic_scope=topic_scope,
				site_docs_dir=site_docs_dir,
				mkdocs_path=mkdocs_path,
			)
	if dry_run:
		return manifest
	output_dir = os.path.dirname(output_path) or "."
	os.makedirs(output_dir, exist_ok=True)
	with open(output_path, "w", encoding="utf-8") as file_pointer:
		json.dump(manifest, file_pointer, indent=2, sort_keys=True)
		file_pointer.write("\n")
	return manifest

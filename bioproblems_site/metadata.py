"""Loader and validator for topics_metadata.yml.

Reads the YAML source of truth for subject and topic metadata and
cross-checks it against mkdocs.yml nav so that the two files cannot
drift silently.
"""

# Standard Library
import os
import re
import dataclasses

# PIP3 modules
import yaml

#============================================
# Nav entries that are allowed to exist in mkdocs.yml without a
# matching YAML subject key. These are the top-level non-subject pages
# (home, puzzles, tutorials, author, license).
RESERVED_NAV_TARGETS = (
	"index.md",
	"author.md",
	"license.md",
)
RESERVED_NAV_DIR_PREFIXES = (
	"daily_puzzles/",
	"tutorials/",
)

SUBJECT_KEY_RE = re.compile(r"^[a-z_]+$")
TOPIC_KEY_RE = re.compile(r"^topic\d{2}$")
TOPIC_ALIAS_RE = re.compile(r"^[a-z0-9_]+$")
LIBRETEXTS_PREFIX = "https://bio.libretexts.org/"


#============================================
class MetadataError(ValueError):
	"""Raised when topics_metadata.yml fails schema or sync checks."""


class MetadataMkdocsMismatchError(MetadataError):
	"""YAML subject keys do not match mkdocs.yml nav subject keys."""


#============================================
@dataclasses.dataclass(frozen=True)
class LibreTextsLink:
	url: str
	# Some LibreTexts books, such as Advanced Genetics, use chapter-only
	# links; unit is 0 in that case.
	unit: int
	chapter: int


@dataclasses.dataclass(frozen=True)
class Topic:
	key: str
	title: str
	description: str
	libretexts: "LibreTextsLink | None"
	visible: bool
	# Optional human-readable alias used in author-facing inputs
	# (CSV task files, generate_pages.py -t/--topic). None when no
	# alias has been assigned. Charset [a-z0-9_]; unique per subject.
	alias: "str | None"


@dataclasses.dataclass(frozen=True)
class Subject:
	key: str
	title: str
	description: str
	# Topics ordered by zero-padded numeric key ascending.
	topics: tuple


#============================================
def _validate_libretexts(payload: dict, topic_key: str) -> "LibreTextsLink | None":
	if payload is None:
		return None
	if not isinstance(payload, dict):
		raise MetadataError(f"{topic_key}: libretexts must be a mapping")
	allowed = {"url", "unit", "chapter"}
	unknown = set(payload.keys()) - allowed
	if unknown:
		raise MetadataError(
			f"{topic_key}: unknown libretexts keys {sorted(unknown)}"
		)
	if "url" not in payload or "chapter" not in payload:
		raise MetadataError(
			f"{topic_key}: libretexts requires url and chapter together"
		)
	url = payload["url"]
	chapter = payload["chapter"]
	# LibreTexts unit is optional; 0 means the external link has no unit number.
	unit = payload.get("unit", 0)
	if not isinstance(url, str) or not url.startswith(LIBRETEXTS_PREFIX):
		raise MetadataError(
			f"{topic_key}: libretexts.url must start with {LIBRETEXTS_PREFIX}"
		)
	if not isinstance(unit, int) or unit < 0:
		raise MetadataError(f"{topic_key}: libretexts.unit must be int >= 0")
	if not isinstance(chapter, int) or chapter < 1:
		raise MetadataError(f"{topic_key}: libretexts.chapter must be int >= 1")
	return LibreTextsLink(url=url, unit=unit, chapter=chapter)


def _build_topic(topic_key: str, payload: dict) -> Topic:
	if not TOPIC_KEY_RE.match(topic_key):
		raise MetadataError(f"invalid topic key {topic_key!r}")
	if not isinstance(payload, dict):
		raise MetadataError(f"{topic_key}: topic must be a mapping")
	allowed = {"title", "description", "libretexts", "visible", "alias"}
	unknown = set(payload.keys()) - allowed
	if unknown:
		raise MetadataError(f"{topic_key}: unknown keys {sorted(unknown)}")
	if "title" not in payload:
		raise MetadataError(f"{topic_key}: title is required")
	if "description" not in payload:
		raise MetadataError(f"{topic_key}: description is required")
	title = payload["title"]
	description = payload["description"]
	if not (isinstance(title, str) and title.strip()):
		raise MetadataError(f"{topic_key}: title must be non-empty")
	if not (isinstance(description, str) and description.strip()):
		raise MetadataError(f"{topic_key}: description must be non-empty")
	libretexts = _validate_libretexts(payload.get("libretexts"), topic_key)
	visible = payload.get("visible", True)
	if not isinstance(visible, bool):
		raise MetadataError(f"{topic_key}: visible must be boolean")
	# alias is optional; when present it must be a [a-z0-9_]+ slug
	# that does not collide with the canonical topicNN key form.
	alias = payload.get("alias")
	if alias is not None:
		if not isinstance(alias, str):
			raise MetadataError(f"{topic_key}: alias must be a string")
		if not TOPIC_ALIAS_RE.match(alias):
			raise MetadataError(
				f"{topic_key}: alias {alias!r} must match [a-z0-9_]+"
			)
		if TOPIC_KEY_RE.match(alias):
			raise MetadataError(
				f"{topic_key}: alias {alias!r} collides with the "
				f"canonical topicNN key form"
			)
	# Strip trailing newlines from pipe-literal descriptions; preserve
	# internal whitespace.
	description_clean = description.rstrip("\n").strip()
	return Topic(
		key=topic_key,
		title=title.strip(),
		description=description_clean,
		libretexts=libretexts,
		visible=visible,
		alias=alias,
	)


def _build_subject(subject_key: str, payload: dict) -> Subject:
	if not SUBJECT_KEY_RE.match(subject_key):
		raise MetadataError(f"invalid subject key {subject_key!r}")
	if not isinstance(payload, dict):
		raise MetadataError(f"{subject_key}: subject must be a mapping")
	allowed = {"title", "description", "topics"}
	unknown = set(payload.keys()) - allowed
	if unknown:
		raise MetadataError(f"{subject_key}: unknown keys {sorted(unknown)}")
	if "title" not in payload:
		raise MetadataError(f"{subject_key}: title is required")
	if "description" not in payload:
		raise MetadataError(f"{subject_key}: description is required (may be empty string)")
	if "topics" not in payload:
		raise MetadataError(f"{subject_key}: topics is required")
	title = payload["title"]
	description = payload["description"]
	topics_raw = payload["topics"]
	if not (isinstance(title, str) and title.strip()):
		raise MetadataError(f"{subject_key}: title must be non-empty")
	if not isinstance(description, str):
		raise MetadataError(f"{subject_key}: description must be a string")
	if not isinstance(topics_raw, dict):
		raise MetadataError(f"{subject_key}: topics must be a mapping")
	# Order topics by zero-padded numeric key ascending.
	ordered_keys = sorted(topics_raw.keys())
	topics = tuple(_build_topic(k, topics_raw[k]) for k in ordered_keys)
	# Aliases must be unique within a subject; the same alias text
	# may legally repeat across different subjects.
	seen_aliases = {}
	for topic in topics:
		if topic.alias is None:
			continue
		if topic.alias in seen_aliases:
			raise MetadataError(
				f"{subject_key}: alias {topic.alias!r} is duplicated by "
				f"topics {seen_aliases[topic.alias]!r} and {topic.key!r}"
			)
		seen_aliases[topic.alias] = topic.key
	return Subject(
		key=subject_key,
		title=title.strip(),
		description=description.rstrip("\n").strip(),
		topics=topics,
	)


#============================================
def build_topic_alias_map(subjects: dict) -> dict:
	"""Return {subject_key: {alias: topic_key}} for every aliased topic.

	Subjects without any aliased topics still appear in the result
	with an empty inner dict, so callers can index unconditionally
	without KeyError on a known subject.

	Args:
		subjects: dict[str, Subject] as returned by load_metadata_file
			or load_topics_metadata.

	Returns:
		dict mapping subject_key to a dict mapping alias -> topic_key.
	"""
	alias_map = {}
	for subject_key, subject in subjects.items():
		inner = {}
		for topic in subject.topics:
			if topic.alias is None:
				continue
			# Per-subject uniqueness already enforced in _build_subject;
			# this loop is a straightforward inversion.
			inner[topic.alias] = topic.key
		alias_map[subject_key] = inner
	return alias_map


#============================================
def load_metadata_file(path: str) -> dict:
	"""Load and schema-validate topics_metadata.yml. Returns dict[key, Subject]."""
	if not os.path.isfile(path):
		raise FileNotFoundError(f"metadata file not found: {path}")
	with open(path, "r") as file_pointer:
		raw = yaml.safe_load(file_pointer)
	if not isinstance(raw, dict):
		raise MetadataError(f"{path}: top-level must be a mapping")
	subjects = {}
	for subject_key in sorted(raw.keys()):
		subjects[subject_key] = _build_subject(subject_key, raw[subject_key])
	return subjects


#============================================
def _nav_subject_keys(nav: list) -> tuple:
	"""Walk mkdocs.yml nav and return subject keys in nav order.

	A subject key is the first path segment of any nav entry whose
	path is '<segment>/index.md' and which is not a reserved top-level
	page.
	"""
	ordered = []
	seen = set()

	def handle(entry):
		if isinstance(entry, dict):
			for _label, value in entry.items():
				if isinstance(value, str):
					handle(value)
				elif isinstance(value, list):
					for item in value:
						handle(item)
			return
		if not isinstance(entry, str):
			return
		if entry in RESERVED_NAV_TARGETS:
			return
		if any(entry.startswith(prefix) for prefix in RESERVED_NAV_DIR_PREFIXES):
			return
		# Expect subject_key/index.md OR subject_key/topicNN/index.md
		parts = entry.split("/")
		if len(parts) < 2 or parts[-1] != "index.md":
			return
		subject_key = parts[0]
		if subject_key in seen:
			return
		seen.add(subject_key)
		ordered.append(subject_key)

	for entry in nav:
		handle(entry)
	return tuple(ordered)


def load_mkdocs_nav(mkdocs_path: str) -> tuple:
	"""Return the ordered tuple of subject keys found in mkdocs.yml nav."""
	with open(mkdocs_path, "r") as file_pointer:
		config = yaml.safe_load(file_pointer) or {}
	nav = config.get("nav", [])
	if not isinstance(nav, list):
		raise MetadataError(f"{mkdocs_path}: nav must be a list")
	return _nav_subject_keys(nav)


#============================================
def load_topics_metadata(
	metadata_path: str = "topics_metadata.yml",
	mkdocs_path: str = "mkdocs.yml",
) -> tuple:
	"""Load YAML + cross-check mkdocs.yml.

	Returns a 2-tuple (subjects_dict, subject_order) where subject_order
	is the tuple of subject keys in mkdocs.yml nav order.
	"""
	subjects = load_metadata_file(metadata_path)
	nav_order = load_mkdocs_nav(mkdocs_path)
	yaml_keys = set(subjects.keys())
	nav_keys = set(nav_order)
	missing_in_nav = yaml_keys - nav_keys
	missing_in_yaml = nav_keys - yaml_keys
	if missing_in_nav or missing_in_yaml:
		message_parts = []
		if missing_in_nav:
			message_parts.append(
				f"present in {metadata_path} but missing from "
				f"{mkdocs_path} nav: {sorted(missing_in_nav)}"
			)
		if missing_in_yaml:
			message_parts.append(
				f"present in {mkdocs_path} nav but missing from "
				f"{metadata_path}: {sorted(missing_in_yaml)}"
			)
		raise MetadataMkdocsMismatchError("; ".join(message_parts))
	return subjects, nav_order

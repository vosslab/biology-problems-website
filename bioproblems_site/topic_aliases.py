"""Pure helpers that resolve author-facing topic references.

Authors type aliases (e.g. "amino_acids") in CSV task files and on the
generate_pages.py -t/--topic CLI; the canonical internal id stays
"topicNN". This module turns the author-facing form into the canonical
form using the alias map produced by metadata.build_topic_alias_map.

Module is intentionally pure: no file I/O, no YAML reading. Callers
pass in `subjects` and `alias_map`. This keeps the resolver trivial
to unit-test and prevents hidden side effects.
"""

# Standard Library
import re

# local repo modules
import bioproblems_site.metadata as metadata


#============================================
# Cell charset for author-facing input. Matches metadata.TOPIC_ALIAS_RE
# but re-declared here so the resolver does not depend on a private
# detail of metadata.
_TOPIC_CELL_RE = re.compile(r"^[a-z0-9_]+$")


#============================================
def is_topic_key(text: str) -> bool:
	"""Return True if text is exactly a canonical topicNN key."""
	# Exactly two digits, leading 'topic' prefix.
	return bool(metadata.TOPIC_KEY_RE.match(text))


#============================================
def validate_topic_cell(text: str) -> str:
	"""Return the cleaned topic cell or raise MetadataError.

	Strips surrounding whitespace ONLY. Does not lowercase. Rejects
	uppercase, embedded whitespace, empty cells, or any character
	outside [a-z0-9_]. Silent case-correction is intentionally not
	done so authors see the actual input that failed.

	Args:
		text: raw value from a CSV cell or CLI argument.

	Returns:
		The whitespace-stripped value, guaranteed to match
		[a-z0-9_]+ or topic\\d{2}.

	Raises:
		metadata.MetadataError on any malformed input.
	"""
	if not isinstance(text, str):
		raise metadata.MetadataError(
			f"topic cell must be a string, got {type(text).__name__}"
		)
	cleaned = text.strip()
	if not cleaned:
		raise metadata.MetadataError("topic cell is empty after stripping")
	# Reject uppercase up front with a specific message before the
	# generic charset check fires; this gives the author a clearer
	# remediation hint.
	if cleaned != cleaned.lower():
		raise metadata.MetadataError(
			f"topic cell {text!r}: uppercase is not allowed; "
			f"use lowercase [a-z0-9_] only"
		)
	if not _TOPIC_CELL_RE.match(cleaned):
		raise metadata.MetadataError(
			f"topic cell {text!r}: must match [a-z0-9_]+ "
			f"(e.g. 'amino_acids') or topic\\d{{2}} (e.g. 'topic03')"
		)
	return cleaned


#============================================
def _format_source(source: str, line_number) -> str:
	"""Compose 'source:line N' or 'source' for error messages.

	Uses physical file line numbers (matching what the author sees
	in their editor), not data-row numbers, so a header on line 1
	plus first data row on line 2 reports as 'line 2'.
	"""
	if line_number is None:
		return source
	location = f"{source}:line {line_number}"
	return location


def _suggest_alias(unknown: str, known_aliases: list) -> str:
	"""Return a short suggestion phrase for an unknown alias.

	Picks the closest known alias by simple prefix/substring match.
	When no obvious neighbour exists, lists every alias for the
	subject (limited list keeps the message readable).
	"""
	# Cheap typo heuristic: a known alias that shares a 4+ char
	# prefix is usually what the author meant.
	prefix_hits = [a for a in known_aliases if len(unknown) >= 4 and a.startswith(unknown[:4])]
	if len(prefix_hits) == 1:
		message = f"did you mean {prefix_hits[0]!r}?"
		return message
	# Substring fallback for swapped letters or shortened forms.
	substring_hits = [a for a in known_aliases if unknown in a or a in unknown]
	if len(substring_hits) == 1:
		message = f"did you mean {substring_hits[0]!r}?"
		return message
	# No clean suggestion; list available aliases.
	if known_aliases:
		joined = ", ".join(sorted(known_aliases))
		message = f"available aliases: {joined}"
		return message
	message = "no aliases defined for this subject"
	return message


#============================================
def resolve_topic_key(
	subject: str,
	topic_text: str,
	alias_map: dict,
	*,
	source: str,
	line_number=None,
) -> str:
	"""Resolve a per-row topic cell to a canonical topicNN key.

	Used by run_bbq_tasks.py for CSV authoring; subject is known
	per-row, so this does not return the subject.

	Resolution:
	  1. Cleaned text matches topic\\d{2}: if that topicNN has an
	     alias defined for this subject, raise (author must use the
	     alias). Otherwise accept and return as-is.
	  2. Cleaned text matches [a-z0-9_]+: look up under subject in
	     alias_map; raise if missing; return the canonical topicNN.
	  3. Otherwise: validate_topic_cell already raised.

	Args:
		subject: subject_key for this row.
		topic_text: raw CSV cell value for the topic column.
		alias_map: dict from metadata.build_topic_alias_map.
		source: file path used in error messages.
		line_number: physical file line number (matches the editor;
			header is line 1). None when not applicable.

	Returns:
		Canonical topicNN string.

	Raises:
		metadata.MetadataError on any resolution failure.
	"""
	location = _format_source(source, line_number)
	if subject not in alias_map:
		raise metadata.MetadataError(
			f"{location}: unknown subject {subject!r}; "
			f"known subjects: {sorted(alias_map.keys())}"
		)
	subject_aliases = alias_map[subject]
	cleaned = validate_topic_cell(topic_text)
	# Case 1: canonical topicNN literal.
	if is_topic_key(cleaned):
		# If this topicNN has an alias, the author must use the alias
		# (consistent with the CSV policy stated in the plan).
		topic_to_alias = {tn: a for a, tn in subject_aliases.items()}
		if cleaned in topic_to_alias:
			alias_form = topic_to_alias[cleaned]
			raise metadata.MetadataError(
				f"{location}: subject {subject!r} topic {cleaned!r} has "
				f"alias {alias_form!r}; use the alias instead of the "
				f"canonical key in author-facing input"
			)
		# topicNN with no alias defined: accept.
		return cleaned
	# Case 2: alias lookup.
	if cleaned in subject_aliases:
		canonical = subject_aliases[cleaned]
		return canonical
	# Unknown alias under known subject.
	suggestion = _suggest_alias(cleaned, list(subject_aliases.keys()))
	raise metadata.MetadataError(
		f"{location}: unknown topic alias {cleaned!r} under subject "
		f"{subject!r}; {suggestion}"
	)


#============================================
def resolve_topic_filter(
	text: str,
	alias_map: dict,
	subjects: dict,
) -> tuple:
	"""Resolve a CLI -t/--topic argument to (subject_key, topic_key).

	Used by generate_pages.py. Accepts (preferred form first):
	  - "biochemistry:amino_acids" -- always unambiguous
	  - "biochemistry:topic03"     -- always unambiguous; raises if
	                                  the topic has an alias defined
	  - "amino_acids"              -- bare alias; valid only if exactly
	                                  one subject defines it
	  - "topic03"                  -- bare canonical; valid only if
	                                  exactly one subject defines it
	                                  AND that topic has no alias

	Args:
		text: raw -t/--topic argv value.
		alias_map: dict from metadata.build_topic_alias_map.
		subjects: dict[str, Subject] from metadata.load_metadata_file.

	Returns:
		(subject_key, topic_key) tuple.

	Raises:
		metadata.MetadataError on ambiguity, unknown, or malformed input.
	"""
	source = "--topic argument"
	if not isinstance(text, str) or not text.strip():
		raise metadata.MetadataError(f"{source}: empty value")
	raw = text.strip()
	# Subject:topic shorthand; route through resolve_topic_key for
	# consistent error semantics with the CSV path.
	if ":" in raw:
		parts = raw.split(":")
		if len(parts) != 2 or not parts[0] or not parts[1]:
			raise metadata.MetadataError(
				f"{source}: malformed subject:alias form {text!r}"
			)
		subject_key, topic_text = parts[0], parts[1]
		canonical = resolve_topic_key(
			subject_key, topic_text, alias_map, source=source,
		)
		return subject_key, canonical
	# Bare form: search every subject for a unique match.
	cleaned = validate_topic_cell(raw)
	if is_topic_key(cleaned):
		# Must exist as a topic key in exactly one subject AND have
		# no alias defined there (otherwise prefer the alias form).
		matches = []
		for subject_key, subject in subjects.items():
			topic_keys = {t.key: t for t in subject.topics}
			if cleaned in topic_keys:
				topic_obj = topic_keys[cleaned]
				if topic_obj.alias is None:
					matches.append(subject_key)
		if len(matches) == 1:
			return matches[0], cleaned
		if len(matches) == 0:
			# Either no subject has this topicNN, or every subject
			# that does has an alias defined.
			raise metadata.MetadataError(
				f"{source}: bare canonical key {cleaned!r} is not "
				f"resolvable; either no subject defines it, or every "
				f"subject that does has an alias for it (use "
				f"<subject>:<alias> instead)"
			)
		candidates = ", ".join(f"{s}:{cleaned}" for s in sorted(matches))
		raise metadata.MetadataError(
			f"{source}: bare canonical key {cleaned!r} is ambiguous "
			f"across subjects; pass one of: {candidates}"
		)
	# Bare alias: search every subject's alias_map for a unique hit.
	matches = []
	for subject_key, inner in alias_map.items():
		if cleaned in inner:
			matches.append((subject_key, inner[cleaned]))
	if len(matches) == 1:
		return matches[0]
	if len(matches) == 0:
		raise metadata.MetadataError(
			f"{source}: unknown alias {cleaned!r} in any subject"
		)
	candidates = ", ".join(f"{s}:{cleaned}" for s, _ in sorted(matches))
	raise metadata.MetadataError(
		f"{source}: alias {cleaned!r} is ambiguous across subjects; "
		f"pass one of: {candidates}"
	)

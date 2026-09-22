"""Small data contracts shared by the unified site build stages."""

from dataclasses import dataclass, field
from pathlib import Path


#============================================
@dataclass(frozen=True, order=True)
class TopicRef:
	"""Canonical topic identity; topic keys are unique only within a subject."""

	subject: str
	topic: str


#============================================
@dataclass(frozen=True)
class BuildChanges:
	"""Files and topics changed or selected by the BBQ stage."""

	changed_topics: set[TopicRef] = field(default_factory=set)
	changed_subjects: set[str] = field(default_factory=set)
	changed_files: set[Path] = field(default_factory=set)
	selected_topics: set[TopicRef] = field(default_factory=set)


#============================================
@dataclass(frozen=True)
class BuildScope:
	"""The public build selection and execution mode."""

	subject: str | None = None
	tasks_csv: Path | None = None
	limit: int | None = None
	shuffle: bool = False
	dry_run: bool = False
	full: bool = False
	max_questions: int | None = None
	model: str | None = None

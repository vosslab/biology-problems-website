"""Dependency order for the unified site build; domain work stays in stages."""

from dataclasses import dataclass, field
from pathlib import Path

import bioproblems_site.bbq_workflow as bbq_workflow
import bioproblems_site.build_stages as build_stages
import bioproblems_site.metadata as metadata_module
from bioproblems_site.build_contracts import BuildChanges, BuildScope, TopicRef


#============================================
@dataclass(frozen=True)
class BuildReport:
	"""Aggregate outputs selected or written by a unified build."""

	changes: BuildChanges
	stage_files: dict[str, set[Path]] = field(default_factory=dict)


#============================================
def _full_scope_topics(scope: BuildScope) -> set[TopicRef]:
	"""Return metadata-owned topics within the requested full-build scope."""
	subjects, nav_order = metadata_module.load_topics_metadata(
		metadata_path=str(build_stages.DEFAULT_METADATA_PATH),
		mkdocs_path=str(build_stages.DEFAULT_MKDOCS_PATH),
	)
	subject_keys = [scope.subject] if scope.subject else list(nav_order)
	topics = {
		TopicRef(subject_key, topic.key)
		for subject_key in subject_keys
		for topic in subjects[subject_key].topics
	}
	return topics


#============================================
def build_site(scope: BuildScope) -> BuildReport:
	"""Build configured BBQ work and its downstream content in dependency order."""
	changes = bbq_workflow.run_if_needed(scope)
	# Include configured topics so missing/stale downstream outputs recover even
	# when their already-fresh BBQ source did not need regeneration.
	affected_topics = set(changes.selected_topics)
	if not affected_topics:
		affected_topics = bbq_workflow.configured_topics(scope)
	affected_topics.update(changes.changed_topics)
	# A full unrestricted or subject build owns every metadata topic in that
	# scope. A task CSV or development limit instead owns only the BBQ topics
	# selected above; full bypasses stale checks but never expands that scope.
	if scope.full and scope.tasks_csv is None and scope.limit is None:
		affected_topics.update(_full_scope_topics(scope))
	stage_files: dict[str, set[Path]] = {"bbq": set(changes.changed_files)}
	for topic_ref in sorted(affected_topics):
		if build_stages.selftests_need_run(topic_ref, scope, changes):
			stage_files.setdefault("selftests", set()).update(build_stages.run_selftests(topic_ref, scope))
		if build_stages.topic_page_needs_run(topic_ref, scope, changes):
			stage_files.setdefault("topic_pages", set()).update(build_stages.run_topic_page(topic_ref, scope))
		if build_stages.downloads_need_run(topic_ref, scope, changes):
			stage_files.setdefault("downloads", set()).update(build_stages.run_downloads(topic_ref, scope))
	stage_files["indexes"] = build_stages.run_subject_indexes(scope)
	return BuildReport(changes=changes, stage_files=stage_files)

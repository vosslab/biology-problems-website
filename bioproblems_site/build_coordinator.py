"""Dependency order for the unified site build; domain work stays in stages."""

from dataclasses import dataclass, field
from pathlib import Path
import time

import bioproblems_site.bbq_workflow as bbq_workflow
import bioproblems_site.build_stages as build_stages
import bioproblems_site.metadata as metadata_module
from bioproblems_site.build_contracts import BuildChanges, BuildScope, TaskBuildResult, TopicRef


#============================================
@dataclass(frozen=True)
class BuildReport:
	"""Aggregate outputs selected or written by a unified build."""

	changes: BuildChanges
	stage_files: dict[str, set[Path]] = field(default_factory=dict)
	stage_seconds: dict[str, float] = field(default_factory=dict)
	elapsed_seconds: float = 0.0


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
		if scope.topic is None or topic.key == scope.topic
	}
	return topics


#============================================
def _run_task_row_artifact_stages(
	task_result: TaskBuildResult,
	scope: BuildScope,
	changes: BuildChanges,
	stage_files: dict[str, set[Path]],
	stage_seconds: dict[str, float],
) -> None:
	"""Complete one row's self-test and download stages before the next row."""
	topic_ref = task_result.topic_ref
	source_paths = task_result.source_files
	stage_start = time.perf_counter()
	if build_stages.selftests_need_run(topic_ref, scope, changes, source_paths):
		stage_files.setdefault("selftests", set()).update(
			build_stages.run_selftests(topic_ref, scope, source_paths)
		)
	stage_seconds["selftests"] += time.perf_counter() - stage_start
	# Publish a page only after its linked converter outputs are ready.
	stage_start = time.perf_counter()
	if build_stages.downloads_need_run(topic_ref, scope, changes, source_paths):
		stage_files.setdefault("downloads", set()).update(
			build_stages.run_downloads(topic_ref, scope, source_paths)
		)
	stage_seconds["downloads"] += time.perf_counter() - stage_start


#============================================
def build_site(scope: BuildScope) -> BuildReport:
	"""Build row-owned artifacts in order, then each affected topic page once."""
	build_start = time.perf_counter()
	stage_files: dict[str, set[Path]] = {"bbq": set()}
	stage_seconds = {
		"bbq": 0.0,
		"selftests": 0.0,
		"downloads": 0.0,
		"topic_pages": 0.0,
		"indexes": 0.0,
	}
	selected_topics: set[TopicRef] = set()
	changed_topics: set[TopicRef] = set()
	changed_subjects: set[str] = set()
	changed_files: set[Path] = set()
	processed_topics: set[TopicRef] = set()
	# Finish each CSV row's local stages before advancing to the next row.
	task_results = iter(bbq_workflow.iter_task_results(scope))
	while True:
		stage_start = time.perf_counter()
		try:
			task_result = next(task_results)
		except StopIteration:
			stage_seconds["bbq"] += time.perf_counter() - stage_start
			break
		stage_seconds["bbq"] += time.perf_counter() - stage_start
		topic_ref = task_result.topic_ref
		processed_topics.add(topic_ref)
		selected_topics.add(topic_ref)
		if task_result.needs_run:
			changed_topics.add(topic_ref)
			changed_subjects.add(topic_ref.subject)
			changed_files.update(task_result.changed_files)
			stage_files["bbq"].update(task_result.changed_files)
		row_changes = BuildChanges(
			changed_topics={topic_ref} if task_result.needs_run else set(),
			changed_subjects={topic_ref.subject} if task_result.needs_run else set(),
			changed_files=task_result.changed_files,
			selected_topics={topic_ref},
		)
		_run_task_row_artifact_stages(
			task_result, scope, row_changes, stage_files, stage_seconds
		)

	# A full unrestricted or subject build also owns metadata topics without CSV rows.
	if scope.full and scope.tasks_csv is None and scope.limit is None:
		for topic_ref in sorted(_full_scope_topics(scope) - processed_topics):
			topic_sources = set(build_stages.topic_sources(topic_ref))
			task_result = TaskBuildResult(topic_ref=topic_ref, source_files=topic_sources)
			row_changes = BuildChanges(selected_topics={topic_ref})
			_run_task_row_artifact_stages(
				task_result, scope, row_changes, stage_files, stage_seconds
			)
			selected_topics.add(topic_ref)

	changes = BuildChanges(
		changed_topics=changed_topics,
		changed_subjects=changed_subjects,
		changed_files=changed_files,
		selected_topics=selected_topics,
	)
	# A topic page summarizes every BBQ source in its folder. Refresh it once after
	# all selected rows have produced their own self-tests and converter outputs.
	stage_start = time.perf_counter()
	for topic_ref in sorted(selected_topics):
		if build_stages.topic_page_needs_run(topic_ref, scope, changes):
			stage_files.setdefault("topic_pages", set()).update(
				build_stages.run_topic_page(topic_ref, scope)
			)
	stage_seconds["topic_pages"] = time.perf_counter() - stage_start
	stage_start = time.perf_counter()
	stage_files["indexes"] = build_stages.run_subject_indexes(scope, selected_topics)
	stage_seconds["indexes"] = time.perf_counter() - stage_start
	elapsed_seconds = time.perf_counter() - build_start
	return BuildReport(
		changes=changes,
		stage_files=stage_files,
		stage_seconds=stage_seconds,
		elapsed_seconds=elapsed_seconds,
	)

"""Dependency order for the unified site build; domain work stays in stages."""

from dataclasses import dataclass, field
from pathlib import Path
import time

import bioproblems_site.bbq_workflow as bbq_workflow
import bioproblems_site.build_stages as build_stages
import bioproblems_site.metadata as metadata_module
from bioproblems_site.build_contracts import BuildChanges, BuildScope, TaskBuildResult, TopicRef
from bioproblems_site.build_progress import BuildCancelledError, BuildProgress


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
	row_index: int | None,
	row_label: str,
	progress: BuildProgress | None,
) -> None:
	"""Complete one row's self-test and download stages before the next row."""
	topic_ref = task_result.topic_ref
	source_paths = task_result.source_files
	row_details: dict[str, object] = {"label": row_label}
	if row_index is not None:
		row_details["row"] = row_index
	if progress:
		progress.check_cancelled()
	stage_start = time.perf_counter()
	selftests_required = build_stages.selftests_need_run(
		topic_ref, scope, changes, source_paths,
	)
	if progress and selftests_required:
		progress.check_cancelled()
	if selftests_required:
		if progress:
			progress.emit("stage_started", phase="selftests", **row_details)
		try:
			if progress:
				outputs = build_stages.run_selftests(
					topic_ref, scope, source_paths, progress,
				)
			else:
				outputs = build_stages.run_selftests(topic_ref, scope, source_paths)
			stage_files.setdefault("selftests", set()).update(
				outputs
			)
		except BuildCancelledError:
			raise
		except Exception as error:
			if progress:
				progress.emit(
					"stage_failed",
					phase="selftests",
					duration=time.perf_counter() - stage_start,
					detail=str(error),
					**row_details,
				)
			raise
		if progress:
			progress.emit(
				"stage_completed",
				phase="selftests",
				duration=time.perf_counter() - stage_start,
				executed=not scope.dry_run,
				planned=scope.dry_run,
				**row_details,
			)
	else:
		if progress:
			progress.emit(
				"stage_skipped", phase="selftests", detail="up to date", **row_details,
			)
	stage_seconds["selftests"] += time.perf_counter() - stage_start
	# Publish a page only after its linked converter outputs are ready.
	if progress:
		progress.check_cancelled()
	stage_start = time.perf_counter()
	downloads_required = build_stages.downloads_need_run(
		topic_ref, scope, changes, source_paths,
	)
	if progress and downloads_required:
		progress.check_cancelled()
	if downloads_required:
		if progress:
			progress.emit("stage_started", phase="downloads", **row_details)
		try:
			if progress:
				outputs = build_stages.run_downloads(
					topic_ref, scope, source_paths, progress,
				)
			else:
				outputs = build_stages.run_downloads(topic_ref, scope, source_paths)
			stage_files.setdefault("downloads", set()).update(
				outputs
			)
		except BuildCancelledError:
			raise
		except Exception as error:
			if progress:
				progress.emit(
					"stage_failed",
					phase="downloads",
					duration=time.perf_counter() - stage_start,
					detail=str(error),
					**row_details,
				)
			raise
		if progress:
			download_count, download_total = build_stages.count_downloads(
				source_paths,
				task_result.expected_pgml_files,
			)
			progress.emit(
				"stage_completed",
				phase="downloads",
				duration=time.perf_counter() - stage_start,
				executed=not scope.dry_run,
				planned=scope.dry_run,
				download_count=download_count,
				download_total=download_total,
				**row_details,
			)
	else:
		if progress:
			download_count, download_total = build_stages.count_downloads(
				source_paths,
				task_result.expected_pgml_files,
			)
			progress.emit(
				"stage_skipped",
				phase="downloads",
				detail="up to date",
				download_count=download_count,
				download_total=download_total,
				**row_details,
			)
	stage_seconds["downloads"] += time.perf_counter() - stage_start


#============================================
def build_site(scope: BuildScope, progress: BuildProgress | None = None) -> BuildReport:
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
	if progress:
		task_results = iter(bbq_workflow.iter_task_results(scope, progress))
	else:
		task_results = iter(bbq_workflow.iter_task_results(scope))
	row_index = 0
	while True:
		stage_start = time.perf_counter()
		try:
			task_result = next(task_results)
		except StopIteration:
			stage_seconds["bbq"] += time.perf_counter() - stage_start
			break
		stage_seconds["bbq"] += time.perf_counter() - stage_start
		row_index += 1
		topic_ref = task_result.topic_ref
		row_label = f"{topic_ref.subject}/{topic_ref.topic}"
		if progress:
			progress.check_cancelled()
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
			task_result,
			scope,
			row_changes,
			stage_files,
			stage_seconds,
			row_index,
			row_label,
			progress,
		)

	# A full unrestricted or subject build also owns metadata topics without CSV rows.
	if scope.full and scope.tasks_csv is None and scope.limit is None:
		for topic_ref in sorted(_full_scope_topics(scope) - processed_topics):
			if progress:
				progress.check_cancelled()
			topic_sources = set(build_stages.topic_sources(topic_ref))
			task_result = TaskBuildResult(topic_ref=topic_ref, source_files=topic_sources)
			row_changes = BuildChanges(selected_topics={topic_ref})
			_run_task_row_artifact_stages(
				task_result,
				scope,
				row_changes,
				stage_files,
				stage_seconds,
				None,
				f"{topic_ref.subject}/{topic_ref.topic}",
				progress,
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
	if progress:
		progress.emit("phase_plan", phase="topic_pages", total=len(selected_topics))
	for topic_ref in sorted(selected_topics):
		if progress:
			progress.check_cancelled()
		page_label = f"{topic_ref.subject}/{topic_ref.topic}"
		page_start = time.perf_counter()
		page_required = build_stages.topic_page_needs_run(topic_ref, scope, changes)
		if progress and page_required:
			progress.check_cancelled()
		if page_required:
			if progress:
				progress.emit("stage_started", phase="topic_pages", label=page_label)
				progress.check_cancelled()
			try:
				stage_files.setdefault("topic_pages", set()).update(
					build_stages.run_topic_page(topic_ref, scope)
				)
			except BuildCancelledError:
				raise
			except Exception as error:
				if progress:
					progress.emit(
						"stage_failed",
						phase="topic_pages",
						label=page_label,
						duration=time.perf_counter() - page_start,
						detail=str(error),
					)
				raise
			if progress:
				progress.emit(
					"stage_completed",
					phase="topic_pages",
					label=page_label,
					duration=time.perf_counter() - page_start,
					executed=not scope.dry_run,
					planned=scope.dry_run,
				)
		else:
			if progress:
				progress.emit(
					"stage_skipped", phase="topic_pages", label=page_label,
					detail="up to date",
				)
	stage_seconds["topic_pages"] = time.perf_counter() - stage_start
	stage_start = time.perf_counter()
	if progress:
		progress.emit("phase_plan", phase="indexes", total=1)
		progress.check_cancelled()
		progress.emit("stage_started", phase="indexes", label="Indexes, navigation, manifest")
	try:
		if progress:
			stage_files["indexes"] = build_stages.run_subject_indexes(
				scope, selected_topics, progress,
			)
		else:
			stage_files["indexes"] = build_stages.run_subject_indexes(
				scope, selected_topics,
			)
	except BuildCancelledError:
		raise
	except Exception as error:
		if progress:
			progress.emit(
				"stage_failed",
				phase="indexes",
				label="Indexes, navigation, manifest",
				duration=time.perf_counter() - stage_start,
				detail=str(error),
			)
		raise
	if progress:
		progress.emit(
			"stage_completed",
			phase="indexes",
			label="Indexes, navigation, manifest",
			duration=time.perf_counter() - stage_start,
			executed=not scope.dry_run,
			planned=scope.dry_run,
		)
		progress.check_cancelled()
	stage_seconds["indexes"] = time.perf_counter() - stage_start
	elapsed_seconds = time.perf_counter() - build_start
	return BuildReport(
		changes=changes,
		stage_files=stage_files,
		stage_seconds=stage_seconds,
		elapsed_seconds=elapsed_seconds,
	)

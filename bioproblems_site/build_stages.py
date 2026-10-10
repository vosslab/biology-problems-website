"""Stage-local stale checks and writers for the unified site build."""

from pathlib import Path

import bioproblems_site.llm_helpers as llm_helpers
import bioproblems_site.bbq_workflow as bbq_workflow
import bioproblems_site.file_write as file_write
import bioproblems_site.metadata as metadata_module
import bioproblems_site.mkdocs_nav as mkdocs_nav_module
import bioproblems_site.orphan_prune as orphan_prune_module
import bioproblems_site.question_index as question_index_module
import bioproblems_site.question_finder as question_finder_module
import bioproblems_site.scanner as scanner_module
import bioproblems_site.selftest_manifest as selftest_manifest_module
import bioproblems_site.subject_index as subject_index_module
import bioproblems_site.topic_page as topic_page_module
import bioproblems_site.git_paths as git_paths
import bioproblems_site.homepage_data as homepage_data
from bioproblems_site.build_contracts import BuildChanges, BuildScope, TopicRef
from bioproblems_site.build_progress import BuildProgress


REPO_ROOT = Path(git_paths.get_repo_root())
DEFAULT_SITE_DOCS = REPO_ROOT / "site_docs"
DEFAULT_METADATA_PATH = REPO_ROOT / "topics_metadata.yml"
DEFAULT_MKDOCS_PATH = REPO_ROOT / "mkdocs.yml"


#============================================
def topic_folder(topic_ref: TopicRef, site_docs_dir: Path = DEFAULT_SITE_DOCS) -> Path:
	"""Return the configured documentation folder for one canonical topic."""
	path = site_docs_dir / topic_ref.subject / topic_ref.topic
	return path


#============================================
def topic_sources(topic_ref: TopicRef, site_docs_dir: Path = DEFAULT_SITE_DOCS) -> list[Path]:
	"""Return the BBQ sources directly owned by one topic."""
	paths = sorted(topic_folder(topic_ref, site_docs_dir).glob("bbq-*-questions.txt"))
	return paths


#============================================
def is_newer_than_any(output_path: Path, input_paths: list[Path]) -> bool:
	"""Return whether any existing direct input is newer than an output."""
	if not output_path.is_file():
		return True
	output_mtime = output_path.stat().st_mtime
	newer = any(path.is_file() and path.stat().st_mtime > output_mtime for path in input_paths)
	return newer


#============================================
def topic_page_needs_run(topic_ref: TopicRef, scope: BuildScope, changes: BuildChanges) -> bool:
	"""Check direct topic-page inputs without scanning unrelated topics."""
	page_path = topic_folder(topic_ref) / "index.md"
	inputs = [DEFAULT_METADATA_PATH]
	inputs.extend(topic_sources(topic_ref))
	if scope.full or topic_ref in changes.changed_topics:
		return True
	return is_newer_than_any(page_path, inputs)


#============================================
def run_topic_page(topic_ref: TopicRef, scope: BuildScope) -> set[Path]:
	"""Render one topic page without creating self-tests or downloads."""
	if not topic_folder(topic_ref).is_dir():
		return set()
	page_path = topic_folder(topic_ref) / "index.md"
	if scope.dry_run:
		return {page_path}
	llm_helpers.validate_backend(scope.backend, scope.model)
	client = llm_helpers.create_llm_client(
		backend=scope.backend,
		model=scope.model,
	)
	options = topic_page_module.RenderOptions(
		verbose=True,
		llm_client=client,
	)
	topic_page_module.render_all(
		options,
		topic_ref.subject,
		topic_ref.topic,
		base_dir=str(DEFAULT_SITE_DOCS),
	)
	return {page_path}


#============================================
def count_downloads(
		source_paths: set[Path],
		expected_pgml_files: set[Path],
) -> tuple[int, int]:
	"""Return available downloads and expected downloads for BBQ sources."""
	expected_paths: set[Path] = set()
	pgml_paths = set(expected_pgml_files)
	for source_path in source_paths:
		# Browser-generated packages are controls, not expected disk files.
		expected_paths.add(source_path)
		# Non-YAML tasks have no configured PGML path; count a matching file if found.
		if not expected_pgml_files:
			pgml_path = topic_page_module.find_pgml_file(str(source_path))
			if pgml_path:
				pgml_paths.add(Path(pgml_path))
	available_count = sum(path.is_file() for path in expected_paths | pgml_paths)
	expected_count = len(expected_paths | pgml_paths)
	return available_count, expected_count


#============================================
def _write_subject_index(subject: object, site_docs_dir: Path, dry_run: bool) -> Path:
	"""Render one subject index using metadata-owned topic order."""
	topic_keys = tuple(topic.key for topic in subject.topics)
	scans = scanner_module.scan_subject(str(site_docs_dir), subject.key, topic_keys)
	output_path = site_docs_dir / subject.key / "index.md"
	text = subject_index_module.render_subject_index(subject, scans)
	if output_path.is_file() and not subject_index_module.has_generated_marker(str(output_path)):
		raise RuntimeError(
			f"Refusing to overwrite {git_paths.display_path(output_path)}: "
			"no generated marker."
		)
	if not dry_run:
		file_write.write_text(output_path, text)
	return output_path


#============================================
def run_subject_indexes(
	scope: BuildScope,
	selected_topics: set[TopicRef] | None = None,
	progress: BuildProgress | None = None,
) -> set[Path]:
	"""Unconditionally refresh cheap subject indexes, nav, and manifest."""
	subjects, nav_order = metadata_module.load_topics_metadata(
		metadata_path=str(DEFAULT_METADATA_PATH),
		mkdocs_path=str(DEFAULT_MKDOCS_PATH),
	)
	subject_keys = [scope.subject] if scope.subject else list(nav_order)
	outputs: set[Path] = set()
	if progress:
		progress.check_cancelled()
	# Orphan status is repository-global, even when generation is narrowly scoped.
	# Reconcile first so indexes, nav, and the manifest see only current task-owned
	# BBQ sources after a removed CSV row is cleaned up.
	if scope.mode == "indexes":
		# A standalone page refresh preserves existing BBQ and converter artifacts.
		reconciliation = {"strip_includes": []}
	else:
		try:
			task_owned_patterns, task_owned_pgml_paths = bbq_workflow.load_task_ownership()
		except bbq_workflow.TaskOwnershipError as exc:
			print(f"WARNING: skipping orphan reconciliation because task ownership is uncertain: {exc}")
			reconciliation = {"strip_includes": []}
		else:
			reconciliation = orphan_prune_module.reconcile_all(
				str(DEFAULT_SITE_DOCS), scope.dry_run, verbose=True,
				task_owned_pattern_map=task_owned_patterns,
				task_owned_pgml_paths=task_owned_pgml_paths,
			)
	question_index_path = DEFAULT_SITE_DOCS / "sitemap.md"
	if progress:
		progress.check_cancelled()
		progress.emit("log", message="Finalizing searchable question index")
	question_index_module.write(
		question_index_path,
		DEFAULT_SITE_DOCS,
		DEFAULT_METADATA_PATH,
		DEFAULT_MKDOCS_PATH,
		dry_run=scope.dry_run,
	)
	outputs.add(question_index_path)
	finder_path = DEFAULT_SITE_DOCS / "assets/data/question_finder.json"
	if progress:
		progress.check_cancelled()
		progress.emit("log", message="Finalizing Question Finder catalog")
	question_finder_module.write(
		finder_path, DEFAULT_SITE_DOCS, DEFAULT_METADATA_PATH, DEFAULT_MKDOCS_PATH,
		dry_run=scope.dry_run,
	)
	outputs.add(finder_path)
	for subject_key in subject_keys:
		if progress:
			progress.check_cancelled()
			progress.emit("log", message=f"Finalizing subject index: {subject_key}")
		outputs.add(_write_subject_index(subjects[subject_key], DEFAULT_SITE_DOCS, scope.dry_run))
	# Navigation is global and inexpensive. Rebuild it even for a selected
	# subject so its visibility and counts cannot lag behind source content.
	if progress:
		progress.check_cancelled()
		progress.emit("log", message="Finalizing MkDocs navigation")
	mkdocs_nav_module.update_from_sources(
		metadata_path=str(DEFAULT_METADATA_PATH),
		mkdocs_path=str(DEFAULT_MKDOCS_PATH),
		site_docs_dir=str(DEFAULT_SITE_DOCS),
		dry_run=scope.dry_run,
	)
	outputs.add(DEFAULT_MKDOCS_PATH)
	manifest_topics = set(selected_topics or ())
	for changed_index in reconciliation["strip_includes"]:
		relative_path = Path(changed_index["path"]).relative_to(DEFAULT_SITE_DOCS)
		if len(relative_path.parts) >= 3:
			manifest_topics.add(TopicRef(relative_path.parts[0], relative_path.parts[1]))
	outputs.update(run_selftest_manifest(scope, manifest_topics, progress))
	if progress:
		progress.emit("log", message="Finalizing homepage statistics and activity")
	outputs.update(homepage_data.write(
		REPO_ROOT, DEFAULT_SITE_DOCS, DEFAULT_METADATA_PATH, DEFAULT_MKDOCS_PATH,
		dry_run=scope.dry_run,
	))
	return outputs


#============================================
def run_selftest_manifest(
	scope: BuildScope,
	selected_topics: set[TopicRef],
	progress: BuildProgress | None = None,
) -> set[Path]:
	"""Refresh self-test IDs without rewriting indexes or pruning source files."""
	manifest_path = DEFAULT_SITE_DOCS / "assets/data/selftest_question_manifest.json"
	if progress:
		progress.check_cancelled()
		progress.emit("log", message="Finalizing self-test manifest")
	if not scope.dry_run:
		unrestricted = not any((scope.subject, scope.topic, scope.tasks_csv, scope.limit))
		manifest_topic_scope = None if unrestricted else {
			(topic.subject, topic.topic) for topic in selected_topics
		}
		selftest_manifest_module.write_manifest(
			output_path=str(manifest_path),
			site_docs_dir=str(DEFAULT_SITE_DOCS),
			mkdocs_path=str(DEFAULT_MKDOCS_PATH),
			metadata_path=str(DEFAULT_METADATA_PATH),
			topic_scope=manifest_topic_scope,
		)
	outputs = {manifest_path}
	return outputs

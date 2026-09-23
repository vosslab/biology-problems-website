"""Stage-local stale checks and writers for the unified site build."""

from pathlib import Path

import bioproblems_site.llm_helpers as llm_helpers
import bioproblems_site.bbq_workflow as bbq_workflow
import bioproblems_site.atomic_write as atomic_write
import bioproblems_site.metadata as metadata_module
import bioproblems_site.mkdocs_nav as mkdocs_nav_module
import bioproblems_site.orphan_prune as orphan_prune_module
import bioproblems_site.question_index as question_index_module
import bioproblems_site.scanner as scanner_module
import bioproblems_site.selftest_manifest as selftest_manifest_module
import bioproblems_site.subject_index as subject_index_module
import bioproblems_site.topic_page as topic_page_module
import bioproblems_site.git_paths as git_paths
from bioproblems_site.build_contracts import BuildChanges, BuildScope, TopicRef


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
def selected_topic_sources(
	topic_ref: TopicRef,
	source_paths: set[Path] | None,
) -> list[Path]:
	"""Return one task row's BBQ files, or every file in the topic when unscoped."""
	if source_paths is None:
		return topic_sources(topic_ref)
	owner_folder = topic_folder(topic_ref)
	return sorted(source_path for source_path in source_paths if source_path.parent == owner_folder)


#============================================
def is_newer_than_any(output_path: Path, input_paths: list[Path]) -> bool:
	"""Return whether any existing direct input is newer than an output."""
	if not output_path.is_file():
		return True
	output_mtime = output_path.stat().st_mtime
	newer = any(path.is_file() and path.stat().st_mtime > output_mtime for path in input_paths)
	return newer


#============================================
def selftests_need_run(
	topic_ref: TopicRef,
	scope: BuildScope,
	changes: BuildChanges,
	source_paths: set[Path] | None = None,
) -> bool:
	"""Check direct BBQ-to-self-test relationships for one topic."""
	sources = selected_topic_sources(topic_ref, source_paths)
	if not sources:
		return False
	if scope.full or topic_ref in changes.changed_topics:
		return True
	for source_path in sources:
		output_path = Path(topic_page_module.get_outfile_name(str(source_path), "selftest", "html"))
		if is_newer_than_any(output_path, [source_path]):
			return True
	return False


#============================================
def run_selftests(
	topic_ref: TopicRef,
	scope: BuildScope,
	source_paths: set[Path] | None = None,
) -> set[Path]:
	"""Write self-tests for one task row, or all files in a topic when unscoped."""
	sources = selected_topic_sources(topic_ref, source_paths)
	outputs = {
		Path(topic_page_module.get_outfile_name(str(source_path), "selftest", "html"))
		for source_path in sources
	}
	if scope.dry_run:
		return outputs
	for source_path in sources:
		topic_page_module.create_downloadable_format(str(source_path), "selftest", "html")
	return outputs


#============================================
def topic_page_needs_run(topic_ref: TopicRef, scope: BuildScope, changes: BuildChanges) -> bool:
	"""Check direct topic-page inputs without scanning unrelated topics."""
	page_path = topic_folder(topic_ref) / "index.md"
	inputs = [DEFAULT_METADATA_PATH]
	inputs.extend(topic_sources(topic_ref))
	for source_path in topic_sources(topic_ref):
		inputs.append(Path(topic_page_module.get_outfile_name(str(source_path), "selftest", "html")))
		inputs.extend(expected_downloads(source_path))
	if scope.full or topic_ref in changes.changed_topics:
		return True
	return is_newer_than_any(page_path, inputs)


#============================================
def run_topic_page(topic_ref: TopicRef, scope: BuildScope) -> set[Path]:
	"""Render one topic page without creating self-tests or downloads."""
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
		generate_downloads=False,
		regenerate_selftests=False,
		render_missing_download_links=False,
	)
	topic_page_module.render_all(
		options,
		topic_ref.subject,
		topic_ref.topic,
		base_dir=str(DEFAULT_SITE_DOCS),
	)
	return {page_path}


#============================================
def expected_downloads(source_path: Path) -> set[Path]:
	"""Return converter-owned artifacts expected for one BBQ source."""
	outputs = {
		Path(topic_page_module.get_outfile_name(str(source_path), "canvas_qti_v1_2", "zip")),
		Path(topic_page_module.get_outfile_name(str(source_path), "human_readable", "html")),
	}
	if topic_page_module.supports_blackboard_export(str(source_path)):
		outputs.add(Path(topic_page_module.get_outfile_name(
			str(source_path), "blackboard_export_zip", "zip"
		)))
	return outputs


#============================================
def downloads_need_run(
	topic_ref: TopicRef,
	scope: BuildScope,
	changes: BuildChanges,
	source_paths: set[Path] | None = None,
) -> bool:
	"""Check direct BBQ-to-download relationships for one topic."""
	sources = selected_topic_sources(topic_ref, source_paths)
	if not sources:
		return False
	if scope.full or topic_ref in changes.changed_topics:
		return True
	for source_path in sources:
		for output_path in expected_downloads(source_path):
			if is_newer_than_any(output_path, [source_path]):
				return True
	return False


#============================================
def run_downloads(
	topic_ref: TopicRef,
	scope: BuildScope,
	source_paths: set[Path] | None = None,
) -> set[Path]:
	"""Write converter-owned artifacts for one row or all files in a topic."""
	outputs: set[Path] = set()
	for source_path in selected_topic_sources(topic_ref, source_paths):
		outputs.update(expected_downloads(source_path))
		if scope.dry_run:
			continue
		topic_page_module.generate_download_artifacts(str(source_path), verbose=True)
	return outputs


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
		atomic_write.atomic_write_text(output_path, text)
	return output_path


#============================================
def run_subject_indexes(
	scope: BuildScope,
	selected_topics: set[TopicRef] | None = None,
) -> set[Path]:
	"""Unconditionally refresh cheap subject indexes, nav, and manifest."""
	subjects, nav_order = metadata_module.load_topics_metadata(
		metadata_path=str(DEFAULT_METADATA_PATH),
		mkdocs_path=str(DEFAULT_MKDOCS_PATH),
	)
	subject_keys = [scope.subject] if scope.subject else list(nav_order)
	outputs: set[Path] = set()
	# Orphan status is repository-global, even when generation is narrowly scoped.
	# Reconcile first so indexes, nav, and the manifest see only current task-owned
	# BBQ sources after a removed CSV row is cleaned up.
	try:
		task_owned_patterns = bbq_workflow.load_task_owned_patterns()
	except bbq_workflow.TaskOwnershipError as exc:
		print(f"WARNING: skipping orphan reconciliation because task ownership is uncertain: {exc}")
		reconciliation = {"strip_includes": []}
	else:
		reconciliation = orphan_prune_module.reconcile_all(
			str(DEFAULT_SITE_DOCS), scope.dry_run, verbose=True,
			task_owned_pattern_map=task_owned_patterns,
		)
	question_index_path = DEFAULT_SITE_DOCS / "sitemap.md"
	question_index_module.write(
		question_index_path,
		DEFAULT_SITE_DOCS,
		DEFAULT_METADATA_PATH,
		DEFAULT_MKDOCS_PATH,
		dry_run=scope.dry_run,
	)
	outputs.add(question_index_path)
	for subject_key in subject_keys:
		outputs.add(_write_subject_index(subjects[subject_key], DEFAULT_SITE_DOCS, scope.dry_run))
	# Navigation is global and inexpensive. Rebuild it even for a selected
	# subject so its visibility and counts cannot lag behind source content.
	mkdocs_nav_module.update_from_sources(
		metadata_path=str(DEFAULT_METADATA_PATH),
		mkdocs_path=str(DEFAULT_MKDOCS_PATH),
		site_docs_dir=str(DEFAULT_SITE_DOCS),
		dry_run=scope.dry_run,
	)
	outputs.add(DEFAULT_MKDOCS_PATH)
	manifest_path = DEFAULT_SITE_DOCS / "assets/data/selftest_question_manifest.json"
	if not scope.dry_run:
		unrestricted = not any((
			scope.subject,
			scope.topic,
			scope.tasks_csv,
			scope.limit,
		))
		manifest_topic_scope = None
		if not unrestricted:
			manifest_topics = set(selected_topics or ())
			for changed_index in reconciliation["strip_includes"]:
				relative_path = Path(changed_index["path"]).relative_to(DEFAULT_SITE_DOCS)
				if len(relative_path.parts) >= 3:
					manifest_topics.add(TopicRef(relative_path.parts[0], relative_path.parts[1]))
			manifest_topic_scope = {
				(topic.subject, topic.topic) for topic in manifest_topics
			}
		selftest_manifest_module.write_manifest(
			output_path=str(manifest_path),
			site_docs_dir=str(DEFAULT_SITE_DOCS),
			mkdocs_path=str(DEFAULT_MKDOCS_PATH),
			metadata_path=str(DEFAULT_METADATA_PATH),
			topic_scope=manifest_topic_scope,
		)
	outputs.add(manifest_path)
	return outputs

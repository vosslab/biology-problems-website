"""Stage-local stale checks and writers for the unified site build."""

from pathlib import Path

import bioproblems_site.llm_helpers as llm_helpers
import bioproblems_site.bbq_workflow as bbq_workflow
import bioproblems_site.metadata as metadata_module
import bioproblems_site.mkdocs_nav as mkdocs_nav_module
import bioproblems_site.orphan_prune as orphan_prune_module
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
def is_newer_than_any(output_path: Path, input_paths: list[Path]) -> bool:
	"""Return whether any existing direct input is newer than an output."""
	if not output_path.is_file():
		return True
	output_mtime = output_path.stat().st_mtime
	newer = any(path.is_file() and path.stat().st_mtime > output_mtime for path in input_paths)
	return newer


#============================================
def selftests_need_run(topic_ref: TopicRef, scope: BuildScope, changes: BuildChanges) -> bool:
	"""Check direct BBQ-to-self-test relationships for one topic."""
	if scope.full or topic_ref in changes.changed_topics:
		return True
	for source_path in topic_sources(topic_ref):
		output_path = Path(topic_page_module.get_outfile_name(str(source_path), "selftest", "html"))
		if is_newer_than_any(output_path, [source_path]):
			return True
	return False


#============================================
def run_selftests(topic_ref: TopicRef, scope: BuildScope) -> set[Path]:
	"""Write stale self-tests for one topic, unless planning only."""
	sources = topic_sources(topic_ref)
	outputs = {
		Path(topic_page_module.get_outfile_name(str(source_path), "selftest", "html"))
		for source_path in sources
	}
	if scope.dry_run:
		return outputs
	topic_page_module.regenerate_all_selftests(
		topic_ref.subject,
		topic_ref.topic,
		str(DEFAULT_SITE_DOCS),
		verbose=True,
	)
	return outputs


#============================================
def topic_page_needs_run(topic_ref: TopicRef, scope: BuildScope, changes: BuildChanges) -> bool:
	"""Check direct topic-page inputs without scanning unrelated topics."""
	page_path = topic_folder(topic_ref) / "index.md"
	inputs = [DEFAULT_METADATA_PATH]
	inputs.extend(topic_sources(topic_ref))
	for source_path in topic_sources(topic_ref):
		inputs.append(Path(topic_page_module.get_outfile_name(str(source_path), "selftest", "html")))
	if scope.full or topic_ref in changes.changed_topics:
		return True
	return is_newer_than_any(page_path, inputs)


#============================================
def run_topic_page(topic_ref: TopicRef, scope: BuildScope) -> set[Path]:
	"""Render one topic page without creating self-tests or downloads."""
	page_path = topic_folder(topic_ref) / "index.md"
	if scope.dry_run:
		return {page_path}
	model = scope.model or llm_helpers.DEFAULT_OLLAMA_MODEL
	llm_helpers.validate_ollama_model(model)
	client = llm_helpers.create_llm_client(model=model)
	options = topic_page_module.RenderOptions(
		verbose=True,
		llm_client=client,
		generate_downloads=False,
		regenerate_selftests=False,
		render_missing_download_links=True,
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
def downloads_need_run(topic_ref: TopicRef, scope: BuildScope, changes: BuildChanges) -> bool:
	"""Check direct BBQ-to-download relationships for one topic."""
	if scope.full or topic_ref in changes.changed_topics:
		return True
	for source_path in topic_sources(topic_ref):
		for output_path in expected_downloads(source_path):
			if is_newer_than_any(output_path, [source_path]):
				return True
	return False


#============================================
def run_downloads(topic_ref: TopicRef, scope: BuildScope) -> set[Path]:
	"""Write converter-owned download artifacts without rendering a topic page."""
	outputs: set[Path] = set()
	for source_path in topic_sources(topic_ref):
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
		raise RuntimeError(f"Refusing to overwrite {output_path}: no generated marker.")
	if not dry_run:
		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text(text)
	return output_path


#============================================
def run_subject_indexes(scope: BuildScope) -> set[Path]:
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
	task_owned_patterns = bbq_workflow.load_task_owned_patterns()
	orphan_prune_module.reconcile_all(
		str(DEFAULT_SITE_DOCS), scope.dry_run, verbose=True,
		task_owned_pattern_map=task_owned_patterns,
	)
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
	selftest_manifest_module.write_manifest(
		output_path=str(DEFAULT_SITE_DOCS / "assets/data/selftest_question_manifest.json"),
		site_docs_dir=str(DEFAULT_SITE_DOCS),
		mkdocs_path=str(DEFAULT_MKDOCS_PATH),
		metadata_path=str(DEFAULT_METADATA_PATH),
		dry_run=scope.dry_run,
	)
	outputs.add(DEFAULT_SITE_DOCS / "assets/data/selftest_question_manifest.json")
	return outputs

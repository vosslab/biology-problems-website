"""Stable contracts for the unified content-build workflow."""

from pathlib import Path
from types import SimpleNamespace

import pytest

import build_site
import bioproblems_site.bbq_workflow as bbq_workflow
import bioproblems_site.build_coordinator as build_coordinator
import bioproblems_site.build_stages as build_stages
from bioproblems_site.build_contracts import BuildChanges, BuildScope, TopicRef


#============================================
def test_parse_scope_rejects_legacy_subcommands() -> None:
	"""The replacement CLI has no compatibility aliases for pages or BBQ."""
	with pytest.raises(SystemExit):
		build_site.parse_scope(["pages"])


#============================================
def test_parse_scope_resolves_task_and_model_from_repository_root(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""The public command is independent of the caller's current directory."""
	repo_root = Path(__file__).resolve().parents[1]
	monkeypatch.chdir(repo_root / "tests")
	scope = build_site.parse_scope([
		"--tasks", "task_files/biochem_tasks1.csv", "--model", "gemma4:e4b",
	])

	assert scope.tasks_csv == repo_root / "task_files/biochem_tasks1.csv"
	assert scope.model == "gemma4:e4b"


#============================================
def test_task_needs_run_uses_direct_input_mtime(tmp_path: Path) -> None:
	"""An output older than its configured source is selected again."""
	script_path = tmp_path / "generator.py"
	output_path = tmp_path / "bbq-example-questions.txt"
	script_path.write_text("source")
	output_path.write_text("output")
	output_path.touch()
	script_path.touch()
	task = {
		"script": str(script_path),
		"input_path": "",
		"task_file": "",
		"settings_path": "",
		"output": str(output_path),
	}
	assert bbq_workflow.task_needs_run(task, BuildScope())
	assert bbq_workflow.task_needs_run(task, BuildScope(full=True))


#============================================
def test_dry_run_reports_canonical_subject_qualified_topic(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""Planning returns CSV-owned canonical scope without calling generators."""
	output_path = tmp_path / "missing.txt"
	task = {
		"subject": "genetics",
		"topic": "topic01",
		"script": str(tmp_path / "generator.py"),
		"input_path": "",
		"task_file": "",
		"settings_path": "",
		"output": str(output_path),
	}
	monkeypatch.setattr(bbq_workflow, "_load_scoped_tasks", lambda scope: [task])

	def generator_must_not_run(*args: object, **kwargs: object) -> bool:
		raise AssertionError("dry run launched a generator")

	monkeypatch.setattr(bbq_workflow.bbq_runner, "run_task", generator_must_not_run)
	changes = bbq_workflow.run_if_needed(BuildScope(dry_run=True))
	assert changes.changed_topics == {TopicRef("genetics", "topic01")}
	assert changes.changed_subjects == {"genetics"}
	assert changes.changed_files == {output_path}


#============================================
def test_coordinator_orders_downstream_stages(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""BBQ changes propagate only through the ordered downstream stages."""
	topic_ref = TopicRef("genetics", "topic01")
	changes = BuildChanges({topic_ref}, {"genetics"}, set())
	stage_order: list[str] = []
	monkeypatch.setattr(build_coordinator.bbq_workflow, "run_if_needed", lambda scope: changes)
	monkeypatch.setattr(build_coordinator.bbq_workflow, "configured_topics", lambda scope: {topic_ref})
	monkeypatch.setattr(build_stages, "selftests_need_run", lambda topic, scope, result: True)
	monkeypatch.setattr(build_stages, "topic_page_needs_run", lambda topic, scope, result: True)
	monkeypatch.setattr(build_stages, "downloads_need_run", lambda topic, scope, result: True)
	monkeypatch.setattr(build_stages, "run_selftests", lambda topic, scope: stage_order.append("selftests") or set())
	monkeypatch.setattr(build_stages, "run_topic_page", lambda topic, scope: stage_order.append("pages") or set())
	monkeypatch.setattr(build_stages, "run_downloads", lambda topic, scope: stage_order.append("downloads") or set())
	monkeypatch.setattr(build_stages, "run_subject_indexes", lambda scope: stage_order.append("indexes") or set())
	build_coordinator.build_site(BuildScope())
	assert stage_order == ["selftests", "pages", "downloads", "indexes"]


#============================================
def test_limited_full_build_does_not_expand_topic_scope(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Full mode bypasses stale checks but keeps a development limit narrow."""
	topic_ref = TopicRef("genetics", "topic01")
	changes = BuildChanges({topic_ref}, {"genetics"}, set())
	selected_topics: list[TopicRef] = []
	monkeypatch.setattr(build_coordinator.bbq_workflow, "run_if_needed", lambda scope: changes)
	monkeypatch.setattr(build_coordinator.bbq_workflow, "configured_topics", lambda scope: {topic_ref})
	monkeypatch.setattr(build_stages, "selftests_need_run", lambda topic, scope, result: True)
	monkeypatch.setattr(build_stages, "topic_page_needs_run", lambda topic, scope, result: False)
	monkeypatch.setattr(build_stages, "downloads_need_run", lambda topic, scope, result: False)
	monkeypatch.setattr(build_stages, "run_selftests", lambda topic, scope: selected_topics.append(topic) or set())
	monkeypatch.setattr(build_stages, "run_subject_indexes", lambda scope: set())
	build_coordinator.build_site(BuildScope(full=True, limit=1, subject="genetics"))
	assert selected_topics == [topic_ref]


#============================================
def test_subject_dry_run_plans_global_reconciliation_without_mutating_site_files(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A scoped dry run plans every orphan action without changing site files."""
	updates: list[dict[str, object]] = []
	manifest_calls: list[dict[str, object]] = []
	stage_order: list[str] = []
	subject = SimpleNamespace(key="genetics", topics=())
	site_docs_dir = tmp_path / "site_docs"
	orphan_path = site_docs_dir / "genetics/topic01/downloads/selftest-orphan.html"
	orphan_path.parent.mkdir(parents=True)
	orphan_path.write_text("orphaned generated content\n")
	orphan_content = orphan_path.read_text()
	monkeypatch.setattr(
		build_stages.metadata_module,
		"load_topics_metadata",
		lambda **kwargs: ({"genetics": subject}, ["genetics"]),
	)
	monkeypatch.setattr(build_stages, "DEFAULT_SITE_DOCS", site_docs_dir)
	monkeypatch.setattr(
		build_stages,
		"_write_subject_index",
		lambda subject, site_docs_dir, dry_run: (
			stage_order.append("index") or site_docs_dir / subject.key / "index.md"
		),
	)
	monkeypatch.setattr(
		build_stages.mkdocs_nav_module,
		"update_from_sources",
		lambda **kwargs: stage_order.append("nav") or updates.append(kwargs),
	)
	monkeypatch.setattr(
		build_stages.selftest_manifest_module,
		"write_manifest",
		lambda **kwargs: stage_order.append("manifest") or manifest_calls.append(kwargs) or {"questions": []},
	)
	monkeypatch.setattr(
		build_stages.orphan_prune_module.git_paths,
		"tracked_paths_set",
		lambda: set(),
	)
	reconciliation_plans: list[dict] = []
	reconciliation_maps: list[dict[str, object] | None] = []
	original_reconcile_all = build_stages.orphan_prune_module.reconcile_all

	def record_reconciliation(
		site_docs_dir: str,
		dry_run: bool,
		verbose: bool,
		task_owned_pattern_map: dict[str, object] | None = None,
	) -> dict:
		"""Record the real dry-run plan for the scoped workflow assertion."""
		plan = original_reconcile_all(
			site_docs_dir, dry_run, verbose, task_owned_pattern_map,
		)
		reconciliation_plans.append(plan)
		reconciliation_maps.append(task_owned_pattern_map)
		stage_order.append("reconcile")
		return plan

	monkeypatch.setattr(build_stages.orphan_prune_module, "reconcile_all", record_reconciliation)
	global_pattern_map = {str(site_docs_dir / "other/topic02"): []}
	monkeypatch.setattr(
		build_stages.bbq_workflow,
		"load_task_owned_patterns",
		lambda: global_pattern_map,
	)

	build_stages.run_subject_indexes(BuildScope(subject="genetics", dry_run=True))

	assert updates == [{
		"metadata_path": str(build_stages.DEFAULT_METADATA_PATH),
		"mkdocs_path": str(build_stages.DEFAULT_MKDOCS_PATH),
		"site_docs_dir": str(build_stages.DEFAULT_SITE_DOCS),
		"dry_run": True,
	}]
	assert reconciliation_plans[0]["delete_downloads"] == [str(orphan_path)]
	assert reconciliation_plans[0]["delete_sources"] == []
	assert reconciliation_maps == [global_pattern_map]
	assert stage_order == ["reconcile", "index", "nav", "manifest"]
	assert orphan_path.read_text() == orphan_content
	assert manifest_calls[0]["dry_run"] is True


#============================================
@pytest.mark.parametrize("scope, expected_model", [
	(BuildScope(model="test-model"), "test-model"),
	(BuildScope(), build_stages.llm_helpers.DEFAULT_OLLAMA_MODEL),
])
def test_topic_page_validates_effective_model_before_creating_client(
	monkeypatch: pytest.MonkeyPatch,
	scope: BuildScope,
	expected_model: str,
) -> None:
	"""A real topic-page render validates the requested or default model first."""
	topic_ref = TopicRef("genetics", "topic01")
	stage_order: list[str] = []
	monkeypatch.setattr(
		build_stages.llm_helpers,
		"validate_ollama_model",
		lambda model: stage_order.append(f"validate:{model}"),
	)
	monkeypatch.setattr(
		build_stages.llm_helpers,
		"create_llm_client",
		lambda model: stage_order.append(f"client:{model}") or object(),
	)
	monkeypatch.setattr(
		build_stages.topic_page_module,
		"render_all",
		lambda *args, **kwargs: stage_order.append("render"),
	)

	build_stages.run_topic_page(topic_ref, scope)

	assert stage_order == [
		f"validate:{expected_model}", f"client:{expected_model}", "render"
	]


#============================================
def test_dry_run_topic_page_does_not_validate_or_create_client(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Planning a topic page does not contact Ollama or create a client."""
	topic_ref = TopicRef("genetics", "topic01")

	def ollama_must_not_run(model: str) -> None:
		raise AssertionError(f"dry run validated {model}")

	def client_must_not_run(model: str) -> object:
		raise AssertionError(f"dry run created client for {model}")

	monkeypatch.setattr(build_stages.llm_helpers, "validate_ollama_model", ollama_must_not_run)
	monkeypatch.setattr(build_stages.llm_helpers, "create_llm_client", client_must_not_run)

	assert build_stages.run_topic_page(topic_ref, BuildScope(dry_run=True)) == {
		build_stages.topic_folder(topic_ref) / "index.md"
	}


#============================================
def test_expected_download_paths_do_not_create_downloads_directory(tmp_path: Path) -> None:
	"""Expected-path checks remain pure until the download stage writes artifacts."""
	source_path = tmp_path / "bbq-example-questions.txt"
	source_path.write_text("MC\tquestion\n")

	build_stages.expected_downloads(source_path)

	assert not (tmp_path / "downloads").exists()


#============================================
def test_all_task_mode_alone_sets_the_batch_question_limit(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""Only all-task selection supplies the historical 199-question limit."""
	output_path = tmp_path / "missing.txt"
	task = {
		"subject": "genetics",
		"topic": "topic01",
		"script": str(tmp_path / "generator.py"),
		"input_path": "",
		"task_file": "",
		"settings_path": "",
		"output": str(output_path),
		"args": [],
	}
	seen_args: list[list[object]] = []
	monkeypatch.setattr(bbq_workflow, "_load_scoped_tasks", lambda scope: [task.copy()])
	monkeypatch.setattr(bbq_workflow.bbq_config, "load_bbq_config", lambda path: {})
	monkeypatch.setattr(bbq_workflow.bbq_config, "check_pythonpath", lambda settings: (True, ""))
	monkeypatch.setattr(bbq_workflow.bbq_config, "build_pythonpath", lambda settings: "")
	monkeypatch.setattr(bbq_workflow.bbq_outputs, "rotate_log", lambda path: None)
	monkeypatch.setattr(
		bbq_workflow.bbq_runner,
		"run_task",
		lambda task, *args, **kwargs: seen_args.append(task.get("extra_args", [])) or True,
	)

	bbq_workflow.run_if_needed(BuildScope())
	bbq_workflow.run_if_needed(BuildScope(tasks_csv=tmp_path / "one.csv"))

	assert seen_args == [["-x", "199"], []]

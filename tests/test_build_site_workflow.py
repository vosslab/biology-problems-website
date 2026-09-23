"""Stable contracts for the unified content-build workflow."""

from pathlib import Path
from types import SimpleNamespace

import pytest

import build_site
import bioproblems_site.bbq_workflow as bbq_workflow
import bioproblems_site.build_coordinator as build_coordinator
import bioproblems_site.build_stages as build_stages
import bioproblems_site.metadata as metadata
from bioproblems_site.build_contracts import BuildChanges, BuildScope, TaskBuildResult, TopicRef


#============================================
def test_parse_scope_rejects_legacy_subcommands() -> None:
	"""The replacement CLI has no compatibility aliases for pages or BBQ."""
	with pytest.raises(SystemExit):
		build_site.parse_scope(["pages"])


#============================================
def test_parse_scope_supports_task_option_and_short_options(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""The public selector aliases resolve repository paths from any working directory."""
	repo_root = Path(__file__).resolve().parents[1]
	monkeypatch.chdir(repo_root / "tests")
	scope = build_site.parse_scope([
		"-S", "genetics", "-T", "topic01", "-t", "task_files/genetics_tasks1.csv", "-l", "2",
		"-R", "-n", "-F", "-b", "codex", "-m", "gpt-5-codex",
	])

	assert scope.tasks_csv == repo_root / "task_files/genetics_tasks1.csv"
	assert scope.subject == "genetics"
	assert scope.topic == "topic01"
	assert scope.limit == 2
	assert scope.shuffle is True
	assert scope.dry_run is True
	assert scope.full is True
	assert scope.backend == "codex"
	assert scope.model == "gpt-5-codex"
	assert build_site.parse_scope([
		"--task", "task_files/genetics_tasks1.csv",
	]).tasks_csv == scope.tasks_csv
	with pytest.raises(ValueError, match="--topic requires --subject"):
		build_site.parse_scope(["-T", "topic01"])


#============================================
def test_topic_filter_intersects_subject_and_task_rows(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A focused subject/topic selection excludes other CSV topics and subjects."""
	task_csv = tmp_path / "tasks.csv"
	task_csv.write_text(
		"subject,topic,script,flags,input,notes\n"
		"genetics,topic01,first.py,,,\n"
		"genetics,topic02,second.py,,,\n"
		"biochemistry,topic01,third.py,,,\n"
	)
	topic01 = metadata.Topic("topic01", "Topic 1", "", None, True, None)
	topic02 = metadata.Topic("topic02", "Topic 2", "", None, True, None)
	subjects = {
		"genetics": metadata.Subject("genetics", "Genetics", "", (topic01, topic02)),
		"biochemistry": metadata.Subject("biochemistry", "Biochemistry", "", (topic01,)),
	}
	monkeypatch.setattr(bbq_workflow, "DEFAULT_SETTINGS_PATH", tmp_path / "settings.yml")
	monkeypatch.setattr(bbq_workflow.bbq_config, "load_bbq_config", lambda path: {})
	monkeypatch.setattr(
		bbq_workflow.metadata_module,
		"load_topics_metadata",
		lambda: (subjects, ["genetics", "biochemistry"]),
	)
	monkeypatch.setattr(
		bbq_workflow.bbq_config.bioproblems_site.git_paths,
		"get_repo_root",
		lambda: str(tmp_path),
	)

	task_rows = bbq_workflow._load_scoped_task_rows(
		BuildScope(subject="genetics", topic="topic01", tasks_csv=task_csv)
	)

	assert [
		(task["subject"], task["topic"])
		for task_row in task_rows
		for task in task_row
	] == [("genetics", "topic01")]


#============================================
def test_codex_backend_selects_codex_transport(monkeypatch: pytest.MonkeyPatch) -> None:
	"""The Codex backend maps to the wrapper's Codex transport."""
	seen: dict[str, object] = {}

	class FakeTransport:
		def __init__(self, model: str | None) -> None:
			seen["model"] = model

	class FakeClient:
		def __init__(self, transports: list[object], quiet: bool) -> None:
			seen["transport"] = transports[0]
			seen["quiet"] = quiet

	monkeypatch.setattr(build_stages.llm_helpers.llm, "CodexTransport", FakeTransport)
	monkeypatch.setattr(build_stages.llm_helpers.llm, "LLMClient", FakeClient)

	build_stages.llm_helpers.create_llm_client("codex", "gpt-5-codex")

	assert isinstance(seen["transport"], FakeTransport)
	assert seen["model"] == "gpt-5-codex"
	assert seen["quiet"] is True


#============================================
def test_shuffle_is_applied_before_limit(monkeypatch: pytest.MonkeyPatch) -> None:
	"""Random selection shuffles complete CSV rows before applying the row limit."""
	task_rows = [
		[{"subject": "genetics", "topic": "0", "output": "single"}],
		[
			{"subject": "genetics", "topic": "1", "output": "match"},
			{"subject": "genetics", "topic": "1", "output": "multiple-choice"},
		],
		[{"subject": "genetics", "topic": "2", "output": "single"}],
	]
	monkeypatch.setattr(bbq_workflow.random, "shuffle", lambda values: values.reverse())
	scope = build_site.parse_scope(["--shuffle", "--limit", "2"])

	selected_rows = bbq_workflow._apply_task_selection(
		task_rows, BuildScope(shuffle=scope.shuffle, limit=scope.limit),
	)

	assert [[task["topic"] for task in row] for row in selected_rows] == [["2"], ["1", "1"]]
	assert [task["output"] for task in selected_rows[1]] == ["match", "multiple-choice"]


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
	monkeypatch.setattr(bbq_workflow, "_load_scoped_task_rows", lambda scope: [[task]])

	def generator_must_not_run(*args: object, **kwargs: object) -> bool:
		raise AssertionError("dry run launched a generator")

	monkeypatch.setattr(bbq_workflow.bbq_runner, "run_task", generator_must_not_run)
	changes = bbq_workflow.run_if_needed(BuildScope(dry_run=True))
	assert changes.changed_topics == {TopicRef("genetics", "topic01")}
	assert changes.changed_subjects == {"genetics"}
	assert changes.changed_files == {output_path}


#============================================
def test_csv_row_finishes_row_artifacts_before_next_generator_and_page_runs_once(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""Row outputs precede the next generator; each aggregate page renders once at the end."""
	tasks_dir = tmp_path / "task_files"
	tasks_dir.mkdir()
	(tasks_dir / "tasks.csv").write_text(
		"subject,topic,script,flags,input,notes\n"
		"genetics,topic01,PAIR,,,\n"
		"genetics,topic01,ADDITIONAL,,,\n"
		"genetics,topic02,NEXT,,,\n"
	)
	site_docs_dir = tmp_path / "site_docs"
	settings = {
		"paths": {"bp_root": str(tmp_path)},
		"script_aliases": {
			"PAIR": [str(tmp_path / "match_generator.py"), str(tmp_path / "mc_generator.py")],
			"ADDITIONAL": str(tmp_path / "additional_generator.py"),
			"NEXT": str(tmp_path / "next_generator.py"),
		},
	}
	topics = tuple(
		metadata.Topic(key=key, title=key, description="", libretexts=None, visible=True, alias=None)
		for key in ("topic01", "topic02")
	)
	subjects = {
		"genetics": metadata.Subject(key="genetics", title="Genetics", description="", topics=topics),
	}
	events: list[str] = []
	monkeypatch.chdir(tmp_path)
	monkeypatch.setattr(bbq_workflow, "DEFAULT_TASK_DIR", tasks_dir)
	monkeypatch.setattr(bbq_workflow, "DEFAULT_SETTINGS_PATH", tmp_path / "settings.yml")
	monkeypatch.setattr(bbq_workflow.bbq_config, "load_bbq_config", lambda path: settings)
	monkeypatch.setattr(
		bbq_workflow.metadata_module,
		"load_topics_metadata",
		lambda: (subjects, ["genetics"]),
	)
	monkeypatch.setattr(
		bbq_workflow.bbq_config.bioproblems_site.git_paths,
		"get_repo_root",
		lambda: str(tmp_path),
	)
	monkeypatch.setattr(build_stages, "DEFAULT_SITE_DOCS", site_docs_dir)
	monkeypatch.setattr(bbq_workflow, "task_needs_run", lambda task, scope: True)
	monkeypatch.setattr(bbq_workflow.bbq_config, "check_pythonpath", lambda value: (True, ""))
	monkeypatch.setattr(bbq_workflow.bbq_config, "build_pythonpath", lambda value: "")

	def run_task(task: dict[str, object], *args: object, **kwargs: object) -> bool:
		script_name = Path(str(task["script"])).stem
		events.append(f"bbq {script_name}")
		output_path = Path(str(task["output_dir"])) / f"bbq-{script_name}-questions.txt"
		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text("question\n")
		task["output"] = str(output_path)
		return True

	monkeypatch.setattr(bbq_workflow.bbq_runner, "run_task", run_task)
	monkeypatch.setattr(build_stages, "selftests_need_run", lambda *args: True)
	monkeypatch.setattr(build_stages, "topic_page_needs_run", lambda *args: True)
	monkeypatch.setattr(build_stages, "downloads_need_run", lambda *args: True)

	def record_selftests(
		topic: TopicRef,
		scope: BuildScope,
		sources: set[Path],
	) -> set[Path]:
		events.append(f"selftest {topic.topic} ({len(sources)})")
		return set()

	monkeypatch.setattr(
		build_stages, "run_selftests", record_selftests,
	)
	monkeypatch.setattr(
		build_stages, "run_topic_page",
		lambda topic, scope: events.append(f"page {topic.topic}") or set(),
	)
	def record_downloads(
		topic: TopicRef,
		scope: BuildScope,
		sources: set[Path],
	) -> set[Path]:
		events.append(f"downloads {topic.topic} ({len(sources)})")
		return set()

	monkeypatch.setattr(
		build_stages, "run_downloads", record_downloads,
	)
	monkeypatch.setattr(build_stages, "run_subject_indexes", lambda scope, selected=None: set())

	build_coordinator.build_site(BuildScope(subject="genetics"))

	assert events == [
		"bbq match_generator",
		"bbq mc_generator",
		"selftest topic01 (2)",
		"downloads topic01 (2)",
		"bbq additional_generator",
		"selftest topic01 (1)",
		"downloads topic01 (1)",
		"bbq next_generator",
		"selftest topic02 (1)",
		"downloads topic02 (1)",
		"page topic01",
		"page topic02",
	]


#============================================
def test_failed_csv_row_stops_before_downstream_and_later_generators(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A failed generator prevents local stages and later CSV rows from running."""
	task_rows = [
		[
			{
				"subject": "genetics",
				"topic": "topic01",
				"script": "first_generator.py",
				"args": [],
				"output": "",
				"output_dir": str(tmp_path / "site_docs/genetics/topic01"),
			}
		],
		[
			{
				"subject": "genetics",
				"topic": "topic02",
				"script": "second_generator.py",
				"args": [],
				"output": "",
				"output_dir": str(tmp_path / "site_docs/genetics/topic02"),
			}
		],
	]
	events: list[str] = []
	monkeypatch.chdir(tmp_path)
	monkeypatch.setattr(bbq_workflow, "_load_scoped_task_rows", lambda scope: task_rows)
	monkeypatch.setattr(bbq_workflow, "task_needs_run", lambda task, scope: True)
	monkeypatch.setattr(bbq_workflow.bbq_config, "load_bbq_config", lambda path: {})
	monkeypatch.setattr(bbq_workflow.bbq_config, "check_pythonpath", lambda settings: (True, ""))
	monkeypatch.setattr(bbq_workflow.bbq_config, "build_pythonpath", lambda settings: "")
	monkeypatch.setattr(build_stages, "selftests_need_run", lambda *args: True)
	monkeypatch.setattr(build_stages, "topic_page_needs_run", lambda *args: True)
	monkeypatch.setattr(build_stages, "downloads_need_run", lambda *args: True)
	monkeypatch.setattr(
		build_stages,
		"run_selftests",
		lambda topic, scope, sources: events.append(f"selftest {topic.topic}") or set(),
	)
	monkeypatch.setattr(
		build_stages,
		"run_topic_page",
		lambda topic, scope: events.append(f"page {topic.topic}") or set(),
	)
	monkeypatch.setattr(
		build_stages,
		"run_downloads",
		lambda topic, scope, sources: events.append(f"downloads {topic.topic}") or set(),
	)

	def fail_first_task(task: dict[str, object], *args: object, **kwargs: object) -> bool:
		events.append(f"generator {task['topic']}")
		return False

	monkeypatch.setattr(bbq_workflow.bbq_runner, "run_task", fail_first_task)
	with pytest.raises(RuntimeError, match="BBQ task failed"):
		build_coordinator.build_site(BuildScope(subject="genetics"))

	assert events == ["generator topic01"]


#============================================
def test_missing_download_is_rebuilt_for_a_fresh_bbq_source(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""A missing converter artifact is repaired even when its BBQ source is current."""
	topic_ref = TopicRef("genetics", "topic01")
	site_docs = tmp_path / "site_docs"
	source_path = site_docs / "genetics/topic01/bbq-example-questions.txt"
	output_path = site_docs / "genetics/topic01/downloads/canvas-example.zip"
	source_path.parent.mkdir(parents=True)
	source_path.write_text("question\n")
	monkeypatch.setattr(build_stages, "DEFAULT_SITE_DOCS", site_docs)
	monkeypatch.setattr(build_stages, "topic_folder", lambda topic: source_path.parent)
	monkeypatch.setattr(build_stages, "expected_downloads", lambda source: {output_path})
	generated_sources: list[Path] = []

	def create_downloads(source: str, verbose: bool = True) -> None:
		generated_sources.append(Path(source))
		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text("converted")

	monkeypatch.setattr(build_stages.topic_page_module, "generate_download_artifacts", create_downloads)
	assert build_stages.downloads_need_run(
		topic_ref,
		BuildScope(),
		BuildChanges(),
		{source_path},
	)

	build_stages.run_downloads(topic_ref, BuildScope(), {source_path})

	assert generated_sources == [source_path]
	assert output_path.read_text() == "converted"


#============================================
def test_limited_full_build_does_not_expand_topic_scope(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Full mode bypasses stale checks but keeps a development limit narrow."""
	topic_ref = TopicRef("genetics", "topic01")
	selected_topics: list[TopicRef] = []
	monkeypatch.setattr(
		build_coordinator.bbq_workflow,
		"iter_task_results",
		lambda scope: iter([TaskBuildResult(topic_ref, needs_run=True)]),
	)
	monkeypatch.setattr(build_stages, "selftests_need_run", lambda *args: True)
	monkeypatch.setattr(build_stages, "topic_page_needs_run", lambda topic, scope, result: False)
	monkeypatch.setattr(build_stages, "downloads_need_run", lambda *args: False)
	monkeypatch.setattr(
		build_stages, "run_selftests",
		lambda topic, scope, sources: selected_topics.append(topic) or set(),
	)
	monkeypatch.setattr(build_stages, "run_subject_indexes", lambda scope, selected=None: set())
	build_coordinator.build_site(BuildScope(full=True, limit=1, subject="genetics"))
	assert selected_topics == [topic_ref]


#============================================
def test_full_topic_build_stays_within_selected_topic(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""A full subject/topic selection does not expand to sibling topics."""
	topics = (
		metadata.Topic("topic01", "Topic 1", "", None, True, None),
		metadata.Topic("topic02", "Topic 2", "", None, True, None),
	)
	subjects = {
		"genetics": metadata.Subject("genetics", "Genetics", "", topics),
	}
	selected_pages: list[TopicRef] = []
	monkeypatch.setattr(
		build_coordinator.metadata_module,
		"load_topics_metadata",
		lambda **kwargs: (subjects, ["genetics"]),
	)
	monkeypatch.setattr(build_coordinator.bbq_workflow, "iter_task_results", lambda scope: iter([]))
	monkeypatch.setattr(build_stages, "topic_sources", lambda topic: set())
	monkeypatch.setattr(build_stages, "selftests_need_run", lambda *args: False)
	monkeypatch.setattr(build_stages, "topic_page_needs_run", lambda *args: True)
	monkeypatch.setattr(
		build_stages,
		"run_topic_page",
		lambda topic, scope: selected_pages.append(topic) or set(),
	)
	monkeypatch.setattr(build_stages, "downloads_need_run", lambda *args: False)
	monkeypatch.setattr(build_stages, "run_subject_indexes", lambda scope, selected=None: set())

	build_coordinator.build_site(
		BuildScope(full=True, subject="genetics", topic="topic01")
	)

	assert selected_pages == [TopicRef("genetics", "topic01")]


#============================================
def test_unreadable_task_inventory_skips_pruning_and_preserves_sources(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
	capsys: pytest.CaptureFixture[str],
) -> None:
	"""Uncertain task ownership must not delete sources or block index updates."""
	task_dir = tmp_path / "task_files"
	task_dir.mkdir()
	(task_dir / "broken.csv").write_text("subject,topic,scrip\ngenetics,topic01,generate.py\n")
	settings_path = tmp_path / "bbq_settings.yml"
	settings_path.write_text("{}\n")
	site_docs_dir = tmp_path / "site_docs"
	topic_dir = site_docs_dir / "genetics" / "topic01"
	topic_dir.mkdir(parents=True)
	source_path = topic_dir / "bbq-preserve-this-questions.txt"
	source_path.write_text("MC\tOriginal question\n")
	subject = metadata.Subject("genetics", "Genetics", "", ())

	monkeypatch.setattr(build_stages, "DEFAULT_SITE_DOCS", site_docs_dir)
	monkeypatch.setattr(bbq_workflow, "DEFAULT_TASK_DIR", task_dir)
	monkeypatch.setattr(bbq_workflow, "DEFAULT_SETTINGS_PATH", settings_path)
	monkeypatch.setattr(bbq_workflow.bbq_config, "load_bbq_config", lambda path: {})
	monkeypatch.setattr(
		build_stages.metadata_module,
		"load_topics_metadata",
		lambda **kwargs: ({"genetics": subject}, ["genetics"]),
	)
	monkeypatch.setattr(build_stages.question_index_module, "write", lambda *args, **kwargs: None)
	monkeypatch.setattr(
		build_stages,
		"_write_subject_index",
		lambda subject, site_docs, dry_run: site_docs / "genetics" / "index.md",
	)
	monkeypatch.setattr(
		build_stages.mkdocs_nav_module,
		"update_from_sources",
		lambda **kwargs: None,
	)
	monkeypatch.setattr(
		build_stages.orphan_prune_module,
		"reconcile_all",
		lambda *args, **kwargs: pytest.fail("unsafe orphan pruning was attempted"),
	)

	build_stages.run_subject_indexes(BuildScope(subject="genetics", dry_run=True))

	assert source_path.read_text() == "MC\tOriginal question\n"
	assert "skipping orphan reconciliation" in capsys.readouterr().out


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
		lambda **kwargs: (
			stage_order.append("manifest")
			or manifest_calls.append(kwargs)
			or {"questions": []}
		),
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

	stage_outputs = build_stages.run_subject_indexes(BuildScope(subject="genetics", dry_run=True))

	assert updates == [{
		"metadata_path": str(build_stages.DEFAULT_METADATA_PATH),
		"mkdocs_path": str(build_stages.DEFAULT_MKDOCS_PATH),
		"site_docs_dir": str(build_stages.DEFAULT_SITE_DOCS),
		"dry_run": True,
	}]
	assert reconciliation_plans[0]["delete_downloads"] == [str(orphan_path)]
	assert reconciliation_plans[0]["delete_sources"] == []
	assert reconciliation_maps == [global_pattern_map]
	assert stage_order == ["reconcile", "index", "nav"]
	assert orphan_path.read_text() == orphan_content
	assert manifest_calls == []
	manifest_path = site_docs_dir / "assets/data/selftest_question_manifest.json"
	assert manifest_path in stage_outputs


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
	monkeypatch.setattr(bbq_workflow, "_load_scoped_task_rows", lambda scope: [[task.copy()]])
	monkeypatch.setattr(bbq_workflow.bbq_config, "load_bbq_config", lambda path: {})
	monkeypatch.setattr(bbq_workflow.bbq_config, "check_pythonpath", lambda settings: (True, ""))
	monkeypatch.setattr(bbq_workflow.bbq_config, "build_pythonpath", lambda settings: "")
	monkeypatch.setattr(
		bbq_workflow.bbq_runner,
		"run_task",
		lambda task, *args, **kwargs: seen_args.append(task.get("extra_args", [])) or True,
	)

	bbq_workflow.run_if_needed(BuildScope())
	bbq_workflow.run_if_needed(BuildScope(tasks_csv=tmp_path / "one.csv"))

	assert seen_args == [["-x", "199"], []]

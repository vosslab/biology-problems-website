# Root CLI, script consolidation, and pytest cleanup

## Context

Scripts are scattered across the repo root, `tools/`, `devel/`, and `bbq_control/` with no single
inventory saying what each does. `run_bbq_tasks.py` (1588 lines) carries the entire BBQ runner
in a root script, violating the root-script contract (root = short orchestrators over
package-owned behavior). Three vendored gates fail: `tests/test_function_typing.py`
(22 files, ~200 missing annotations), `tests/test_support_dirs_not_imported.py`
(`tools/dump_topics_csv.py` imports `bioproblems_site`), and
`tests/test_bash_script_line_limit.py` (`run_playwright_tests.sh` is 122/100 lines).
Everything else passes (5585 cases).

Governing rules (from `docs/REPO_STYLE.md`, `devel/DEVEL_README.md`, `tools/TOOLS_README.md`,
`docs/CODE_ARCHITECTURE.md`, and the user):

- Repo root exposes only primary workflows and essential environment entrypoints, as short
  orchestrators. Root count is diagnostic, not a target.
- `bioproblems_site/` owns reusable generation and repository-domain logic.
- `devel/` owns maintainer command surfaces and repository-engineering behavior; it invokes
  package logic rather than housing it. Local commands sit beside vendored ones.
- `tools/` holds standalone domain utilities with no repo-package imports.
- Single user, pre-production: no compatibility aliases, no legacy entrypoints.

Outcome: the root holds one application CLI (`bioproblems.py`, subcommands `pages` and
`bbq`) plus `source_me.sh` and config/data files. Secondary maintenance lives behind
`devel/site_maint.py`; browser tests behind `devel/run_playwright_tests.sh`; `bbq_control/`
dissolved; redundant wrappers removed. `docs/FILE_STRUCTURE.md` is the authoritative script
inventory; `pytest tests/` is green.

Script count (non-test `.py`/`.sh`, excluding the git-ignored `bbq_converter.py` symlink):
33 today (6 root, 7 tools, 18 devel, 2 bbq_control) -> 24 after (2 root, 2 tools, 20 devel).
Repository-owned: 7 (`bioproblems.py`, `source_me.sh`, 2 tools, `devel/site_maint.py`,
`devel/run_playwright_tests.sh`, `devel/setup_playwright.sh`); 17 existing vendored `devel/`
files are untouched.

## Findings that shape the plan

- `devel/`: 16 of 17 files are vendored; only `setup_playwright.sh` is local, and the
  (vendored) `docs/PLAYWRIGHT_USAGE.md` documents it, so it stays.
- User never runs `run_web_server.sh` (uses `mkdocs serve`) or `run_playwright_tests.sh`.
- `generate_pages.py` is already thin (158 lines: argparse + flag normalization + `pipeline.run`).
- `run_bbq_tasks.py` has identifiable ownership clusters for timing, configuration and CSV
  loading, output detection and logging, command execution, the Textual TUI, and the plain-mode
  loop. Those source regions are discovery evidence only. The extracted modules must be checked
  against call relationships and shared state so `bbq_runner`, `bbq_outputs`, and `bbq_config`
  do not acquire circular imports. `textual` is already a required dependency
  (`pip_requirements.txt`), so the `try/except ImportError` guard goes away.
- `tests/test_run_bbq_alias.py` imports `run_bbq_tasks.load_tasks_csv`; the only test coupling
  to the root script.
- `ignore_gen_content.sh` and `tools/reset_bbq.sh` duplicate each other; the git-aware one wins.
- `tools/check_question_counts.sh` = `wc -l` per `bbq-*.txt`; `bioproblems_site/scanner.py`
  already owns question scanning (files per topic); extend it with a per-file line count.
- `flow_for_html_generation.txt` names a nonexistent `bb_text_to_html.py`.
- `bbq_control/all_tasks.py` and `all_tasks.sh` hard-code a python3.12 path.

## Goal 1: organization

Use Git-aware moves for history preservation when the local Git executable is available; if a
host tool gate prevents `git mv`, use a plain non-destructive rename and verify that Git detects
the content-preserving rename afterward. Use Git-aware deletion when available.

### Root after the plan

| File | Role |
| --- | --- |
| `bioproblems.py` | application CLI: `pages` (site generation) and `bbq` (question generation) |
| `source_me.sh` | environment contract |
| `topics_metadata.yml`, `bbq_settings.yml`, `task_files/`, `mkdocs.yml` | config and data |

### Root CLI: `bioproblems.py`

Short orchestrator (target under 60 lines): shebang, module docstring, `build_parser() ->
argparse.ArgumentParser` that creates `subparsers(dest="command", required=True)` and calls
`bioproblems_site.pages_cli.add_arguments(sub)` and `bioproblems_site.bbq_cli.add_arguments(sub)`;
`main() -> None` parses, dispatches `{"pages": pages_cli.run, "bbq": bbq_cli.run}[args.command](args)`,
and raises `SystemExit(code)` on non-zero. No generation logic.

Invocations:

```bash
source source_me.sh && python3 bioproblems.py pages            # subject indexes + nav
source source_me.sh && python3 bioproblems.py pages -T -G      # topic pages + downloads
source source_me.sh && python3 bioproblems.py pages --full
source source_me.sh && python3 bioproblems.py bbq -t task_files/other_tasks.csv --flat
source source_me.sh && python3 bioproblems.py bbq --all-tasks --max-questions 199
source source_me.sh && python3 bioproblems.py bbq --list-tasks
```

### Package modules (new or extended)

| Module | Owns | Source |
| --- | --- | --- |
| `bioproblems_site/pages_cli.py` | `add_arguments(subparsers)` (every flag from `generate_pages.parse_args`, same dests/help, the two `parser.error` checks), `run(args) -> int` (flag normalization block + Ollama preflight + topic-filter resolution + `pipeline.run`) | extracted from `generate_pages.py`; behavior checked against the explicit CLI changes |
| `bioproblems_site/bbq_cli.py` | `add_arguments(subparsers)` (existing `-t/-s/-n/-F/-x/-l/-R` plus new `-a/--all-tasks`, `--list-tasks`), `run(args) -> int`: batch/list dispatch to `bbq_batch`, else the single-CSV setup from `run_bbq_tasks.main` (settings, pythonpath check, metadata load, task shaping) then `bbq_tui.run_app` or `bbq_runner.run_tasks_plain` | `run_bbq_tasks.py` 127-165, 1448-1582 |
| `bioproblems_site/bbq_config.py` | `find_settings_yaml`, `load_bbq_config`, alias/env/pythonpath helpers, `expand_text`, `normalize_path`, `add_input_args`, missing-message helpers, `load_tasks`, `load_tasks_csv` | 168-520 (~350 lines) |
| `bioproblems_site/bbq_outputs.py` | `ensure_parent_dir` ... `count_output_lines_path`, `cleanup_dry_run_output`, `log_line`, `log_error`, `rotate_log` | 520-780 (~260 lines) |
| `bioproblems_site/bbq_runner.py` | `color`, `COLOR_*`, timing helpers (`format_elapsed_time`, `get_slowest_task_timings`, `write_task_timing`, `print_slowest_task_timings`, `TASK_TIMING_LOG_ENV`), `build_command`, `task_label`, `shorten_text`, `RunContext`, `run_pgml_generation`, `copy_sister_pgml`, `run_task_capture`, `run_task`, `run_tasks_plain(tasks, args, run_context) -> int` (the loop from `main`) | 58-125, 783-1270, 1529-1582 (~650 lines) |
| `bioproblems_site/bbq_tui.py` | `BBQTaskApp` and `run_app(tasks, args, run_context) -> int`; imports `textual` and `rich` at module top (no try/except) | 1275-1445 (~170 lines) |
| `bioproblems_site/bbq_batch.py` | `find_task_files`, `build_runner_command`, `run_task_file`, `print_slowest_task_timings` (batch-wide, reads the JSONL log), `run_all_task_files(args) -> int`, `list_task_files() -> int`; `sys.executable` replaces `PYTHON312`; per-CSV subprocess runs `bioproblems.py bbq --flat --settings ... --tasks ...` via `bash -c "source source_me.sh && ..."` so per-file isolation and the `BBQ_TASK_TIMING_LOG` env contract stay identical | `bbq_control/all_tasks.py` |
| `bioproblems_site/topics_csv.py` | `dump_topics_to_csv(metadata_path, mkdocs_path, output_path) -> None` | `tools/dump_topics_csv.py` |
| `bioproblems_site/biomacromolecule_data.py` | YAML merge + JS emit; external source paths become function parameters with current defaults | `tools/build_biomacromolecule_data.py` (tabs, annotations) |
| `bioproblems_site/deletion_wordbank.py` | `filter_words(words, length) -> list`, `update_wordbank_block(js_path, words) -> None` | `tools/build_deletion_mutants_wordbank.py` (drop `from __future__`) |
| `bioproblems_site/scanner.py` (extend) | `count_bbq_lines(site_docs_dir) -> list[tuple[int, str]]` sorted descending | `tools/check_question_counts.sh` |

The extraction preserves existing behavior except for the explicitly listed interface and
behavior changes: batch shuffle becomes opt-in, Textual is a required dependency, the Python
interpreter comes from `sys.executable`, the root CLI and question-count implementation change,
builder paths become parameters, and batch invocation goes through `bioproblems.py bbq`. Verify
each moved responsibility by contract and call relationship, not by requiring verbatim bodies.
All new modules stay under 900 lines (largest is `bbq_runner.py` at ~650).

`bbq` CLI contract (`bbq_cli.add_arguments`):

- `-t/--tasks`, `-a/--all-tasks`, `--list-tasks`: one mutually exclusive group, required.
- `-a/--all-tasks`: run every `task_files/*.csv` in filename order, one subprocess per CSV,
  then print the ten slowest tasks batch-wide. Exit 0 if all succeed; 1 if any fails or no
  CSV exists.
- `--list-tasks`: print repo-relative `task_files/*.csv` paths, exit 0, run nothing.
- Forwarded to each batch subprocess: `-x/--max-questions` (batch default 199), `-l/--limit`,
  `-R/--shuffle`, `-n/--dry-run`; `-F/--flat` always. Shuffle is opt-in in both modes (old
  batch shuffle-on default goes away; noted in changelog).
- `-s/--settings`: honored if given, else `<repo_root>/bbq_settings.yml`.
  `find_settings_yaml` drops the `bbq_control` candidate.
- The shared parser leaves `--max-questions` as `None` by default. Batch dispatch applies 199
  explicitly before constructing subprocess arguments; single-CSV dispatch keeps its existing
  unset behavior.
- Single-CSV behavior, TUI selection (`textual` present, not `--flat`, stdout is a tty), logs
  (`bbq_generation.log`, `bbq_generation_errors.log` in CWD), and exit codes are unchanged.

### One maintainer CLI: `devel/site_maint.py`

Thin surface: `subparsers(dest="command", required=True)`, one `run_<name>(args) -> int` per
subcommand that resolves paths via `bioproblems_site.git_paths.get_repo_root`, calls the
package function, prints one result line, and returns an exit status; `main() -> None` dispatches
via a dict. Judge thinness by keeping argument handling, path resolution, dispatch, and reporting
in the CLI while leaving domain implementation in the package. Shebang + exec bit.

| Subcommand | Calls | Replaces |
| --- | --- | --- |
| `topics-csv [-o OUT] [-m META] [-k MKDOCS]` | `topics_csv.dump_topics_to_csv` | `tools/dump_topics_csv.py` |
| `count-questions` | `scanner.count_bbq_lines` | `tools/check_question_counts.sh` |
| `build-biomacromolecule-data` | `biomacromolecule_data.write_js` | `tools/build_biomacromolecule_data.py` |
| `build-deletion-wordbank [--length N] [--source PATH]` | `deletion_wordbank.*` | `tools/build_deletion_mutants_wordbank.py` |
| `reset-generated` | in the CLI itself: `git checkout -- <pathspecs>` then `git clean -f -- <pathspecs>` via `subprocess.run`, identical pathspec list | `ignore_gen_content.sh` |

`reset-generated` stays in `devel/`: git hygiene is repository engineering, not site logic.

### Other moves

| Current | Action | Reason |
| --- | --- | --- |
| `run_playwright_tests.sh` | `git mv` -> `devel/run_playwright_tests.sh`, trimmed under 100 lines | browser testing is repository engineering; user never runs it directly. Update the comment in `playwright.config.ts:10` and any `docs/PLAYWRIGHT_USAGE.md` local section that names the root path |
| `bbq_control/task_files/` | `git mv` -> `task_files/` | user request |
| `bbq_control/bbq_settings.yml` | `git mv` -> `bbq_settings.yml` | root config beside `topics_metadata.yml` |
| `bbq_control/USAGE.md` | `git mv` -> `docs/BBQ_TASKS_USAGE.md`, rewritten for `bioproblems.py bbq` | docs live in `docs/` |
| `bbq_control/` | `rmdir` once empty | |

`tools/` keeps `csv_topic_sorter.py` and `ultra_transfer_audit.py` (standalone, no package
imports). `csv_topic_sorter.py` docstring/help mention of `run_bbq_tasks.py` -> `bioproblems.py bbq`.

### Deletions (`git rm`), after the replacements are verified

`generate_pages.py`, `run_bbq_tasks.py`, `run_web_server.sh` (adds nothing over
`mkdocs serve`), `ignore_gen_content.sh`, `flow_for_html_generation.txt`,
`tools/dump_topics_csv.py`, `tools/check_question_counts.sh`, `tools/reset_bbq.sh`,
`tools/build_biomacromolecule_data.py`, `tools/build_deletion_mutants_wordbank.py`,
`bbq_control/all_tasks.py`, `bbq_control/all_tasks.sh`.

### `.gitignore`

`bbq_control/bbq_generation.log*` -> `/bbq_generation.log*`;
`bbq_control/bbq_generation_errors.log` -> `/bbq_generation_errors.log`; drop
`bbq_control/*.png`.

### Tests and conftest

- `tests/test_run_bbq_alias.py`: `import bioproblems_site.bbq_config` and call
  `bbq_config.load_tasks_csv`; annotate.
- `tests/test_dump_topics_csv.py`: `import bioproblems_site.topics_csv`; annotate.
- `tests/test_generate_pages_topic_alias.py`: docstring wording only (it already tests the
  package functions); annotate.
- `tests/conftest.py`: remove the `TOOLS_DIR` sys.path block (lines 28-32) and its docstring
  mention.
- `tests/test_source_file_line_limit.py` is not present in this repo; module sizes above are
  kept under 900 anyway per `docs/REPO_STYLE.md`.

### Documentation

- `docs/FILE_STRUCTURE.md` is the authoritative script map. Replace the top-level bullets for
  `generate_pages.py`, `run_bbq_tasks.py`, `bbq_control/`, `tools/`, `devel/` with
  `bioproblems.py`, `task_files/`, `bbq_settings.yml`, and the new `bioproblems_site/` modules.
  Add `## Script inventory`: tables grouped Root / `tools/` / `devel/` (repository-owned) /
  `devel/` (vendored). Repository-owned rows: linked path, purpose, invocation (the
  `bioproblems.py` and `site_maint.py` rows list their subcommands). Vendored group: one
  paragraph (propagated from the shared style repo; changelog, version, release, graphify,
  clean helpers) plus a compact path + one-line-purpose table. Success: every tracked
  `.py`/`.sh` outside `tests/`, `site_docs/`, `bioproblems_site/` appears exactly once and no
  two repository-owned rows describe variants of one operation.
- `docs/USAGE.md`: quick start becomes `source source_me.sh && python3 -m mkdocs serve`;
  "Page generation" and "BBQ task runner" sections rewritten for `bioproblems.py pages` /
  `bioproblems.py bbq`; new "Maintainer commands" section for the five `site_maint.py`
  subcommands and `devel/run_playwright_tests.sh`.
- `README.md:40`: `./run_web_server.sh` -> `python3 -m mkdocs serve`.
- `docs/CODE_ARCHITECTURE.md`: entrypoint section describes `bioproblems.py` -> `pages_cli` /
  `bbq_cli`; list the new `bbq_*`, `topics_csv`, `biomacromolecule_data`, `deletion_wordbank`
  modules; replace `bbq_control/` bullets; `tools/dump_topics_csv.py` -> `site_maint.py topics-csv`.
- `docs/TOPICS_METADATA_FORMAT.md`, `docs/BBQ_TASK_CSV_FORMAT.md`, `docs/SELFTEST_PROGRESS.md`,
  `docs/RELATED_PROJECTS.md`, `docs/DELETION_MUTANTS_PLAN.md`, `topics_metadata.yml` comments,
  and docstrings in `bioproblems_site/{metadata,problem_set_title,topic_aliases,pipeline,
  topic_page}.py`: rename `generate_pages.py` / `run_bbq_tasks.py` / `bbq_control/` mentions.
- `docs/CHANGELOG.md`: new `## 2026-09-21` block -- Additions (`bioproblems.py`,
  `site_maint.py`, package modules, `--all-tasks`/`--list-tasks`), Behavior or Interface
  Changes (entrypoint rename, `task_files/` and `bbq_settings.yml` at root, shuffle opt-in,
  Playwright runner path), Removals (twelve deletions), Fixes (typing, bash trim), Decisions
  (root = short orchestrators over package logic; devel invokes, package owns).

## Goal 2: pytest fixes

### test_bash_script_line_limit (`devel/run_playwright_tests.sh`)

- Drop the 20-line header comment that duplicates `usage()`; keep a 3-line header.
- Collapse node/npm checks into two `command -v ... || { echo ...; exit 1; }` lines.
- Merge the two mkdocs branches: `if [ "$FORCE_BUILD" -eq 1 ] || [ ! -d site ]; then`.
- Requirement: under 100 lines; interface and behavior unchanged.

### test_support_dirs_not_imported

Resolved by removing `tools/dump_topics_csv.py`.

### test_function_typing

Mechanical, no refactoring beyond the moves above: add return and parameter annotations.
Concrete builtin types where obvious (`str`, `int`, `list`, `dict`, `pathlib.Path` for
`tmp_path`, `argparse.Namespace`); `object` where the surrounding library makes stronger typing
disproportionate (`client` for the Ollama client in `topic_page.py`, `event` for the Textual
key event in `bbq_tui.py`). Exact list in `report_function_typing.txt`.

Files: `bioproblems_site/{metadata,mkdocs_nav,pipeline,problem_set_title,topic_aliases,
topic_page}.py`; the BBQ functions (annotated as they land in `bbq_*.py`); 14 `tests/test_*.py`
files from the report. Parallelize with fresh subagents in 3 groups (package modules, BBQ
modules, test files), each running
`pytest tests/test_function_typing.py tests/test_pyflakes_code_lint.py -k <file>`.

## Execution order

1. Package extraction: `bbq_config`, `bbq_outputs`, `bbq_runner`, `bbq_tui`, `bbq_batch`,
   `bbq_cli`, `pages_cli`, `topics_csv`, `biomacromolecule_data`, `deletion_wordbank`,
   `scanner` extension. Old root scripts still present; nothing imports them.
2. `bioproblems.py` and `devel/site_maint.py`. Before deleting old entrypoints, compare
   representative argument combinations, defaults, invalid arguments, and exit codes. For
   `generate_pages.py`, cover bare, `-T`, `-G` without `-T`, and `--full` combinations; for the
   BBQ runner, cover single CSV, dry-run, limit, max-question, shuffle, missing input, and
   missing settings cases.
3. Moves: `task_files/`, `bbq_settings.yml`, `docs/BBQ_TASKS_USAGE.md`,
   `devel/run_playwright_tests.sh` (trim). `.gitignore`. Tests/conftest imports.
4. Deletions (twelve files), `rmdir bbq_control`.
5. Typing fixes (parallel).
6. Docs + changelog.
7. Verification.

## Verification (behavior-focused)

1. `source source_me.sh && pytest tests/` -- 0 failures; no `report_*.txt` files.
2. `python3 bioproblems.py --help`, `pages --help`, `bbq --help` exit 0 and list every flag
   the old scripts had.
3. Pages: `python3 bioproblems.py pages -n` runs the dry default path;
   `python3 bioproblems.py pages -n -T -s biochemistry` runs the dry topic path.
4. BBQ single: `python3 bioproblems.py bbq --flat -t task_files/other_tasks.csv --limit 1 -n`
   completes one task and writes `bbq_generation.log`. Batch: `--list-tasks` lists the 10 CSVs
   and exits 0; `--all-tasks --limit 1 --max-questions 1 -n --flat` runs one row per CSV and
   prints batch-wide slowest tasks.
5. Maintainer CLI: `python3 devel/site_maint.py topics-csv -o /tmp/topics.csv` writes header
   `subject,topic_key,alias,title,description` + one row per topic; `count-questions` prints
   descending counts; `reset-generated` restores tracked generated files
   (`git status --short site_docs` shrinks); both `build-*` subcommands answer `--help`
   (full builds need the external `biology-problems` checkout; run if present).
6. Playwright: `bash devel/run_playwright_tests.sh --help` exits 0;
   `pytest tests/test_bash_script_line_limit.py` passes.
7. Docs: `pytest tests/test_markdown_links.py` passes; `docs/FILE_STRUCTURE.md` inventory
   covers every tracked script exactly once with distinct responsibilities.
8. No live references to removed paths: search Markdown, Python, YAML, shell, TypeScript, CSV,
   JSON, and TOML files for the removed filenames and directory names, excluding the changelog,
   archived or active plans, and generated `site/` output. Include CSVs and executable
   configuration formats in this audit because task files are operational inputs.

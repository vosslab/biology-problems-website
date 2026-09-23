# Code architecture

## Overview

This repository builds and serves a MkDocs site from [site_docs/](../site_docs/)
using [mkdocs.yml](../mkdocs.yml). The root [build_site.py](../build_site.py)
CLI exposes one dependency-aware content build workflow.

## Major components

- [build_site.py](../build_site.py): short public argument parser and build entrypoint.
- [bioproblems_site/build_coordinator.py](../bioproblems_site/build_coordinator.py):
  ordered BBQ, self-test, download, topic-page, and index/navigation orchestration
  with stage timing summaries.
- [bioproblems_site/build_stages.py](../bioproblems_site/build_stages.py): local
  stale checks and output-owned stage entrypoints.
- [bioproblems_site/file_write.py](../bioproblems_site/file_write.py): shared
  direct text-file writing for generated site files.
- [bioproblems_site/topic_metadata.py](../bioproblems_site/topic_metadata.py):
  cached topic title, description, and LibreTexts metadata lookup.
- [bioproblems_site/topic_page.py](../bioproblems_site/topic_page.py): topic
  page rendering and generated-download helpers.
- [bioproblems_site/title_cache.py](../bioproblems_site/title_cache.py): shared
  title-cache path, YAML parsing, and writing.
- [bioproblems_site/question_index.py](../bioproblems_site/question_index.py):
  generated human-readable problem-set title index.
- [bioproblems_site/llm_helpers.py](../bioproblems_site/llm_helpers.py):
  title-generation backend seam for Ollama, Codex CLI, and Claude Code CLI.
- [bioproblems_site/bbq_workflow.py](../bioproblems_site/bbq_workflow.py): task
  selection, local BBQ stale checks, per-task timing, and structured change reporting.
- [bioproblems_site/bbq_config.py](../bioproblems_site/bbq_config.py): settings,
  aliases, environment paths, and CSV task shaping.
- [bioproblems_site/bbq_outputs.py](../bioproblems_site/bbq_outputs.py): output
  discovery, movement, cleanup, line counting, and logs.
- [bioproblems_site/bbq_runner.py](../bioproblems_site/bbq_runner.py): generator
  command construction, task execution, PGML follow-up, and plain-mode timing.
- [bioproblems_site/topics_csv.py](../bioproblems_site/topics_csv.py),
  [bioproblems_site/biomacromolecule_data.py](../bioproblems_site/biomacromolecule_data.py),
  and [bioproblems_site/deletion_wordbank.py](../bioproblems_site/deletion_wordbank.py):
  package-owned maintainer operations.
- [devel/site_maint.py](../devel/site_maint.py): thin maintainer command surface.
- [devel/run_playwright_tests.sh](../devel/run_playwright_tests.sh): browser-test
  preflight and runner wrapper.
- [tools/](../tools/): standalone utilities that do not import the repository
  package, including the task CSV topic sorter and Ultra transfer audit.
- [task_files/](../task_files/) and [bbq_settings.yml](../bbq_settings.yml):
  BBQ operational inputs.
- [problem_set_titles.yml](../problem_set_titles.yml): shared generated-title
  cache keyed by BBQ source basename across every subject and topic.

The remaining `devel/` helpers are propagated repository-maintenance commands for
versioning, changelog, release, graphify, and cleanup workflows.

## Data flow

The coordinator loads the selected task CSVs from [task_files/](../task_files/),
resolves their canonical subject/topic keys from metadata, and reports `TopicRef`
changes rather than inferring identity from paths. It completes each selected
configured CSV row's BBQ generation, self-tests, and downloads before advancing
to the next row. Since a topic page summarizes every question file in its folder,
each affected page is rendered once after the selected rows finish. The coordinator
then runs repository-wide reconciliation, the searchable question index, selected
subject indexes, navigation, and the self-test manifest. Each stage owns its direct
stale check and outputs. The index stage updates source navigation in
[mkdocs.yml](../mkdocs.yml); MkDocs separately renders the final site and owns
`sitemap.xml`.

Topic aliases are resolved by
[bioproblems_site/topic_aliases.py](../bioproblems_site/topic_aliases.py) while
task CSVs load. A CSV row becomes a subject-qualified canonical topic before its
downstream stages run. The index stage reconciles generated artifacts against the
live BBQ question files, prunes the shared title cache against all live source
basenames, and then writes the self-test manifest.

## Extension points

- Add or edit a subject or topic in [topics_metadata.yml](../topics_metadata.yml),
  seed its label in [mkdocs.yml](../mkdocs.yml), then run `./build_site.py`.
- Add generation behavior under [bioproblems_site/](../bioproblems_site/) and
  call it from the relevant package workflow.
- Add BBQ tasks under [task_files/](../task_files/) using aliases from
  [bbq_settings.yml](../bbq_settings.yml).
- Add independent utilities under [tools/](../tools/).

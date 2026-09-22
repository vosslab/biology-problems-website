# Code architecture

## Overview

This repository builds and serves a MkDocs site from [site_docs/](../site_docs/)
using [mkdocs.yml](../mkdocs.yml). The root [build_site.py](../build_site.py)
CLI exposes one dependency-aware content build workflow.

## Major components

- [build_site.py](../build_site.py): short public argument parser and build entrypoint.
- [bioproblems_site/build_coordinator.py](../bioproblems_site/build_coordinator.py):
  ordered BBQ, self-test, topic-page, download, and index/navigation orchestration.
- [bioproblems_site/build_stages.py](../bioproblems_site/build_stages.py): local
  stale checks and output-owned stage entrypoints.
- [bioproblems_site/bbq_workflow.py](../bioproblems_site/bbq_workflow.py): task
  selection, local BBQ stale checks, and structured change reporting.
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

The remaining `devel/` helpers are propagated repository-maintenance commands for
versioning, changelog, release, graphify, and cleanup workflows.

## Data flow

The coordinator loads the selected task CSVs from [task_files/](../task_files/),
resolves their canonical subject/topic keys from metadata, and reports `TopicRef`
changes rather than inferring identity from paths. It owns stage order: BBQ task
generation, self-tests, topic pages, downloads, then subject indexes, navigation,
reconciliation, and the self-test manifest. Each stage owns its direct stale
check and outputs. The index stage updates source navigation in
[mkdocs.yml](../mkdocs.yml); MkDocs separately renders the final site and owns
`sitemap.xml`.

Topic aliases are resolved by
[bioproblems_site/topic_aliases.py](../bioproblems_site/topic_aliases.py) while
task CSVs load. A CSV row becomes a subject-qualified canonical topic before its
downstream stages run. The index stage reconciles generated artifacts against the
live BBQ question files before writing the self-test manifest.

## Extension points

- Add or edit a subject or topic in [topics_metadata.yml](../topics_metadata.yml),
  seed its label in [mkdocs.yml](../mkdocs.yml), then run `./build_site.py`.
- Add generation behavior under [bioproblems_site/](../bioproblems_site/) and
  call it from the relevant package workflow.
- Add BBQ tasks under [task_files/](../task_files/) using aliases from
  [bbq_settings.yml](../bbq_settings.yml).
- Add independent utilities under [tools/](../tools/).

# Code architecture

## Overview

This repository builds and serves a MkDocs site from [site_docs/](../site_docs/)
using [mkdocs.yml](../mkdocs.yml). The root [bioproblems.py](../bioproblems.py)
CLI exposes the two primary workflows: `pages` regenerates site content and
`bbq` runs question-generation task CSVs.

## Major components

- [bioproblems.py](../bioproblems.py): short application dispatcher.
- [bioproblems_site/pages_cli.py](../bioproblems_site/pages_cli.py): page CLI
  flags, validation, topic-filter resolution, and pipeline dispatch.
- [bioproblems_site/pipeline.py](../bioproblems_site/pipeline.py): page,
  download, reconcile, navigation, and self-test orchestration.
- [bioproblems_site/bbq_cli.py](../bioproblems_site/bbq_cli.py): single-CSV
  setup and application-level BBQ dispatch.
- [bioproblems_site/bbq_config.py](../bioproblems_site/bbq_config.py): settings,
  aliases, environment paths, and CSV task shaping.
- [bioproblems_site/bbq_outputs.py](../bioproblems_site/bbq_outputs.py): output
  discovery, movement, cleanup, line counting, and logs.
- [bioproblems_site/bbq_runner.py](../bioproblems_site/bbq_runner.py): generator
  command construction, task execution, PGML follow-up, and plain-mode timing.
- [bioproblems_site/bbq_tui.py](../bioproblems_site/bbq_tui.py): optional
  interactive Textual dashboard over the runner contract.
- [bioproblems_site/bbq_batch.py](../bioproblems_site/bbq_batch.py): one
  subprocess per task CSV and batch-wide timing summary.
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

The page path loads [topics_metadata.yml](../topics_metadata.yml), validates its
subject navigation against [mkdocs.yml](../mkdocs.yml), scans [site_docs/](../site_docs/),
and writes subject/topic pages and generated artifacts. The BBQ path loads one
CSV from [task_files/](../task_files/), resolves aliases from [bbq_settings.yml](../bbq_settings.yml)
and metadata, executes the configured generator scripts, and places generated
question files in the matching topic folder.

Topic aliases are resolved by
[bioproblems_site/topic_aliases.py](../bioproblems_site/topic_aliases.py) and are
shared by both `pages -t/--topic` and BBQ CSV loading. The page pipeline reconciles
generated artifacts against the live BBQ question files before writing the
self-test manifest.

## Extension points

- Add or edit a subject or topic in [topics_metadata.yml](../topics_metadata.yml),
  seed its label in [mkdocs.yml](../mkdocs.yml), then run `bioproblems.py pages`.
- Add generation behavior under [bioproblems_site/](../bioproblems_site/) and
  call it from the relevant package workflow.
- Add BBQ tasks under [task_files/](../task_files/) using aliases from
  [bbq_settings.yml](../bbq_settings.yml).
- Add independent utilities under [tools/](../tools/).

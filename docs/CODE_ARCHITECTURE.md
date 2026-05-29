# Code architecture

## Overview

This repo builds and serves a MkDocs site from [site_docs/](../site_docs/) using
[mkdocs.yml](../mkdocs.yml), with helper scripts that generate or update topic
indexes and pages and with optional BBQ batch runners for producing question sets.

## Major components

- [site_docs/](../site_docs/): MkDocs content root with topic pages, tutorials, and
  daily puzzles.
- [site_docs/assets/](../site_docs/assets/): CSS, JavaScript, fonts, and images used
  by the site and daily puzzles.
- [mkdocs.yml](../mkdocs.yml): MkDocs configuration, navigation, theme, and assets.
- [topics_metadata.yml](../topics_metadata.yml): Topic descriptions and LibreTexts
  links used by generators.
- [generate_pages.py](../generate_pages.py): Single page-generation entrypoint
  for subject indexes, topic pages, the generated MkDocs nav block, and the
  self-test progress manifest.
- [bioproblems_site/](../bioproblems_site/): Importable generator package for
  metadata validation, scanning, subject rendering, topic rendering, nav
  updates, and self-test manifest creation.
- [bbq_control/](../bbq_control/): Batch runner tooling and CSV configuration for
  generating BBQ outputs.
- [tools/](../tools/): Small helper scripts for site content generation tasks.

## Data flow

- Primary site flow: edit Markdown and assets under [site_docs/](../site_docs/),
  then run `mkdocs serve` or `mkdocs build` to serve or generate the static site in
  the git-ignored `site/` directory.
- Page generation flow: [generate_pages.py](../generate_pages.py) reads
  [mkdocs.yml](../mkdocs.yml), [topics_metadata.yml](../topics_metadata.yml), and
  BBQ question files under [site_docs/](../site_docs/) to assemble generated
  subject indexes, topic pages, and nav entries.
- Self-test completion flow:
  [bioproblems_site/selftest_manifest.py](../bioproblems_site/selftest_manifest.py)
  scans reachable topic pages from the generated nav, follows their self-test
  includes, and writes
  [site_docs/assets/data/selftest_question_manifest.json](../site_docs/assets/data/selftest_question_manifest.json).
  [site_docs/assets/scripts/selftest_progress.js](../site_docs/assets/scripts/selftest_progress.js)
  uses that manifest plus browser `localStorage` to mark questions completed
  after the first fully correct answer. Wrong answers are not stored. See
  [docs/SELFTEST_PROGRESS.md](SELFTEST_PROGRESS.md) for the manifest schema and
  storage model.
- BBQ batch flow: [run_bbq_tasks.py](../run_bbq_tasks.py) (at the repo
  root, next to `generate_pages.py`) reads task CSVs in
  [bbq_control/task_files/](../bbq_control/task_files/) and
  [bbq_control/bbq_settings.yml](../bbq_control/bbq_settings.yml) to execute
  script-based tasks and write outputs to configured paths.

## Testing and verification

- [tests/test_pyflakes_code_lint.py](../tests/test_pyflakes_code_lint.py):
  Pyflakes lint gate.
- [tests/test_ascii_compliance.py](../tests/test_ascii_compliance.py): Repo-wide ASCII
  compliance check.
- [tests/check_ascii_compliance.py](../tests/check_ascii_compliance.py): Single-file
  ASCII compliance check.
- [tests/test_selftest_manifest.py](../tests/test_selftest_manifest.py): Manifest
  source-of-truth and CRC uniqueness coverage.
- [tests/selftest_progress_storage_test.mjs](../tests/selftest_progress_storage_test.mjs),
  [tests/selftest_correctness_contract_test.mjs](../tests/selftest_correctness_contract_test.mjs),
  and [tests/selftest_progress_dom_test.mjs](../tests/selftest_progress_dom_test.mjs):
  browser-side progress storage and wrapper coverage.

## Extension points

- Add new topic content under [site_docs/](../site_docs/) and regenerate with
  [generate_pages.py](../generate_pages.py).
- Add or update topic metadata in [topics_metadata.yml](../topics_metadata.yml).
- Add new generators or utilities at the repo root or under [tools/](../tools/).
- Add or update BBQ batch tasks in [bbq_control/task_files/](../bbq_control/task_files/)
  and related settings in [bbq_control/bbq_settings.yml](../bbq_control/bbq_settings.yml).

## Known gaps

- Confirm the expected location and setup for the git-ignored `bbq_converter.py`
  symlink used by the BBQ generation flow.
- Document the standard workflow for BBQ generation, including how outputs are
  routed into [site_docs/](../site_docs/) or other destinations.

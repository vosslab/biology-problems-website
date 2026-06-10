# Code architecture

## Overview

This repo builds and serves a MkDocs site from [site_docs/](../site_docs/) using
[mkdocs.yml](../mkdocs.yml). A single page-generation entry point,
[generate_pages.py](../generate_pages.py), regenerates subject indexes, topic
pages, and the generated nav block from [topics_metadata.yml](../topics_metadata.yml).
A separate batch runner, [run_bbq_tasks.py](../run_bbq_tasks.py), produces BBQ
question sets from per-subject task CSVs.

## Major components

- [site_docs/](../site_docs/): MkDocs content root with one folder per subject and
  topic, plus tutorials and daily puzzles.
- [site_docs/assets/](../site_docs/assets/): CSS, JavaScript, fonts, and images used
  by the site and daily puzzles.
- [mkdocs.yml](../mkdocs.yml): MkDocs configuration, theme, assets, and the
  navigation. Subject nav lives between the `BEGIN/END GENERATED SUBJECT NAV`
  markers and is rewritten by the generator.
- [topics_metadata.yml](../topics_metadata.yml): Single source of truth for subjects
  and topics (titles, descriptions, aliases, LibreTexts links). Schema is documented
  in [docs/TOPICS_METADATA_FORMAT.md](TOPICS_METADATA_FORMAT.md).
- [generate_pages.py](../generate_pages.py): Page-generation entry point. Thin CLI
  wrapper over the [bioproblems_site/](../bioproblems_site/) package.
- [bioproblems_site/](../bioproblems_site/): Python package holding the generation
  logic:
  - [bioproblems_site/pipeline.py](../bioproblems_site/pipeline.py): Orchestrates a
    generation run (subject indexes, topic pages, downloads, reconcile, nav update).
  - [bioproblems_site/orphan_prune.py](../bioproblems_site/orphan_prune.py): Orphan
    reconcile via `reconcile_all`: detects and deletes generated orphans, strips dead
    self-test includes, prunes the `problem_set_titles.yml` title cache, and
    quarantines orphan topic-level `.pgml`/`.pg` masters to a repo-root `orphaned/`
    folder.
  - [bioproblems_site/metadata.py](../bioproblems_site/metadata.py): Loads and
    validates `topics_metadata.yml`; enforces subject sync with `mkdocs.yml`.
  - [bioproblems_site/topic_aliases.py](../bioproblems_site/topic_aliases.py): Pure
    resolver that converts author-facing topic aliases to canonical `topicNN` ids.
  - [bioproblems_site/scanner.py](../bioproblems_site/scanner.py): Scans `site_docs/`
    topic folders for question counts.
  - [bioproblems_site/subject_index.py](../bioproblems_site/subject_index.py) and
    [bioproblems_site/topic_page.py](../bioproblems_site/topic_page.py): Render
    subject index pages and topic pages.
  - [bioproblems_site/mkdocs_nav.py](../bioproblems_site/mkdocs_nav.py): Rewrites the
    generated nav block in `mkdocs.yml`, preserving hand-authored subject labels.
  - [bioproblems_site/selftest_manifest.py](../bioproblems_site/selftest_manifest.py):
    Builds the self-test question manifest from reachable topic pages.
  - [bioproblems_site/download_buttons.py](../bioproblems_site/download_buttons.py)
    and [bioproblems_site/formats.py](../bioproblems_site/formats.py): Download
    section and output-format helpers.
  - [bioproblems_site/llm_helpers.py](../bioproblems_site/llm_helpers.py) and
    [bioproblems_site/problem_set_title.py](../bioproblems_site/problem_set_title.py):
    Optional LLM-assisted problem-set titles. These import `local_llm_wrapper`
    (vendored on `PYTHONPATH` by [source_me.sh](../source_me.sh); also on PyPI as
    `local-llm-wrapper`).
  - [bioproblems_site/git_paths.py](../bioproblems_site/git_paths.py): Repo-root and
    path helpers, plus git staging helpers (`git_rm`, `git_mv`, `tracked_paths_set`)
    used by the reconcile step.
- [run_bbq_tasks.py](../run_bbq_tasks.py): BBQ batch runner driven by per-subject task
  CSVs.
- [bbq_control/](../bbq_control/): Task CSVs in
  [bbq_control/task_files/](../bbq_control/task_files/),
  [bbq_control/bbq_settings.yml](../bbq_control/bbq_settings.yml) path/script aliases,
  and operational notes in [bbq_control/USAGE.md](../bbq_control/USAGE.md).
- [tools/](../tools/): Small helper scripts, including
  [tools/dump_topics_csv.py](../tools/dump_topics_csv.py).

## Data flow

- Site flow: edit Markdown and assets under [site_docs/](../site_docs/), then run
  `mkdocs serve` or `mkdocs build` to serve or build the static site in the
  git-ignored `site/` directory.
- Page generation: [generate_pages.py](../generate_pages.py) loads
  [topics_metadata.yml](../topics_metadata.yml), validates it against the `mkdocs.yml`
  subject nav, scans [site_docs/](../site_docs/) for question counts, then writes
  subject indexes and rewrites the generated nav block. With `-T` it also rebuilds
  topic pages; with `-G` it creates missing download artifacts. On every gated run,
  `reconcile_all` from
  [bioproblems_site/orphan_prune.py](../bioproblems_site/orphan_prune.py) runs before
  `write_manifest`, so the manifest never sees an orphan (reconcile-first ordering).
- Topic resolution: topic aliases (for example `biochemistry:amino_acids`) resolve to
  canonical `topicNN` ids via
  [bioproblems_site/topic_aliases.py](../bioproblems_site/topic_aliases.py), shared by
  both the generator `-t/--topic` filter and the BBQ runner.
- Self-test completion flow:
  [bioproblems_site/selftest_manifest.py](../bioproblems_site/selftest_manifest.py)
  scans reachable topic pages from the generated nav, follows their self-test
  includes, and writes
  [site_docs/assets/data/selftest_question_manifest.json](../site_docs/assets/data/selftest_question_manifest.json).
  [site_docs/assets/scripts/selftest_progress.js](../site_docs/assets/scripts/selftest_progress.js)
  uses that manifest plus browser `localStorage` to mark questions completed after
  the first fully correct answer. See
  [docs/SELFTEST_PROGRESS.md](SELFTEST_PROGRESS.md) for the manifest schema and
  storage model.
- BBQ batch flow: [run_bbq_tasks.py](../run_bbq_tasks.py) reads a per-subject CSV from
  [bbq_control/task_files/](../bbq_control/task_files/) (selected with `-t`) and the
  aliases in [bbq_control/bbq_settings.yml](../bbq_control/bbq_settings.yml), runs the
  configured scripts, and writes question outputs into the matching `site_docs/`
  topic folders. CSV schema is documented in
  [docs/BBQ_TASK_CSV_FORMAT.md](BBQ_TASK_CSV_FORMAT.md).

## Extension points

- Add or edit a subject or topic in [topics_metadata.yml](../topics_metadata.yml), seed
  its label in the [mkdocs.yml](../mkdocs.yml) nav block, then run
  [generate_pages.py](../generate_pages.py).
- Add generation logic as a new module under
  [bioproblems_site/](../bioproblems_site/), called from
  [bioproblems_site/pipeline.py](../bioproblems_site/pipeline.py).
- Add BBQ tasks in a per-subject CSV under
  [bbq_control/task_files/](../bbq_control/task_files/), using aliases from
  [bbq_control/bbq_settings.yml](../bbq_control/bbq_settings.yml).
- Add small helper scripts under [tools/](../tools/).

## Known gaps

- `bbq_converter.py` at the repo root is a git-ignored symlink; confirm its source
  and setup for [run_bbq_tasks.py](../run_bbq_tasks.py).

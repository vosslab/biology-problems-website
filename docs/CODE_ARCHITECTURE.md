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
- [generate_subject_indexes.py](../generate_subject_indexes.py): Builds subject
  index pages from [mkdocs.yml](../mkdocs.yml) and
  [topics_metadata.yml](../topics_metadata.yml).
- [generate_topic_pages.py](../generate_topic_pages.py): Builds topic pages and
  download sections for BBQ question files, using
  [llm_generate_problem_set_title.py](../llm_generate_problem_set_title.py) and
  [llm_wrapper.py](../llm_wrapper.py) when LLM titles are needed.
- [bbq_control/](../bbq_control/): Batch runner tooling and CSV configuration for
  generating BBQ outputs.
- [tools/](../tools/): Small helper scripts for site content generation tasks.

## Data flow

- Primary site flow: edit Markdown and assets under [site_docs/](../site_docs/),
  then run `mkdocs serve` or `mkdocs build` to serve or generate the static site in
  [site/](../site/).
- Index generation flow: [generate_subject_indexes.py](../generate_subject_indexes.py)
  reads [mkdocs.yml](../mkdocs.yml) and [topics_metadata.yml](../topics_metadata.yml)
  and writes subject index pages under [site_docs/](../site_docs/).
- Topic page flow: [generate_topic_pages.py](../generate_topic_pages.py) reads
  [mkdocs.yml](../mkdocs.yml), [topics_metadata.yml](../topics_metadata.yml), and
  BBQ question files in [site_docs/](../site_docs/) topic folders to assemble topic
  pages and download links.
- BBQ batch flow: [bbq_control/run_bbq_tasks.py](../bbq_control/run_bbq_tasks.py)
  reads [bbq_control/bbq_tasks.csv](../bbq_control/bbq_tasks.csv) and
  [bbq_control/bbq_settings.yml](../bbq_control/bbq_settings.yml) to execute
  script-based tasks and write outputs to configured paths.

## Testing and verification

- [tests/run_pyflakes.sh](../tests/run_pyflakes.sh): Pyflakes lint runner.
- [tests/run_ascii_compliance.py](../tests/run_ascii_compliance.py): Repo-wide ASCII
  compliance check.
- [tests/check_ascii_compliance.py](../tests/check_ascii_compliance.py): Single-file
  ASCII compliance check.

## Extension points

- Add new topic content under [site_docs/](../site_docs/) and update navigation in
  [mkdocs.yml](../mkdocs.yml).
- Add or update topic metadata in [topics_metadata.yml](../topics_metadata.yml).
- Add new generators or utilities at the repo root or under [tools/](../tools/).
- Add or update BBQ batch tasks in [bbq_control/bbq_tasks.csv](../bbq_control/bbq_tasks.csv)
  and related settings in [bbq_control/bbq_settings.yml](../bbq_control/bbq_settings.yml).

## Known gaps

- Confirm the expected location and setup for the ignored
  [bbq_converter.py](../bbq_converter.py) dependency used by
  [generate_topic_pages.py](../generate_topic_pages.py).
- Document the standard workflow for BBQ generation, including how outputs are
  routed into [site_docs/](../site_docs/) or other destinations.

# Code architecture

## Overview

This repository builds and serves a MkDocs site from [site_docs/](../site_docs/)
using [mkdocs.yml](../mkdocs.yml). The root [build_site.py](../build_site.py)
CLI exposes one dependency-aware content build workflow.

## Major components

- [build_site.py](../build_site.py): short public argument parser and build entrypoint.
- [bioproblems_site/build_coordinator.py](../bioproblems_site/build_coordinator.py):
  ordered BBQ, native self-test, topic-page, and index/navigation orchestration
  with stage timing summaries.
- [bioproblems_site/build_stages.py](../bioproblems_site/build_stages.py): local
  stale checks and output-owned stage entrypoints.
- [bioproblems_site/file_write.py](../bioproblems_site/file_write.py): shared
  direct text-file writing for generated site files.
- [bioproblems_site/mkdocs_styles.py](../bioproblems_site/mkdocs_styles.py): MkDocs
  post-build hook using `tinycss2` to scope copied website styles outside mounted
  QPM content. Root-only rules and asset declarations remain global; see
  [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) for the isolation rationale.
- [bioproblems_site/topic_metadata.py](../bioproblems_site/topic_metadata.py):
  cached topic title, description, and LibreTexts metadata lookup.
- [bioproblems_site/topic_page.py](../bioproblems_site/topic_page.py): topic
  page rendering, direct BBQ/PGML links, and browser-export controls.
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
configured CSV row's BBQ generation and native self-tests before advancing to
the next row. Browser controls generate package exports from BBQ source on demand;
BBQ and PGML remain direct files. Since a topic page summarizes every question file in its folder,
each affected page is rendered once after the selected rows finish. The coordinator
then runs repository-wide reconciliation, the searchable question index, selected
subject indexes, navigation, and the self-test manifest. Each stage owns its direct
stale check and outputs. The index stage updates source navigation in
[mkdocs.yml](../mkdocs.yml); MkDocs separately renders the final site and owns
`sitemap.xml`. Its post-build hook transforms output stylesheets only, placing
website selectors outside `.selftest-reroll-content`; the resulting site requires
a browser supporting CSS `@scope`.

Topic aliases are resolved by
[bioproblems_site/topic_aliases.py](../bioproblems_site/topic_aliases.py) while
task CSVs load. A CSV row becomes a subject-qualified canonical topic before its
downstream stages run. The index stage reconciles generated artifacts against the
live BBQ question files, prunes the shared title cache against all live source
basenames, and then writes the self-test manifest.

## Browser self-test lifecycle

Topic pages contain empty `.qti-selftest` containers rather than embedded
standalone question HTML. Each container identifies its BBQ bank, stable page
placement, and standalone self-test artifact with `data-bbq` and
`data-selftest`. The standalone artifact remains the manifest source; the
browser uses the BBQ bank and vendored WebAssembly converter to make its active
question.

[selftest_reroll.js](../site_docs/assets/scripts/selftest_reroll.js) owns the
whole question lifecycle: it creates the question header, generates the first
container on page load, mounts converter output, wraps the generated answer
checker, and advances after a fully correct answer. It emits bubbling
`selftest:ready` and `selftest:graded` events. The next question begins loading
alongside the 500 ms feedback pause and receives focus only when it is ready.
Manual **New version** replaces one container without retaining attempt history.

[selftest_progress.js](../site_docs/assets/scripts/selftest_progress.js) and
[streak.js](../site_docs/assets/scripts/streak.js) subscribe to those events.
Progress stores completed BBQ filename basenames in browser `localStorage`; a
correct generated version completes its shared source set. CRCs remain scoped
to generated DOM and grading. Streak rules remain independent of question
navigation. This separates lifecycle ownership from lightweight motivational
records and lets dynamically generated questions use the same grading path as
the initial question.

## Homepage snapshot and source history

Index finalization also refreshes the global homepage and both full activity pages through
[homepage_data.py](../bioproblems_site/homepage_data.py) and
[homepage_render.py](../bioproblems_site/homepage_render.py), including scoped builds.
Current task CSVs own inventory membership; existing BBQ bank placements supply set counts.
Generated question quantities are not collection metrics. The snapshot stores complete dated
family lists; only the homepage renderer limits previews to five entries. The same renderer
creates `latest_additions.md` and `recently_updated.md` with collection links and honest empty
states. Both normal and index-only builds refresh these globally.
[source_history.py](../bioproblems_site/source_history.py) follows upstream Git
lineage and local task admissions. Successful generation records the source and
output fingerprints through
[question_provenance.py](../bioproblems_site/question_provenance.py).
Only matching provenance supplies published revision dates. MkDocs consumes the
committed snapshot and HTML fragment without querying upstream Git.

## Extension points

- Add or edit a subject or topic in [topics_metadata.yml](../topics_metadata.yml),
  seed its label in [mkdocs.yml](../mkdocs.yml), then run `./build_site.py`.
- Add generation behavior under [bioproblems_site/](../bioproblems_site/) and
  call it from the relevant package workflow.
- Add BBQ tasks under [task_files/](../task_files/) using aliases from
  [bbq_settings.yml](../bbq_settings.yml).
- Add independent utilities under [tools/](../tools/).

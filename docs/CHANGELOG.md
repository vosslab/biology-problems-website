# Changelog

## 2026-07-12

### Behavior or Interface Changes

- Expanded the ten `bbq_control/task_files/*.csv` controls from the prior
  narrow placement model to 432 curated rows. A concrete question variant can
  now appear in every applicable course subject while remaining limited to one
  chapter per subject.
- BBQ task runs now print each task's elapsed runtime after generation and any
  PGML work. Direct CSV runs summarize their ten slowest tasks, while
  `bbq_control/all_tasks.py` reports the ten slowest tasks across the full
  batch.

### Fixes and Maintenance

- Assigned every frozen biology-problems generator and YAML bank, removed an
  exact duplicate row, corrected several existing chapter placements, and
  added cross-subject placements for DNA, PCR, statistics, genetics,
  laboratory, biotechnology, and cell-biology material.
- Restored genetics task coverage for the complementary prime, HLA marker and
  color, English-palindrome, linear-digest, and restriction-overhang variants
  that had been omitted during the task-file split.
- Replaced bare Genetics Gene Trees defaults with the maintained
  matrix-interpreting Levels 1 through 5 plus SAME and DIFFERENT comparison
  questions at EASY, MEDIUM, and RIGOROUS difficulty.
- Replaced bare deletion-mutant defaults with explicit EASY, MEDIUM, and
  RIGOROUS table-based MC variants for both random gene labels and word-based
  gene labels.
- Sorted `bbq_control/task_files/molecular_bio_tasks.csv` by the Molecular
  Biology topic order in `topics_metadata.yml`, with `,,,,,` separator rows
  between populated topic groups.
- Added [`tools/csv_topic_sorter.py`](../tools/csv_topic_sorter.py), a
  standalone in-place sorter that groups BBQ task CSV rows by
  `topics_metadata.yml` and writes separator rows between topic groups.
- Aligned `AGENTS.md` and BBQ command examples with the shared
  `source source_me.sh && python3` Python bootstrap.
- Added `bbq_control/all_tasks.py` as the root-aware coordinator for every
  `bbq_control/task_files/*.csv` file. It discovers files deterministically,
  passes absolute task and settings paths to the root runner, and has a
  non-generating `--list` verification mode. `bbq_control/all_tasks.sh` now
  delegates to it.

### Developer Tests and Notes

- The sibling biology-problems validator reports 178/178 generators and 98/98
  YAML banks covered, with zero invalid chapters, routing failures, exact
  duplicates, or same-subject chapter conflicts.

## 2026-07-04

### Additions and New Features
- Added a Playwright runner-model smoke test. [playwright.config.ts](../playwright.config.ts)
  chooses a random port once (8000 + rand(0..999), PORT override), pins it into use.baseURL and
  the webServer url on 127.0.0.1, builds the site with `mkdocs build` and serves `site/` over
  HTTP, and runs specs across 4 parallel workers with failure-only screenshots.
  [tests/playwright/smoke.spec.ts](../tests/playwright/smoke.spec.ts) reads the built
  `sitemap.xml` and generates one test per route (67 routes), asserting the mkdocs-material shell
  (`.md-header`, `article.md-typeset`/`.md-content`, `.md-footer`, a top-level `h1`; nav and
  search present in the DOM) with zero console/page errors and driving each self-test
  question-agnostically (confirms the machinery reacts; never asserts a specific "Correct"
  verdict). Run it with `./run_playwright_tests.sh` or `npm run test:smoke`.
- Added shared Playwright helpers
  [tests/playwright/helper_discover.mjs](../tests/playwright/helper_discover.mjs) (sitemap parsing
  and route discovery: `parseSitemap` plus `discoverRoutes`) and
  [tests/playwright/helper_smoke_checks.mjs](../tests/playwright/helper_smoke_checks.mjs)
  (structural checks plus the question-agnostic self-test driver), with `.d.mts` type
  declarations so the `.ts` spec can import them.
- Added `-H`/`--selftests` to [generate_pages.py](../generate_pages.py): a standalone pass that
  force-regenerates every self-test HTML from its `bbq-*.txt` source via qti-package-maker
  (treats all as stale), honoring `-s`/`--subject` and `-t`/`--topic`, without rewriting
  `index.md` or contacting the LLM. Backed by `run_selftests` in
  [bioproblems_site/pipeline.py](../bioproblems_site/pipeline.py) and shared
  `enumerate_topic_jobs`/`regenerate_all_selftests` in
  [bioproblems_site/topic_page.py](../bioproblems_site/topic_page.py).

### Behavior or Interface Changes
- `run_playwright_tests.sh` is the runner-model front door: it preflights tooling, builds the site
  (`mkdocs build`) when needed, runs `npx playwright test`, prints a single PASS or FAIL line, and
  exits with the runner's code. `package.json` `test:smoke` runs `playwright test smoke.spec.ts`.
- Added `site_url: https://biologyproblems.org/` to [mkdocs.yml](../mkdocs.yml) (matches the
  gh-pages deploy CNAME). MkDocs now populates `sitemap.xml` (previously empty), enabling route
  discovery and correct canonical URLs.
- Self-test regeneration is decoupled from `--generate-downloads`. During a `-T` topic-page build,
  self-tests rotate by default (a fresh random question drawn from the `bbq-*.txt` source per
  build); `--no-selftests` skips that inline rotation. The rotating-artifact intent is documented
  in-code so the regeneration stays on across builds.
- Consolidated the shell environment to a single root [source_me.sh](../source_me.sh) in the
  starter-template modular style: a `prepend_pythonpath` helper adds local-llm-wrapper and
  qti-package-maker to PYTHONPATH once each. Removed `bbq_control/source_me.sh` (overkill:
  folder-existence checks and an unnecessary content-repo PYTHONPATH entry); `bbq_control/all_tasks.sh`
  now runs under bash and sources the root `source_me.sh`. The `biology-problems/problems` content
  is referenced by file path (bbq_settings.yml `bp_root`), not imported, so it needs no PYTHONPATH
  entry.
- Established the `helper_` prefix naming policy for permanent Playwright support files (see
  [docs/PLAYWRIGHT_TEST_STYLE.md](PLAYWRIGHT_TEST_STYLE.md)); a bare leading underscore stays
  reserved for deletable scratch.

### Decisions and Failures
- The self-test driver accepts three answer archetypes (radio/checkbox, text/number,
  drag-and-drop) to stay question-agnostic across matching and fill-in-the-blank questions.
- The smoke suite surfaced 3 stale broken fill-in-the-blank self-tests: fossil HTML from an older
  converter that emitted an unsubstituted `{crc16_text}` placeholder, breaking the `checkAnswer_*`
  function on biochemistry/topic03 (2 fragments) and molecular_biology/topic09 (1). The converter
  is already fixed upstream; running `generate_pages.py -H` regenerates every self-test and clears
  them, after which the smoke suite passes all 67 routes.

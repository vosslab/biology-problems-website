# Changelog

## 2026-09-23

### Fixes and Maintenance

- Aligned build documentation with row-local task stages, repository-wide
  finalization, task topic alias rules, and configured-output failure handling.
- Corrected stale pipeline comments and helper documentation.
- Topic pages now preserve the last complete `index.md` if rendering fails. Topic
  metadata lookup is split into its own module, and BBQ/converter preservation
  coverage includes oversized candidates and nonzero converter exits.
- Subprocess launch handlers now report expected operating-system errors while
  allowing programming errors to retain their traceback.
- Missing converter outputs are built before the topic page is published. Focused
  builds refresh manifest rows for selected topics and preserve the other current
  rows; unrestricted builds still validate every reachable self-test include.
- Normal builds omit per-topic orphan-prune summaries when a folder has no actions.
- Topic pages now render once per affected topic after row-owned self-tests and
  downloads finish, avoiding repeated whole-topic scans. Page-render logs identify
  absent downloads as files this stage does not generate.
- Task CSV headers and rows are validated before use. If repository-wide task ownership
  cannot be established, orphan cleanup is skipped while index generation continues.
- Configured PGML generation/copy failures now fail the owning task row. PGML files are
  staged before publication so a failed generator preserves the prior file.
- Generated subject/question indexes, navigation, and orphan-prune edits now publish
  text atomically, preserving the prior complete file if writing is interrupted.
- Each configured build now writes one fresh `bbq_generation.log` across all CSV rows;
  errors share that log, and numbered backups are removed at startup.
- Build status and diagnostic paths are shown relative to the current working directory.
- Consolidated per-topic `problem_set_titles.yml` caches into one repository-root
  title map shared by every subject and topic. Title generation and the public
  question index now read the shared map; repository-wide orphan reconciliation
  prunes stale title keys once against all live BBQ basenames.
- The `-T/--topic` filter accepts a canonical key, metadata alias, or display
  title and resolves each form to the same canonical topic internally.
- Added `--rebuild` as the clearer spelling for `-F`; it forces work only within
  the selected filters. The existing `--full` spelling remains accepted.

## 2026-09-22

### Behavior or Interface Changes

- Replaced the root `bioproblems.py pages` and `bioproblems.py bbq` commands
  with the unified [build_site.py](../build_site.py) workflow. It selects stale
  BBQ tasks and propagates changed subject-qualified topics through self-tests,
  topic pages, downloads, and subject indexes/navigation.
- Added `-S/--subject`, `-t/--task`, `-l/--limit`, `-R/--shuffle`, `-n/--dry-run`,
  `-F/--full`, and `-m/--model` to the public build command. Dry runs are planning-only;
  `--full` bypasses stale checks without expanding the requested scope. Existing
  `--tasks` remains as a migration spelling through 2026-12-31.
- Added `-T/--topic` to narrow a subject build to one canonical topic. A topic filter
  requires `-S/--subject` and intersects with any selected task CSV.
- Added `-b/--backend` to choose Ollama, Codex CLI, or Claude Code CLI for generated
  page titles. Ollama remains the default; Codex uses its configured CLI model
  when `--model` is omitted.
- Configured builds finish each CSV task row's self-test and download stages before
  starting the next row. Topic pages render once per affected topic afterward;
  site-wide indexes remain final.

### Fixes and Maintenance

- BBQ task runners now reject empty or oversized candidates and restore configured outputs when
  generation fails, including when a generator writes directly to its destination. Validated
  candidates replace existing outputs only after they are ready.
- Self-test conversion stages HTML and preserves prior output when conversion fails or returns no
  output. Configured the nucleotide-components bank for four choices, matching its three available
  distractor groups.
- Separated self-test and download writes from topic-page rendering, retained
  batch-only `--max-questions 199`, and left final sitemap generation to MkDocs.
- Added a generated, user-visible `All Questions` page that lists problem-set
  titles for native browser search while keeping SEO `sitemap.xml` generation
  under MkDocs.

## 2026-09-21

### Additions and New Features

- Added `bioproblems.py` as the short application CLI with
  `pages` and `bbq` subcommands.
- Extracted BBQ configuration, output handling, runner, TUI, and batch behavior
  into `bioproblems_site/bbq_*.py` modules.
- Added package-owned maintainer helpers for topic CSV export, BBQ line counts,
  biomacromolecule data, and the deletion wordbank, exposed through
  [devel/site_maint.py](../devel/site_maint.py).
- Added `--all-tasks` and `--list-tasks` to the BBQ CLI and moved task CSVs and
  BBQ settings to the repository root.

### Behavior or Interface Changes

- Replaced the separate page and BBQ root entrypoints with
  `bioproblems.py pages` and `bioproblems.py bbq`; there are no compatibility
  aliases for the removed commands.
- Batch BBQ execution now uses `sys.executable`, one subprocess per CSV, a
  batch-only default of 199 maximum questions, and opt-in shuffling.
- Moved the Playwright runner to `devel/run_playwright_tests.sh` and kept its
  command-line interface intact.

### Removals

- Removed the redundant page, BBQ, preview-server, generated-reset, question-
  count, data-builder, and old BBQ-control wrapper scripts.

### Fixes and Maintenance

- Reduced the maintained script inventory from 33 to 24 and made
  [docs/FILE_STRUCTURE.md](FILE_STRUCTURE.md) the complete script map.
- Removed the support-directory import violation by moving topic CSV export
  into `bioproblems_site/` and removed the obsolete `tools/` test-path hook.
- Trimmed the Playwright shell wrapper below the repository line limit and
  annotated the moved CLI and package functions.

### Decisions and Failures

- Root scripts remain short workflow dispatchers; reusable behavior belongs to
  `bioproblems_site/`, maintainer surfaces belong to `devel/`, and independent
  utilities remain in `tools/`.

### Developer Tests and Notes

- Focused CLI and repository hygiene checks pass with Homebrew Git selected on
  the host. The system Git executable is blocked by an unaccepted Xcode
  license, so the full pytest command must use the same Git selection until the
  host license is addressed.

### Existing Support Synchronization

- Synchronized shared style guides, tests, and repository support files from the starter template.

## 2026-09-20

### Fixes and Maintenance

- Reviewed and revised the genetics problem-set titles in topics 1 through 4 for consistent,
  collection-level descriptions. Removed incidental generated examples such as individual
  restriction enzymes, sequences, and blood types, and aligned related restriction-digest,
  restriction-cut, HLA, paternity, crime-scene gel-matching, Mendelian-cross, monohybrid,
  Punnett-square, and pedigree titles around their stable tasks, formats, and difficulty levels.
  Matching banks and their parallel "which one" banks now explicitly distinguish matching from
  multiple-choice response formats.

## 2026-08-25

### Additions and New Features

- Added `run_web_server.sh` as the repository-aware local preview command.
  It resolves the Git root, loads [source_me.sh](../source_me.sh), serves MkDocs at
  `http://127.0.0.1:8000/`, opens the browser, and cleans up automatically after five minutes
  while preserving early server failures.
- Routed the README and usage-guide preview examples through the new script and documented the
  Python 3.12 module command for direct static builds.

### Behavior or Interface Changes

- Made Ollama with `gemma4:e4b` the default backend for problem-set title generation after
  Apple Intelligence stopped supporting the workflow. Removed the obsolete `-O/--ollama`
  switch; `-m/--model` still selects another installed Ollama model explicitly.
- Replaced MkDocs Material's externally loaded Roboto text face with self-hosted Atkinson
  Hyperlegible Next variable fonts. The upright and italic web fonts cover weights 200 through
  800, apply through Material's `--md-text-font` token, and ship with their SIL Open Font License.
- Disabled Material's automatic Google Fonts loading so the site typography has no external font
  request and uses the bundled files on GitHub Pages.

### Fixes and Maintenance

- Removed obsolete `YMMS` rows from the active genetics task file. The old
  `yaml_make_match_sets.py` generator was renamed to `yaml_match_to_bbq.py` and already runs
  through each corresponding `YMATCH` row.
- Removed the obsolete `--no-hidden-terms` and `--allow-click` arguments from BBQ batch commands;
  current generators disable both anti-cheat transformations by default and no longer accept the
  negative flags.
- Extended the Atkinson text font through the daily puzzle roots and embedded selftest content.
  Daily puzzles now inherit the site font instead of resetting to the system UI face, and the site
  overrides legacy inline Arial declarations without changing intentional monospace content.

### Decisions and Failures

- Kept preview-server lifecycle probes as one-time implementation checks rather than permanent
  tests. Removed the temporary fake-child harness and its custom environment control because a
  timing-dependent subprocess fixture was disproportionate to this small convenience script.

### Developer Tests and Notes

- Verified the bundled WOFF2 files byte-match their upstream sources by SHA-256 and expose
  upright and italic `wght` axes from 200 through 800, then completed a clean MkDocs build.
- Confirmed through Chromium at 1440x1000 in light and dark modes and at 390x844 in light mode
  that both font faces load, Material resolves the new text token for body, heading, and
  navigation text, no Google Fonts links remain, and the layouts remain readable without
  overflow. Added a browser regression check for loaded local font faces, computed text styles on
  the homepage, Peptidyle puzzle, and an embedded selftest table, and the absence of Google Fonts.
  The full Playwright smoke suite passed all 77 checks across the rendered site, and the complete
  pytest suite passed all 5,309 tests.
- Validated the local preview script with `bash -n`, a live HTTP request to the served homepage,
  Ctrl-C cleanup with status 130, and 3,120 focused shebang, Markdown-link, and README tests.

## 2026-08-19

### Behavior or Interface Changes

- Switched the website's Blackboard Ultra download from the QTI v2.1 ZIP to qti-package-maker's
  Blackboard pool-export ZIP (`--blackboard_export_zip`). The generated files, download buttons,
  scanner, orphan reconciliation, and Ultra import tutorial now use the pool-export path, which
  supports the site's matching questions through Ultra's **Import from file** workflow.
- Corrected download-format scanning to use the generated filename patterns, including
  `blackboard_export_zip-*.zip`, so the Blackboard Ultra export is discoverable after generation.
- Omit the Ultra pool-export control for ORDER question sets, which the exporter cannot write,
  and remove a stale empty ZIP during reconciliation instead of offering a broken download.
- Shortened the visible control label to **Blackboard Ultra ZIP** while retaining the pool-export
  format detail in its accessible name and import tutorial.
- Renamed the canonical question-source download from **Blackboard Learn TXT** to **BBQ Text**,
  separating the source format from Blackboard's retired product branding.

## 2026-07-15

### Behavior or Interface Changes

- Standardized the website footer, public license page, and repository licensing
  rule on CC BY 4.0 for non-code content. Removed the prior reciprocal licensing
  requirement and retained separate GPLv3 and LGPLv3 licensing for source code.

## 2026-07-12

### Additions and New Features

- Added `tests/playwright/capture_docs_screenshots.mjs` as a self-contained
  documentation capture command. It starts and stops `mkdocs serve`, waits for
  readiness, and captures stable website views through a directly executable
  Node shebang. The `npm run docs:screenshots` alias invokes the same script.
  Added `docs/screenshots/website_home.png`,
  `docs/screenshots/hla_problem_sets.png`, and
  `docs/screenshots/daily_puzzles.png` and embedded them in `README.md`.
- Added `docs/RELATED_PROJECTS.md`, `docs/RELEASE_HISTORY.md`, and `docs/NEWS.md`
  as the sourced project map, full release summary, and curated highlights.

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

- Refreshed the repository docset and rewrote `README.md` around the live
  `biologyproblems.org` experience, interactive practice, daily puzzles, and
  instructor-ready download formats.
- Individually reviewed all 500 problem-set titles across 56 topic files. MATCH
  titles now explicitly say "Matching", TFMS titles use "True/False Statements
  About", and similar parameterized sets expose their distinguishing format,
  difficulty, count, layout, label, or color details.
- Aligned repeated BBQ keys to the same title across subjects and updated the
  naming guide and title-generation prompt to preserve these conventions.
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
- Replaced the bare DNA-profiling father and killer generators in Biotechnology,
  Genetics, Laboratory, and Molecular Biology task files with explicit EASY,
  MEDIUM, and HARD variants.
- Replaced bare Genetics two- and three-point test-cross tasks with explicit
  MC/NUM and genotype-type variants while retaining each generator's default
  hint behavior.
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

- Verified the executable documentation capture workflow end to end and ran the
  full repository suite with 5,492 passing tests.
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
- Added `-H`/`--selftests` to `generate_pages.py`: a standalone pass that
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

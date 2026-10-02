# Changelog

## 2026-10-01

### Fixes and Maintenance

- Update the new-title prompt and editorial guidance for sitemap browsing: preserve explicit
  difficulty labels including Rigorous and Bonus, distinguish variants with consistent qualifiers,
  and demonstrate parallel family titles using curated pedigree, restriction-map, and statistics
  examples.

- Review all 405 cached problem-set titles in sitemap context and align 48 titles
  across related banks. Restore Rigorous and Bonus pedigree labels; standardize
  MATCH/WOMC pairs, restriction-map variants, tree comparisons, transcription,
  statistical calculations, and other paired titles. Preserve source keys and
  question-format labels, and refresh generated indexes from the curated cache.

- Accept any task CSV line starting with `#` as a comment, including disabled
  rows such as `#biostatistics,...`. Previously only `# comment` was recognized.
  Preserve original row numbers and retain support for existing comments.

- Updated biostatistics task inputs for the renamed
  `null_and_alternative_hypotheses.py` and `hypothesis_statement_errors.py` generators.

- Updated three biostatistics task inputs for renamed question banks:
  `selecting_statistical_tests.yml`, `hypothesis_testing_terms.yml`, and
  `hypothesis_testing_decisions.yml`.

## 2026-09-30

### Behavior or Interface Changes

- Group CLI help examples by workflow and show self-test rebuilds for all subjects,
  one subject, and one topic by alias or title. Clarify that subject/topic filters
  apply to standalone modes and include a focused dry-run example.

- Restore standalone rebuild modes in `build_site.py`: `-H/--selftests-only`
  rebuilds self-test HTML and its manifest from existing BBQ files;
  `-I/--indexes-only` rewrites topic and subject indexes, navigation, and catalogs.
  Both force their selected artifacts and honor subject/topic filters and dry runs.

- Ignore lines beginning with `# comment` in task CSV files, including standalone
  notes and disabled task rows. Preserve original line numbers for active tasks
  and validation errors; comments may appear before the header.

### Fixes and Maintenance

- Start build estimates after three complete rows (or all rows in smaller builds).
  Exclude one longest timing sample from each phase and row-overhead average once
  three samples exist, reducing startup inflation in build finish estimates. Retain
  raw durations and report the same trimmed averages in JSONL (estimator version 3).

- Document the fixed HTTPS npm registry and fixed package names at the URL-open
  call, with a narrow B310 false-positive exemption. Preserve the vendored
  Bandit and typing gates; annotate the catalog capture helper and give its
  cleanup mock the real reconciliation-report shape.

### Developer Tests and Notes

- Apply the permanent-test checklist to recent rebuild and Finder coverage.
  Remove duplicated flag-mapping checks, legacy-command rejection, and advisory
  message-format verification as one-time implementation proof. Keep durable
  catalog identity, global catalog scope, dry-run behavior, CSV comment handling,
  and isolation of standalone rebuilds from generators and converters.
  Disposable converter/render checks remain one-time evidence and are removed.
- After the fixes and test retention review, `source source_me.sh && pytest tests/ -q`
  passes the complete suite: 5,775 tests, zero failures.

- Validate standalone rebuild selection, CLI flags, existing-source conversion,
  manifest refresh, topic/subject index writers, and dry-run file preservation.
  All 78 focused build, loader, cleanup, manifest, page, timing, and dashboard
  tests pass; real conversion and index rendering pass in a disposable site copy.

- Add focused loader coverage for notes, disabled rows, malformed comment text,
  original task line numbers, and validation errors following comments.
- All 57 focused loader, build workflow, and orphan cleanup tests pass. Pyflakes
  passes for the changed Python files.

## 2026-09-29

### Behavior or Interface Changes

- Add a magnifying glass emoji to the Question Finder navigation entry.

- Hide streak and self-test progress personalization on the sitemap and Question Finder.
  Move All Questions to the bottom of the left navigation.

- Remove the self-test wrong-answer buzzer and reduce correct-answer playback volume
  to 0.2. Visual answer feedback remains available for incorrect answers.

- Add a Question Finder with sortable metadata, searchable column filters, active-filter
  removal, and tab-session state. Link it from navigation, the home page, and the sitemap.
  Preserve one row per visible BBQ file, source-derived types, and existing topic links.

- Add a prominent All Questions sitemap link near the top of the home page.
  Confirm the existing All Questions entry in the left navigation links to the same page.

### Fixes and Maintenance

- Refresh the complete Finder catalog during final indexing, including scoped builds.
  Load versioned DataTables/ColumnControl CDN assets with SRI only on the Finder page.
  Add an advisory dependency freshness command and Pages workflow check.

- Remove Git operations from the site build except repository-root discovery.
  Orphan deletion and quarantine now use the filesystem regardless of staging
  state. Filesystem cleanup failures are reported for retry while indexing
  continues. Preserve task-owned PGML companions using the same discovery as
  generation, even when BBQ filenames include variant suffixes.

### Developer Tests and Notes

- Self-test storage, completion, and correctness Node tests pass. A temporary playback
  check confirms incorrect answers stay silent and correct audio plays at volume 0.2.

- Validate Finder generation and build integration with focused Python tests and the
  rendered page with Playwright. Check real CDN/SRI loading, filter combinations,
  session restoration, sorting, pagination, keyboard controls, and load recovery;
  inspect desktop light and mobile dark presentation.

- Recovered the completed build by rerunning only final cleanup and indexing:
  reconciled 59 topic folders and refreshed 10 index, navigation, and manifest
  outputs without repeating question generation or export conversion.

## 2026-09-28

### Fixes and Maintenance

- Show the download-stage average plus/minus one sample standard deviation in the
  dashboard after two measured stages, excluding skips. Show stage averages and
  download spread in seconds with one decimal place for remaining-task calculations.

- Show elapsed/task durations and remaining-time estimates in whole seconds in the
  CLI and dashboard; show subsecond durations as `<1s`. Keep precise JSONL timings.

- Apply the permanent-test checklist to build timing coverage. Keep pipeline-cost,
  skip-invariance, log-retention/accounting, and dashboard-result contracts; remove
  duplicate cached-row, timer-wrapper, terminal-event, and dashboard-wording checks.
  Remove dashboard column-width, row-order, and total-row assertions. Treat layout
  captures and live timing-log analysis as one-time implementation evidence.

- Exclude skipped stages and fully cached rows from build estimate timing samples.
  Count skips as completed work without diluting measured stage costs or overhead.

- Replace current-step details in the build dashboard's upper-left box with
  average BBQ generation, download, and self-test stage times. Exclude cached
  skips from these averages and keep estimated finish and time remaining visible.

- Append a dedicated `build_timing.jsonl` log for normal CLI and dashboard builds.
  Preserve measurements across runs, including start timestamps, total wall time,
  complete rows, individual stages and export formats, task arguments, counts,
  estimate snapshots, and terminal outcomes. Report accounted, active, and
  untracked seconds to expose work outside stage timers; dry runs write no log.

- Estimate remaining build time across generation, self-tests, downloads, topic
  pages, and final indexing in both CLI and dashboard output. Include completed
  rows' conversion overhead, estimate after two complete rows (six operations),
  and reserve full-row costs for final stages until they supply timing samples.
  Retain finish time and time left during slow conversions. Include indexing and
  extra full-build topics in progress totals.

- Move answer sizing and diagram row selection into qti-package-maker's shared
  self-test output. Keep only Material table-gutter integration in website CSS;
  refresh existing self-test markup and shared styles without changing questions.

- Make answer labels allocate available space to their content while keeping
  the answer letter visible. Remove Material's article-table gutters inside
  answer labels so they do not introduce horizontal scrollbars. Remove the
  blanket table-width, presentation-table display, and boxplot-specific overrides;
  diagrams own their sizing independently of this shared choice layout.

- Give table-based self-test choices a full row and scroll their content on narrow
  screens so box plots retain readable scales without overlapping nearby choices.
  Restore normal table layout for presentation tables so percentage-based plots
  use the authored table width.
- Split biostatistics hypothesis-testing tasks into Hypothesis Testing Concepts,
  Z-Tests, T-Tests, F-Tests, and ANOVA, and Chi-Square Tests.
- Group the three biostatistics Hardy-Weinberg tasks in their own topic, including
  frequency calculations and the chi-square equilibrium test.
- Renumber biostatistics topics from descriptive statistics and graphs through
  distributions and probability, z-scores, hypothesis testing, chi-square,
  Hardy-Weinberg equilibrium, and regression for the planned full regeneration.
  Update browser-check routes to retain their intended topic coverage.
- Merge measures of center and variance into Descriptive Statistics, using the
  `descriptive_statistics` task alias; keep Distributions and Probability separate.
- Convert HTML tables and RDKit canvases to packaged images in Blackboard Ultra
  ZIP downloads when the BBQ source contains those drawings. Rebuild ZIPs whose
  pool still contains HTML tables; on conversion failure, omit the affected
  download so a later build can retry it.
- Keep two durable dashboard checks and the generated-title regression check;
  remove the one-time ETA wording check and trim assertions tied to internal
  progress events and title-cache storage.
- Allow up-to-date BBQ rows to finish when the optional progress observer is absent.
- Report actual BBQ question counts against each task's effective `-x` limit in
  the CLI and dashboard, including current files that skip regeneration.
- Remove a brittle test that pinned the default question limit to a specific value.
- Shorten two existing human-guidance bullets to meet the repository's format rule.
- Restore the import-audit allowance for the `qti_package_maker` sibling checkout
  configured by `source_me.sh`.
- Default `build_site.py` title generation to Codex for CLI and programmatic builds.
  `-b ollama` remains available when the required local model is installed.
- List every build operation in the TUI, including topic pages and indexes.
- Normalize generated prime marks to ASCII apostrophes so DNA-orientation titles
  pass the title validator and topic-page rendering can finish.
- Let TUI status cells grow when download counts exceed the initial column width.
- Updated all seven RNA transcription task rows in the biochemistry, molecular biology,
  and biotechnology CSVs to use the consolidated `rna_transcribe.py` executable with
  explicit format and direction flags. Existing course/topic assignments and variants
  remain intact.
- Synchronized shared style guides, tests, and repository support files from the starter template.

### Developer Tests and Notes

- Pass 299 focused timing, dashboard, log, typing, lint, and import checks after
  reducing the timing/dashboard coverage from ten cases to five durable contracts.
  Earlier render and live-log checks remain one-time evidence.

- Pass 295 timing, dashboard, log, typing, lint, and import checks after excluding
  skipped work from estimates; cover skips before and after measured rows.

- Pass 290 timing, dashboard, typing, lint, and import checks after replacing
  current-step details with averages. Verify the rendered box at 126x34 and 80x24.

- Pass 317 focused build, timing-log, converter, typing, lint, and import checks.
  Observe the running full rebuild writing real stage and export measurements.
  Full-suite collection remains blocked while its generated biochemistry index
  is absent during that rebuild; leave the active build and generated files alone.

- Pass all 5,958 offline tests, including full-pipeline timing and slow-conversion
  dashboard regressions. Check rendered timing and progress boxes at 126x34 and
  80x24 terminal sizes, and run a scoped CLI dry run without changing site output.

- Verify one real Blackboard export from a table question contains packaged PNGs
  and no table markup. Keep this browser-backed check as one-time evidence, not
  a permanent pytest; remove the implementation-coupled mock test.
- Check that every topic linked from `mkdocs.yml` navigation has an existing
  `site_docs/<subject>/topic##/index.md` page.
- Pass the full offline test suite (5,885 tests) after the BBQ count and guidance fixes.
- Pass focused CLI, dashboard, and title-generation tests plus `pyflakes` on changed Python files.
- Loaded all ten task CSVs through the website loader and validated all seven transcription
  commands with the consolidated CLI. All 30 focused topic-alias and task-loader tests passed.

## 2026-09-25

### Additions and New Features

- Display question formats as colored, labeled badges in generated topic download rows and
  before titles in the All Questions index. Share one renderer, retain meaningful title qualifiers, and
  resolve variable generator formats from each file with palettes for light and dark themes.
- Distinguish MC and WOMC from `TFMS`, displayed as `T/F Statements (MC)`. Use compact
  rectangular badges with muted fills and colored side bars, outside catalog links,
  to distinguish static question metadata from download actions.

### Fixes and Maintenance

- Align biotechnology topic aliases with the approved task assignments while
  retaining the broader DNA, environmental and synthetic biology, and regulation titles.
- Derive displayed question-type badges from each BBQ file's first record. Shared
  `MC/NUM` cache titles now show the actual MC or NUM output in each topic and
  catalog entry; classify MC generator subtypes from their filenames.
- Align all 47 TFMS filename titles with their TFMS badge while retaining the
  source-verified descriptions of the assessed tasks.
- Generate the badge palette from the existing QTI package maker CAM16 wheel, using
  fixed hues and balanced light/dark mode pairs. Give the four common classes
  distinct red MC, violet WOMC, magenta TFMS, and warm-brown Matching colors.
- Distinguish `FIB_PLUS` records as `MULTI_FIB` with a `Multi-FiB` badge and
  matching cached title suffixes.
- Use 14px type badges in both topic download rows and the catalog.
- Move type badges from variable positions after topic titles to the start of each
  download row; align badges before titles in the All Questions index. Let each badge
  fit its label rather than stretching short labels to a fixed width.
  Emit the markup during the Python site build, with CSS handling only presentation.
- Align paired MATCH/WOMC titles in `problem_set_titles.yml` using the same subject
  wording with format labels at the end.
- Align related restriction-digest, fatty-acid, enzyme-condition, peptide-sequence,
  and paternity-test titles while retaining their distinguishing parameters.
- Align format and content variants for pedigrees, consensus sequences, transcription,
  box plots, monosaccharide classification, restriction-enzyme cut types, and offspring
  counts; use "Enzyme Catalytic Strategies" across MATCH, WOMC, and TFMS titles.
- Shorten question-format labels to `FiB`, `MC`, `MA`, `NUM`, `TFMS`, and `MULTI_FIB` in cached
  titles and title-generation instructions. Record the canonical spellings in
  [PROBLEM_TITLE_ABBREVIATIONS.md](PROBLEM_TITLE_ABBREVIATIONS.md).
- Curate titles for instructors selecting course material: lead with the topic and
  assessed skill, replace format-first boilerplate, and explain variant differences
  using source-verified content instead of opaque type, level, or course codes.
- Record the instructor audience in [HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md) and update
  title-generation guidance and examples to follow the catalog conventions.
- Audit response formats against every generated bank and add consistent final format
  labels. Identify TFMS and WOMC generator families among MC records,
  distinguish generator-variable MC/NUM banks and multiple-blank `MULTI_FIB`
  sets, and document `ORD` for ordering questions.
- Correct titles that conceal content or tasks, including functional-group bond types,
  alpha-amino-acid identification, Wordle pentapeptides, protonation states, and
  serial-dilution volumes; normalize difficulty qualifier capitalization.
- Correct gene-pair distance and monohybrid Punnett-square scope; distinguish
  macromolecule banks by names and properties and amino-acid variants by structure diagrams.
- Inspect all TFMS bank stems so titles describe their assessed task; 33 banks
  evaluate statements and 14 use other MC prompts. Clarify second-messenger
  identification, the 2022 Nobel Prize scope, and reciprocal epistasis-ratio
  tasks. Update the title prompt and abbreviation guide accordingly.

### Developer Tests and Notes

- Regenerate all 55 topic pages and the 478-entry question index. Pass the MkDocs build,
  12 focused renderer/download tests, `pyflakes`, and whitespace checks. Verify badges
  on desktop and mobile in light and dark themes across eight browser cases, including
  noninteractive labels, no horizontal overflow, and keyboard-operated previews.
- Recheck source-specific MC/NUM badges and the final CAM16 palette in desktop
  and mobile browser views, including light/dark colors, distinct common types,
  download controls, and no horizontal overflow.
- Measure all 18 badge text/background pairs at 6.77:1 contrast or higher and verify
  that each CSS pair matches the fixed CAM16 wheel. Preserve all
  379 title keys and parallel MATCH/WOMC content names while introducing explicit MC subtypes.
- Validate all 379 titles as nonempty strings with unique, unchanged cache keys;
  verify parallel names for all 51 MATCH/WOMC pairs and pass `git diff --check`.
- Verify abbreviation replacements preserve all title keys and parallel pairs;
  check the title-generation module with `pyflakes`.
- Verify catalog titles keep all keys and paired base names, and smoke-check the
  instructor prompt. Check enzyme tasks, tree sizes, and course variants against
  their generator or bank sources.
- Verify all 379 titles against the response formats present in their generated BBQ
  records and retain all 51 parallel MATCH/WOMC pairs.
- Recheck every TFMS question stem: 33 banks evaluate statements and 14 use other MC
  tasks. Confirm unchanged unique keys, all 51 parallel pairs, and passing `pyflakes`
  and whitespace checks after the final wording corrections.

## 2026-09-23

### Additions and New Features

- Interactive `build_site.py` runs display the Textual dashboard for the complete
  coordinator pipeline, with live finish estimates and confirmed cooperative cancellation.
- Added mutually exclusive `--cli` and `--tui` options to select plain output or
  explicitly request the dashboard; automatic TTY detection remains the default.
- Restored `-x/--max-questions` on `build_site.py` so CLI and TUI builds can set
  a common per-task question maximum; unrestricted builds default to 50.
- Generators default to `-d 2`; with a common question maximum, the runner now
  passes `-d ceil(max_questions * 1.1)` to request enough output, respecting
  task-specific duplicate counts.
- TUI download cells show available outputs out of applicable downloads.
  Configured YMATCH/YMCS PGML outputs count in the total even when missing;
  other tasks count PG/PGML only when a matching file exists.

### Fixes and Maintenance

- Allow the import-requirements audit to recognize qti-package-maker as a sibling
  dependency supplied through `source_me.sh`.
- Removed per-task `-c 4` flags for the nucleotide-components and mRNA-processing banks after
  moving those defaults into their YAML files.
- Aligned build documentation with row-local task stages, repository-wide
  finalization, task topic alias rules, and configured-output failure handling.
- Corrected stale pipeline comments and helper documentation.
- Topic metadata lookup is split into its own module.
- Subprocess launch handlers now report expected operating-system errors while
  allowing programming errors to retain their traceback.
- Missing converter outputs are built before the topic page is published. Focused
  builds refresh manifest rows for selected topics and preserve the other current
  rows; unrestricted builds still validate every reachable self-test include.
- Human-readable downloads skip sources with no text-renderable questions. Non-selftest
  download and optional PGML errors skip the affected artifact and page button; selftest
  failures still stop the build.
- Normal builds omit per-topic orphan-prune summaries when a folder has no actions.
- Topic pages now render once per affected topic after row-owned self-tests and
  downloads finish, avoiding repeated whole-topic scans. Page-render logs identify
  absent downloads as files this stage does not generate.
- Task CSV headers and rows are validated before use. If repository-wide task ownership
  cannot be established, orphan cleanup is skipped while index generation continues.
- Generated site files, self-test manifests, and optional downloads now write directly to
  their destinations without temporary output files.
- The unified build reports per-task elapsed time and ETA, stage totals, and total build time.
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

- BBQ task runners reject empty or oversized candidates before moving them to configured
  outputs. Per-run backups and PGML temp staging are removed; rerun failed generation and use Git
  history to restore tracked files.
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

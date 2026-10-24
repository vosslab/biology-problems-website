# Changelog

## 2026-10-23

### Behavior or Interface Changes

- Open Human-Readable questions at permanent, filename-based HTML addresses beside their BBQ
  source files. MkDocs publishes lightweight wrappers and QPM converts on demand, so links can
  be copied, bookmarked, shared, and reloaded without UUIDs or query parameters.

### Fixes and Maintenance

- Remove the retired dice-connect matching bank and its cached metadata and generated
  catalog references; its generator mode and task registration were already removed.
- Remove the retired offspring-outcomes MA bank and its title, Bloom, provenance, and
  generated website references. Refresh the Genetics topic 07 indexes and shared catalogs.
- Synchronized shared style guides, tests, and repository support files from the starter template.

## 2026-10-22

- Alternate stacked bank borders between the theme green and a slightly deeper green.
  Preserve the connected edges and match the final bottom border to its card.

- Join topic banks into a continuous stack with rounded green top edges and a bottom
  border only on the final bank. Use the shared Material primary green for visible
  borders across all topic pages, preserving question content and controls.
  Validate the MkDocs build and Chromium desktop, dark-theme, and mobile layouts:
  all 24 Genetics topic07 banks connect without gaps or page overflow, with only
  the final bank drawing a bottom border.

- Apply one shared topic-page layout to all 57 pages. Remove chapter-top progress and Bloom guides,
  number problem headings, and separate bank sections. Record the approved scope and closeout in
  [topic_page_layout.md](archive/topic_page_layout.md). Preserve all 499 bank sections,
  heading IDs, download targets, controls, labels, questions, and grading behavior. No question-bank,
  cached-title, or metadata sources changed.
- Validation: baseline and final MkDocs builds pass; the targeted Python suite passes 542 checks and
  the Chromium suite passes 93 browser tests. Temporary all-page checks confirm section containment,
  IDs, controls, and all 499 rendered bank sections across all 57 pages. Independent specification
  and layout-quality reviews pass. Desktop, dark-theme, 390px mobile, enlarged-text, deep-link,
  download, completion, clear, reroll, and wide-table browser checks pass without overflow or
  console errors. Two rendering issues found during review were corrected: preserve the existing
  heading font size, and insert a blank block boundary between each download row and practice host
  so Markdown keeps every bank inside the outer topic-page wrapper.
  Independent integration review accepts the implementation, confirming all 57 pages, all 499
  bank sections, 556 heading IDs, 499 download containers, focused checks, and composed screenshots
  with no findings or architecture drift.

- Remove duplicate-count overrides from the genetics probability task file; the
  build script owns the generated question count.

- Remove the dice quantity-to-value matching task; its separate MC tasks assess
  expected counts, degrees of freedom, calculations, and interpretation.

- Refocus the four offspring-probability task rows on factorial meaning, factorial
  arrangement counts, binomial setup, and the repeated-phenotype denominator.
  Keep the chi-square assignments unchanged. Retire the four introductory modes
  from the generator so the available modes match this narrower class scope.

## 2026-10-21

### Behavior or Interface Changes

- Increase the global Material layout limit from 61rem to 80rem. Remove that limit on
  Question Finder through its page-only stylesheet, retaining normal navigation and margins.

- Use a three-bar filter icon in every Question Finder column heading. Keep headings left-aligned
  with title, sort, and filter in the same order; reserve intrinsic control widths to prevent
  squeezed icons. Preserve the existing accessible filter dialogs and active-filter states.

- Replace Bloom badges with outlined SVG chevrons and sans-serif circled levels. Connect both
  dimensions on topic pages and in one sitemap column; keep Finder dimensions separate.
  Preserve shared explanations, category colors, readable scale guides, and static label text.
  Fit Finder metadata columns to content, give Name the spare width, and keep titles readable
  when horizontal scrolling is needed. Remove the obsolete sitemap flex-row styling.

- Clarify acceptable MA design in [HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md): multiple valid
  outcomes or properties of one problem, with restriction digest, ABO, gene mapping, metabolic
  rescue, and monosaccharide examples. Distinguish these from independent true/false bundles.

- Remove the combined multiple-answer dice bank from Genetics Topic 07 and its task assignment,
  caches, provenance, catalog, and practice manifest. Its independent statement checks overlap
  the separate dice tasks; retain those tasks. Topic 07 now contains 20 problem sets.
  Remove the retired bank from title-guide and generation-prompt examples.

- Establish [PROBLEM_TITLE_STYLE.md](PROBLEM_TITLE_STYLE.md) as the editorial guide for
  instructor recognition, with before/after examples, chapter-level comparison, and a review
  workflow. Keep format and badge rules in the abbreviation guide, link the style guide from
  agent instructions, and align the generation prompt with the reviewed titles.

- Revise Genetics Topic 07 problem-set titles for instructors selecting class questions.
  Review all 21 together for recognition within the chapter. Distinguish independent births,
  binomial offspring counts, table selection, hypothesis-pair errors, and test conclusions.
  Preserve the approved rejection-criteria and process-error titles. Update the title guide and
  generation prompt to favor the shortest wording that uniquely identifies each problem set.
  Name null and alternative hypotheses explicitly and distinguish dice calculations and statistical
  significance. Verify the dice bank scope: 23 questions
  ask for individual contributions and 27 for totals; all 50 interpretation questions assess
  significance at alpha = 0.05. Keep Calculations rather than the narrower Totals title.
  Refresh topic pages, catalogs, and activity labels, including the shared Biostatistics bank.

- Make the secondary practice control Hide-only. Hide it when the question is collapsed
  and return keyboard focus to Show another question, eliminating the duplicate Show button.
- Double the correct-answer pause from half a second to one second. Cancel pending
  advancement when the reader scrolls, touches, clicks, presses a key, or leaves the tab.
  Keep native smooth scrolling and reduced-motion support.
- Add compact Hide/Show controls beside Show another question, including the first question.
  Collapse only the question body, retain its current content, and cancel pending automatic
  scrolling when hiding. Visibility lasts only for the current page visit.
- Number both Bloom dimensions and explain each label with a tooltip based on Anderson and
  Krathwohl (2001), chapters 4-5. Share the ten definitions across topic pages, the sitemap,
  and Question Finder; add a collapsed scale guide for keyboard and touch access.

### Developer Tests and Notes

- Layout width: MkDocs builds successfully. One-time Chromium and Firefox checks at 390,
  1440, and 1920 pixels in both themes confirm the 80rem global cap, uncapped Finder,
  and no horizontal page overflow. No permanent tests added for these cosmetic settings.

- Finder filter icons: MkDocs builds and all four existing Finder browser tests pass.
  One-time Firefox/Chromium checks verify equal icon sizes, consistent ordering, no overlapping
  controls, and active-filter indication at desktop/mobile widths and enlarged text in both themes.

- Regenerate all 57 topic pages and the sitemap from existing banks and classifications.
  Share SVG geometry and resize handling between generated pages and Finder redraws.
  Preserve homepage history by undoing two unrelated index-build side effects.
  MkDocs builds successfully; all 32 focused Python tests and 11 Finder/practice browser tests pass.
  One-time Chromium 156 and Firefox 157 checks cover both themes, narrow/wide layouts, enlarged
  text, opened scales, Finder redraws, content-sized columns, and labels without JavaScript.
  Remove the temporary checks; add no permanent tests for cosmetic values or taxonomy wording.
  Finder paging and sorting expose a Material theme `delegateTarget` exception in current
  browsers; reproduce the same exception with the unchanged pre-integration Finder script.

- After removing the combined dice bank, verify 20 remaining Topic 07 sets, no live references
  to the retired bank, and byte-identical content in all 495 remaining question-bank files.
  Refresh counts while preserving source history. All 194 focused documentation, title, catalog,
  homepage, and practice-manifest checks pass.
- Title-guide update: 175 documentation-link and focused title/index/download checks pass.
  Smoke-check the prompt's dice examples and verify the two revised catalog titles and formats.
- Update the local SVG Bloom gallery with connected sitemap/topic labels, separate Finder
  columns, thicker outlines, smaller circled numbers, and unbroken text at natural width.
  Keep Finder metadata columns fitted to their content, with Name taking the spare width.
  One-time checks pass in Firefox 157 and Chromium 156 at normal and doubled text size:
  selectable text, tooltips, resizing, offline operation, and no script errors. This is a
  preview only; production rendering is unchanged and ESR has not been tested.
- Verify the revised titles against topic headings and Question Finder; preserve remaining cache
  keys, format labels, and existing homepage history. All 12 focused title/index/download tests pass.
  Two one-time checks cover all 21 chapter titles and the revised prompt with a real question;
  live LLM title generation has not been evaluated.
- Verify the Hide-only controls with a fresh MkDocs build and all eight focused practice
  browser tests, including keyboard focus, independent collapse, and advancement cancellation.
- Review automatic advancement with the HCI, UI/UX, and TypeScript skills; record scope and
  evidence in [SELFTEST_ADVANCEMENT_REVIEW.md](ux/SELFTEST_ADVANCEMENT_REVIEW.md).
  Extend the existing interaction test without pinning the exact pause. All 12 focused browser
  tests pass; one-time checks confirm the doubled pause, reduced motion, and click/touch cancellation.
- Keep one new permanent browser test for reversible, independent question collapse; extend
  existing keyboard-navigation and delayed-advancement checks. Remove new tests that pinned
  Bloom display wording and values after reviewing the permanent-test checklist.
- Refresh all 57 topic pages and the sitemap from existing banks and cached labels. Treat the
  scale-content and desktop/mobile theme review as one-time implementation evidence.
- MkDocs build and all 12 focused browser tests pass. Desktop/mobile review in both themes
  confirms usable scales, no page overflow, and practice buttons staying together when wrapped.
- Full pytest with automatic fixing disabled: 3,442 passed; three unchanged question banks
  retain their existing trailing-whitespace failures. No question-bank content was edited.

## 2026-10-20

- Move the existing offspring-probability bank unchanged from Genetics chapter 6
  to chapter 7 and update its task assignment. Expand chapter 7's description to
  include probability while preserving its title, alias, and URL.
- Add 12 Genetics quiz banks: four probability modes, six dice chi-square modes,
  and separate null/alternative hypothesis questions. Refresh the lab-partner
  bank and replace the Genetics paired-hypothesis placement. Biostatistics retains
  its paired bank. Keep the new/revised tasks together in
  `task_files/genetics_probability_tasks.csv` for scoped regeneration.
- Curate titles and regenerate affected topic pages, catalogs, navigation,
  self-test metadata, and homepage activity. Smaller probability batches respect
  their finite scenario pools rather than inflating counts with cosmetic variants.
- Validation: independently verify 272 probability/dice keys and 90 hypothesis
  keys. The read-only full suite passes 3,416 checks and reports pre-existing
  trailing whitespace in three unrelated banks. An initial default test run
  automatically stripped that whitespace; restore those three files byte-for-byte
  and rerun with automatic fixing disabled. No unrelated bank edits remain.

## 2026-10-19

### Behavior or Interface Changes

- Add cognitive-process and knowledge-type columns to each sitemap topic table, using the
  same cached Bloom labels and theme-aware badges as Question Finder.

- Color cognitive and knowledge labels independently using the matching-template palette. Share
  compact Bloom badges between topic pages and Question Finder, with light/dark theme contrast.
  All 20 rendered category/theme pairs exceed 5.5:1 (minimum 6.06:1); keep palette evidence local.

- Consolidate question-bank headers into title, downloads, and metadata/actions rows. Keep type,
  bank-level Bloom labels, completion and practice controls together; remove redundant practice
  hints and success messages, and shorten the download label to Human-Readable.

- Add estimated Bloom cognitive-process and knowledge labels to Question Finder filters/sorting
  and question-bank displays. Labels persist across instance rerolls and regenerated questions.
- Classify missing filenames with JEV during content generation and index-only builds. Keep the
  editable classification map as one `filename: Cognitive, Knowledge` entry per bank; preserve
  cached labels on ordinary builds and API failures. Provide explicit refresh and coverage commands.
- Keep API credentials, request evidence, probabilities, model/rubric versions, and experimental
  results outside the published site; experimental files live in ignored `LOCAL_ONLY/` storage.

### Developer Tests and Notes

- Complete six independent Bloom audit passes. Update workflow and ownership documentation,
  explain deferred imports, and remove an incidental sitemap cell-count assertion. Flag unrelated
  homepage provenance loss and a staged obsolete experiment for release preparation.


- Move the standalone Bloom utility into `devel/` for explicit refresh/report maintenance.
  Normal `build_site.py` generation and index builds already classify missing filenames.

- Check the unchanged Bloom rubric against 24 blinded official ISU objectives and independent
  assessments of eight banks, then compare a reasoning-first candidate on six fresh banks. Keep
  rubric version 2 and existing labels: evidence does not justify automatic upward promotion.
  Document results in `BLOOM_EXTERNAL_VALIDATION.md`; keep scripts and raw experiments untracked.

- Rank all 414 banks by pre-conversion compression and inspect the largest reductions. Experimentally restore
  pedigree relationships, tree branches, molecular canvases, box-plot marks, DNA gel bands,
  genetic-code associations, and pipette color cues in JEV evidence. Preserve numeric answer fields.
- Remove specialized visual parsers and their tests after the experiment; retain simple extraction,
  the numeric-field fix, cached classifications and documented evidence limitations.
- Reassess 78 affected filenames with the existing model and rubric: 10 pairs change; Analyze rises
  from 30 to 32, while all 12 pedigree banks remain Understand / Conceptual. Keep raw experiments
  untracked and document source-type confounding and remaining visual gaps in `BLOOM_EVIDENCE_AUDIT.md`.
- Revise the taxonomy guide for BPW and add a small live diagnostic set, source-backed rubric
  boundaries, and a coverage report. Reference agreement and stability do not establish accuracy.
- Classify all 414 filenames, then refine the rubric and rerun: 108 pairs change. Provisional
  reference agreement increases from 16/20 to 20/20; the same 25-bank stress sample improves from
  16 unchanged pairs to 23. Record remaining category ambiguities in `BLOOM_FINDINGS.md`.
- Verify compact persistence, source selection, failure/dry-run behavior, shared-bank placements,
  combined Bloom filters, taxonomy sorting, and labels surviving browser rerolls.
- The default pytest whitespace fixer touches three existing BBQ files with trailing empty fields;
  restore their original bytes after verification, keeping question content outside this change.

## 2026-10-14

### Fixes and Maintenance

- Regenerate the 16 BBQ banks with demonstrated invalid CSS from the corrected
  biology-problems generators: Beadle-Tatum pathways, ordered tetrads, tree choices
  and matches, and optimal-enzyme questions. Preserve all bank paths, modes, and
  50-question counts. Reuse the same five-metabolite pathway bank at both course
  placements; new random variants come directly from ordinary generation.

### Developer Tests and Notes

- Verify all 800 question placements with Python QPM parsing and Rust QPM
  `ple_native_json` conversion before replacement. All 15 unique generator runs
  produce 50 accepted questions and 50 native JSON items; verify replacement
  hashes against the generated banks. This validates source-bank conversion.

## 2026-10-12

### Behavior or Interface Changes

- Rename BPW's project-owned browser hooks and WebAssembly package references from `qti`
  to `qpm`; preserve the established `qti_package_maker` Python integration key. Topic indexes use
  `qpm-*` selectors. QTI names remain for Canvas and Blackboard interoperability formats.
- Replace the custom `QPM_ROOT` configuration variable in `devel/vendor_qpm_wasm.py` with the
  explicit `--qpm-root` option. Its default retains the actual `qti-package-maker-rs` checkout
  path while the package path is `packages/qpm-wasm`.

### Developer Tests and Notes

- Rename the existing generated WASM binding files with `git mv` before the next canonical QPM
  package refresh. The producer build replaces the vendored runtime and hashes as one artifact.
- Refresh the vendored package from `packages/qpm-wasm/dist`. The valid-bank browser lanes pass
  all nine self-test and package-download checks. The complete smoke lane reports the already
  identified invalid BPW CSS in three banks; source generators own those corrections.

## 2026-10-11

### Behavior or Interface Changes

- Rename the website's vendored QPM asset directory to `site_docs/assets/qpm_wasm/`
  and its refresh helper to `devel/vendor_qpm_wasm.py`. Update browser consumers,
  browser-test routes, and maintenance documentation. Preserve upstream runtime
  filenames and source provenance.

### Removals and Deprecations

- Remove unused browser and Node demos from the vendored QPM package and exclude
  `examples/` during future refreshes. Keep the runtime, license, and hashes for
  the files the website actually ships.

### Developer Tests and Notes

- Verify unchanged runtime hashes and demo exclusion with two temporary checks,
  then remove those checks. Focused Python validation passes 1,623 checks;
  all three Node checks and nine download/practice browser tests pass against
  the rebuilt MkDocs site. Chromium requires execution outside the macOS sandbox.

## 2026-10-10

### Behavior or Interface Changes

- Distinguish the practice button states with two greens: Roosevelt green for
  **Show practice question** and a slightly deeper green with a thin darker border for
  **Show another question**. Reuse the existing placeholder state and adjust padding
  for the border, preserving compact dimensions and white labels.
- Use Roosevelt green with white text for the practice action, at a compact 28px minimum
  height. Consume Rust QPM's matching green Check Answer buttons and tighter MC/MA rows.
  This requested styling update intentionally differs from the unchanged Python references.
- Tighten the practice toolbar to 8px gaps so its button, completion badge, and hint read
  as one compact group. Preserve existing button padding, heights, colors, and QPM controls.
- Make **Show another question** advance through a bank's source records in
  order, returning to the first record after the last, rather than randomly
  selecting a replacement. Each page visit begins with the first record. QPM
  retains its existing MATCH and ORDER response shuffles. A failed load keeps
  the same position for Retry; a one-question bank restarts with fresh controls.

### Additions and New Features

- Add durable Playwright screenshot evidence for the complete Python QPM and
  BPW self-test set: all ten saved fixtures in light and dark modes, the loaded
  site context, MATCH feedback, mobile table scrolling, an RDKit structure, and
  a short one-play MATCH interaction GIF. Preserve the user-supplied unstyled
  MATCH image as a hash-recorded before-fix reference. Document provenance,
  rerun commands, and source-owned contrast limits in
  [SELFTEST_SCREENSHOTS.md](SELFTEST_SCREENSHOTS.md).

### Fixes and Maintenance

- Consolidate README and self-test captures under `devel/capture_screenshots.sh`.
  The command loads the environment, owns one MkDocs server, refreshes the full corpus
  and its receipt, and shuts down the browser and server. Move capture code out of
  `tests/`; read frozen Python references directly without a separate gallery server.
  Point `npm run docs:screenshots` at the same complete refresh.
- Store the 48 static documentation captures as WebP using the text preset at
  quality 90. Refresh their embeds and receipt, retaining the MATCH GIF and original
  regression PNG. Complete captures in a temporary directory before replacing the corpus.
  Remove the superseded static PNGs; their combined size falls from 4.67 MB to 2.41 MB.
- Make the self-test screenshot capture script executable to match its Node shebang and
  the existing screenshot runner convention.

### Developer Tests and Notes

- Verify both practice button states in light/dark modes at desktop and mobile widths.
  Both retain a 28px height; white-label contrast is 4.52:1 initially and 6.20:1 after
  loading. Keyboard activation and replacement pass, and the WebP corpus is refreshed.
- Run the unified capture command successfully for all 48 WebP images and the GIF.
  Verify receipt hashes, all live embeds, and unchanged frozen Python files. Temporary
  occupied-port, encoder-failure, and interruption checks confirm server cleanup and
  preservation of the published corpus. Remove these one-time checks after verification.
- Verify sequential selection, wraparound, single-question restart, and failed-load
  recovery through the real MkDocs browser lane (seven tests pass). All three Node
  self-test checks pass. An independent Chromium walk visits all 50 questions in the
  shipped genetics MATCH bank in source order, then wraps to question 1 without errors.
  A separate browser assessment confirms MATCH/ORDER shuffling, grading, and Reset
  after replacement in light and dark modes, with no page errors.
  Remove the screenshot runner's obsolete random-number override; question selection
  now follows the normal website sequence.
- Refresh the README screenshots through a local MkDocs server. The HLA capture
  waits for a real WebAssembly-rendered question and installed QPM stylesheet,
  settles the navigation transition before capture, and rejects page or request
  errors.

## 2026-10-09

### Additions and New Features

- Initially add a **New version** control to embedded self-tests. Its behavior was to load the
  vendored QTI WebAssembly converter and question bank on first use, then show another variant.
  The build-time question was the no-JavaScript default; the dynamic-container design below
  supersedes that default. The real-WASM A/B reroll browser
  journey passes across the complete consumer rollout; separate specification and quality reviews
  pass together with fresh isolated combined integration evidence.
- Superseded Phase 2 progress contract: completion was keyed by question CRC, with bank identity used only
  to locate and group variants. Rerolling resets answer controls and feedback while retaining any
  completion record for the shown CRC. The filename-based v2 design below replaces this contract
  and discards old progress without migration.
- Add `devel/vendor_qti_wasm.py` to copy the sibling QTI WebAssembly distribution into the site
  and record its source path and per-file SHA256 in `source.json`; `sourceCommit` is null when no
  revision receipt is supplied.

### Behavior or Interface Changes

- Start every self-test visit at question 1 with fresh WASM-generated content in ordinary HTML
  containers. Generate the next question during a 500 ms feedback pause, retain answered work for
  review, and leave the last question visible. Header controls offer Start question or New version.
- Track completion directly by BBQ filename in `selftest_progress_v2`. Any correct version earns
  the problem-set achievement; rerolls retain it. Shared sets count once across topics. Old CRC
  progress is ignored without migration, while the daily streak rules remain unchanged.

- Generate Blackboard Ultra ZIP, Canvas/ADAPT QTI ZIP, and Human-Readable HTML in the browser
  from the original BBQ source on demand. Load the vendored converter on first use and drawing
  dependencies when needed; show progress and permit retry after failure. Human HTML opens in
  a new tab. Native site builds retain self-tests and skip these prebuilt exports. Direct BBQ and
  PGML downloads remain available.
- Add pinned modern-screenshot/RDKit asset refresh through `devel/vendor_package_render.mjs`,
  with local license texts and version/hash receipts. Refresh canonical QTI WASM by building
  the sibling private package and copying its complete distribution.
- Site artifact generation now requires the executable
  `../qti-package-maker-rs/target/release/bbq-converter`; a missing or non-executable binary
  stops generation rather than selecting the Python converter.
- Run independent native self-test bank conversions concurrently with half of the detected CPU
  count, using one worker when fewer than two CPUs are reported. Each bank's log is emitted as a
  whole.

### Fixes and Maintenance

- Replace Playwright's default static-server startup with the standard-library
  `tests/playwright/helper_serve_site.py` server and listen queue 128. Controlled three-by-32
  request probes reproduce backlog 5 dropping 75/96 requests; backlog 128 serves 96/96 with
  identical bytes and zero errors. The configured four-worker suite passes 94 cases in 11.9s,
  with zero retries and unchanged assertions. Actual-MkDocs acceptance separately passes
  94 cases in 29.2s; earlier MkDocs failures remain unexplained.

- Preserve parsed-head self-test scripts/styles during mounting and execute scripts through the
  existing re-execution path. Add the compact Practice question placeholder and Show practice
  question, Loading question..., Show another question, and Retry states with their hint.
  Keep first automatic loading and filename-based v2 achievements in the website controller.
- Split grouped stylesheet selectors at top level before isolation so global root selectors retain
  Material theme variables, including `--md-hue` in slate mode. Keep other branches scoped through
  the existing isolation boundary. Refresh all 18 vendored QPM files from the local built package;
  their hashes match. Six light/dark checks at 360, 390, and 1280px show readable body text, no
  overflow, and no script errors. Final suite lane passes: 3263 Python checks, three Node checks,
  and 94 post-correction actual-MkDocs Playwright cases with one worker in 29.2s. Minimal local
  horizontal scrolling restores narrow FIB table access; 16 targeted probes and independent
  mobile specification/quality and final composition reviews pass. Earlier asset/readiness
  failures remain unexplained; clean-server acceptance makes no concurrency-fix claim.
  Record isolated evidence, decision propagation, initial failures, and source-owned limits in
  [bpw_python_parity_ledger.md](active_plans/active/bpw_python_parity_ledger.md).
- Complete six independent KISS audit passes. Remove the obsolete standalone-HTML
  Playwright survey tools and `test:survey` entrypoint, fix retired-mode usage text,
  and correct the updater command example and a function separator. Keep the shared
  vendored collector's unstaged-deletion failure separate from BPW behavior.
  All 3,257 tests pass in a temporary current-file checkout. Record findings and
  validation boundaries in the
  [KISS audit](active_plans/audits/bpw_flat_html_kiss_audit_2026_10_09.md).
- Make `devel/vendor_qti_wasm.py` the one-command QPM browser update: install locked
  npm dependencies, run the canonical Rust/WASM and TypeScript build, then vendor
  the result. Stop before touching BPW's current package if either command fails.
  Reuse the existing sibling checkout and `QPM_ROOT` selection without adding modes.
  Verify a real build and WASM conversion in a temporary destination, plus both
  failure paths; leave BPW's accepted WASM artifacts unchanged and remove the probes.
- Retire flat self-test HTML generation and all 482 artifacts. Derive the v2 progress
  manifest directly from reachable topic declarations and nonempty BBQ banks; preserve
  all 482 placements, 411 bank identities, topic metadata, and row order. Remove the unused
  sample CRC, fingerprint, and standalone path fields from the regenerated manifest.
- Remove native QPM vendoring and conversion stages, the self-test build mode, and related
  timing UI. Keep WASM self-tests, browser exports, and direct BBQ/PGML downloads unchanged.
  Compare the old and new manifests before deletion and preserve external reference evidence.
  Record build, test, and fresh-browser evidence in [BPW_FLAT_HTML_RETIREMENT.md](BPW_FLAT_HTML_RETIREMENT.md).
- Apply KISS to the cleanup: remove the unused naming wrapper, duplicate naming and
  filesystem-side-effect tests, migration-only field stripping, redundant sorting,
  and the speculative symlink gate. Keep the manifest's reachability, identity,
  invalid-bank, scoped-refresh, and dry-run contracts; document recovery on failure.
  Treat migration counts and hashes as one-time evidence rather than permanent gates.

- Install the shared `pip_requirements.txt` for GitHub Pages deployment instead
  of a separate incomplete package list;
  this supplies `tinycss2`, required by the CSS-isolation build hook.
- Vendor the macOS ARM64 Rust `bbq-converter` as a Git-tracked BPW dependency.
  Normal builds select the local binary by OS/CPU and require no QPM checkout or
  Cargo. Move Cargo preparation into the explicit QPM refresh helper, supporting
  native-only, WASM-only, or combined refresh with native provenance and license.
  This supersedes automatic Cargo preparation during site builds described below.
- Verify the vendored binary with QPM checkout reads denied and Cargo/rustc absent
  from PATH: the actual `build_site.py -H --cli` regenerates all 482 self-tests and
  the manifest. Retain platform-selection and source-independent resolution tests;
  exclude native machine code from the script-only shebang hygiene check. The final
  Python suite passes 4,248 tests, and the MkDocs build succeeds.
- Recover a missing native converter by preparing QPM with Cargo before bank jobs.
  Resolve its checkout from `QPM_ROOT` or the sibling default and use Cargo's reported
  executable path instead of assuming `target/release`. Cargo reuses current builds.
  Report dependency failures without a CLI traceback and retain existing self-tests.
  Keep native preparation separate from WASM vendoring.
- Validate native recovery from the missing release binary, then rerun
  `source source_me.sh && ./build_site.py -H --cli`: 482 self-test files and the
  manifest regenerated successfully. All 4,241 Python tests and `mkdocs build` pass;
  an unavailable QPM checkout reports actionable instructions without a traceback.
- Refresh the vendored QPM WASM from the corrected upstream package using
  `devel/vendor_qti_wasm.py`; retain the existing CSS isolation boundary.
- Validate MC, MA, MATCH, ORDER, scientific tables, and molecular drawings in light
  and dark themes, including selection, grading, clearing/reset, repeated New version,
  advancement, and persistent completion. Keep the representative rendering and
  randomization probes temporary. MATCH/ORDER shuffle in QPM; MC/MA retain the
  source's intentional choice ordering.
- The approved BP source contrast correction pairs fixed light table backgrounds
  with black text. Refresh the two affected dihybrid and macromolecule banks from
  those corrected generators. Validation passes: 16 browser checks (11 temporary), 4,240 BPW Python
  tests, and 5,084 BP Python tests. Four additional temporary browser journeys verify
  the refreshed banks directly from the built site in light and dark modes.
- Keep Material and website CSS outside dynamically mounted self-test content using a scoped
  build-output stylesheet boundary. Remove obsolete question-specific website overrides.
- Stop adding result-pill classes to answer rows; QPM owns feedback presentation and clearing.
- Record independently reproduced renderer findings in
  [RUST_QPM_SELFTEST_HANDOFF.md](RUST_QPM_SELFTEST_HANDOFF.md).

- Consolidate initial generation, replacement, script readiness, grading notifications, and
  advancement in the question controller. Progress and streaks consume the same grading event;
  replaced questions and navigation invalidate pending advancement.
- Discover manifest entries and prune orphan containers using the generated topic declarations.
  Use the WASM renderer's button styles for New version and keep source banks/downloads unchanged.
- Record human guidance in the user's wording and move implementation rationale to design decisions.
- Rotate older changelog entries into [CHANGELOG-2026-10a.md](CHANGELOG-2026-10a.md).
- Six independent audit passes identified superseded changelog wording, a curriculum-dependent
  browser test branch, and unused summary arguments. Clarify the history, trim the fragile test
  branch, document Retry, and remove the unused arguments.

- Order reroll initialization after the external converter script loads successfully, handle load
  errors before inline initialization, and reenable retry after a load failure.
- Correct build help and developer documentation to describe browser-generated package exports,
  direct BBQ/PGML files, and native self-test timing. Remove two request-path assertions that
  duplicated semantic package and retry coverage.

### Developer Tests and Notes

- Documentation closeout check: `source source_me.sh && python3 -m pytest tests/test_markdown_links.py -q`
  passes all 155 checks in 0.11s. This focused result does not establish final parity acceptance.
- Retain one real-WASM clearing/progress journey alongside the four lifecycle browser tests:
  incorrect and correct feedback clear, while completion survives clearing, reroll, and reload.
  Keep CSS comparisons and layout diagnostics as temporary implementation validation, not
  permanent tests. Document the isolation alternatives in [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md).
  Earlier isolation probes checked MATCH in Chromium, Firefox, and WebKit at desktop/mobile
  widths in both themes; the corrected-WASM integration checks above used Chromium.
- Six independent audit passes completed. Add the CSS hook to the architecture map,
  clarify its docstrings and validation history, and remove feedback-class assertions
  from the permanent Clear Selection journey while retaining behavioral checks.

- After the six-pass audit cleanup, all four focused lifecycle browser tests and three Node
  checks pass against the updated source. The full-suite counts below precede audit cleanup;
  no new permanent tests were added.
- Validate the dynamic question lifecycle with 4,224 passing Python tests, three Node checks,
  and all 92 Playwright tests. Review initial and regenerated grading for MC, MATCH, NUM,
  ORDER, and molecular drawings, plus desktop/mobile layouts in light and dark modes.
  Verify retained answers, fresh reloads, the last question, and practice without browser storage.
- Regenerate 57 topic pages and 15 index/metadata outputs, then build MkDocs successfully.
  The filename-based manifest contains 482 placements for 411 unique problem sets; all 1,220
  protected source and download files retain their previous hashes.
- Earlier Phase 2 evidence, before the filename/container redesign: the website parser accepts
  valid class-first question containers. Full native `-H` generation
  refreshes 482 self-tests in 13 seconds; `-I` refreshes 57 topic pages and 15 metadata outputs
  in 22 seconds.
  Wrapper/manifest sets match all 482 banks with no missing inputs/includes. The real-WASM
  A/B/A journey passes, including incorrect B without stored completion, separate correct A/B
  records, fresh controls on return to A, and one-time reload/multi-slot checks without page errors.
- Earlier Phase 2 evidence, before the filename/container redesign: after KISS trimming,
  3 permanent Playwright checks pass in 2.0 seconds against the existing
  HTTP site on port 8734, 7 manifest cases pass in 0.05 seconds, and 3 Node checks pass. Retained
  checks protect per-question completion, native attribute order/missing roots, and demonstrated
  script readiness/retry. Removed speculative attribute matrices, repeated grading, redundant
  permanent reload, and the v2-null assertion; one-time receipts preserve the broader proof.
- A prefix inventory of 482 banks, 16,157 MC/MA rows, and 80,088 choices finds no affected raw
  prefixes. The synthetic CRC discrepancy remains upstream-owned and does not block website
  acceptance. Artifact hashes and `sourceCommit: null` record provenance, not compatibility gates.
- Phase 1 full-build verification passes with zero failed exports, semantic question/grading/media
  checks, matched native/Python timing, and 6,075 passing tests. Phase 2 consumer and fresh isolated
  combined integration acceptance pass, including 482 matching wrappers/manifest rows, a successful
  MkDocs build, and 3 browser checks including the real-WASM journey. The user intentionally
  restored live generated files; future generation/browser proof runs in isolation. See
  [optimized_spindle_phase2_acceptance.md](active_plans/reports/optimized_spindle_phase2_acceptance.md)
  and [optimized_spindle_execution.md](active_plans/reports/optimized_spindle_execution.md).
- Phase 3a representative visual review selects uniform full-color modern-screenshot captures at
  scale 1; palette reduction changes guide heading colors. Fresh specification, quality, and local
  integration reviews pass. The manager accepts Phase 3a and selects D under the revised local
  acceptance criteria; Phase 3b and final independent local integration are complete. Actual
  Ultra compatibility remains unverified.
- Phase 3b source checks pass 6,081 website tests and 5 browser checks. Three real source banks
  retain all 150 question identities, order, and grading with 1,051 valid packaged PNGs. PNG
  completion rejects signature-only, truncated, and corrupt images before packaging. Final
  scientific assessment passes for 14 sampled native/browser image pairs. Migrate 57 topic pages
  and remove 1,424 retired generated exports after replacement acceptance; 1,400 protected files
  remain unchanged. Site storage falls by 559,762,347 bytes. Live MkDocs and 5 post-cleanup browser
  checks pass; final independent integration accepts the complete plan. Remote publication remains
  unperformed; actual Ultra compatibility remains unverified external evidence. Temporary
  experiments are archived at
  `/private/tmp/optimized_spindle_evidence_20261009/` with path mappings and receipts. See
  [optimized_spindle_phase3_acceptance.md](active_plans/reports/optimized_spindle_phase3_acceptance.md).

## 2026-10-05

### Additions and New Features

- Add the six pedigree task variants to Genetics Topic 06 (Chromosomal Inheritance),
  using the full inheritance-pattern set including X-linked and Y-linked inheritance.

- Add a compact teaching homepage with featured, grant-supported Biochemistry and Genetics
  courses, additional subjects, a prominent Question Finder link, subject statistics, recent
  additions, daily puzzles, and a real pedigree preview.
- Generate homepage data and HTML during build finalization, including index-only and scoped
  builds. Track task-file admission history and upstream source lineage across Git-detected
  renames. Group format variants in activity feeds and treat the initial task inventory as a
  baseline rather than new content.
- Capture source and output fingerprints after successful question generation. Show revision
  dates only for verified generated outputs; existing outputs begin with unknown provenance.
- Complete activity navigation with generated Latest additions and Recently updated pages,
  homepage View all links, full dated family lists, subject/topic context, and direct links to
  question-bank preview/download controls. Refresh the pages globally during normal and
  index-only builds, including subject/topic-scoped builds.

### Fixes and Maintenance

- Restrict all six Genetics Topic 05 pedigree tasks to autosomal inheritance with
  `--autosomal`; sex-linked inheritance has not been covered at this point.

- Move Latest additions and Recently updated to separate bottom-of-sidebar links, replacing
  the Collection activity group.
- Use emoji consistently for sidebar navigation, including puzzle and tutorial links.
- Add a clock emoji to Collection activity so every top-level sidebar entry has an icon.
- Use jack-o'-lantern orange for Other's chart entry and Cell Biology/Biophysics links,
  with a deeper light-theme accent and a brighter dark-theme companion.
- Tint dark-mode course card surfaces and borders with their assigned identities and use
  neutral descriptive text. Unassigned subjects use neutral dark cards instead of green fills.
- Add Molecular Biology magenta and Laboratory teal-green course identities in both themes,
  including their card surfaces and chart accents.
- Reuse the existing subject emojis from MkDocs navigation on homepage course cards;
  remove the separate Font Awesome subject mapping so identities stay consistent.
- Compact the homepage hero and give it distinct light/dark surfaces: pale green with dark
  text in light mode, deep green with light text in dark mode. Shorten introductory copy
  and reduce padding and headline/stat sizing while retaining the primary search action.
- Align homepage course cards and subject chart with the syllabus course palette: purple
  Biochemistry, blue Genetics, dark lime Biostatistics, and brick red Biotechnology.
  Reuse the documented dark accents and review a light-purple Biochemistry companion;
  unassigned subjects retain site green.
- Label subject-index bank counts as question sets, distinguishing them from generated question
  counts. Keep topics as chapters and subjects as course areas.

### Decisions and Failures

- Keep Biochemistry and Genetics featured as complete, grant-supported courses. Use active task
  CSVs for membership and upstream Git for authored history; do not infer dates from output
  filenames or filesystem timestamps. Shared renderer changes do not refresh every YAML bank.
- Two macromolecule inputs currently own the same output. Count that bank once and leave its
  history unresolved until a successful generation records its actual input.
- Homepage summaries alone did not complete the activity workflow. Add the dedicated pages
  and verify both preview-to-download paths before closing the work.
- Track question sets rather than individual generated questions; generated quantity is an
  arbitrary build setting. Remove that quantity from the homepage snapshot and chart.

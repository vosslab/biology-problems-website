# Changelog
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

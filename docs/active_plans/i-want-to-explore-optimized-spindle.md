# Rust QPM integration for biology-problems-website

## Goal and context

Use the Rust port `~/nsh/PROBLEMS/qti-package-maker-rs` to (1) speed up `build_site.py`,
(3) let students draw a new selftest variant in the browser, and (2) build download packages
on demand in the browser so the repo stops storing prebuilt packages, including the
Blackboard ZIPs that need HTML-table-to-image rendering.

### Evidence

- **Current export path:** `topic_page.create_downloadable_format`
  (`bioproblems_site/topic_page.py:172`). It runs the **Python** `bbq_converter.py` (a symlink
  to `qti-package-maker`): one process per file per format, fully serial. `human_readable`
  goes through the Python API instead (`topic_page.py:133`).
- **Rust CLI is a drop-in:** the Rust `bbq-converter` (`qti-cli/src/app.rs:19-77`) accepts
  every flag the site passes: `--canvas_qti_v1_2`, `--blackboard_export_zip`, `--selftest`,
  `--human_readable`, `--quiet`, `--input`, `--output`, `--html-to-image`. The release binary
  is already built.
- **Rust speed** (`docs/WEBSITE_EXPORT_BENCHMARK.md`):
  - All exports take 0.58x the Python time.
  - Without HTML-to-image: 0.39x.
  - With HTML-to-image: 0.65x.
  - Blackboard ZIPs with tables average 11.4 s each and dominate the build.
- **WASM package** (`packages/qti-wasm`):
  - `convert` takes BBQ bytes plus companion files, `outputFormat`, `shuffleSeed` and `limit`.
  - Size is 1.5 MB gzipped; one conversion takes 7-25 ms.
  - It has no renderer, but it already packages pre-rendered PNG companions into a correct
    Blackboard ZIP with no Rust changes (`WASM_PACKAGE.md:94-105`).
- **Why tables become images:** Blackboard Ultra strips `style`, `class`, `<style>` and table
  attributes on import, and runs no scripts and no SVG (`qti-package-maker/docs/BLACKBOARD_ULTRA_NOTES.md:28-58,288-309,518-522`).
  - Plain data tables survive as grids.
  - Drawing tables (gels, Punnett squares, projections) and RDKit canvases do not.
  - Rust uses Chromium because it has no WeasyPrint-like HTML/CSS engine. A browser is
    that engine.
- **Render pipeline:** `qti-native/src/html_to_image/`.
  - It renders every outermost `<table>` in the stem, choices and answers. It is not limited
    to styled tables.
  - Viewport is 1280x720 at `DEVICE_SCALE_FACTOR = 2`, with embedded Atkinson fonts and a
    16 px margin.
  - Output is the default PNG with no optimization.
  - About 2,000 lines of the rewrite logic are pure Rust: `selectors.rs`, `convert.rs`,
    `naming.rs`, `cache.rs`, `canvas_script.rs`.
  - These are blocked from WASM only by crate dependencies (`chromiumoxide`, `tokio`,
    `tempfile`, and `CanvasSource` living in `qti-molecule`).
  - `selectors.rs:41-135` already has a plan/replace split.
- **Site behavior:**
  - Each bank is a fixed pool of 50 variants (422 of 482 banks).
  - The selftest shows one random item chosen at build time.
  - Progress tracking keys on question CRC (`selftest_manifest.py:136-157`).

### Storage, measured

| Artifact | Files | Size |
| --- | --- | --- |
| Blackboard ZIP (all) | 479 | 509 MB |
| Blackboard ZIP, table banks | 187 | 488 MB (96%) |
| Blackboard ZIP, canvas-only banks | 14 | 15 MB |
| human_readable HTML | 466 | 43 MB |
| selftest HTML | 482 | 14 MB |
| Canvas QTI ZIP | 479 | 7 MB |
| BBQ txt (source, stays) | 482 | 163 MB |
| `.git` (Blackboard ZIP blobs about 1.5 GB of it) | | 1.8 GB |

- **Inside the Blackboard ZIPs:** 28,129 PNGs, all rendered at DPR 2.
- **Duplicates:** 23% of the PNGs are repeats inside the same ZIP.
- **Compression** on a sample of 200 PNGs:
  - Lossless optimization: 2% smaller.
  - 64-color palette: 67% smaller.
  - DPR 1 plus 64 colors: 83% smaller.
- **Git growth:** git cannot delta-compress ZIPs, so every full rebuild adds about 0.5 GB of
  history.

### Phase 3 options compared (working-tree savings, approx)

| Option | Prebuilt kept | Saved | Git growth per full rebuild |
| --- | --- | --- | --- |
| A. Status quo | 573 MB | 0 | about 0.5 GB |
| B. Prior plan: on demand except Chromium Blackboard ZIPs | about 503 MB | about 70 MB (12%) | about 0.5 GB |
| C. Keep prebuilt, shrink PNGs (DPR 1 + 64 colors + writer dedup) | about 100 MB | about 470 MB | about 0.1 GB |
| D. **All formats on demand, browser renders tables (recommended)** | about 0 (plus about 2 MB WASM/lib/fonts) | about 570 MB | about 0 |

C applies only if Phase 3a finds a fundamental limit. Class-specific failures lead to D with a
small prebuilt exception set (for example canvas banks: 15 MB). Its PNG shrinking also improves D's
downloaded ZIPs. Existing history (1.8 GB) shrinks only with a `git filter-repo` rewrite.
Working-tree cleanup removes replaced generated packages after independent review and automated
replacement-download checks. Record the actual storage delta; approximately 570 MB is an estimate,
not an acceptance threshold. Existing Git history and index changes are outside this plan.

## Approach

Use the smallest coherent design supported by demonstrated needs. Follow
[PYTEST_STYLE.md](../PYTEST_STYLE.md): retain permanent tests for meaningful behavior, use
`tests/_temp/` for one-time evidence, and review those checks for removal at closeout.
Hashes and source revision records identify consumed artifacts; they are not compatibility
requirements. Avoid arbitrary byte, pixel, version, or exhaustive-matrix gates.

Each phase ships on its own. Phase 1 comes first because the native CLI stays the
reference output that Phase 3 compares against.

The manager and subagents complete every milestone using independent assessments and automated
behavior checks. D13 in [optimized_spindle_execution.md](reports/optimized_spindle_execution.md)
supersedes earlier human acceptance gates, including those in historical experiment reports.
Independent agents assess scientific fidelity from the native/browser gallery. Automated checks
verify source grading, package validity, complete media, authored display geometry, and actual
browser download behavior. Actual Blackboard Ultra import remains optional external evidence
and an explicitly unverified compatibility limitation; local checks do not establish Ultra
compatibility. Credentials and human availability are not dependencies. The manager assigns
isolated Rust source-owner work in the approved sibling checkout when required and reviews the
result before consuming it.

Delegated instructions state the desired behavior, exact owned files, and required checks.
Owners may raise clarification, challenge, or escalation questions with the manager; the manager
records decisions and verifies their application before dependent work continues.

### Phase 1: Rust CLI in build_site.py

1. In `git_paths.py`, next to `find_bbq_converter`, discover
   `../qti-package-maker-rs/target/release/bbq-converter`. A missing binary raises an error;
   there is no Python fallback.
2. In `create_downloadable_format`, build the command as
   `[binary, "--quiet", f"--{prefix}", "--input", ..., "--output", ...]`.
   - Route `human_readable` through `--human_readable`.
   - Delete `_create_human_readable_download`. Keep its "no supported questions, so skip"
     behavior by checking the Rust exit code and output.
3. Parallelize the per-bank subprocess calls in `build_stages.run_downloads` and
   `run_selftests`.
   - Use `concurrent.futures.ThreadPoolExecutor`, since the work runs in child processes.
   - Use a fixed worker count of `os.cpu_count() // 2`, with no CLI flag.
   - Print each task's output whole so lines do not interleave.

A PyO3 module is not needed. Chromium rendering is already inside the CLI, and Rust process
startup costs milliseconds.

### Phase 2: "New version" button for selftests

1. Vendor the complete built `packages/qti-wasm/dist` into `site_docs/assets/qti_wasm/`
   with a devel copy script that records source path and consumed-file hashes. Record the
   source commit only when supplied; otherwise use null with its provenance qualification.
2. Before implementing rerolls, compare Python and Rust selftest HTML, grading hooks, and question
   identifiers. Fix the source-owner contract in the Rust QPM implementation so it preserves the
   Python behavior intended by the site. Do not compensate in the website for unintended Rust
   output changes. Assign the findings and owner-side fixes to an isolated Rust QPM subagent workstream.
   The coordinating manager accepts that source-owner work before website consumption.
3. Add `site_docs/assets/scripts/selftest_reroll.js`. It adds a button to each `.qti-selftest`.
   On the first click it:
   - Lazy-loads the WASM.
   - Fetches the bank's published `bbq-*-questions.txt`, whose path is in a `data-bbq`
     attribute written by `update_index_md`.
   - Calls `convert({outputFormat: "html_selftest", shuffleSeed})` and swaps the block in.
   - Re-creates the inline `<script>` nodes so `checkAnswer_*` is defined.
4. Preserve progress by question identifier in `selftest_manifest.py` and
   `selftest_progress.js`. Bank metadata routes and groups variants; it does not own completion.
   Each variant retains its own completion status, so completing one question leaves every other
   variant incomplete. A reroll presents a fresh opportunity to answer while retaining the
   selected variant's own completion status when that variant is shown again. Keep answer UI state
   for the new attempt distinct from its completion record.
5. Keep the build-time selftest include as the no-JS default.

### Phase 3a: feasibility experiment (decides between options D and C)

Put the experiment under `tests/_temp/blackboard_browser_render/`, or in the Rust repo's
`output_*` folder. It uses the current WASM package as-is.

1. **Corpus covering ten scientific classes**, with nine real banks where classes overlap:
   - gel with box-shadow
   - Punnett square
   - chi-square data table
   - gene tree LEVEL_4
   - tetrad (950 unique jobs)
   - `which_macromolecule-MC` (large guide table)
   - Fischer/Haworth projection
   - an agglutination-wells table
   - an RDKit canvas-only bank
   - the table+canvas case in the same macromolecule bank as the large guide table

   Record class overlap rather than inventing another bank. Preserve the complete job inventory
   for each bank; use representative jobs covering every class and rendering hazard to calibrate
   the libraries, browsers, and scales before full-bank work.
2. **Extract jobs:** a small Python helper using lxml pulls the outermost tables. It wraps
   each one in the same document the native renderer uses (`chromium.rs:347-362`: CSP,
   embedded Atkinson fonts, 16 px margin). It also writes a rewritten BBQ with `<img>`
   references.
3. **Render in the browser:** calibrate representative jobs in Chromium, Firefox and WebKit with
   **modern-screenshot** and **snapdom** at scale 2 and scale 1. Select a passing configuration
   for full heavy-bank rendering and packaging (tetrad, gene tree, macromolecule, and canvas).
   The current inventory contains 1,960 jobs; it does not require 23,520 matrix captures.
   Skip html2canvas: it re-implements CSS painting and does not list box-shadow as supported.
   Canvases are drawn with RDKit.js `draw_to_canvas_with_highlights`, then `toBlob`.
4. **Image optimization:** compare palette-quantized PNGs (64 colors) on representative
   browser output. Retain the option only if scientific content remains readable; record
   measured size changes rather than impose a byte threshold.
5. **Compare to the native output:**
   - Build a side-by-side HTML gallery against the native CDP PNGs.
   - Use perceptual distances as optional triage diagnostics; an independent agent reviews
     scientific fidelity to determine visual acceptance, without an arbitrary imagehash threshold.
   - Time each table and each bank.
6. **Package:** feed the rewritten BBQ and the PNG companions to the existing WASM `convert`
   with `blackboard_export_zip`. Run `qti-package-maker check` on the result.
7. **Automated behavior assessment:** compare browser packages to original-source native/WASM
   conversions. Verify question counts, identities, response conditions, score values, choice
   order, asset references, complete media, and authored image display geometry. Exercise actual
   browser rendering and packaging on the selected complete heavy banks. Preserve the original
   ItemBank identity through planned rendering APIs; reparsed image presentation must not become
   the identity or grading authority.
8. **Decision rule:** two gates decide viability, and both must pass for D:
   - **Visual fidelity:** an independent agent reviews the gallery for scientific content,
     readable labels, geometry, and full-color appearance. Cover all ten classes and demonstrated
     hazards, especially gel bands, projections, and RDKit canvases, in Chromium and Firefox.
     Full-bank render completion and media checks supplement this representative review.
   - **Local behavior correctness:** browser-built ZIPs pass package and original-source grading,
     identity, complete-media, display-geometry, and selected full-bank rendering checks. This
     gate establishes the implementation's local contract. Actual Ultra import/display/grading
     compatibility remains unverified unless external evidence becomes available.

   A gate failure starts triage, not a fallback. Classify every failure before deciding:

   | Failure scope | Example | Response (stay on D) |
   | --- | --- | --- |
   | One library | snapdom drops box-shadow, modern-screenshot does not | Pick the library that passes; try a hand-rolled foreignObject capture as a third candidate |
   | One browser | WebKit foreignObject bug | Support the passing browsers; show the browser notice only on affected buttons |
   | One image type | Gel bands or RDKit canvases fail everywhere | Try a fix in the source: wrapper CSS, or swap the CSS effect in the generator for an equivalent one. If that fails, prebuild only that class, shrunk (canvas banks are 15 MB) |
   | Packaging or display | Images oversized, broken references | Diff browser and native ZIP source grading, media references and authored image geometry. Fix shared packaging behavior at the Rust owner (for example missing width/height). Record any actual external import evidence separately. |

   - **When to choose C:** only for a fundamental limit. That means a table class that no
     library reproduces in any major browser after the source fixes are tried, and whose
     prebuilt share is too large to keep as an exception. A demonstrated shared packaging limit
     after source-owner fixes may also justify C. Missing external Ultra evidence does not
     constitute a failure or select C.
   - **Record the outcome:** the spike report lists each failure, its classification, the fix
     tried, and the result.
   - **What timing and WebKit results decide:** UX only. A progress bar, and the browser
     notice.

   Record the results in `docs/active_plans/reports/blackboard_browser_render_spike.md`.

### Phase 3b: on-demand downloads (if D)

**Rust repo (`qti-package-maker-rs`):**

1. Move the portable rewrite code (`selectors`, `convert`, `naming`, `cache`, `canvas_script`)
   out of `qti-native` into a new portable crate. Split `CanvasSource` out of `qti-molecule`.
   `qti-native` keeps `chromium.rs` and the RDKit shim as its renderer.
   - Gate: native/portable/WASM same-input checks find zero unexplained behavioral regressions
     in identities, grading, media, or logical dimensions. Preserve classified findings and
     baseline evidence. Python comparison is an optional migration reference under the audited
     upstream contract; report its actual differences without claiming zero findings.
2. Add two WASM exports in `qti-wasm/src/boundary.rs`:
   - `planRenderJobs(request)` returns jobs: `{id, kind: table|canvas, html or canvasSpec,
     contentHash}`, the wrapper document, and the font bytes. Table HTML marks each nested
     canvas with a placeholder that refers to its canvas job id.
   - `finishConvert(request, renders[{id, png}])` applies the replacements, naming and alt
     text, builds `MemoryAssets`, overlays them and calls `write_bank`.
   - The same Rust code serves native and browser, so QPM logic is not duplicated in JS.
3. Fold in the size fixes:
   - Content-hash dedup in the Blackboard writer.
   - Optional palette quantization, if the experiment shows it reads well. Native builds
     benefit too.

**Site:**

4. Add `site_docs/assets/scripts/package_download.js`. A download button:
   - Fetches the BBQ.
   - Calls `planRenderJobs`.
   - Renders jobs in a hidden same-origin iframe with the wrapper document, using the
     library chosen in 3a. Rendering stays on the main thread because DOM work cannot run in
     a worker. It shows a progress bar and dedups jobs by hash.
   - Calls `finishConvert` and triggers a Blob download.
   - Canvas, human_readable and Blackboard ZIPs for non-table banks skip the render step and
     call `convert` directly. human_readable opens in a new tab through a blob URL.
5. Keep the ORDER blacklist at build time; it decides which buttons appear.
6. Stop generating Canvas, human_readable and Blackboard artifacts in `build_stages.py` and
   route new UI links through on-demand buttons. An independent agent reviews the affected
   direct-URL patterns and verified replacement behavior after automated download/package checks
   pass. Then remove only the replaced generated Canvas ZIP, Blackboard ZIP, and human-readable
   files through filesystem operations. Preserve BBQ sources, selftest HTML, authored assets,
   and any named prebuilt exceptions. Record removed paths, URL impact, verified replacement
   routes, and actual storage delta. This planned permanent cleanup is distinct from isolated
   transient generation; Git history and index changes remain outside the implementation.

## File scope

- **This repo, Phase 1:**
  - `bioproblems_site/git_paths.py`
  - `bioproblems_site/topic_page.py`
  - `bioproblems_site/build_stages.py`
- **This repo, Phase 2:**
  - `selftest_manifest.py`
  - `site_docs/assets/scripts/selftest_progress.js` and `selftest_reroll.js`
  - `site_docs/assets/qti_wasm/`
  - `extra_javascript` in `mkdocs.yml`
  - the WASM vendor script in `devel/`
- **qti-package-maker-rs, Phase 2 contract fixes:**
  - Rust selftest HTML generation, grading hooks, and question identifiers identified by the
    Python/Rust contract investigation
- **This repo, Phase 3:**
  - `tests/_temp/blackboard_browser_render/` (experiment, removed after the report)
  - `site_docs/assets/scripts/package_download.js`
  - the vendored rendering library and fonts under `site_docs/assets/`
  - download-button rendering in `topic_page.py` and `download_buttons.py`
  - build-stage and UI routing changes, followed by reviewed removal of replaced generated artifacts
- **qti-package-maker-rs, Phase 3b:**
  - the new portable crate
  - `crates/qti-native`, `crates/qti-molecule`
  - `crates/qti-wasm/src/boundary.rs`, `packages/qti-wasm/src/index.ts`
  - the Blackboard writer dedup
  - `docs/WASM_PACKAGE.md`, `docs/HTML_TO_IMAGE.md`
- **Docs in both repos:**
  - `docs/INSTALL.md` (Rust binary)
  - `docs/USAGE.md`
  - `docs/CHANGELOG.md`

## Completion checks

- **Phase 1:**
  - A full `source source_me.sh && python3 build_site.py` run completes with required native
    rendering successful. Exit zero with renderer failures and skipped exports is insufficient.
  - Compare regenerated question content, grading semantics, media references/completeness,
    and package validity. Explain actual differences; serialization, timestamps, and the
    selftest pick may differ without breaking those contracts.
  - `qti-package-maker check` passes on sample ZIPs.
  - Record full-build stage work and timing, then measure native and Python conversion on
    matched unchanged-source workloads. The historical roughly 1183 s run included 1069 s
    of BBQ generation; cached stages or a current 116-stale-bank build do not establish
    converter speedup against it.
  - `pytest tests/` passes.
- **Phase 2:**
  - The Python/Rust selftest contract investigation records HTML, grading-hook, and identifier
    differences; manager-assigned source-owner fixes preserve intended Python behavior in Rust
    for the real website corpus. Keep the synthetic prefixed-choice CRC discrepancy in the
    upstream findings record: D8 finds no affected website choices, so it does not block consumer acceptance.
  - On `mkdocs serve`, "New version" shows a different variant that grades correctly.
  - Completing variant A leaves variant B incomplete; returning to A retains A's completion status.
  - A rerolled variant provides a fresh answer attempt while its completion status remains specific
    to that variant.
  - A page with no click loads no WASM.
  - Playwright coverage checks reroll grading, fresh answer UI, and per-variant completion across
    two variants.
- **Phase 3a:** the spike report has the scientific-class inventory and overlap, representative
  cross-browser/library/scale calibration, gallery review, full heavy-bank rendering and
  packaging with a selected passing configuration, timings, package check results, independent
  scientific assessment, automated source-grading/identity/media/display checks, the failure
  triage table, and the decision: D, D with a named exception set, or C. State the actual Ultra
  compatibility limitation explicitly; no human import is required for milestone acceptance.
- **Phase 3b:**
  - Native/portable/WASM same-input checks find zero unexplained behavioral regressions in
    identities, grading, media, or logical dimensions. Classify and retain baseline/reference
    differences; Python parity is an optional migration reference and its nonzero findings remain
    reported limitations.
  - Native and WASM share source-owner render planning/replacement behavior, preserving original
    question identities, grading, media references, scientific content, and authored image size.
  - Independent agent scientific assessment and automated package/source-grade/media/render checks
    accept browser-built table and canvas packages against the native/original-source reference.
  - Playwright exercises actual on-demand downloads, validates their packages and source grading,
    and checks direct conversion for formats that need no image rendering. Failures return to
    the responsible source owner for correction and fresh assessment.
  - Isolated generation and MkDocs verification show new UI links use on-demand conversion and
    future builds skip replaced prebuilt exports. After isolated acceptance, migrate the 57
    permanent topic indexes with `regenerate_selftests=False`: the publication workflow builds
    committed `site_docs` directly. Preserve existing selftest HTML and question CRCs. D15 in the
    execution ledger separates this permanent deployment migration from transient proof.
  - After automated replacement downloads pass, an independent agent accepts the recorded
    direct-URL impact and replacement routes. Remove only replaced generated Canvas ZIP,
    Blackboard ZIP and human-readable files, preserving BBQ sources, selftest HTML, authored
    assets and named exceptions. Verify the isolated site still builds and downloads correctly
    after removal. Record the actual storage delta without a fixed byte threshold.
  - The manager integrates source and documentation updates, runs the appropriate full suites and
    the native/portable/WASM regression checks, and obtains fresh specification, quality, scientific, and consumer assessments.
    Review temporary checks under PYTEST_STYLE, retain meaningful behavior coverage, and remove
    one-time scratch work after durable evidence is recorded. Record Ultra compatibility as
    unverified external evidence unless an actual result is available.

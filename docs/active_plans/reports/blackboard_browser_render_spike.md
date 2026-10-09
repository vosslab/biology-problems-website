# Blackboard browser rendering feasibility experiment

Date: 2026-10-09. Authority: [optimized spindle plan](../i-want-to-explore-optimized-spindle.md),
Phase 3a. Status: native/browser calibration, full-bank stress, package checks, and fresh visual,
specification, quality, and local integration reviews pass. The manager accepts Phase 3a and
selects D under D13; Phase 3b and final local integration are complete. Actual Blackboard Ultra compatibility
remains unverified external evidence.

## Current decision

The manager selects D using independent scientific assessment, source-grading/media/package
checks, and fresh local integration evidence. D13 replaces the earlier human import gate with
local automated acceptance. Actual Ultra import, display size, and grading remain unverified.
The selected D11 configuration is uniform modern-screenshot at scale 1 with full-color PNGs. Palette variants
remain experiment comparisons because the guide's heading hues visibly change after quantization.

## Scope and preserved evidence

The temporary experiment is archived under
`/private/tmp/optimized_spindle_evidence_20261009/tests/_temp/blackboard_browser_render/`.
Repository-relative paths elsewhere in this historical report resolve beneath the archive root.
Its browser harness is archived at the same root beneath `tests/playwright/_temp/`.
All scripts, source snapshots, installed dependencies, render evidence, and packages are
temporary experiment receipts.
The archive preserves the receipts separately from generated-download cleanup.
`archive_receipt.json` and `ARCHIVE_RECEIPT.md` at the archive root record 6,639 files,
6,297 PNGs, and 35 ZIPs across the preserved Phase 3 experiments. Historical absolute paths
in JSON remain original; the receipt maps their repository roots to archived paths.
Paths below identify local evidence; ignored temporary files are not durable repository links.
The temporary browser harness lives at `tests/playwright/_temp/blackboard_browser_render.mjs`,
following the repository's browser-import placement rule while sharing the experiment evidence.

The full inventory contains 384 real published questions and 1,960 unique render jobs. Ten
scientific classes occur across nine distinct banks: `which_macromolecule-MC` supplies both the
large identification guide and the sole published table+canvas bank. Those classes share one
workload. There is no fabricated tenth bank.

| Bank case | Questions | Unique jobs | Coverage |
| --- | ---: | ---: | --- |
| `gel` | 50 | 50 | DNA fingerprint gel with box-shadow bands |
| `punnett` | 14 | 6 | Punnett squares |
| `chi_square` | 50 | 51 | Chi-square data tables |
| `gene_tree` | 50 | 550 | LEVEL_4 gene tree diagrams |
| `tetrad` | 50 | 950 | Unordered two-gene tetrad distance choices |
| `macromolecule` | 50 | 51 | Large guide plus nested table+RDKit canvas |
| `projection` | 50 | 94 | Fischer-to-Haworth pyranose projections |
| `agglutination` | 50 | 188 | Blood-group agglutination wells |
| `rdkit` | 20 | 20 | Amino-acid canvas-only drawings |

The plan's approximately 800 tetrad PNGs are an earlier estimate. Current source measurement is
950 unique outer-table jobs for the selected distance-choice bank. Exact paths, SHA256 receipts,
source question positions, and full job inventory are in `jobs.json`.

Final cross-browser calibration uses 29 representative jobs, each covered by modern-screenshot and
snapdom in Chromium, Firefox, and WebKit at scales 2 and 1 (348 effective comparison rows). Selection covers the
first three distinct fragments, largest source markup for each render kind, and ordinary versus
nested canvas tables. Exact selected IDs and their reasons are in `calibration_jobs.json`.
The provisionally chosen configuration renders full gene-tree, tetrad, macromolecule, and RDKit
banks. The complete 1,960-job by 12-setting matrix is unnecessary for this temporary experiment.

## Tooling and prerequisite receipt

- Temporary Node dependencies: Playwright, modern-screenshot, `@zumer/snapdom`, and `@rdkit/rdkit`.
- Python uses `source source_me.sh && python3`; lxml, Pillow, and imagehash are available.
- Native references must be PNG media recovered from actual current release CLI exports of the
  same real-source calibration questions. A freshly captured Playwright CDP screenshot alone is
  useful diagnostic evidence but does not constitute an actual native-export reference.
- The optional native RDKit shim was initially missing. The installed Homebrew RDKit SDK,
  Boost, and Cairo suffice for the existing upstream build script; no Rust patch was needed.

The successful prerequisite command (exit 0) was:

```bash
RDKIT_PREFIX=/opt/homebrew/opt/rdkit BOOST_PREFIX=/opt/homebrew/opt/boost \
CAIRO_PREFIX=/opt/homebrew/opt/cairo \
OUTPUT_DIR=/Users/vosslab/nsh/PROBLEMS/biology-problems-website/tests/_temp/blackboard_browser_render/native_shim \
bash ../qti-package-maker-rs/crates/qti-molecule/native/build_shim.sh
```

Result: `native_shim/libqti_rdkit_shim.dylib`. The Phase 1 build agent has the path. Native experiment
exports set the supported `QTI_RDKIT_SHIM` variable to this explicit path.

`prepare.py` extracts the literal current native wrapper from `chromium.rs`, substitutes the
current Atkinson font bytes, preserves its CSP and 16 px body margin, and selects outermost tables
with lxml. Script elements are removed after static canvas specifications are recovered.

## Source observations and failure triage

| Observation | Scope | Classification and action | Result |
| --- | --- | --- | --- |
| Optional native RDKit shim absent | Native environment prerequisite | Build existing upstream shim with installed SDKs | Build exit 0 |
| Packaging helper module path failed after an incorrect directory-depth edit | Temporary harness | Restore the original four-parent sibling path, verified by actual Node execution | All ten packages convert successfully |
| Existing helper checked only WASM integrity | Evidence gap | Add actual `qti-package-maker check` command and preserve exit/output | Complete: all ten browser-built ZIPs pass `checkPackage` and the actual release CLI check; see package results and inspection below |
| Existing reference was Playwright CDP capture | Evidence gap | Recover actual native-export media by original PNG names in Blackboard LOM metadata | Complete: nine native CLI exports succeeded, nine CLI checks exited 0, and all selected reference PNGs were recovered; see `native_results.json` and calibration results below |
| Raw stereochemical backslashes in macromolecule authored SMILES literals | Scientific source representation | Match native static SMILES capture rather than evaluating author JavaScript | Complete: corpus extraction succeeds and the independent visual review passes the reviewed macromolecule content; see [fresh visual review](blackboard_browser_render_visual_review.md) |
| Initial protein migration case was a numerical table, without gel bands | Corpus selection | Replace it with the real `who_father_html-MEDIUM-5_males` bank; retain old evidence as misclassified | Corrected bank has 50 outer tables and 2,784 box-shadow declarations; native and both-library gel captures complete |
| macOS sandbox prevents Chromium MachPort launch | Execution prerequisite | Use the approved unrestricted browser/native execution lane | Native exports succeed; no renderer fidelity failure |
| Installed RDKit.js does not consume the supplied `wasmBinary` option | Temporary harness API | Use supported `instantiateWasm` to instantiate local WASM bytes | All engines initialize successfully |
| Native generated names use recomputed CRC, rather than embedded source marker | Reference mapping | Read actual export item titles in source-question order and original LOM media filenames | All selected reference PNGs recovered |
| Both libraries omit gene-tree caption when freezing computed table height | Capture geometry | Measured capture container alone did not resolve it; modern-screenshot's documented clone hook resets table height to `auto` | Native caption and branch geometry restored in Chromium and Firefox |
| Firefox snapdom wraps `86 + 516` and clips the fraction denominator | One library/browser | Try documented `reconcile` option; select passing modern-screenshot | Reconciliation failed; modern retains numerator and denominator |
| HTML serialization emits non-self-closing `img`; structural checks accept empty packages after all questions are skipped | Temporary rewrite/package evidence | Serialize XML-compatible void elements and require the exact source question count | All final packages retain expected counts; preserved failure receipt `package_void_element_failures.json` |
| lxml serialization decodes authored entities into Unicode rejected by BBQ's ASCII identity computation | Temporary rewrite | Use ASCII XML character references, preserving authored meanings | Tetrad source retains all 50 questions |
| Generic image alt causes distinct rewritten macromolecule items 24 and 43 to share `29bc_8112`; reparse silently deduplicates them | Prototype packaging/identity boundary | Replace generic alt with native-style ASCII table-cell content/SMILES as legitimate accessible presentation; preserve collision reproducer | Source-faithful output has 50 unique identities and retains all 50 questions; planned `finishConvert` must retain original ItemBank identity instead of reparse |
| 64-color guide changes purple phosphate heading toward brown/mauve | Image optimization appearance | Choose uniform full-color scale 1; retain palette only for comparison | Fresh appearance-sensitive full-color review passes |

Perceptual distances are descriptive measurements. No arbitrary pixel, hash-distance, byte-count,
or timing cutoff decides scientific readability. A fidelity failure is classified by library,
browser, image type, or packaging/import scope before considering source fixes or exceptions.

## Calibration results and review evidence

The local gallery, `tests/_temp/blackboard_browser_render/gallery.html`, presents actual
native export images beside browser images and their 64-color alternatives. Data are in
`measurements.json`, `measurements.csv`, and `summary.json`. The native receipt `native_results.json`
records nine successful current CLI exports, nine actual `qti-package-maker check` exit-0 results,
and zero missing selected reference PNGs.

Every calibration capture returned PNG bytes; successful capture alone does not prove fidelity.
Original failures are preserved in `initial_renders/` and `calibration_initial_results.json`.
The first 360-capture matrix included a misclassified numerical gel case. Corrected coverage uses
29 real scientific jobs. After a measured-container trial, a focused two-job, 24-capture probe
tested the caption/fraction corrections. A selected-library acceptance sweep captures all 29 jobs
with modern-screenshot at both scales in all three engines, plus both libraries for the corrected
three gel jobs: 192 captures. Snapdom is not repeatedly tested for unrelated unchanged cases.

Modern-screenshot is the provisional choice. Its only additional renderer glue is the measured
container and a documented `onCloneNode` callback setting cloned table height to `auto`; there is
no generic CSS repair framework. Standalone canvases use RDKit.js and `toBlob` directly.

| Modern-screenshot calibration | Jobs | Capture milliseconds | Raw PNG bytes | 64-color bytes | Median perceptual distance |
| --- | ---: | ---: | ---: | ---: | ---: |
| Chromium, scale 2 | 29 | 1,315 | 1,941,679 | 456,420 | 0 |
| Chromium, scale 1 | 29 | 969 | 751,805 | 173,969 | 0 |
| Firefox, scale 2 | 29 | 1,636 | 1,522,717 | 438,304 | 2 |
| Firefox, scale 1 | 29 | 1,369 | 595,786 | 166,467 | 2 |
| WebKit, scale 2 | 29 | 1,528 | 1,661,429 | 437,315 | 2 |
| WebKit, scale 1 | 29 | 1,152 | 724,796 | 193,165 | 0 |

Chromium scale 1 plus 64 colors reduces the selected PNG total by about 91% relative to Chromium
scale 2 full-color capture. This is this corpus's measured result, not a universal guarantee.
Timing totals measure individual capture calls, excluding browser startup and RDKit initialization.
`calibration_bank_times.json` additionally records per-job harness wall time, including setup and
diagnostic screenshots; do not interpret it as production UX latency.

The [fresh visual review](blackboard_browser_render_visual_review.md) directly inspected 29 native
references and 58 selected quantized browser images, then six native references and twelve
full-color browser images for the D11 appearance-sensitive follow-up. It passes the reviewed
scientific content, labels, geometry, and full-color appearance in Chromium and Firefox. It does
not claim direct review of every full-bank image or WebKit acceptance. A numerical perceptual
distance never substitutes for that scientific review.

## Full-bank stress and actual packaging

The chosen Chromium/modern-screenshot/scale-1 run completes all 1,571 unique jobs with zero capture
errors. Each bank is its complete captured source pool. The small gel import fixture additionally
uses the three real calibration questions; no synthetic question is added.

| Bank | Jobs | Capture-call seconds | Harness seconds | Full-color ZIP bytes | Palette ZIP bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Gene tree | 550 | 27.534 | 36.448 | 10,626,478 | 2,724,435 |
| Tetrad | 950 | 24.448 | 113.471 | 3,831,298 | 1,683,880 |
| Macromolecule | 51 | 2.030 | 8.542 | 2,695,957 | 679,615 |
| RDKit | 20 | 1.295 | 3.287 | 338,702 | 91,860 |
| Gel import subset | 3 | Calibration above | Calibration above | 150,362 | 27,683 |

Harness seconds include document setup, canvas drawing, CDP diagnostic screenshots, and file
output. They are experiment wall times, not claimed production latency. Capture-call totals
isolate the selected library/direct canvas capture. `stress_results.json`, `stress_bank_times.json`,
and `stress_summary.json` preserve exact measurements.

All ten final actual WASM Blackboard packages pass `checkPackage` and the actual current release
`qti-package-maker check` command, with zero conversion warnings. Their item counts are exactly
3 gel, 50 gene-tree, 50 tetrad, 50 macromolecule, and 20 RDKit questions in both variants. PNG counts
are 3, 550, 950, 51, and 20 respectively. Macromolecule uses 100 image references because its common
guide PNG is shared; no missing question is hidden by image deduplication.

`package_inspection.json` verifies source grading for all ten packages by comparing each item's
response-processing XML with conversion of the corresponding original source through the same
WASM and seed. The comparison normalizes presentation CRCs in condition titles/response labels,
retaining option ordinals, score values, conditions, and ordering. Source question count is checked
before acceptance. An empty ZIP passing structural checks is insufficient.

The identity repro is preserved in `inputs/bbq-macromolecule-generic-alt-repro-questions.txt` and
`identity_collision.json`: 50 individual valid reads, 49 distinct identities, collision at source
items 24 and 43. Source-faithful table-cell/SMILES alt produces 50 distinct identities. This is a
prototype presentation-reparse boundary finding, not a scientific visual failure or fundamental
reason for C. Original ItemBank identity remains the source-owner contract of planned `finishConvert`.

Successful experiment commands were:

```bash
source source_me.sh && python3 tests/_temp/blackboard_browser_render/prepare.py
source source_me.sh && python3 tests/_temp/blackboard_browser_render/native.py
node tests/playwright/_temp/blackboard_browser_render.mjs acceptance
node tests/playwright/_temp/blackboard_browser_render.mjs stress chromium modern 1
source source_me.sh && python3 tests/_temp/blackboard_browser_render/analyze.py
node tests/_temp/blackboard_browser_render/package.mjs
source source_me.sh && python3 tests/_temp/blackboard_browser_render/inspect_packages.py
node tests/_temp/blackboard_browser_render/inspect_identity.mjs
source source_me.sh && python3 tests/_temp/blackboard_browser_render/prepare_imports.py
```

Browser/native rendering uses the approved unrestricted execution lane because of the macOS
sandbox launch restriction. Native preparation is a reduced real-source reference run, not a
full-bank rendering benchmark. A gel-only native rerun updated the corrected gel references.
Syntax checks pass; the focused browser-import placement suite passes 5 tests. These are temporary
verification receipts, not a new permanent exhaustive test suite.

## Optional Ultra import fixtures

The import candidates use full color uniformly. They are preserved in
`tests/_temp/blackboard_browser_render/ultra_import/`, with exact hashes and sizes in `manifest.json`.

| Fixture | Questions | Images | ZIP |
| --- | ---: | ---: | --- |
| Gel box-shadow bands | 3 | 3 | `01_gel_bands_3_questions_fullcolor.zip` |
| Full tetrad bank | 50 | 950 | `02_tetrad_50_questions_fullcolor.zip` |
| Full nested macromolecule bank | 50 | 51 | `03_macromolecule_50_questions_fullcolor.zip` |

For optional external evidence, import these into a Blackboard Ultra sandbox and record:

1. Exact imported question counts of 3, 50, and 50, and absence of import errors.
2. Gel lane labels and bands, tetrad grids/fractions, guide headings, molecule bonds/atom labels,
   and adjacent information tables display completely at usable sizes. Confirm small molecule
   labels can be enlarged as needed; display size is specifically open because replacement images
   lack explicit width/height attributes.
3. With answer shuffling off, use `ultra_import/import_answer_key.json` for the first two questions
   of each fixture. A recorded correct option earns credit and another option does not. Confirm
   grading in Ultra rather than relying solely on the preserved source scoring XML.

Actual Ultra result: **unverified**. No successful import is inferred from local acceptance.
These fixtures support an optional external check and do not block Phase 3b.

## Acceptance and next phase

Phase 3a is accepted locally and D is selected without named retained-artifact exceptions.
Phase 3b verifies canonical source identity/grading, browser downloads, isolated build/UI
behavior, independent URL impact, permanent topic migration, and narrow generated-file cleanup.
The final receipts are [optimized_spindle_phase3_acceptance.md](optimized_spindle_phase3_acceptance.md)
and [optimized_spindle_phase3_migration.md](optimized_spindle_phase3_migration.md).
Source and local static-site acceptance are complete; remote publication is unperformed. Actual Ultra compatibility remains unverified.

The Phase 1 benchmark released the shared machine before rendering began. The separate Phase 1/2
integration browser journey had an exclusive window between calibration correction and final
acceptance/stress. No heavy benchmark workload overlapped these timing measurements.

# Phase 1 native build validation

Source plan: [i-want-to-explore-optimized-spindle.md](../i-want-to-explore-optimized-spindle.md).

## Scope and interpretation

The full default build, focused/full pytest, sample package integrity, scientific content/grading,
and matched converter timing checks pass. Fresh independent reviews remain manager-owned.
Hashes identify inputs and artifacts; they are not byte-equivalence
acceptance gates. Scientific question content, grading, media completeness, and actual package
checks determine acceptance. Output serialization and self-test selection may differ.

The historical 1182.852-second build included 1069.268 seconds of BBQ generation and 108.537
seconds of downloads. A current cached build cannot establish converter speed against that
different workload. A separate unchanged-source, native/Python export measurement will report
converter timing without forcing question regeneration.

## Read-only preparation

`source source_me.sh && python3 build_site.py -n --cli` exits 0 in about one second. It plans
116 BBQ files, 116 self-test files, 397 downloadable files, 29 topic pages, and 15 indexes.
The explicit task-aware orphan dry run proposes zero source deletions, download deletions,
include removals, cache drops, quarantines, unmanaged files, or deferred actions. Existing
prebuilt artifacts remain within the authorized build scope.

Local receipts are under the ignored `output_rust_qpm_validation/` directory:
`full_dry_run.log` and `prune_dry_run.json`.

## Focused and full pytest

`source source_me.sh && python3 -m pytest tests/test_native_exports.py
tests/test_build_site_workflow.py tests/test_topic_page_generate_downloads.py -q` initially
reports 27 passed and 1 failed in 0.37 seconds. The failing Blackboard pool-export test's fake
converter omitted the new optional `capture_output` argument; the independent fixer corrected
that test double. The fresh focused rerun passes all 28 tests in 0.32 seconds.

`source source_me.sh && python3 -m pytest tests/ -q` initially reports 6066 passed and three
failures in 5.58 seconds: an existing five-line guidance bullet, the new vendor script's
non-executable shebang, and the temporary Playwright harness outside `tests/playwright/`.
The responsible owners correct those findings without deleting or skipping tests. The browser
harness now lives in `tests/playwright/_temp/blackboard_browser_render.mjs`; its corpus and
results remain in the spike scratch directory. The fresh full rerun passes all 6069 tests
in 4.88 seconds (external wall time 5.41 seconds). After the vendor helper's final source
correction, the final full run passes all 6075 collected tests in 5.49 seconds (external
wall time 6.11 seconds). Local logs: `focused_pytest.log`,
`focused_pytest_rerun.log`, `full_pytest.log`, `full_pytest_rerun.log`, and
`full_pytest_final.log`.

## Build runtime prerequisite

The upstream RDKit shim build succeeds using the existing upstream `build_shim.sh` and
Homebrew RDKit, Boost, and Cairo. Canvas rendering uses the source-owner documented
`QTI_RDKIT_SHIM` setting, pointing to
`tests/_temp/blackboard_browser_render/native_shim/libqti_rdkit_shim.dylib`.

The initial default full build runs in the filesystem sandbox. Chromium table rendering fails
at macOS `bootstrap_check_in` with `Permission denied (1100)`. Optional Blackboard exports
are skipped while atomic staging preserves their existing ZIPs. This run does not establish
successful renderer acceptance even if the enclosing build returns zero. An unrestricted
default full-build retry completes successfully and renders all 13 previously failed exports.

## Full default build

Both executions use `source source_me.sh && python3 build_site.py`, with the documented
upstream `QTI_RDKIT_SHIM` runtime prerequisite supplied. The second execution has unrestricted
browser launch permission. Both return 0; only the second resolves the renderer failure.

| Lane | Build timing seconds | External wall seconds | Actual conversion result |
| --- | ---: | ---: | --- |
| Initial sandbox | 157.947 | 158.30 | 117 self-tests, 118 Canvas ZIPs, 118 human-readable HTMLs, 105 Blackboard ZIPs completed; 13 Blackboard failures; 25 unsupported human-readable skips |
| Unrestricted retry | 94.099 | 94.45 | 13 Blackboard ZIPs completed; zero artifact failures; 25 unsupported human-readable skips |

The unsupported skips are zero-output success for the existing format policy, not swallowed
renderer errors. The whole bank log names each result. Prior valid artifacts survive failed
converter execution; the successful retry replaces the failed banks' ZIPs.

| Stage | Initial executed/skipped rows | Initial seconds | Retry executed/skipped rows | Retry seconds |
| --- | --- | ---: | --- | ---: |
| BBQ | 99 / 329 | 79.958 | 0 / 428 | 0.228 |
| Self-tests | 99 / 329 | 10.963 | 0 / 428 | 0.019 |
| Downloads | 117 / 311 | 49.131 | 30 / 398 | 79.300 |
| Topic pages | 29 / 28 | 4.195 | 5 / 52 | 0.657 |
| Indexes | 1 / 0 | 13.698 | 1 / 0 | 13.894 |

Declared stage file counts differ from actual converter calls because existing files can be
retained, formats can be unsupported, and task rows can share a bank. The initial run declares
116 BBQ files, 116 self-test files, 397 downloads, 29 topic pages, and 15 index files; the retry
declares 85 downloads, 5 topic pages, and 15 index files. The actual conversion counts above
come from `artifact_completed`, `artifact_failed`, and `artifact_skipped` events. Duplicate task
ownership explains the 117 self-test conversions for 116 distinct declared files.

Build run IDs are `def04382a62a47229a7ac70e6180b45f` and
`364c1096ca464dcea1f8db931ce2f159`. Local receipts: `full_build.log`,
`full_build_unrestricted.log`, and `build_stage_receipts.json`.

The homepage warning still names the already documented ambiguous macromolecule bank with
two task owners. It does not report a conversion failure. Neither current full-build timing
is a controlled comparison with the historical generation workload.

## Artifact and grading checks

The post-build inventory retains all 1906 downloadable files and all 62485 ZIP members.
There are zero added/missing downloadable paths and zero added/missing ZIP member paths.
After stale question generation, 118 source-bank hashes differ from the immutable baseline.
There are 833 changed file hashes and 4589 changed member hashes. These receipts
identify changed inputs, randomized content, serialization, and rendered output; they do not
impose byte equality. Local evidence: `post_native/comparison.json`, the two post-build
inventories, and `output_comparison.log`.

The measured unchanged-source sample contains 370 questions across eight banks:
functional groups (MC), bond types (MATCH), alpha-helix hydrogen bonds (MA), Hardy-Weinberg
frequency (NUM), RNA transcription (FIB), DNA gels (MC), amino-acid structures (MC/canvas),
and macromolecule classification (MC/table plus canvas).

All 96 generated ZIPs have clean ZIP CRCs, parseable XML, matching question counts, and
`qti-package-maker check` output `OK` with exit 0. The native and Python rendered Blackboard
sample each contains 220 PNGs per round; the relevant banks have 50, 50, 20, and 100 PNGs.
The first-round native and Python Blackboard pools are also inspected against their unchanged
source banks: all 370 question bodies outside replaced drawing elements, choices, MC/MA correct
choice indexes, MATCH prompt/answer associations, numeric answers/tolerances, and FIB answers
are preserved. MATCH display order is not treated as grading. Numeric pool-reader subtraction
noise (for example `0.00990000000000002` for `0.0099`) is normalized for inspection.

The Python package reader's CRC-keyed bank aggregation initially reports only 49 MATCH items
despite 50 actual XML items. Inspecting each raw item before that aggregation confirms all
50 source associations survive in both exports. This is an inspection-tool deduplication issue,
not a missing question or a website regression. No CRC equality gate is introduced.

Three native/Python PNG pairs are visually inspected: Hardy-Weinberg table counts, the
amino-acid molecular diagram including stereochemistry, and the macromolecule drawing/information
table. Scientific labels and diagram content match. The Hardy-Weinberg SUM row has the same
tight/overlapping label layout in both outputs; it is a shared source-format limitation rather
than a new native-rendering regression. This narrow sample does not replace the Phase 3 gallery
or Blackboard Ultra import acceptance.

Actual site packages also pass the exact native integrity command, each with stdout `OK` and
exit 0:

```bash
../qti-package-maker-rs/target/release/qti-package-maker check site_docs/biostatistics/topic08/downloads/blackboard_export_zip-chi_square_hypotheses-pair.zip
../qti-package-maker-rs/target/release/qti-package-maker check site_docs/genetics/topic04/downloads/blackboard_export_zip-punnett_choice.zip
../qti-package-maker-rs/target/release/qti-package-maker check site_docs/molecular_biology/topic08/downloads/canvas_qti_v1_2-TFMS-intron_splicing.zip
```

## Controlled export performance

Eight unchanged published source banks, 370 questions, four website formats, three rounds,
alternating implementation order: 192 actual subprocess attempts. Every process returns 0.
Six paired human-readable attempts produce no output in either implementation because the
amino-acid and macromolecule canvas banks have no supported text questions. Those pairs are
explicitly excluded from useful-export timing; 90 successful matched pairs remain. No ORDER
bank is included because the site's existing ZIP blacklist excludes it.

The inputs are hashed before measurement and checked afterward; all remain unchanged.
Each command uses a fresh output directory and a fresh process. Only Blackboard inputs with
tables/canvases enable `--html-to-image`, matching the website caller. OS caches are warm;
application render caches are process-local. Rendering is serialized with the Phase 3 spike
and other browser work. The source owner's current release binary and documented RDKit shim
are used; no source changes, version gate, question regeneration, or production benchmark flag
is added.

| Successful matched workload | Native median seconds | Python median seconds | Native/Python |
| --- | ---: | ---: | ---: |
| All four formats | 12.115 | 21.810 | 0.555 |
| Blackboard with HTML-to-image | 8.894 | 14.616 | 0.608 |
| Without HTML-to-image | 3.180 | 7.127 | 0.446 |

Per-round matched totals are native 12.565, 12.115, 12.065 seconds and Python 22.933, 21.810,
21.647 seconds. Native uses about 44% less elapsed time on this sample. This supports converter
improvement on this host and workload; it does not claim a 44% complete-build improvement or
represent the full website's format distribution. Fresh process startup and renderer startup
are included in timed conversion commands; package checks occur after the timed subprocess.

Local reproduction:

```bash
source source_me.sh
export QTI_RDKIT_SHIM=/Users/vosslab/nsh/PROBLEMS/biology-problems-website/tests/_temp/blackboard_browser_render/native_shim/libqti_rdkit_shim.dylib
python3 output_rust_qpm_validation/benchmark_exports.py
python3 output_rust_qpm_validation/check_semantics.py
```

Local evidence: `benchmark/metadata.json` (input and binary hashes), `benchmark/results.jsonl`
(every command, duration, exit, count, PNG count, and package-check output),
`benchmark/summary.json`, `benchmark/split_timings.json`, `benchmark/semantics.json`,
`benchmark/sample_images/`, per-command logs/outputs, and `benchmark_run.log`.

## Outstanding evidence

- Fresh specification, quality, and integration reviews assigned by the manager.

Phase 1 acceptance does not claim native speedup from the 1183-second historical whole-build
number. The controlled useful-export improvement supplies the meaningful performance evidence.
Phase 3 scientific gallery, browser packaging, and human Blackboard Ultra import gates remain
distinct work.

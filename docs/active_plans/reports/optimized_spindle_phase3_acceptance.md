# Phase 3b real scientific acceptance

Date: 2026-10-09. Authority: [optimized spindle plan](../i-want-to-explore-optimized-spindle.md),
Phase 3b and revised D13. Automated real-bank acceptance and the independent scientific visual assessment pass. The
[visual review](optimized_spindle_phase3_visual_review.md) directly covers the 14 named
final/native PNG pairs. Actual Blackboard Ultra import,
display size, and grading remain unverified external evidence.

## Actual website downloads

The frozen final site was served from
`/private/tmp/optimized_spindle_phase3_20261009/biology-problems-website/site` on port 8849.
Playwright Chromium clicked the actual topic-page Blackboard Ultra ZIP buttons, followed their
actual same-origin BBQ requests, and saved the resulting browser download events. No topic HTML,
BBQ source, controller, converter, drawing library, or download response was replaced.

All three BBQ source SHA256 values match the approved Phase 3a inventory exactly. The topic
routes and banks were:

- `genetics/topic03/`: `bbq-who_father_html-MEDIUM-5_males-questions.txt`.
- `genetics/topic08/`: `bbq-tetrad_unordered_two_gene-find_distance-MC-6_choices-questions.txt`.
- `biochemistry/topic01/`: `bbq-which_macromolecule-MC-questions.txt`.

These are full 50-question published banks. The actual download results are:

| Bank | Questions | Render jobs | PNG files | Image references | Download seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Gel bands | 50 | 50 | 50 | 50 | 9.50 |
| Tetrad distance choices | 50 | 950 | 950 | 950 | 12.15 |
| Macromolecule guide and nested molecule | 50 | 150 | 51 | 100 | 2.94 |

The macromolecule plan exposes 50 canvas jobs and 100 table jobs. Reused guide/table content is
rendered and packaged once where appropriate; the downloaded presentation has two image
references per question, with the shared guide plus each nested molecule table. The earlier
Phase 3a table-only estimate of 1,051 combined jobs is not this final API's job inventory; the
actual final API exposes 1,150 jobs across the three banks.

Times measure click through browser download save in this sequential local Chromium run,
including first-use dependencies for the gel bank. They are observations of these journeys,
not a renderer benchmark or general performance guarantee.

## Identity, grading and media

All three downloaded packages pass the shipped WASM `checkPackage` with no errors and the actual
release `qti-package-maker check` command with exit 0 and `OK`. For each bank, the same browser
WASM also directly exports its original, unrewritten BBQ source to a separate reference ZIP.
Independent Python ZIP/XML inspection checks actual downloaded and direct-original bytes:

- Exactly 50 items survive in original order for every bank, with original item `ident`, title
  CRC, and `bbmd_asi_object_id` unchanged.
- Every item's response-processing XML is exactly unchanged, including score rules and original
  response identifiers. Choice identifiers and their order also remain exact. An independent evaluator also selects every option and compares the
  resulting scores in choice order: each MC question has one full-credit answer and zero-credit
  distractors in both packages.
- Every presentation image reference resolves to exactly one packaged PNG. All 1,051 packaged
  PNGs decode successfully and contain visible ink; this is a decoding sanity check, not a
  scientific visual verdict.
- Every image's HTML logical width and height match its scale-1 PNG dimensions after the capture
  canvas truncates fractional CSS pixels to integer pixels. No table or canvas remains in the
  downloaded presentation fields.

The UI showed loading, image drawing, building, and `Download ready.`; row controls were disabled
while drawing and enabled on completion, and progress was hidden on completion. No page errors
were observed. Actual source and drawing dependency requests, progress snapshots, package hashes,
original item identities and per-choice scores are retained in the temporary receipts.

## Scientific visual evidence

The independent visual reviewer receives 14 named final-PNG/native-PNG pairs with exact source
item/BBQ field provenance and intended CSS dimensions. Native references come from actual
release CLI exports, not CDP captures. The original nine reference images reuse the accepted
Phase 3a native exports; five added references come from two fresh native exports, both of which
also pass the actual CLI package checker. Added native item identities and choice scores match
their corresponding original source positions.

The gallery covers:

- Gel questions 1, 2, 3, 25, and 50: box-shadow bands, lane labels, and bank variation.
- Tetrad question 1: genotype/count grid and the first choice's two fraction tables.
- Macromolecule question 1: large guide and nested arachidic-acid molecule table.
- Macromolecule question 2: nested Lys-Leu peptide with molecular labels and stereobonds.
- Macromolecule questions 4, 18, and 47: guanosine-3'-monophosphate, cholesterol, and ribose,
  covering ring structures, phosphate labels, and additional stereochemical drawings.

An initial temporary extraction matched the deduplicated job ordinal to the second item's
reused guide, rather than its Lys-Leu table. The independent reviewer caught this mapping error.
The extractor now matches exact original source fragments to their outer-table positions before
pairing references; corrected outputs were delivered before the scientific verdict. This did
not indicate a rendering or package-content failure.

The fresh [visual review](optimized_spindle_phase3_visual_review.md) passes all 14 directly
inspected pairs. Gel bands/labels, tetrad grids/fractions, full-color guide headings, molecular
connectivity, captions, labels, and stereochemical cues remain usable in the reviewed images.
Cholesterol has tighter H/CH3 ring-junction label spacing than the native backend; direct enlarged
inspection resolves separate glyphs and endpoints without ambiguity. The original source supplies
no fixed atom coordinates or label-placement metadata. No source-owner correction is required.
This scoped scientific assessment does not claim direct visual review of all 1,051 packaged PNGs
or actual Ultra display. Captures, nonblank checks, package integrity, and numerical measurements
remain separate from the visual verdict.

## Reproduction and receipts

Archived browser script:
`/private/tmp/optimized_spindle_evidence_20261009/tests/playwright/_temp/optimized_spindle_phase3_acceptance.mjs`.
Archived output root:
`/private/tmp/optimized_spindle_evidence_20261009/tests/_temp/optimized_spindle_phase3_acceptance/`.
The gallery is directly reviewable at that output root as `gallery.html`. Archive scope and counts
are retained in `/private/tmp/optimized_spindle_evidence_20261009/archive_receipt.json`
and `ARCHIVE_RECEIPT.md`. These local paths contain one-time evidence, not permanent tests.

The commands below record the original acceptance run before archival. The experiment directories
and both temporary browser harnesses have been removed from the source tree by a reversible
filesystem move preserving repository-relative paths. For paths in historical commands and
unchanged JSON receipts, replace the original repository root
`/Users/vosslab/nsh/PROBLEMS/biology-problems-website` with the archive root above.
The archive preserves inputs, PNGs, ZIPs, native references, scripts, and experiment dependencies;
its relative gallery links still resolve. The old native RDKit shim is retained as historical
experiment evidence; ordinary builds and selftests use canonical helper/vendor locations.

```bash
source source_me.sh && python3 -m http.server 8849 --directory \
  /private/tmp/optimized_spindle_phase3_20261009/biology-problems-website/site
node tests/playwright/_temp/optimized_spindle_phase3_acceptance.mjs
source source_me.sh && python3 \
  tests/_temp/optimized_spindle_phase3_acceptance/inspect_downloads.py
```

Chromium initially hit the known macOS MachPort sandbox launch restriction. The same browser
command succeeded in the authorized unrestricted execution lane. The local HTTP server was
closed after acceptance; no publication or remote deployment occurred.

Preserved outputs under the archived output root:

- `browser_receipts.json`: actual routes, source requests, UI progress, WASM/CLI results, and jobs.
- `independent_inspection.json`: source identity/order, exact response-processing comparison,
  independent scores, PNG reference resolution, dimensions, and downloaded ZIP hashes.
- `extra_native_receipts.json`: added reference-export commands, source positions, hashes, and CLI checks.
- `asset_receipts.json`: SHA256 and sizes of the frozen controller, WASM, and renderer dependencies.
- `representative_images.json` and `gallery.html`: named source/native/final-PNG mappings.
- `gel-actual-download.zip`, `tetrad-actual-download.zip`, and
  `macromolecule-actual-download.zip`: actual browser downloads.
- `gel-original-direct.zip`, `tetrad-original-direct.zip`, and
  `macromolecule-original-direct.zip`: unrewritten source grading/identity references.
- `gel-extra-native.zip` and `macromolecule-extra-native.zip`: fresh extra reference exports.
- `gel/`, `tetrad/`, and `macromolecule/`: extracted actual/native representative PNGs.

The browser/API journey and scientific corpus matrix are one-time acceptance evidence. Permanent
coverage remains owned by the two compact behavior tests in
[package_download.spec.ts](../../../tests/playwright/package_download.spec.ts), with their focused
and full-suite validation reported separately.

## Integration evidence boundaries

Canonical source and package behavior remain owned by QPM, as documented in
[DESIGN_DECISIONS.md](../../DESIGN_DECISIONS.md). Complete build/vendor refresh commands are in
[INSTALL.md](../../INSTALL.md). The following owner-reported receipts complement this report's
independently executed real-bank browser/XML/PNG checks; they are distinct validation lanes.

The durable native versus portable same-input contract is
`qti-package-maker-rs/crates/qti-native/src/html_to_image/convert/tests.rs`:
`native_adapter_matches_portable_identity_grading_media_and_css_sizing`. A common deterministic
PNG renderer drives native `convert_bank` and portable `plan_bank` plus `finish_bank`; it compares
original CRCs, order, item numbers, rewritten bodies/grading, asset maps, and CSS sizes. Portable
contracts in `crates/qti-render/src/render_plan_tests.rs` protect distinct original items whose
rendered presentations match, nested canvas dependencies, visible-image materialization, and
missing/duplicate/unknown/invalid completion diagnostics. WASM transport tests in
`crates/qti-wasm/tests/render_contract.rs` exercise actual exported API completion behavior.

Fresh source review exposed signature-only PNG acceptance. The shared correction fully decodes
PNG rows and verifies CRC/Adler32/end chunks before substitution or packaging, and uses valid PNG
fixtures across native, portable, and WASM tests. The correction owner reported 31 portable/WASM
and 15 native conversion checks passing; a fresh independent re-review reported 20 portable,
3 WASM transport, and 15 native conversion checks passing. The final exported website WASM replay
rejects a signature-only PNG with a render diagnostic and produces a checker-clean package for a
complete PNG. Its receipt is
`/private/tmp/optimized_spindle_phase3_20261009/png_export_boundary.log`.

Final build and consumption receipts are
`/private/tmp/optimized_spindle_phase3_20261009/integration_handoff.md` and
`/private/tmp/optimized_spindle_phase3_20261009/artifact_receipt.json`. They identify corrected
native/WASM hashes, complete distribution consumption, canonical build/typecheck/release results,
12 final Node tests, 5 browser checks, and the 6,081-test website Python run before the final
artifact rebuild. Named logs include `qpm_npm_build_final.log`, `qpm_typecheck_final.log`,
`qpm_cargo_build_final.log`, `website_pytest_full.log`, and `png_export_boundary.log` in that root.
The failed pre-fixture-correction Node receipt remains explicitly classified in the handoff;
its final 12/12 result comes from the fresh fixture owner. These counts do not represent a fresh
full-suite rerun by this real-corpus acceptance agent.

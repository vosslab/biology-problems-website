# Phase 2 consumer acceptance

Source plan: [i-want-to-explore-optimized-spindle.md](../i-want-to-explore-optimized-spindle.md).
Decision D6 in [optimized_spindle_execution.md](optimized_spindle_execution.md) remains authoritative.
Phase 1 validation and Phase 3a preparation are active; their acceptance gates remain open.
This report does not claim whole-plan completion.

## Artifact identity

On 2026-10-09, build the native tools from the sibling Rust checkout with:

```bash
cargo build --locked --release -p qti-cli --bins
```

Result: exit 0, optimized release build in 41.25 seconds. No Rust sources changed in this workstream.
Native `bbq-converter` SHA256:
`03c04dde59037d6ba860674388ddb2f17f852c5a6598eaa8131fedf6466364f3`.

From `qti-package-maker-rs/packages/qti-wasm`, `npm run build` exits 0.
The complete distribution is copied to the website's `site_docs/assets/qti_wasm`.
Its `source.json` records `sourceCommit: null`, source path, provenance qualification, and
SHA256 for every consumed file. No current revision receipt was supplied; the previous
`sourceCommit` must not imply current-source certification. This identity limitation does not
prevent runtime checking of the recorded bytes.

WASM SHA256 before and after rebuilding:
`d2cee028cb5ace2ba11fe81eff2f7acf49d48db1122cc79b45ee5fd2c3181adc`.

The native initial WOMC selftest and WASM seed 0 both emit CRC `6304_a249`.
The one-time identity probe and JSON receipt remain under ignored `output_phase2_acceptance/`.

## Source-owner synthetic CRC finding

The agreed prefixed-choice probe from
[optimized_spindle_rust_selftest_handoff.md](optimized_spindle_rust_selftest_handoff.md) still fails:

```text
MC<TAB>12. <p>abcd_1234</p> Question?<TAB>A. one<TAB>Incorrect<TAB>B. two<TAB>Correct
```

Required established CRC: `3891_574a`. Fresh native and rebuilt WASM emit `3891_d9cb`.
Native reproduction from the website root:

```bash
../qti-package-maker-rs/target/release/bbq-converter --quiet --selftest \
  --input output_phase2_acceptance/bbq-prefix_probe-questions.txt \
  --output output_phase2_acceptance/native_prefix_probe.html
```

The Rust BBQ reader still strips choice prefixes before item construction at
`crates/qti-engines/src/bbq_text_upload/mod.rs:242-244`.
Generated controls do expose the statement ID and dispatch grading through the mutable public
hook. The synthetic CRC discrepancy is independent of those completed hook fixes. Fresh rebuilds
from the current local source still emit `3891_d9cb` in both native and WASM; the fresh receipt
is `output_phase2_acceptance/prefix_probe_refreshed.json`. The D8 bank inventory separately
found no affected prefixed choices in the actual website banks, so this remains an upstream
handoff finding rather than a website Phase 2 acceptance gate.
No website identifier translation, completion migration, or compensation is introduced.

## Generated-page correction and rollout

Both canonical scoped commands write their selected outputs but fail manifest finalization:

```bash
source source_me.sh && python3 build_site.py -H -S genetics -T topic01 --cli
source source_me.sh && python3 build_site.py -I -S genetics -T topic01 --cli
```

Error: `ValueError: No question_html_<crc> div in
genetics/topic01/downloads/selftest-MATCH-genetic_disorders.html`.
The actual native HTML has a valid `div` whose `class` precedes its `id`; the website's
`QUESTION_DIV_RE` requires the `id` first. The manager assigned a fresh website fixer for this
parser defect. The released correction accepts valid attribute order and passes fresh
specification and quality review. Both scoped commands then exit 0: three selftests,
one topic page, and refreshed manifest/index outputs. Generation receipts remain in
`output_phase2_acceptance/selftests.log` and `indexes.log`.
The manifest contains the actual native CRC and stable bank routing metadata.

The complete Phase 2 rollout then runs the canonical artifact-only commands:

```bash
source source_me.sh && python3 build_site.py -H --cli
source source_me.sh && python3 build_site.py -I --cli
```

Both exit 0. `-H` refreshes 482 selftest HTML files and the manifest in 13 seconds.
`-I` refreshes 57 topic pages and 15 metadata outputs in 22 seconds. Their logs are
`output_phase2_acceptance/selftests_all.log` and `indexes_all.log`.
The index-only path bypasses orphan reconciliation and preserves BBQ and converter download
artifacts. Its additional generated outputs are subject indexes, sitemap, navigation,
Question Finder, manifest, homepage statistics/fragment, and activity pages. No BBQ generation
or export workload runs. The normal homepage warning identifies one ambiguous bank,
`biochemistry/topic01/bbq-which_macromolecule-MC-questions.txt`; it does not fail the build.

`output_phase2_acceptance/all_topic_rollout.json` records 482 bank wrappers across 57 topic
pages and 482 manifest banks/rows. The wrapper and manifest bank sets match exactly;
all BBQ sources and selftest includes exist.

After the reported upstream audit, native and WASM are rebuilt from the current local source
without Git lookup or repository update. Native exits 0 in 0.29 seconds. WASM initially
encounters a sandbox permission error installing wasm-bindgen; the authorized unrestricted
`npm run build` exits 0. All 18 distribution files and the native binary retain their recorded
hashes, so these regenerated pages already consume the refreshed tools. The complete WASM
distribution is copied and provenance refreshed with `sourceCommit: null`. Hashes identify
consumed bytes; they are not compatibility gates. Build logs are `native_refresh.log`,
`wasm_refresh.log`, and `wasm_refresh_unrestricted.log` under the receipt directory.

## Runtime checks

```bash
source source_me.sh && npx playwright test tests/playwright/selftest_reroll.spec.ts --workers=1
```

Initial run: 2 passed, 1 failed in 12.0 seconds. MkDocs builds and serves the static site.
Both external-script checks pass: ordered library initialization/readiness and failure/retry.
The real journey fails before its first click because the stale manifest supplies no
`data-selftest-status` element for the refreshed native CRC. This run supplies no A/B/A acceptance.
After manifest correction, the sandboxed rerun cannot launch Chromium: MachPortRendezvous
`Permission denied (1100)`, before assertions. An authorized unrestricted rerun executes the
same command and passes all 3 tests in 8.2 seconds. Exact output is preserved in
`output_phase2_acceptance/playwright_unrestricted.log`.

The strengthened final run passes all 3 tests in 7.5 seconds. Exact output is
`output_phase2_acceptance/playwright_complete_journey_final.log`. The first expanded run
used an overly specific incorrect-answer status expectation (`Not completed`); the actual
status intentionally displays `incorrect`. The final test asserts no completed status and
no stored B CRC after the incorrect attempt. No production correction was needed.

The real journey verifies no WASM request before the click, actual fetched-bank conversion,
correct A grading, distinct B initially incomplete with fresh unchecked inputs/blank feedback,
incorrect B grading without a B completion record, correct B grading with separate persisted
A and B CRC records, returning to completed A with fresh controls, and retained A completion
after reload and return. Both external-script tests also pass: ordered dependency readiness
and failure/retry. No browser page errors occur. The sandbox attempt before this run failed
Chromium launch before assertions; its log is `playwright_complete_journey.log`.

A one-time two-slot probe (`multislot_probe_final.log` and `multislot_probe.json`) confirms
independent rerolls, correct real MC grading in the first slot, fresh usable MA controls in
the second slot, the untouched MATCH slot remaining incomplete, and exactly one button/status
per slot after repeated initialization. No page errors occur. Its initial exploratory
assumption that both slots had radios was corrected when the second bank proved to be MA.
This is temporary acceptance evidence, not a new permanent matrix. `navigation.instant` is
not enabled in MkDocs, so no actual instant-navigation acceptance is claimed.

Focused checks pass:

```bash
source source_me.sh && pytest tests/test_selftest_manifest.py -q
node tests/selftest_progress_dom_test.mjs
node tests/selftest_progress_storage_test.mjs
node tests/selftest_correctness_contract_test.mjs
```

Initial results: 5 pytest cases and 3 Node checks pass. After the parser correction, the expanded
manifest checks pass 11 cases in 0.07 seconds. After KISS trimming, 7 manifest cases pass in
0.05 seconds and the 3 Node checks pass. These are focused checks, not a fresh full suite.

The trimmed permanent Playwright file passes all 3 checks in 2.0 seconds against the already
served HTTP site, using `PORT=8734 npx playwright test tests/playwright/selftest_reroll.spec.ts
--workers=1`. This run uses the real A -> incorrect B -> correct B -> A journey and the two
external-script readiness/retry checks. It does not repeat the earlier build, reload, or multi-slot
probe. The 7.5-second strengthened journey and temporary probes above remain separate evidence.

Permanent tests retain demonstrated question completion and v1 timestamp preservation,
valid native attribute order/missing question roots, and script readiness/retry. KISS trimming
removes speculative malformed quote/title/data-id cases, repeated A grading, the redundant
permanent reload branch, and the v2-null assertion. No instant-navigation gate is added because
`navigation.instant` is not enabled.

## Final generated-output recovery

The later Phase 1/2 integration check finds all 482 manifest rows missing `bankId` and
all 57 topic pages missing reroll wrappers, while their native selftest includes remain valid.
The files were replaced in alphabetical order within 0.19 seconds at 09:46:50 on 2026-10-09,
after both default builds finished at 09:37:41 and 09:39:22. The final pytest run starts
at approximately 09:47:37, so it cannot explain that replacement. The validation worker
reports no restore or copyback; its comparison and benchmark helpers write only ignored
evidence. MkDocs has no source-generation hook. The exact bulk writer remains unconfirmed.

Fresh bootstrapped imports resolve the local production modules, whose executable code
contains both contracts. An in-memory manifest built from the affected inputs emits all
482 bank IDs. No production defect is demonstrated, so no speculative source fix or new
permanent test is introduced.

The canonical recovery commands both exit 0:

```bash
source source_me.sh && python3 build_site.py -S genetics -T topic01 -l 1 --cli
source source_me.sh && python3 build_site.py -I --cli
```

The scoped default uses current artifacts and refreshes its metadata; full `-I` renders
all 57 topic pages. `output_phase2_acceptance/composition_recovery.json` records 482 wrappers,
482 manifest rows with bank IDs, exactly matching bank sets, consistent source URIs, and
no missing BBQ sources or includes. Logs are `default_composition_recovery.log` and
`indexes_composition_recovery.log` in the same ignored evidence directory. Fresh browser
acceptance of these final generated files remains manager-owned.

## Remaining acceptance

- Retain the synthetic prefixed-choice CRC discrepancy in the upstream handoff; it does not
  affect the inventoried website corpus or block this Phase 2 consumer rollout.
- Initial website implementation and parser reviews pass; obtain fresh post-KISS specification
  and quality/integration reviews of the current trimmed implementation and evidence.
- Upstream audit and all-seven-kind/native/WASM browser evidence remain separately owned by QPM.

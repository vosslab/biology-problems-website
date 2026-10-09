# Rust self-test contract handoff

## Assignment boundary

This report records read-only Python/Rust contract findings for the Rust QPM source owner.
The website workstream owns only `biology-problems-website`; it does not edit Rust sources.
The synthetic CRC case below remains an upstream compatibility finding. D8 inventoried the
actual website corpus (482 banks, 16,157 MC/MA rows, and 80,088 choices) and found zero choices
matching the affected raw-prefix shape. The finding therefore does not block the website Phase 2
consumer acceptance documented in [optimized_spindle_phase2_acceptance.md](optimized_spindle_phase2_acceptance.md).

The evidence compares Python package sources in
`/Users/vosslab/nsh/PROBLEMS/qti-package-maker` with the Rust checkout at
`/Users/vosslab/nsh/PROBLEMS/qti-package-maker-rs`. Runtime probes used the existing Rust
build and the website-vendored WASM; they do not establish fixed-source behavior.

## Findings for the Rust owner

### CRC identity

Python's BBQ reader passes raw choice strings to its item constructor, which calculates the CRC
before display normalization:

- `qti_package_maker/engines/bbq_text_upload/read_package.py:17`
- `qti_package_maker/assessment_items/item_types.py:148`

Rust's core item constructor already hashes the raw fields correctly when it receives them:
`crates/qti-core/src/item.rs:165`. The Rust BBQ reader strips choice prefixes first, at
`crates/qti-engines/src/bbq_text_upload/mod.rs:242`, which changes the CRC input. The source-owner
fix belongs in that reader; the website must use the CRC Rust emits and must not translate IDs.

Reproducible input (literal tab separators):

```text
MC<TAB>12. <p>abcd_1234</p> Question?<TAB>A. one<TAB>Incorrect<TAB>B. two<TAB>Correct
```

Python oracle:

```python
from qti_package_maker.engines.bbq_text_upload.read_package import make_item_cls_from_line

line = "MC\t12. <p>abcd_1234</p> Question?\tA. one\tIncorrect\tB. two\tCorrect"
print(make_item_cls_from_line(line).item_crc16)
# 3891_574a
```

The existing Rust WASM artifact and website-vendored WASM both emitted `3891_d9cb` for this
input; `3891_574a` is the established Python-compatible result for this synthetic input and a
migration reference for the upstream reader fix. It is not a universal CRC requirement or a
website-corpus acceptance gate.

From the Rust checkout, reproduce the current WASM result with:

```javascript
import {readFile} from "node:fs/promises";
import {initialize, convert} from "./packages/qti-wasm/dist/src/index.js";

await initialize(new Uint8Array(await readFile(
  "./packages/qti-wasm/dist/generated/qti_wasm_bg.wasm"
)));
const line = "MC\t12. <p>abcd_1234</p> Question?\tA. one\tIncorrect\tB. two\tCorrect";
const result = convert({
  inputFormat: "bbq_text_upload",
  outputFormat: "html_selftest",
  input: {
    kind: "file", name: "probe.txt",
    bytes: new TextEncoder().encode(line), companions: []
  },
  shuffleSeed: 0
});
console.log(new TextDecoder().decode(result.artifact.primary.bytes)
  .match(/question_html_([a-f0-9_]+)/)[1]);
// Existing artifact: 3891_d9cb; required: 3891_574a
```

### HTML and grading hooks

The Python self-test contract uses `div#question_html_CRC`,
`div#statement_text_CRC`, and `#result_CRC`. Rust's emitter differs in
`crates/qti-engines/src/html_selftest/mod.rs:182`: it emits a `section` question root and a
`.qti-statement` without the statement ID. Preserve the Python IDs and usable repeated-check
behavior in Rust output.

Rust's controls are in `crates/qti-engines/src/html_selftest/assets/controls.js:8`. The generated
global `checkAnswer_CRC` exists, but button and Enter handlers call private `grade(box)` instead
of the mutable global. As a result, a website wrapper around `window.checkAnswer_CRC` can be
bypassed. Route explicit button grading and NUM Enter grading through that mutable global. Keep
Python's interaction behavior: FIB Enter does not grade, MULTI_FIB Enter is suppressed, and a
successful grade leaves the button usable. Current Rust adds FIB Enter grading and disables the
button after success.

Initialize each actual question element once with an element property sentinel. Check that
sentinel before assigning global grading functions so a second question script or reroll does not
overwrite a website wrapper. A replacement DOM element must initialize independently.

The result text contract is already compatible: completion observes rendered results because both
grading functions return `undefined`. Preserve `CORRECT`, `Total Score: N out of N`, and
`Correct positions: N of N`. Both implementations support MC, MA, MATCH, NUM, FIB, MULTI_FIB, and
ORDER.

## Website behavior and acceptance

This handoff's source-contract observations identify QPM ownership. Website consumer status is
recorded in [optimized_spindle_phase2_acceptance.md](optimized_spindle_phase2_acceptance.md): the
actual native and WASM WOMC selftests emit the same CRC (`6304_a249`), real grading hooks work,
and the real A/B/A completion journey passes. The website uses emitted question CRCs directly and
does not translate identifiers or compensate for unexpected Rust output.

The website stores completion under each question CRC in the existing `selftest_progress_v1`
record. Bank identity supplies fetch and slot context only. There is no bank-level completion,
bank migration, or inference that completing A completes B. Existing version-1 records remain
intact. For display, replace each bank slot's manifest CRC with the CRC currently rendered in that
slot. The answer wrappers must calculate against the current displayed rows after every reroll;
an unchanged slot keeps its currently rendered CRC.

For variants A and B, the observable contract is:

1. Complete A; A's CRC is stored as complete.
2. Reroll to B; B starts with unanswered input and feedback. B is incomplete unless B already
   has its own saved completion.
3. Incorrect or partial B earns no completion. Correct B stores B's CRC independently.
4. Return to A; A's completion remains, while the new answer controls and feedback are fresh.

The current website reroll request must include the full bank. `limit: 1` truncates input before
selection in Rust `crates/qti-engines/src/conversion.rs:68`, preventing selection from the full
pool; the self-test writer already emits one question. Remove that limit.

The repro above remains useful for the QPM source owner to verify the synthetic raw-prefix
compatibility case against native and WASM outputs. Its expected Python CRC is scoped to that
input; artifact hashes and source provenance identify the tested builds but are not compatibility
gates. The current website acceptance is the real native/WASM identity and A/B/A journey recorded
in the Phase 2 report. Broad all-seven-kind and NUM Enter contract coverage belongs to QPM's
upstream audit, not a new website acceptance matrix. `navigation.instant` is not configured in
MkDocs and is not an acceptance requirement. The phase report distinguishes focused checks from
the browser journey and records their evidence separately.

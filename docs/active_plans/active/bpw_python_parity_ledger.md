# Python parity execution ledger

Plan: [bpw_python_parity_restoration.md](bpw_python_parity_restoration.md)

Local parity, specification, quality, visual, final composition, and full-browser checks pass. The manager
accepts implementation and independently verified local integration. Temporary comparison tooling is removed: 770 files / 50,514,227 bytes. All 20 frozen hashes
still match; both MkDocs/gallery servers return HTTP 200.

## Completion evidence

- BPW mounting executes parsed-head scripts/styles. Placeholder, specified button/hint states,
  automatic loading, advancement, and filename-based v2 achievements pass actual-site checks.
- Independent specification review passes six light/dark states; quality review passes the actual
  390px theme switch. Root selector branches retain global Material variables.
- Gallery has a descriptive title. All 20 frozen input/output hashes, 17 Python-source hashes,
  and 18 vendor hashes independently match their receipts; all 22 HTTP links resolve on 8124.
- Delivered Wasm SHA-256:
  `a7839f2c794765d09f56d6d89d97b29a2e5d38c4d0cd858d5a20e12fe3ac0921`.
- The 180-row comparison finishes with zero execution/request errors after one exact-row recovery.
  Feedback/reset/keyboard checks agree. Independent appearance review passes question, lifecycle,
  theme, and gallery captures. MC radio/text sizing agrees in Python/native/Wasm.
- Manager independently verifies all ten actual BPW cases: empty/correct feedback, available
  resets, painted RDKit canvases, one shared stylesheet, and zero JavaScript errors.
- D4 adds only `overflow-x: auto` in
  [custom.css](../../../site_docs/assets/stylesheets/custom.css) to make wide authored tables
  locally reachable. Six focused checks and 16 bank/width/theme probes pass. Fresh mobile
  specification/quality and final composition reviews PASS. A second shipped FIB independently
  passes both-theme final-label access and light keyboard/toolbar/grading checks. The manager
  independently verifies a third shipped RNA FIB at 360x800 in separate light/dark contexts:
  ArrowRight reaches the final cell; real Tab/ShiftTab restores the toolbar; grading is CORRECT;
  document/viewport stay 360px and page/request errors are zero.

## Validation lanes

- Final Python suites after documentation edits and temporary-probe cleanup: BPW 3263 passed;
  Rust QPM 1922 passed. The earlier BPW 3262-pass/one-failure run caught only the now-removed
  disposable Playwright probe outside the browser-test directory.
- Final `cargo test --workspace --locked`: 335 passed, 4 ignored. Formatting, workspace check,
  and strict all-target Clippy pass. BPW's three Node DOM/storage/correctness checks pass.
- Initial Rust package lane on unchanged production passes 12 Node, 42 browser, three
  current-Python checks, TypeScript, native/Wasm builds, and the documented portable-target gate.
- Post-D4 actual MkDocs `PORT=8123 npx playwright test --workers=1`: 94 passed in 29.2s,
  unchanged assertions and no retries, after restarting the same MkDocs command. A 24-navigation
  diagnostic has zero errors. Earlier failures remain separate: pre-D4 84 passed/9 failed,
  nine focused serial passes, then full isolated 93 passes; post-D4 random asset/readiness
  failures precede clean-server acceptance. Their root cause remains unproven, with no
  rebuild/traceback or descriptor/thread exhaustion evidence. No concurrency fix is claimed.
- QPM target cleanup preserves the native release hash and reduces disposable cache from
  10.1 to 7.56 GiB; full Python rerun and checkout/Podman/target budgets pass.
- Reader-test repair restores authored MA `min_answers_required` -2; absent MA metadata defaults
  to 1. Metadata-present NUM tolerance remains 0.01. Missing-report link failures are resolved.

## Test-server capacity

D5 isolates the reliable-test boundary. A default four-worker static-server run passes 88 and
fails 6, with traces showing dropped localhost script/Wasm/source requests. An independent
controlled capacity probe uses the same Python 3.12 handler, asset, and three batches of 32
requests: listen backlog 5 yields 21/96 HTTP 200 and 75 errors; backlog 128 yields 96/96 HTTP 200,
zero errors, and identical bytes. This demonstrates a static test-server queue-capacity defect.
The standard-library [helper_serve_site.py](../../../tests/playwright/helper_serve_site.py)
uses listen queue 128 and replaces Playwright startup. The normal configured four-worker suite passes all 94 cases in 11.9s, with zero retries
and unchanged assertions. Only the test startup/helper changes; no app, bank, or renderer changes.
The actual-MkDocs 94-case acceptance remains a separate result; its earlier failures are not
proven to share this cause. Fresh D5 specification and code-quality reviews pass with no findings.


The manager accepts direct Git-root discovery in the standalone nested server helper as a narrow
exception that avoids import-path/package scaffolding.

## Decisions and propagation

The manager receives owner acknowledgments and independent application evidence for these decisions.

| Decision | Implementer acknowledgment/application | Reviewer acknowledgment/application | Downstream consumer verification |
| --- | --- | --- | --- |
| D1: Keep evidence isolated by owner. | Parity owner moves evidence to its own output; UI/theme owners retain separate outputs; validators use their own directories. | Review uses the complete isolated 180-row recapture. | Manager retains separate suite, parity, and ten-case actual-site checks; vanished old captures are not proof. |
| D2: Use a simple descriptive gallery title. | Planning correction removes invented `Previews` requirement; gallery owner supplies descriptive title. | Specification reviewer explicitly withdraws `Previews` finding; re-review passes. | Manager verifies unchanged 20 input/output hashes and all 22 served links. |
| D3: Keep root selector branches global. | Theme owner splits top-level selector lists; six light/dark states pass. | Fresh specification review checks six live states; quality reviewer verifies actual 390px theme switch. | Parity recapture has one shared stylesheet, root hue 225, and slate background; final visual views confirm application. |
| D4: Make wide authored tables locally reachable. | BPW owner adds only `overflow-x: auto` to the existing question host; six focused checks and 16 bank/width/theme probes pass. | Independent mobile specification PASS; live focused check passes and 20 frozen hashes match. | ArrowRight reaches last cell; Tab/ShiftTab recover toolbar access; correct grading passes. Fresh mobile quality and final composition reviews PASS; full actual-MkDocs suite passes 94/94. |
| D5: Serve concurrent test assets reliably. | Standard-library startup helper uses listen queue 128; configured four-worker suite passes 94/94 with zero retries. | Fresh specification and code-quality reviews PASS with no findings. | Controlled 96-request probe yields all HTTP 200, identical bytes, and zero errors at queue 128; manager accepts the narrow direct Git-root discovery exception. |

## Evidence limits

The pre-D4 matrix's FIB containment finding is superseded by the 16 targeted post-correction
probes and fresh independent reviews. Frozen authored markup is unchanged: the original table
remains 536.281px within a 328px scrolling host and the document remains 360px wide.

Authored source colors retain dark-theme contrast of 2.29-2.56:1; recoloring is outside this scope.
NUM's 3.34 lower edge follows inherited Python floating-point semantics. Realistic RDKit held-
mouse/wheel drag passes on Python and actual BPW at 1280x1000: dragstart/drop/end fire, four
canvases paint, partial score is 1/4, and JavaScript errors are zero. Default offscreen `dragTo`
behavior was a tooling limitation.

Historical receipts retain original provenance and narrower scopes. Temporary comparisons are
one-time evidence removed after acceptance. No permanent pixel/HTML-byte snapshots, Git
staging/commit, remote publication, exhaustive-bank, or complete accessibility claim belongs here.


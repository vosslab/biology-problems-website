# Restore Python self-test parity

## Goal and current state

Restore the current Python self-test's appearance and behavior in the Rust QPM
renderer and in the biology-problems-website (BPW) page that consumes it. The
known integration issue includes parsed-head script/style mounting; retain the
small BPW fix and verify that the mounted script actually executes. The known
renderer mismatch must be diagnosed against real Python output before changing
the owning Rust renderer. This is a stabilization plan: keep changes narrow,
record experiments, and defer any broader design change unless evidence and
architect review call for it.

The Python captures are the frozen visual and functional reference. Compare the
Python renderer, native Rust output, WASM output, and the actual BPW page served
by MkDocs. Use direct visual and interaction evidence; generated HTML or pixel
equality is not a permanent acceptance gate.

## Required behavior

- The unloaded button says `Show practice question`; while loading it says
  `Loading question...`; after a question loads it says `Show another question`;
  on failure it says `Retry`.
- Before the first question loads, show a compact, lightly outlined placeholder
  titled `Practice question` with `Your question will appear here.` Keep the
  button and its hint together at the question location. Remove the placeholder
  when a question is ready.
- Preserve the existing first automatic load, question advancement, and progress
  behavior. The loaded-state hint says `Replaces this question with another
  from the same set.`
- Render the unchanged ten Python captures in a static gallery index with a
  simple descriptive title and direct links to each capture. The fixture set
  covers MC, MA, MATCH, NUM, FIB, MULTI_FIB, ORDER, MATCH tables, MC RDKit, and
  MATCH RDKit.
- Preserve correct/incorrect/empty/partial feedback, clear/reset, numeric
  tolerance and text answers, MATCH click/drag/keyboard actions, ORDER moves,
  question replacement, retry, accessibility, responsive widths, and light and
  dark themes.

## Implementation sequence

1. **Freeze and route references.** Confirm all ten captures exist in the
   sibling `qti-package-maker-rs/tests/fixtures/python_selftest/` tree and
   remain byte-for-byte unchanged. Add only the static gallery index there,
   with working direct links. Keep this work limited to the Rust fixture index
   and its documentation.
2. **Preserve the BPW integration correction.** Retain the small parsed-head
   script/style mounting fix. Verify script execution in the served page, not
   just the presence of script nodes or markup. Place the initial placeholder,
   button, and hint at the question location; preserve automatic loading and
   progress advancement. Implement the explicit button states and loaded hint.
3. **Compare renderers and isolate differences.** Use a temporary browser
   comparison of the ten real captures across Python, native Rust, WASM, and
   actual BPW served under `mkdocs serve`. Record each concrete mismatch and a
   minimal reproduction. Separate renderer defects from integration defects.
4. **Correct at the owning boundary.** Fix demonstrated rendering differences
   in Rust QPM; fix the BPW page integration in BPW. Refresh vendored output
   only for the existing helper. Keep fixes concrete and avoid unrelated broad
   abstractions. Continue parity fixes through integration acceptance,
   recording evidence and routing each issue to its owner.
5. **Review and accept.** Run the behavior matrix against every question type,
   inspect accessibility and responsive/light/dark states, and obtain
   independent visual and functional reviews followed by manager acceptance.
   Run all applicable Rust, Node, and browser checks and both Python suites at
   final acceptance.

## File scope

- BPW self-test controller, CSS, and specs: implement the stated lifecycle and
  presentation contract, plus focused behavior coverage.
- Rust QPM renderer and its focused tests: correct only concrete output
  differences confirmed against the frozen Python references.
- `qti-package-maker-rs/tests/fixtures/python_selftest/`: leave the ten
  reference captures unchanged; add a static gallery index with direct links.
- The existing BPW vendored helper output: refresh only if its owning source
  changed and the generated artifact is required by the established workflow.
- Temporary browser comparison evidence: use for this investigation and remove
  after review; do not turn it into pixel or HTML-byte snapshots.

Do not clean up Python code, add unrelated abstractions, stage or commit files,
or publish/deploy the site as part of this plan.

## Coordination

The execution manager routes work in this order: `bpw_ui` owns the BPW
controller/CSS/specification changes; `reference_gallery` owns only the Rust
fixture gallery index/readme; `parity_validation` owns temporary real-ten
browser comparison; and `runtime_setup` records dependency, server, and check
commands. Keep these boundaries intact. Invite questions and challenges when
evidence conflicts with the contract; report blockers instead of inventing
decisions. The manager routes a fresh specification review, quality reviews,
and integration review before acceptance.

The bounded documentation assignment used Luna. Coding and browser comparison
require `gpt-6.1-sol` for cross-repository judgment.

## Completion checks

- The ten Python reference files are unchanged, and every gallery link resolves
  when served over HTTP.
- Python, native Rust, WASM, and actual BPW output agree on the intended
  appearance and behavior, with each accepted difference documented.
- Script execution is demonstrated in the MkDocs-served BPW page.
- The lifecycle, feedback, input, interaction, accessibility, responsive, and
  theme requirements above pass their behavior and visual reviews.
- Independent visual and functional reviews and manager acceptance are recorded.
- Applicable Rust, Node, and browser checks plus both Python suites pass. Report
  focused checks separately from this final full check set.
- No permanent pixel/HTML-byte snapshots, Python cleanup, unrelated design
  work, Git staging/commit, or publication was introduced.


# Rust QPM self-test presentation handoff

Date: 2026-10-09

Please investigate presentation differences in the standalone HTML produced by Rust QPM's
`html_selftest` writer. The findings below reproduce without MkDocs or website JavaScript.
QPM owns the generated HTML, CSS, controls, and internal interactions. Please choose the
implementation in the Rust QPM repository.

## Reproduction

From the `biology-problems-website` checkout, generate two standalone pages:

```bash
mkdir -p output_qpm_repro

../qti-package-maker-rs/target/release/bbq-converter --selftest -n 1 \
  -i site_docs/biochemistry/topic01/bbq-MATCH-biochemical_functional_groups-questions.txt \
  -o output_qpm_repro/match.html

../qti-package-maker-rs/target/release/bbq-converter --selftest -n 1 \
  -i site_docs/biochemistry/topic04/bbq-alpha_helix_h-bonds-MA-questions.txt \
  -o output_qpm_repro/ma.html

source source_me.sh && python3 -m http.server 8766 --bind 127.0.0.1 \
  --directory output_qpm_repro
```

Open `http://127.0.0.1:8766/match.html` and `http://127.0.0.1:8766/ma.html`.
Start with a 1280px-wide Chromium viewport. Inspect the initial unanswered questions.
These pages contain only QPM's output and browser defaults.

The same writer is exposed through WASM with `inputFormat: "bbq_text_upload"` and
`outputFormat: "html_selftest"`. Current native and vendored WASM output had identical CSS
for the sampled MATCH and dihybrid banks. Different seeds can select different questions;
this is CSS agreement, not a claim of whole-file byte equality.

## Confirmed standalone findings

### MATCH feedback column

- Observed: the table uses `table-layout: fixed`, `width: 100%`, and a 30px first-header
  width. In the desktop standalone capture, the first column's outer width was 37px,
  while the visible word `Feedback` extended into the adjacent header's space.
- Expected: feedback headings and markers fit inside their own column without overlapping
  answer controls or neighboring headings. Longer prompts should retain usable answer slots.
- Reference: the saved fragment has a separately sized feedback column, a 64px minimum,
  and a different table structure. Those values are evidence of the previous design,
  not a required implementation prescription.

### MATCH choice colors

- Observed: generated answer buttons carry `qti-choice-1` through `qti-choice-5`, and the
  stylesheet declares corresponding foreground/background variables. The emitted CSS lacks
  rules that apply those variables to those classes. Raw standalone choices consequently
  render with browser-default button colors rather than the saved colored choices.
- Expected: the intended choice palette is actually applied, with readable text/background
  pairs. Preserve the non-color labels and interaction cues.

### Compact choices and paragraphs

- Observed: the saved MA fragment uses `qti-auto-grid` for short choices; current Rust output
  emits an ordinary vertical choice list and lacks that grid's rules. The difference is visible
  in standalone pages, without host styles.
- Observed: saved question text combines adjacent paragraphs with line breaks. Rust preserves
  separate paragraph elements, producing additional default paragraph margins in raw HTML.
- Expected: short choices and related prompt text retain a compact, readable presentation
  comparable to the saved examples. Preserve semantic meaning and comfortable controls.
  Please determine the appropriate layout and spacing policy; reproducing the old markup
  transformation is not itself a requirement.

The compact-layout and paragraph observations are presentation-parity requests. The evidence
does not establish that every paragraph boundary or every vertical choice list is incorrect.

## References and source locations

Saved appearance references in the website repository:

```text
site_docs/biochemistry/topic01/downloads/selftest-MATCH-biochemical_functional_groups.html
site_docs/biochemistry/topic04/downloads/selftest-alpha_helix_h-bonds-MA.html
```

Treat these as reference artifacts. Their original generator provenance does not need to be
assumed to reproduce the findings above, and the investigation does not establish which earlier
CLI build produced a subsequently remembered working version.

Rust implementation:

```text
crates/qti-engines/src/html_selftest/mod.rs
crates/qti-engines/src/html_selftest/assets/base_styles.css
crates/qti-engines/src/html_selftest/assets/control_styles.css
```

Comparison implementation in the Python QPM repository:

```text
qti_package_maker/engines/html_selftest/control_styles.py
qti_package_maker/engines/html_selftest/html_functions.py
```

## Requested return

Please return the upstream revision/build containing the corrections and standalone browser
evidence for the affected controls at desktop and mobile widths. Verify that grading and
Clear/Reset still work. The website maintainer will manually refresh the vendored WASM from
upstream and validate the complete website afterward.

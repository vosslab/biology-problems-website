# Self-test screenshot evidence

This page records the current browser captures used to review the self-test
integration. They are reproducible evidence of the current local build, not a
timestamped record of how the website appeared on an earlier day.

## Provenance

The captures use the frozen Python QPM references and the served BPW site. Each
comparison uses the same saved BBQ input and named question route. The capture
harness records its viewport, color scheme, fixture provenance, and resulting
asset names; it stops when a page raises a JavaScript error.

## Current captures

User-supplied styling regression, 2026-10-09.

<!-- screenshots:begin (managed by screenshot-docs) -->
![User-supplied unstyled MATCH self-test regression](screenshots/reference_reported_unstyled_match.png)
![BPW fill-in-the-blank question in light mode](screenshots/selftest_bpw_fib_light.png)
![Frozen Python QPM fill-in-the-blank reference in light mode](screenshots/selftest_python_fib_light.png)
![BPW fill-in-the-blank question in dark mode](screenshots/selftest_bpw_fib_dark.png)
![Frozen Python QPM fill-in-the-blank reference in dark mode](screenshots/selftest_python_fib_dark.png)
![BPW multiple-answer question in light mode](screenshots/selftest_bpw_ma_light.png)
![Frozen Python QPM multiple-answer reference in light mode](screenshots/selftest_python_ma_light.png)
![BPW multiple-answer question in dark mode](screenshots/selftest_bpw_ma_dark.png)
![Frozen Python QPM multiple-answer reference in dark mode](screenshots/selftest_python_ma_dark.png)
![BPW MATCH question in light mode](screenshots/selftest_bpw_match_light.png)
![Frozen Python QPM MATCH reference in light mode](screenshots/selftest_python_match_light.png)
![BPW MATCH question in dark mode](screenshots/selftest_bpw_match_dark.png)
![Frozen Python QPM MATCH reference in dark mode](screenshots/selftest_python_match_dark.png)
![BPW RDKit MATCH question in light mode](screenshots/selftest_bpw_match_rdkit_light.png)
![Frozen Python QPM RDKit MATCH reference in light mode](screenshots/selftest_python_match_rdkit_light.png)
![BPW RDKit MATCH question in dark mode](screenshots/selftest_bpw_match_rdkit_dark.png)
![Frozen Python QPM RDKit MATCH reference in dark mode](screenshots/selftest_python_match_rdkit_dark.png)
![BPW table MATCH question in light mode](screenshots/selftest_bpw_match_tables_light.png)
![Frozen Python QPM table MATCH reference in light mode](screenshots/selftest_python_match_tables_light.png)
![BPW table MATCH question in dark mode](screenshots/selftest_bpw_match_tables_dark.png)
![Frozen Python QPM table MATCH reference in dark mode](screenshots/selftest_python_match_tables_dark.png)
![BPW multiple-choice question in light mode](screenshots/selftest_bpw_mc_light.png)
![Frozen Python QPM multiple-choice reference in light mode](screenshots/selftest_python_mc_light.png)
![BPW multiple-choice question in dark mode](screenshots/selftest_bpw_mc_dark.png)
![Frozen Python QPM multiple-choice reference in dark mode](screenshots/selftest_python_mc_dark.png)
![BPW RDKit multiple-choice question in light mode](screenshots/selftest_bpw_mc_rdkit_light.png)
![Frozen Python QPM RDKit multiple-choice reference in light mode](screenshots/selftest_python_mc_rdkit_light.png)
![BPW RDKit multiple-choice question in dark mode](screenshots/selftest_bpw_mc_rdkit_dark.png)
![Frozen Python QPM RDKit multiple-choice reference in dark mode](screenshots/selftest_python_mc_rdkit_dark.png)
![BPW multiple-fill-in-the-blank question in light mode](screenshots/selftest_bpw_multi_fib_light.png)
![Frozen Python QPM multiple-fill-in-the-blank reference in light mode](screenshots/selftest_python_multi_fib_light.png)
![BPW multiple-fill-in-the-blank question in dark mode](screenshots/selftest_bpw_multi_fib_dark.png)
![Frozen Python QPM multiple-fill-in-the-blank reference in dark mode](screenshots/selftest_python_multi_fib_dark.png)
![BPW numeric question in light mode](screenshots/selftest_bpw_num_light.png)
![Frozen Python QPM numeric reference in light mode](screenshots/selftest_python_num_light.png)
![BPW numeric question in dark mode](screenshots/selftest_bpw_num_dark.png)
![Frozen Python QPM numeric reference in dark mode](screenshots/selftest_python_num_dark.png)
![BPW ordering question in light mode](screenshots/selftest_bpw_order_light.png)
![Frozen Python QPM ordering reference in light mode](screenshots/selftest_python_order_light.png)
![BPW ordering question in dark mode](screenshots/selftest_bpw_order_dark.png)
![Frozen Python QPM ordering reference in dark mode](screenshots/selftest_python_order_dark.png)
![BPW page with an automatically loaded practice question](screenshots/selftest_bpw_site_context_loaded.png)
![BPW MATCH assignment with feedback after checking an answer](screenshots/selftest_bpw_match_feedback_light.png)
![BPW mobile fill-in-the-blank question before horizontal table scrolling](screenshots/selftest_bpw_mobile_fib_initial_dark.png)
![BPW mobile fill-in-the-blank question after horizontal table scrolling](screenshots/selftest_bpw_mobile_fib_scrolled_dark.png)
![BPW mobile RDKit MATCH question with painted molecular structure](screenshots/selftest_bpw_mobile_match_rdkit_light.png)
![BPW MATCH assignment and feedback demonstration](screenshots/selftest_match_assignment_demo.gif)
<!-- screenshots:end -->

`reference_reported_unstyled_match.png` is the unchanged 673x368 PNG supplied
with the regression report. Its SHA-256 is
`3ac8bbf2f3ca9b60fcbe04c611ec8f51ba4f0ad01b2629f335caf64299894f44`.
It documents the reported before-fix state and is retained as a `reference_`
image. It does not document the desired appearance from the prior day.

The forty paired captures cover all ten frozen fixtures in light and dark modes.
Each Python/BPW pair uses the same saved input record at a 1280px viewport. The
frozen Python fragment remains unchanged; its visible capture-only host supplies
the measured BPW font, width, colors, and theme variables and labels that
provenance. BPW captures run through its normal page controller and the browser
WebAssembly renderer. The mobile captures show the table before and after local
horizontal scrolling and a separate RDKit structure that has painted.
The initial mobile FIB frame includes the controls; the scrolled frame exposes
the final table cell, with left-side question content outside that local view.

Some authored colored text retains the original Python dark-mode contrast. This
is a source-owned limitation shown by the captures, rather than a claim that
every authored color meets a separate contrast target.

The GIF begins with an unassigned MATCH question, assigns a choice, checks the
answer, and ends with visible feedback. It plays once in under five seconds;
the exact measured duration is in the receipt. The same result remained visible
with reduced motion; the still feedback image provides an equivalent static
record.

## Capture commands

Refresh the README website views, including a loaded HLA question, from the
repository root:

```bash
source source_me.sh && node tests/playwright/capture_docs_screenshots.mjs
```

With the BPW site on port 8123 and the frozen Python gallery on port 8124,
refresh the self-test evidence:

```bash
source source_me.sh && node tests/playwright/capture_selftest_screenshots.mjs
```

The capture receipt is
[screenshots/selftest_capture_receipt.json](screenshots/selftest_capture_receipt.json).

## Verification

The capture harness verifies HTTP availability, records the fixture manifest and
case input, waits for the QPM stylesheet and rendered controls, and fails on
JavaScript errors. It verifies painted RDKit canvases and records image
dimensions, hashes, and GIF duration in the receipt. The README harness also
rejects request failures while it captures the live website views. Visual review
remains separate from functional browser tests. The captures show representative
states; the integration test suite establishes interaction behavior.

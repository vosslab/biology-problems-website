# Self-test screenshot evidence

This page records the current browser captures used to review the self-test
integration. They are reproducible evidence of the current local build, not a
timestamped record of how the website appeared on an earlier day.

## Provenance

The BPW captures include the requested compact green buttons and tighter MC/MA rows.
The Python reference output remains unchanged. Static captures use text-optimized WebP
at quality 90; the original regression PNG and the demonstration GIF retain their formats.

The captures use the frozen Python QPM references and the served BPW site. Each
comparison uses the same saved BBQ input and named question route. The capture
harness records its viewport, color scheme, fixture provenance, and resulting
asset names; it stops when a page raises a JavaScript error.

## Current captures

User-supplied styling regression, 2026-10-09.

<!-- screenshots:begin (managed by screenshot-docs) -->
![User-supplied unstyled MATCH self-test regression](screenshots/reference_reported_unstyled_match.png)
![BPW fill-in-the-blank question in light mode](screenshots/selftest_bpw_fib_light.webp)
![Frozen Python QPM fill-in-the-blank reference in light mode](screenshots/selftest_python_fib_light.webp)
![BPW fill-in-the-blank question in dark mode](screenshots/selftest_bpw_fib_dark.webp)
![Frozen Python QPM fill-in-the-blank reference in dark mode](screenshots/selftest_python_fib_dark.webp)
![BPW multiple-answer question in light mode](screenshots/selftest_bpw_ma_light.webp)
![Frozen Python QPM multiple-answer reference in light mode](screenshots/selftest_python_ma_light.webp)
![BPW multiple-answer question in dark mode](screenshots/selftest_bpw_ma_dark.webp)
![Frozen Python QPM multiple-answer reference in dark mode](screenshots/selftest_python_ma_dark.webp)
![BPW MATCH question in light mode](screenshots/selftest_bpw_match_light.webp)
![Frozen Python QPM MATCH reference in light mode](screenshots/selftest_python_match_light.webp)
![BPW MATCH question in dark mode](screenshots/selftest_bpw_match_dark.webp)
![Frozen Python QPM MATCH reference in dark mode](screenshots/selftest_python_match_dark.webp)
![BPW RDKit MATCH question in light mode](screenshots/selftest_bpw_match_rdkit_light.webp)
![Frozen Python QPM RDKit MATCH reference in light mode](screenshots/selftest_python_match_rdkit_light.webp)
![BPW RDKit MATCH question in dark mode](screenshots/selftest_bpw_match_rdkit_dark.webp)
![Frozen Python QPM RDKit MATCH reference in dark mode](screenshots/selftest_python_match_rdkit_dark.webp)
![BPW table MATCH question in light mode](screenshots/selftest_bpw_match_tables_light.webp)
![Frozen Python QPM table MATCH reference in light mode](screenshots/selftest_python_match_tables_light.webp)
![BPW table MATCH question in dark mode](screenshots/selftest_bpw_match_tables_dark.webp)
![Frozen Python QPM table MATCH reference in dark mode](screenshots/selftest_python_match_tables_dark.webp)
![BPW multiple-choice question in light mode](screenshots/selftest_bpw_mc_light.webp)
![Frozen Python QPM multiple-choice reference in light mode](screenshots/selftest_python_mc_light.webp)
![BPW multiple-choice question in dark mode](screenshots/selftest_bpw_mc_dark.webp)
![Frozen Python QPM multiple-choice reference in dark mode](screenshots/selftest_python_mc_dark.webp)
![BPW RDKit multiple-choice question in light mode](screenshots/selftest_bpw_mc_rdkit_light.webp)
![Frozen Python QPM RDKit multiple-choice reference in light mode](screenshots/selftest_python_mc_rdkit_light.webp)
![BPW RDKit multiple-choice question in dark mode](screenshots/selftest_bpw_mc_rdkit_dark.webp)
![Frozen Python QPM RDKit multiple-choice reference in dark mode](screenshots/selftest_python_mc_rdkit_dark.webp)
![BPW multiple-fill-in-the-blank question in light mode](screenshots/selftest_bpw_multi_fib_light.webp)
![Frozen Python QPM multiple-fill-in-the-blank reference in light mode](screenshots/selftest_python_multi_fib_light.webp)
![BPW multiple-fill-in-the-blank question in dark mode](screenshots/selftest_bpw_multi_fib_dark.webp)
![Frozen Python QPM multiple-fill-in-the-blank reference in dark mode](screenshots/selftest_python_multi_fib_dark.webp)
![BPW numeric question in light mode](screenshots/selftest_bpw_num_light.webp)
![Frozen Python QPM numeric reference in light mode](screenshots/selftest_python_num_light.webp)
![BPW numeric question in dark mode](screenshots/selftest_bpw_num_dark.webp)
![Frozen Python QPM numeric reference in dark mode](screenshots/selftest_python_num_dark.webp)
![BPW ordering question in light mode](screenshots/selftest_bpw_order_light.webp)
![Frozen Python QPM ordering reference in light mode](screenshots/selftest_python_order_light.webp)
![BPW ordering question in dark mode](screenshots/selftest_bpw_order_dark.webp)
![Frozen Python QPM ordering reference in dark mode](screenshots/selftest_python_order_dark.webp)
![BPW page with an automatically loaded practice question](screenshots/selftest_bpw_site_context_loaded.webp)
![BPW MATCH assignment with feedback after checking an answer](screenshots/selftest_bpw_match_feedback_light.webp)
![BPW mobile fill-in-the-blank question before horizontal table scrolling](screenshots/selftest_bpw_mobile_fib_initial_dark.webp)
![BPW mobile fill-in-the-blank question after horizontal table scrolling](screenshots/selftest_bpw_mobile_fib_scrolled_dark.webp)
![BPW mobile RDKit MATCH question with painted molecular structure](screenshots/selftest_bpw_mobile_match_rdkit_light.webp)
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

Refresh every managed screenshot, including the three README website views and
the self-test demonstration GIF, from the repository root:

```bash
./devel/capture_screenshots.sh
```

The command loads the repository environment, starts its own MkDocs server on
port 8765, captures all ten references and their BPW counterparts, and stops the
browser and server. Leave that port free. Frozen Python files are read directly
from the sibling QPM checkout; a Python gallery server is unnecessary.
`npm run docs:screenshots` invokes the same complete refresh.

The capture receipt is
[screenshots/selftest_capture_receipt.json](screenshots/selftest_capture_receipt.json).

## Verification

The capture harness verifies HTTP availability, records the fixture manifest and
case input, waits for the QPM stylesheet and rendered controls, and fails on
JavaScript errors. It verifies painted RDKit canvases and records image
dimensions, hashes, and GIF duration in the receipt. The README captures also
reject request failures while capturing the live website views. Visual review
remains separate from functional browser tests. The captures show representative
states; the integration test suite establishes interaction behavior.

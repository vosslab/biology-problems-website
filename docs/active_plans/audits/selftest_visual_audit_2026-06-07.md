# Self-test visual audit 2026-06-07

This audit synthesizes work package M0-W4 from the rustling-roaming-scone plan
(see `M0`). A Playwright harness captured 148 baseline screenshots across the 8
self-test question types present in this repo, rendered both on full site topic
pages and as standalone fragment pages, at desktop 1280 and mobile 390, in light
and Material-slate dark themes, and in passive and interactive modes. Nine
screenshot-review subagents inspected slices of that baseline and returned
findings. This document merges those findings into one coverage table and
recommends the next-pass (M2) scope. The mojibake character described below is a
stray "A-circumflex" glyph (the byte produced when a UTF-8 non-breaking space or
special character is decoded as Latin-1); it is written here as the literal text
"A-circumflex" rather than as a raw non-ASCII glyph.

## Coverage

- Question types present and surveyed (8): MC, WOMC, MA, TFMS, FIB, NUM,
  EQUATION, MATCH.
- ORDER and MULTI_FIB do not exist in this repo and were not surveyed.
- Page modes (2): rendered site topic pages and standalone fragment pages.
- Viewports (2): desktop 1280 and mobile 390.
- Themes (2): light and Material-slate dark.
- Interaction modes (2): passive (before) and interactive (after).

## Findings

| issue | question types affected | page mode | viewport/theme where seen | severity | scope | recommended action | likely layer |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Mojibake "A-circumflex" trailing glyph on its own line below Check Answer / Reset buttons | WOMC, MA, TFMS, NUM, EQUATION, MATCH, FIB | standalone | both viewports, both themes | high | broad | fix now (investigate root cause first) | needs-investigation (engine escape_non_iso_8859_1 / charset vs question content) |
| Mojibake inline content corruption ("polar covalent A-circumflex bond", plus-minus, "O-H....O" middle-dots, Fischer header) | WOMC, MATCH, EQUATION, MA | both | both viewports, both themes | high | broad | fix now (investigate root cause first) | needs-investigation (engine charset vs question content) |
| EQUATION mojibake corrupts the answer text itself, making choices hard to read | EQUATION | both | both viewports, both themes | medium-high | type-specific | fix now (investigate root cause first) | needs-investigation |
| MATCH after-drag "Your Choice" column shows raw internal CRC IDs (e.g. "42a3_fdf4_001") instead of human-readable dragged answer text | MATCH | both (interactive) | both viewports, both themes | high | broad | HARNESS ARTIFACT -- not an engine bug; corrected in harness (see match_raw_id_2026-06-08.md) | harness (selftest_visual_survey.mjs set textContent to CRC token instead of draggable innerText) |
| RDKit structure canvas (fixed ~480x320) overflows mobile 390 viewport and is clipped (no horizontal scroll) | all pages with a structure canvas (biochem01, biochem03 amino-acid pages) | both | mobile 390, light and dark | critical/high | broad | fix now | engine (responsive canvas max-width:100%; height:auto) |
| RDKit canvas renders white background in dark mode (bright rectangle on dark page) | all RDKit pages | both | desktop and mobile, dark | critical/high | broad | fix now | engine/site-CSS (dark canvas treatment) |
| Fragment interiors do not fully adapt to dark mode: MATCH answer-table rows show light/pastel fills; input fields and buttons keep default light styling | MATCH plus all types with inputs/buttons | both | both viewports, dark | high | broad | fix now / next pass | engine-CSS (dark-scope review; tie to deferred embed_theme_css work) |
| Input fields and Check Answer / Reset buttons use default browser styling rather than site button/input classes | all types with inputs/buttons | standalone (most visible), and dark | both viewports, both themes (worst in dark) | medium | broad | fix now | engine |
| Result-div typography: monospace/large, low visual weight, tight spacing under button; minor blank-line gaps | all types | both | both viewports, both themes | medium | broad | fix now (already in M2-W1/W2) | engine |
| Dense topic pages: question-panel details summaries share visual weight with h2 headings; colored variant-badge pill row repeats under every panel (biochem06) | all types on dense pages | rendered site | both viewports, both themes | medium | type-specific | defer | site-CSS / content |
| Standalone pages have large vertical dead space above the canvas / below content | all types | standalone | both viewports, both themes | low | isolated | defer | site-CSS |
| MA 6-column checkbox grid has uneven column widths on desktop (collapses fine on mobile) | MA | both | desktop, both themes | low | type-specific | defer | engine / site-CSS |
| Long multi-question pages (8-14 panels) have no back-to-top / progress affordance on mobile | all types on long pages | rendered site | mobile 390, both themes | low | type-specific | defer | site-CSS |
| Collapsed accordion rows do not visually distinguish FIB from other types | FIB (vs others) | rendered site | both viewports, both themes | low | type-specific | defer | site-CSS |
| FIB interactive Check Answer produced no feedback (page pixel-identical before/after) due to a ReferenceError | FIB | both (interactive) | both viewports, both themes | high (functional) | type-specific | no action (hotfixed in M1; recorded for after-comparison) | engine |

## Recommended next-pass scope

### Fix now (confirmed broad)

1. Mojibake "A-circumflex" corruption, trailing-glyph and inline forms
   (needs-investigation: root-cause the engine `escape_non_iso_8859_1` / charset
   path versus question content before patching). Engine-leaning but unconfirmed.
2. ~~MATCH after-drag "Your Choice" shows raw CRC IDs instead of display text~~
   REMOVED: this was a harness artifact, not an engine bug. The survey harness
   was setting textContent to the raw CRC token instead of the draggable's
   readable innerText. Fixed in tests/playwright/selftest_visual_survey.mjs.
   See docs/active_plans/audits/match_raw_id_2026-06-08.md for full investigation.
3. RDKit canvas overflow / clipping on mobile (engine: responsive canvas sizing).
4. RDKit canvas white background in dark mode (engine / site-CSS: dark canvas
   treatment).
5. Fragment interiors not fully dark-mode adapted: MATCH table fills, inputs,
   buttons (engine-CSS; tie to deferred embed_theme_css work).
6. Input fields and buttons use default browser styling, not site classes
   (engine).
7. Result-div typography weight/spacing (engine; already scoped in M2-W1/W2).

EQUATION answer-text mojibake is the same root cause as item 1 and resolves with
it; it is type-specific only in where it is most painful.

### Deferred / follow-up

- Dense topic-page hierarchy: details summaries vs h2 weight, repeated
  variant-badge pill row (site-CSS / content).
- Standalone-page vertical dead space (site-CSS).
- MA desktop checkbox-grid uneven columns (engine / site-CSS).
- Long-page back-to-top / progress affordance on mobile (site-CSS).
- Collapsed-accordion FIB visual distinction (site-CSS).

### Layer summary

- Engine fix-now: RDKit overflow, RDKit dark background,
  fragment dark-mode CSS, default-styled inputs/buttons, result-div typography.
- Harness corrected (not engine): MATCH CRC IDs (was survey artifact; fixed in
  selftest_visual_survey.mjs; see match_raw_id_2026-06-08.md).
- Needs-investigation fix-now: mojibake (engine charset vs content).
- Site / content deferred: topic-page hierarchy, dead space, MA grid columns,
  back-to-top, FIB accordion distinction.

## Not-observed / confirmed-acceptable

Do not chase these in the next pass; they were inspected and judged acceptable:

- MC, MA, NUM, TFMS dark-mode text contrast is OK.
- Mobile single-column reflow is OK.
- Choice color-chips are legible in both light and dark.
- MATCH feedback check / cross marks have OK contrast.
- Result "CORRECT" green text is legible.

## Baseline evidence

The before-baseline screenshots and machine-readable report live in
`test-results/selftest_survey/baseline/` (148 PNGs plus `report.json`). This is
the before-baseline for a future after-comparison once the fix-now items land;
the FIB functional fix from M1 is already captured in
`standalone_fib_interactive_after.png` and
`topic_biochem03_interactive_after.png` for that comparison. Note: the
RDKit-slice reviewer ran long, but its area is fully covered by the FIB,
multi-fragment, and dark-mode reviewers' findings recorded above.

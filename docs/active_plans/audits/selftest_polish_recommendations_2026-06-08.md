# Self-test UI visual polish recommendations

## Context

Three screenshot analysts examined the baseline self-test survey under
`test-results/selftest_survey/baseline/` across four polish dimensions:
whitespace and gaps, wrapping, interface understandability, and scoring
interactivity. This report consolidates their findings into one actionable,
engine-implementable set of recommendations. The mojibake (character-encoding)
issue is deliberately EXCLUDED from this report: it is tracked separately and is
already being fixed at the engine level. All findings below are visual or
interaction polish, not encoding.

## Hard constraints

These constraints are non-negotiable. The runtime parses specific result strings
and references specific element IDs. Any recommendation here is ADDITIVE only.

- Do NOT change the result STRINGS the runtime depends on:
  - literal `CORRECT`
  - `Total Score X out of Y`
  - `Correct positions X of Y`
  - `Correct: X of Y`
- Do NOT change element IDs: `question_html_<crc>`, `result_<crc>`.
- Do NOT rename the global `checkAnswer_<crc>` function.
- Improvements must be additive: new CSS classes, wrapper elements, prefixes or
  icons placed OUTSIDE the parsed result string, and extra sibling elements.
  A prefix like `[+]` must sit outside the substring the runtime reads, never
  inside it.

## Whitespace and gaps

| Issue | Question types | Scope | Severity | Recommendation |
| --- | --- | --- | --- | --- |
| Standalone fragment renders content in top 15-30%, then 500-700px dead white space below | all (standalone view) | broad | HIGH | In the standalone wrapper set `body { min-height: unset; height: fit-content; }`; embedded site pages are unaffected and must not change |
| Inter-question vertical gap uneven on topic pages (MATCH blocks have larger bottom margin than MC) | MATCH, MC | broad | MEDIUM | Normalize `margin-bottom` on `.qti-selftest` / the `<details>` block so all question types share one spacing token |
| NUM data table collides with the following prompt (no gap) | NUM | type-specific | MEDIUM | Add `margin-bottom` (or `margin-top` on the prompt) to separate the data table from the prompt text |
| Cross-topic rhythm differs (genetics has tighter question-to-choices gap than biochem) | MC family | broad | MEDIUM | Centralize the choices `ul` `margin-top` in one shared class so question-to-choices spacing is identical across topics |
| RDKit/FIB canvas has large internal padding above and below the molecule | FIB (RDKit) | type-specific | LOW | Reduce vertical padding inside the canvas container; cap canvas wrapper height |
| Consistent result-div margins to separate result from the next question | all | broad | MEDIUM | Apply uniform `margin-top` / `margin-bottom` to the `result_<crc>` wrapper (wrapper class, ID unchanged) |

## Wrapping

| Issue | Question types | Scope | Severity | Recommendation |
| --- | --- | --- | --- | --- |
| MATCH table row-height misalignment on mobile and long-text variant (dropzone fixed height vs prompt wraps) | MATCH | type-specific | MEDIUM | Remove fixed row/cell height; use `min-height` plus `vertical-align: middle` so wrapped prompts and dropzones stay aligned |
| WOMC choices use a fixed-column horizontal row and clip at mid widths | WOMC | broad | MEDIUM | Replace fixed columns with `flex-wrap` and a per-item `min-width`; cap at 4 per row on desktop |
| MA uses a 6-column grid with an orphaned half-row | MA | broad | MEDIUM | Same flex-wrap with per-item `min-width`; cap 4 per row on desktop to avoid orphaned cells |
| Mobile FIB input and button cramped on one line | FIB | type-specific | LOW | Stack input above button on narrow viewports via a flex/column breakpoint |
| WOMC mobile choice wraps with the radio mis-grouped | WOMC | type-specific | LOW | Use a hanging indent (radio in a fixed-width column, label text wraps beside it) |

## Interface understandability

| Issue | Question types | Scope | Severity | Recommendation |
| --- | --- | --- | --- | --- |
| All controls (Check Answer / Clear Selection / Reset Game) are unstyled default browser buttons with no hierarchy; submit is indistinguishable from destructive reset | all | broad | HIGH | Style Check Answer as a filled primary button; Clear / Reset as secondary or ghost buttons (CSS classes only, no label changes that affect parsing) |
| After-submit feedback is terse (small mono CORRECT) with no next-step affordance, no INCORRECT guidance, no try-again, no reveal of correct answer | all | broad | HIGH | Add an additive feedback panel beside `result_<crc>`: a Try Again control and, on wrong answers, a reveal-correct-answer element. Do not alter the parsed strings |
| No prominent question-level "select all that apply" cue (only buried in instructions); students default to single-select | MA | type-specific | HIGH | Add a bold sub-label directly after the stem, e.g. "Select all that apply" |
| Drag-and-drop has no touch alternative; instruction says "Drag" with no mobile path | MATCH | type-specific | HIGH | Add a tap-to-select-then-tap-row interaction; swap the instruction text to a tap-based phrasing on touch devices |
| Draggable tokens lack a grab affordance; dropzone dashed border too light (1px) when embedded | MATCH | type-specific | MEDIUM | Add `cursor: grab` and a grab-handle visual; thicken the dropzone dashed border for embedded contexts |
| Answer-area inputs unstyled, no visual grouping; input and button do not stack on mobile | FIB, NUM | type-specific | MEDIUM | Style inputs and wrap the answer area in a grouped container; stack input above button on narrow viewports |
| Check Answer button sits below the molecule figure, spatially separated from choices; mobile molecule info card collides with choices, choice text truncated | MC (RDKit) | type-specific | MEDIUM | Move the Check Answer button to directly below the choices; add spacing so the molecule card does not overlap choices on mobile |
| After a correct answer, Check Answer stays active and unstyled (no answered/disabled state); student may re-click | all | broad | MEDIUM | Add an answered/disabled CSS state to the button after submission (no string or ID change) |
| Collapsed (before-answer) question blocks lack an expand affordance | topic pages | broad | MEDIUM | Add a chevron icon or tinted header to the collapsed accordion summary |
| WOMC indistinguishable from MC; TFMS has no format badge; decorative per-choice colors have no legend | WOMC, TFMS, MC | broad | LOW | Add small additive format badges and a one-line legend for decorative choice colors |

## Scoring interactivity

| Issue | Question types | Scope | Severity | Recommendation |
| --- | --- | --- | --- | --- |
| Result div is monospace, large, bold, flush under the button with no container; reads as DEBUG text | all | broad | HIGH | Wrap `result_<crc>` in a pill/banner using the EXISTING-but-unused `qti-feedback-success` / `qti-feedback-error` theme classes (border-radius, padding, inline-block, faint bg tint). Highest-impact single change |
| Color alone carries right/wrong (WCAG 1.4.1 fail) | all | broad | HIGH | Add a non-color marker: a prefix such as `[+]` / `[x]` placed OUTSIDE the parsed result string, or an icon element |
| Check Answer stays active after a correct answer | all | broad | HIGH | Disable the button or relabel its visual state to "Answered" via CSS/wrapper (no parsed-string or ID change) |
| N identical green CORRECT labels when all questions expanded; no per-question completion signal | topic pages | broad | HIGH | Add a completion dot or badge in each accordion header |
| Total-score line is the last thing on the page and easily missed, especially on mobile | MATCH | type-specific | HIGH | Move the score summary ABOVE the button pair / above the table; add a header for the per-row check column |
| No per-item feedback | MA, MATCH | type-specific | MEDIUM | Add per-choice / per-row green or red tint classes; on a correct MA add a brief "all N correct" suffix INSIDE the container (outside the parsed substring) |
| No readonly lock or hint after submission | NUM | type-specific | MEDIUM | Lock the input readonly after a correct answer; on incorrect, append expected value/tolerance in an additive span while keeping the `incorrect` string intact |
| Chosen choice row not highlighted after submit | MC family | type-specific | MEDIUM | After submit, highlight the chosen row via CSS (green if right; red plus green-on-correct if wrong) |
| Result-div margins inconsistent, result crowds the next question | all | broad | MEDIUM | Apply consistent `margin-top` / `margin-bottom` to the result wrapper |

## Recommended implementation order

### Quick high-impact CSS wins (do first)

These are additive CSS or small wrapper changes with no interaction logic and no
risk to parsed strings or IDs.

1. Feedback pill: wrap `result_<crc>` in the existing `qti-feedback-success` /
   `qti-feedback-error` classes. Highest-impact single change.
2. Styled buttons: Check Answer as filled primary; Clear / Reset as secondary or
   ghost; add an answered/disabled state after submit.
3. Non-color right/wrong marker: `[+]` / `[x]` prefix or icon OUTSIDE the parsed
   result string (WCAG 1.4.1).
4. Result spacing: consistent `margin-top` / `margin-bottom` on the result
   wrapper so the result separates cleanly from the next question.
5. Standalone dead-space fix: `body { min-height: unset; height: fit-content; }`
   in the standalone wrapper only.

### Larger interaction changes (second pass)

These need new interaction logic or per-item state and should be scheduled after
the CSS wins.

- Touch alternative for MATCH (tap-to-select-then-tap-row) plus touch
  instruction swap.
- Per-item feedback (per-choice / per-row tint) for MA and MATCH.
- Completion dots/badges in accordion headers on topic pages.
- Show-correct-answer-on-wrong reveal plus Try Again control.
- Move MATCH score summary above the button pair / table.
- NUM readonly lock and tolerance-hint span on incorrect.

### Mapping to the deferred next-pass plan

The larger interaction changes above are candidates to fold into the deferred
plan at
[docs/active_plans/active/selftest_engine_polish_next_pass.md](../active/selftest_engine_polish_next_pass.md).
In particular the touch MATCH path, per-item feedback, completion dots, and the
show-correct-on-wrong reveal align with that plan's interaction scope and should
be added there rather than implemented ad hoc.

## Excluded / tracked elsewhere

- Mojibake (character-encoding artifacts): engine fix in progress, tracked
  separately. Not in this report.
- MATCH raw-ID leakage: a harness artifact, already fixed.
- RDKit mobile overflow and dark canvas: already captured in the next-pass plan
  [docs/active_plans/active/selftest_engine_polish_next_pass.md](../active/selftest_engine_polish_next_pass.md).

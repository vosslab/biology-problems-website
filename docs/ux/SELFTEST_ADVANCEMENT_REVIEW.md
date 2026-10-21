# Self-test advancement review

Date: 2026-10-21. Scope: correct-answer feedback and the move to the next question.

## Task and method

Students practice biology questions on desktop and touch devices. The task is to answer,
check the feedback, reflect, and continue. The reported friction is movement away from the
answer before the reader is ready. A canceled move should leave feedback available and the
next question ready below.

Use a focused cognitive walkthrough and browser interaction checks. This is an expert
inspection with automated input, not a participant study or a full accessibility audit.
The decision is how to make the existing automatic advancement less intrusive while retaining
the requested automatic flow.

## Findings and checks

| Task step | Baseline finding | Change or retained behavior | Evidence |
| --- | --- | --- | --- |
| Read feedback | The pause was only 500 ms. | Double it to 1,000 ms; wait longer if the next question is still loading. | One-time virtual-clock check: no move at 999 ms; move at 1,000 ms when ready. Existing loading test passes. |
| Continue reviewing | Wheel or keyboard input did not cancel the pending move. | Reader input cancels pending advancement; feedback remains. | Permanent browser test covers wheel and keyboard; one-time checks cover click and mobile touch. |
| Hide or replace | These explicit actions already canceled advancement. | Retain that behavior. | Existing browser test passes. |
| Move to next question | Native smooth scroll, separate focus with preventScroll, and a header offset already exist. | Retain browser scrolling and focus handling. | Desktop walkthrough reaches the next ready question with keyboard focus. |
| Reduce motion | The existing preference disables the animation. | Retain instant scrolling for reduced motion. | One-time browser check confirms instant versus smooth behavior. |
| Leave the tab | A pending task could survive switching tabs. | Cancel when the document becomes hidden. | Source inspection of visibility-change cancellation; no real background-tab walkthrough performed. |

## Rationale and limits

Predictability and user control favor letting deliberate input override the timer.
[W3C guidance on predictable input](https://www.w3.org/WAI/WCAG22/Understanding/on-input.html)
explains why unexpected context changes can disorient readers. This is relevant rationale,
not a claim that the existing Check Answer button violates that success criterion.
[W3C motion guidance](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)
supports retaining the reduced-motion preference.

The [CSSOM scrolling specification](https://www.w3.org/TR/cssom-view-1/#smooth-scrolling)
leaves native animation timing to the browser. An explicit slower speed would require custom
animation. Retain the native implementation for this bounded change.

One second is the requested adjustment, not an evidence-based reading-time threshold.
A reader who stays still will still advance automatically. If that remains disruptive,
reader-triggered continuation would address the underlying pacing issue more fully; it is
outside this change's retained automatic flow.

## Validation and test scope

- MkDocs build and 12 focused Playwright tests pass.
- One-time Chromium checks cover normal/reduced motion at desktop width and touch cancellation
  at 360 px. Exact timing checks are implementation evidence, not permanent test assertions.
- Extend the existing permanent advancement test to cover reader interruption. It protects
  against stealing focus after deliberate input. A failure requires fixing cancellation or
  stale advancement, not changing a timing snapshot.
- Runtime scrolling stays in JavaScript; TypeScript is used by Playwright. No type-contract
  changes or new dependencies are needed. No standalone TypeScript compiler check is configured.
- No representative students or assistive-technology users participated. Reading comprehension,
  perceived speed, and screen-reader announcement timing remain unmeasured.

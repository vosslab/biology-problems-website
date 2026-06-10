# MATCH raw-ID investigation 2026-06-08

Read-only investigation into the reported MATCH self-test bug: after a drop and
Check Answer, the "Your Choice" column appears to show the internal CRC-derived
token (for example "1d38_7c07_001") instead of the human-readable dragged
answer text. Source audit:
[selftest_visual_audit_2026-06-07.md](selftest_visual_audit_2026-06-07.md),
finding row "MATCH after-drag Your Choice column shows raw internal CRC IDs".

## Summary

The MATCH generator engine code is CORRECT. The real drop handler emitted by
`add_MATCH.py` sets the dropzone display text from the dragged element's visible
text and keeps the CRC token only in `dataset.value` for scoring. The token
that appears in the audit screenshot
(`standalone_match_interactive_after.png`) is a TEST-HARNESS ARTIFACT, not a
product bug.

The Playwright survey harness does not perform a real HTML5 drag. It bypasses
the engine's `drop` handler and writes the CRC token directly into the dropzone
as both `dataset.value` AND visible `textContent`. That harness line is what the
screenshot captured. A real user drag through the engine handler shows readable
text.

Root cause of the screenshot:
`tests/playwright/selftest_visual_survey.mjs:245` sets
`zone.textContent = correctVal;` where `correctVal` is the CRC token from
`data-correct`, simulating the filled state with the token instead of the
choice text.

## Evidence

### Engine drop handler is correct

`qti_package_maker/engines/html_selftest/add_MATCH.py`, the drop listener
emitted by `generate_drag_and_drop_js` (source lines 52-56):

```
// add_MATCH.py:53  visible text taken from the dragged li
let choiceText = draggedItem.innerText.trim();
// add_MATCH.py:54  dropzone DISPLAY set to truncated readable text
this.innerHTML = choiceText.length > 30 ? choiceText.substring(0, 27) + "..." : choiceText;
// add_MATCH.py:55  CRC token kept only in dataset.value, used for scoring
this.dataset.value = draggedItem.dataset.value;
// add_MATCH.py:56  full clean text preserved in the title attribute
this.title = draggedItem.getAttribute("title");
```

`draggedItem` is set in the `dragstart` listener to the `.draggable` `<li>`
(add_MATCH.py:28-29: `draggedItem = this;`). The `<li>` contains a `<span>` with
the readable label, so `innerText` is human-readable.

Confirmed in generated output
`site_docs/biotechnology/topic01/downloads/selftest-MATCH-biotech_vs.html`:

```
line 41-42:
<li class="draggable qti-choice-2" draggable="true" data-value="1d38_7c07_003"
    title="designing a watch to measure blood pressure" ...>
  <span style="color: var(--qti-choice-2-fg);"><strong>A.</strong>
   designing a watch to measure blood pressure</span>

line 87 (emitted JS):  let choiceText = draggedItem.innerText.trim();
line 88 (emitted JS):  this.innerHTML = choiceText.length > 30 ? ... : choiceText;
line 89 (emitted JS):  this.dataset.value = draggedItem.dataset.value;
```

`draggedItem.innerText` on that `<li>` is "A. designing a watch to measure
blood pressure" (readable). The `lxml` reformat in `generate_html`
(add_MATCH.py:258) preserves the inner `<span>`, as seen in the generated file,
so `innerText` is not mangled.

### Harness writes the token, bypassing the handler

`tests/playwright/selftest_visual_survey.mjs`, MATCH branch (lines 233-250):

```
239  const dropzones = container.querySelectorAll('.dropzone');
240  dropzones.forEach(zone => {
242    const correctVal = zone.dataset.correct;   // CRC token, e.g. 1d38_7c07_001
243    zone.dataset.value = correctVal;           // OK: scoring input
245    zone.textContent = correctVal;             // BUG (test-only): token as display text
246    zone.style.border = '2px solid ...';
247  });
248  const fn = window['checkAnswer_' + c];
249  if (fn) fn();
```

The harness never sets `draggedItem` and never fires the engine `dragstart` /
`drop` listeners. It hand-fills the dropzone, and at line 245 it uses the token
as the visible text. The screenshot is taken after this, so the token shows.

## Display-vs-matching separation (scoring stays correct)

The two concerns are already separated in the engine:

- Matching/scoring key: `dataset.value` (the CRC token). Compared against
  `dataset.correct` in `generate_check_answers_js`
  (add_MATCH.py:108-113: `selectedValue === correctValue`). This is correct and
  must not change.
- Visible display: `innerHTML` / `innerText` set from the dragged element's
  text (add_MATCH.py:53-54), plus `title` from the clean choice text
  (add_MATCH.py:56). This is the human-readable channel.

The check-answer handler reads only `dataset.value`, never the visible text, so
scoring is independent of any display change. No scoring logic needs to change
to fix the screenshot, and the engine display is already readable for real
drags.

## Recommended minimal fix (file:line + intended expression)

Two distinct things, ordered by what actually fixes the reported symptom:

1. Primary, fixes the audit screenshot. The defect is in the test harness, not
   the engine. `tests/playwright/selftest_visual_survey.mjs:245` should fill the
   dropzone with the matching draggable's readable text instead of the token.
   Intended replacement expression at that line: look up the `.draggable` whose
   `data-value` equals `correctVal` and copy its display text, for example:

   ```
   const src = container.querySelector('.draggable[data-value="' + correctVal + '"]');
   zone.textContent = src ? src.innerText.trim() : correctVal;
   ```

   This makes the simulated drop mirror what the real engine `drop` handler
   does, so the after-screenshot shows readable text. (Out of this report's
   write scope; recorded for the implementer.)

2. Optional engine display polish (NOT required to fix the bug, not the reported
   defect). `add_MATCH.py:53` uses `draggedItem.innerText`, which includes the
   "A. " letter prefix, so the dropzone shows "A. designing a watch...". If a
   cleaner cell is desired, source the display from the title attribute (the
   pure choice text already stored at add_MATCH.py:56 origin / choice
   `title="{clean_title}"` at add_MATCH.py:221) instead:

   ```
   // add_MATCH.py:53 alternative
   let choiceText = draggedItem.getAttribute("title").trim();
   ```

   This is a cosmetic preference, not a correctness fix, and would also need the
   matching tweak in ORDER for parity. Leave to the implementer's discretion.

## ORDER parity note

`add_ORDER.py` shares the same correct pattern, so it does NOT carry the
reported bug. Its drop handler (add_ORDER.py:46-49):

```
46  let choiceText = draggedItem.innerText.trim();
47  zone.innerHTML = choiceText.length > 30 ? choiceText.substring(0,27)+"..." : choiceText;
48  zone.title = draggedItem.getAttribute('title');
49  zone.dataset.value = draggedItem.dataset.value;
```

Same separation: display from `innerText`/`title`, scoring token only in
`dataset.value` (compared at add_ORDER.py:78). ORDER does not exist in the
bp-website 278 files and was not surveyed, but for the future: ORDER is sound on
this axis. If the optional engine display polish (item 2 above) is adopted for
MATCH, apply the identical `getAttribute("title")` change to add_ORDER.py:46 for
parity. ORDER would also need the same harness fix if it is ever surveyed,
because the harness MATCH-style simulation would have the same token-as-text
trap.

## Confidence

High. The engine drop handler provably sets readable display text and keeps the
token only in `dataset.value`; the generated HTML confirms the `<span>` survives
`lxml` reformatting so `innerText` is readable; and the harness line that writes
the token as visible text is identified exactly. The one residual uncertainty is
purely cosmetic (the "A. " letter prefix in the engine display), which is a
preference call, not the reported defect.

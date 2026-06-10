# Self-test engine polish: next pass

This is the next-pass implementation plan for the html_selftest engine work. It
carries forward milestones M2 through M5, which the prior pass
(`rustling-roaming-scone`) deferred behind the M0 audit gate, and folds in the
M0 visual audit plus three follow-up investigations (mojibake root cause, MATCH
raw-ID, engine JS-emitter hazards). The M0 gate is now satisfied: a 148-shot
Playwright baseline exists, the per-type coverage table is complete, and the
three follow-ups have resolved the high-value findings to confirmed root causes.

This plan reorders the deferred work to lead with the highest-value,
evidence-confirmed item (mojibake), and demotes one finding that an
investigation proved is not an engine bug (MATCH raw-ID). It does not authorize
the broad 278-fragment regeneration without an explicit human approval gate.

## Context

The bp-website embeds 278 generated `selftest-*.html` fragments into mkdocs
Material topic pages via Jinja `{% include %}` inside collapsible `<details>`
panels. The fragments are produced by a separate repo's engine:
`~/nsh/PROBLEMS/qti-package-maker/qti_package_maker/engines/html_selftest/`.
Engine changes are authored in qti-package-maker but every visual change is
verified in bp-website, where the fragments render inside the real theme.

The M0 pass stood up the Playwright survey harness, captured the baseline into
`test-results/selftest_survey/baseline/`, and landed the confirmed M1 FIB
hotfix (the missing f-string plus the result-color theme vars; verified present
in `add_FIB.py` at the `isCorrect` block). The M0 synthesis
(`docs/active_plans/audits/selftest_visual_audit_2026-06-07.md`) produced the
coverage table that this pass re-derives its scope from. Three follow-up
investigations then resolved the audit's three highest-impact unknowns.

### Inputs folded into this plan

- M0 audit and coverage table:
  `docs/active_plans/audits/selftest_visual_audit_2026-06-07.md`.
- Mojibake root cause (verdict ENGINE, HIGH confidence):
  `docs/active_plans/audits/mojibake_root_cause_2026-06-08.md`.
- MATCH raw-ID (verdict TEST-HARNESS artifact, not an engine bug):
  `docs/active_plans/audits/match_raw_id_2026-06-08.md`.
- Engine JS-emitter hazard audit:
  `docs/active_plans/audits/engine_js_emitter_audit_2026-06-08.md`.
- Prior approved plan (M2-M5 deferred): `rustling-roaming-scone`.

### Confirmed engine source state (read 2026-06-08)

- `html_functions.py:31` encodes to `iso-8859-1` with `xmlcharrefreplace`, which
  escapes only characters above U+00FF and passes the entire U+0080-U+00FF
  Latin-1 block through as raw bytes. This is the mojibake root cause.
- `html_functions.py:44` emits the literal entity `&nbsp;` in the result
  placeholder div.
- `html_functions.py:36-42` `add_result_div` still uses `font-size: large` and
  `font-family: monospace`.
- `add_FIB.py:22` still uses `{normalized_answers!r}` (Python repr into a JS
  array literal). The M1 color/f-string fix already landed at `add_FIB.py:30,33`.

### Result-string contract (must not break)

`site_docs/assets/scripts/selftest_progress.js` `classifyResultElement()` treats
these as full-correct: literal `CORRECT`; `Total Score: X out of Y` with `X==Y`;
`Correct positions: X of Y` with `X==Y`; `Correct: X of Y` with `X==Y`. Element
IDs `question_html_<crc>`, `result_<crc>`, `statement_text_<crc>`,
`fib_input_<crc>` and global `checkAnswer_<crc>()` are relied on. All polish must
preserve these verbatim. A contract guard test exists (prior side quest F).

## Objectives

- Eliminate the mojibake corruption at its engine root cause so on-disk fragment
  bytes are pure ASCII and charset-agnostic. Highest value: 266 of 278 fragments
  are affected.
- Close the one remaining runtime-error-class JS-emitter hazard
  (`add_FIB.py:22` repr-into-JS), unless a parallel workstream has already done
  it.
- Make RDKit structure canvases responsive and dark-mode-correct so they stop
  overflowing and stop rendering as bright rectangles on dark pages.
- Bring fragment interiors (inputs, buttons, MATCH table fills) into dark mode,
  tied to the deferred `embed_theme_css` flag decision.
- Drop the result-div monospace typography and tighten spacing so results read
  as native Material body text.
- Land the `embed_theme_css` flag so the site can serve one global stylesheet
  while standalone fragments stay self-contained.
- Regenerate all 278 fragments and re-survey against the M0 baseline, behind an
  explicit human-approval gate.

## Design philosophy

Fix the design, not the symptom: every fix lands in the engine generator so all
regenerated output is correct, never by hand-patching the 278 committed HTML
files. The mojibake fix escapes the full non-ASCII range to numeric entities
rather than papering over the symptom at the consumer's decode step. The
`embed_theme_css` flag rejects the simpler "always move CSS to the site" option
because it would break fragments opened standalone; the flag preserves
portability (embed by default) while letting the site opt out -- long-term over
short-term.

Evidence discipline: scope is re-derived from the M0 coverage table and the
three follow-up investigations, not from re-inspecting a few examples. One
audit-table finding (MATCH raw-ID) is explicitly demoted because an
investigation proved it is a test-harness artifact, not an engine defect.

Python style for qti-package-maker edits: tabs for indentation, avoid broad
try/except, no defensive fallbacks that hide bugs. See `docs/PYTHON_STYLE.md`.

Git boundary: only humans run `git commit`. Each workstream leaves the working
tree ready for human review -- report changed files, commands run, and remaining
risks. `docs/CHANGELOG.md` is updated as part of "done".

## Scope

In scope (this pass, subject to the regeneration gate below):

- Engine mojibake fix in `html_functions.py` (escape function and result-div
  entity), plus an explicit save encoding in `engine_class.py`.
- `add_FIB.py:22` repr-to-json.dumps fix, if not already landed by workstream H.
- Responsive and dark-mode-correct RDKit structure canvases.
- Dark-mode fragment styling for inputs, buttons, and MATCH table fills, tied to
  the `embed_theme_css` flag.
- Result-div typography and spacing cleanup.
- The `embed_theme_css` flag plus the canonical CSS asset and vendored site copy.
- Full regeneration of the 278 fragments and the after-survey, behind the gate.
- `docs/CHANGELOG.md` updates in both repos.

## Non-goals

- MATCH after-drag raw-ID is NOT an engine bug. The investigation
  (`match_raw_id_2026-06-08.md`) proved the engine drop handler sets readable
  display text from `innerText`/`title` and keeps the CRC token only in
  `dataset.value`. The CRC token in the audit screenshot is a harness artifact
  from `selftest_visual_survey.mjs:245`, which is being corrected separately
  (workstream G). Do not add any engine "fix" for this; do not change MATCH
  scoring or display. The optional "A. " prefix cleanup is cosmetic preference
  only and is not authorized here.
- Accessibility remediation (keyboard drag-drop, fieldset/legend, aria-live,
  ARIA labels, color-only-feedback audit). Recorded for a follow-up plan.
- Changing any result string, element ID, or global function name (breaks
  `selftest_progress.js`).
- Editing centrally propagated files (`tests/playwright/repo_root.mjs`,
  `devel/setup_playwright.sh`); changes route upstream.
- Rewriting question content. Upstream generators that embed raw Latin-1
  symbols become harmless once the engine escapes the full block.
- Editing the 278 committed HTML files by hand; they are regenerated.
- Deferred site-side polish (kept deferred, not implemented here): topic-page
  heading hierarchy, repeated variant-badge pill row, long-page back-to-top /
  progress affordance, standalone-page vertical dead space, MA desktop
  checkbox-grid column balance, collapsed-accordion FIB type distinction.

## Milestone plan

Ordered highest-value-first. The mojibake fix leads because it is the
broadest-impact, root-cause-confirmed item.

### Human-review summary table

| M | Title | Summary | Needs human approval before execution |
| --- | --- | --- | --- |
| M2 | Mojibake escape fix | Escape full non-ASCII to numeric entities; emit `&#160;`; explicit save encoding; engine no-raw-high-byte test | YES (regeneration follows; broad output change) |
| M3 | FIB repr-to-json hazard | Replace `{normalized_answers!r}` with `json.dumps`; skip if already done by workstream H | NO (narrow, no output regen by itself) |
| M4 | RDKit canvas | Responsive sizing; dark-mode canvas background | NO to author; YES to ship via regen |
| M5 | Dark-mode fragment styling | Inputs, buttons, MATCH table fills; tie to embed_theme_css | NO to author; YES to ship via regen |
| M6 | Result-div typography | Drop monospace/large; spacing; empty seed not `&nbsp;` | NO to author; YES to ship via regen |
| M7 | embed_theme_css flag | Flag plus canonical CSS asset plus vendored site copy | YES at M7-B (site vendor + regen) |
| M8 | Regenerate and verify | Regenerate 278; re-survey vs baseline; diff | YES (explicit regeneration gate) |

### Regeneration gate (explicit)

Anything that regenerates the 278 fragments, or otherwise produces a broad
change to committed engine output, requires human approval before execution.
This covers M2 (the escape change alters 266 files), M7-B (vendoring plus regen),
and all of M8. Engine-source authoring and unit tests in M2-M7 may proceed and
leave a review-ready tree; the actual regeneration write to the 278 files is the
gated step, owned solely by M8-W1. Humans run `git commit` after review.

### Architecture boundaries and mapping

| Milestone | Workstream | Component(s) | Repo |
| --- | --- | --- | --- |
| M2 | M2-W1 escape fix + save encoding + test | html_functions.py, engine_class.py | qti-pkg |
| M3 | M3-W1 FIB repr-to-json | add_FIB.py | qti-pkg |
| M4 | M4-W1 responsive + dark canvas | structure emitters, html_functions.py CSS | qti-pkg |
| M5 | M5-W1 dark-mode inputs/buttons/MATCH fills | html_functions.py CSS, add_MATCH.py | qti-pkg |
| M6 | M6-W1 result-div typography + spacing | html_functions.py (add_result_div) | qti-pkg |
| M7 | M7-A flag + canonical CSS asset | html_functions.py, engine_class.py, write_item.py, qti_selftest_theme.css | qti-pkg |
| M7 | M7-B finalize CSS + vendor into site | qti_selftest_theme.css, site_docs/assets/stylesheets/, mkdocs.yml | bp-website + qti-pkg |
| M8 | M8-W1 pipeline flag wiring + regen 278 | bioproblems_site/*, 278 html | bp-website |
| M8 | M8-W2 re-survey + diff vs baseline | tests/playwright/selftest_visual_survey.mjs | bp-website |

### Milestone detail

M2 -- Mojibake escape fix (HIGHEST VALUE; root-cause confirmed, HIGH confidence).
- M2-W1 (Depends on: none to author; regeneration gated to M8): in
  `html_functions.py` `escape_non_iso_8859_1` (lines 25-31), change the encode
  target so the full non-ASCII range is escaped to numeric entities rather than
  only characters above U+00FF. Encode to ASCII with `xmlcharrefreplace` so
  U+00A0, U+00B1, U+00B7, U+00B0, and the fraction characters become `&#160;`,
  `&#177;`, `&#183;`, and friends, keeping on-disk bytes pure ASCII and
  charset-agnostic. At `html_functions.py:44` emit `&#160;` instead of `&nbsp;`
  in the result-div placeholder so an upstream entity-decode pass cannot turn it
  into a raw non-breaking space. In `engine_class.py` (the `save_package` write,
  around line 37) declare an explicit encoding rather than relying on the
  platform default, so intent is recorded. Add an engine test asserting that
  generated self-test output contains no raw bytes above 0x7F (feed a fragment
  containing a non-breaking space, plus-minus, and middle dot through the
  generator and assert the emitted bytes are pure ASCII). Follow-ons: update qti
  `docs/CHANGELOG.md`, run `source source_me.sh && pytest tests/`.
- Exit criteria: the new test passes; a freshly generated fragment with
  Latin-1-range input bytes contains only ASCII bytes and numeric entities; no
  result string changed; working tree ready for human review. The 278-file
  regeneration that lands this broadly is gated to M8. Parallel-plan ready: yes
  (single self-contained workstream).

M3 -- FIB repr-to-json hazard (the last runtime-error-class emitter hazard).
- NOTE: this may already be done by parallel workstream H. Before editing,
  read `add_FIB.py:22`. If it already uses `json.dumps(normalized_answers)`,
  mark this milestone DONE and skip it. As of this draft (read 2026-06-08) the
  line still reads `f"const fibAnswers_{crc16_text} = {normalized_answers!r};"`,
  so the work is outstanding.
- M3-W1 (Depends on: none): replace the `{normalized_answers!r}` repr with
  `json.dumps(normalized_answers)`, matching the reference-correct pattern in
  `add_MULTI_FIB.py:11`. This prevents a parse-time JS SyntaxError when an answer
  contains a single quote, backslash, or non-ASCII character. Add a focused unit
  test feeding an answer like `it's` through the FIB generator and asserting the
  emitted JS is valid (the array uses JSON quoting, not Python repr). Follow-ons:
  update qti `docs/CHANGELOG.md`, run `pytest tests/`.
- Exit criteria: test passes; emitted FIB JS array is valid for quote/backslash
  answers; result strings unchanged; working tree ready for human review.
  Parallel-plan ready: yes.

M4 -- RDKit canvas (responsive + dark-mode; audit-confirmed broad, critical).
- M4-W1 (Depends on: none to author; ship via M8): make RDKit structure canvases
  responsive with `max-width: 100%; height: auto` so they scale within mobile
  390 viewports instead of clipping with no horizontal scroll. Add a dark-mode
  canvas background treatment so the canvas does not render as a bright white
  rectangle on dark pages (apply the theme background or a wrapper so the canvas
  fill matches the page). Place CSS in the engine theme block (or the canonical
  asset once M7-A lands). Follow-ons: qti `docs/CHANGELOG.md`, `pytest tests/`.
- Exit criteria: harness screenshots (after regen) show no canvas overflow on
  mobile 390 and no bright rectangle in dark mode; no console errors; result
  strings unchanged. Parallel-plan ready: yes (disjoint CSS path).

M5 -- Dark-mode fragment styling (audit-confirmed broad; tie to embed_theme_css).
- M5-W1 (Depends on: M7-A decision for where the CSS lives): bring fragment
  interiors into dark mode -- input fields and Check Answer / Reset buttons
  currently keep default browser light styling, and MATCH answer-table rows show
  light/pastel fills on dark pages. Apply theme-var-based styling so inputs,
  buttons, and MATCH table fills adapt in Material-slate dark. Where the audit
  noted inputs/buttons use default browser styling rather than site classes,
  give them theme-scoped styling in the engine CSS. Tie the location of this CSS
  to the `embed_theme_css` decision (M7): the same rules must be present whether
  embedded or served from the vendored stylesheet. Follow-ons: qti
  `docs/CHANGELOG.md`, `pytest tests/`.
- Exit criteria: harness dark screenshots (after regen) show inputs, buttons,
  and MATCH table fills adapted to dark; light mode unchanged; no console
  errors; result strings unchanged. Parallel-plan ready: yes once M7-A fixes the
  CSS home.

M6 -- Result-div typography (M2-W1/W2 from the prior plan).
- M6-W1 (Depends on: none to author; coordinate the placeholder seed with M2):
  in `html_functions.add_result_div` (lines 34-45) drop `monospace` and
  `font-size: large`, align with Material body font and weight, and replace the
  `&nbsp;` seed with an empty, zero-height-until-filled result element. Preserve
  the `result_<crc>` ID and the exact result text the contract depends on. Note
  the placeholder entity is also addressed in M2 (emit `&#160;`); if this
  milestone removes the seed entirely, coordinate so the two edits agree on the
  final placeholder form. Follow-ons: qti `docs/CHANGELOG.md`, `pytest tests/`.
- Exit criteria: harness screenshots (after regen) show no monospace result
  text, no reserved blank gap before fill; result strings unchanged; no console
  errors. Parallel-plan ready: yes (coordinate the seed with M2-W1).

M7 -- embed_theme_css flag (single source of truth for the theme CSS).
- M7-A (Depends on: human approval of this pass): store the theme CSS in a single
  file `qti_selftest_theme.css` shipped inside the `html_selftest` engine
  package. Have embedded mode read that file and inject its contents into the
  `<style id='qti-selftest-theme'>` block. Add an `embed_theme_css: bool = True`
  flag threaded from `engine_class.py` / `write_item.py` into the wrap step
  (`__init__._wrap_selftest_html`): when `True`, embed the asset; when `False`,
  emit the fragment with no style block. Keep `True` as default so standalone
  fragments stay self-contained. The dark-mode rules from M4 and M5 live in this
  asset. Add a unit test covering both branches (asset present vs absent).
- M7-B (Depends on: M7-A, plus M4/M5/M6 CSS finalized): apply the final CSS
  values into the same `qti_selftest_theme.css`, then vendor a byte-identical
  copy into `site_docs/assets/stylesheets/qti-selftest-theme.css` and register it
  once via `extra_css` in `mkdocs.yml`. Record in bp-website docs that the engine
  asset is the source and the site file is a vendored copy. This is a gated step
  (touches site config and pairs with regen).
- Exit criteria: flag works both ways (M7-A unit test); with the flag off the
  vendored stylesheet renders fragments identically in the harness (light + dark)
  and the site copy is byte-identical to the engine asset (M7-B). qti version
  bump (`pyproject.toml` + `VERSION`, CalVer) and both `docs/CHANGELOG.md` files;
  working tree ready for human review. Parallel-plan ready: M7-A yes; M7-B after
  M7-A and the CSS-producing milestones.

M8 -- Regenerate and verify (EXPLICIT REGENERATION GATE; needs human approval).
- M8-W1 (Depends on: human approval, M2-W1, M4-W1, M5-W1, M6-W1, M7-B): point
  bp-website at the updated qti-package-maker, pass `embed_theme_css=False`
  through the generation pipeline (`bioproblems_site/topic_page.py` /
  `bbq_converter` invocation), and regenerate all 278 `selftest-*.html` via the
  generation pipeline. This is the single owner of the 278-file writes, keeping
  all broad output changes in one lane. Inspect `git diff` (review only; humans
  commit).
- M8-W2 (Depends on: M8-W1): re-run `selftest_visual_survey.mjs` (both modes)
  into `test-results/selftest_survey/after/`; diff against the M0 baseline in
  `test-results/selftest_survey/baseline/`; confirm mojibake gone (no raw
  high bytes, no A-circumflex glyph), RDKit canvases responsive and
  dark-correct, fragment interiors dark-adapted, result typography native,
  zero console errors, result strings unchanged.
- Exit criteria: regenerated fragments form a review-ready tree; after-survey
  clean vs baseline per the coverage table; both `docs/CHANGELOG.md` updated;
  bp-website `pytest tests/` green. Parallel-plan ready: W2 after W1.

## Risks and mitigations

| Risk | Impact | Trigger | Mitigation |
| --- | --- | --- | --- |
| Escape change alters result strings | Breaks completion/sound/confetti | Numeric-entity escape touches result text | Contract guard test (side quest F); assert no result-string change; M8 after-vs-baseline diff |
| Regeneration produces a huge noisy diff | Hard human review | Mojibake fix touches 266 files at once | Gate regen to M8-W1 only; review diff per type; expect uniform entity-substitution changes |
| Dark-mode CSS regresses light mode | Light fragments restyled | Shared theme block edits | Keep light rules intact; harness verifies both light and dark before commit |
| embed_theme_css off but stylesheet not loaded | Unstyled fragments on site | Flag off, vendored CSS missing/late | M7-B registers `extra_css` once; M8 harness verifies light + dark; byte-identical vendored copy |
| Re-attempting the MATCH raw-ID non-bug | Wasted effort, possible regression | Treating audit row as engine defect | Recorded in Non-goals; investigation proved harness artifact; do not touch MATCH scoring/display |
| H already landed the FIB json fix | Duplicate/conflicting edit | M3 starts without checking | M3 reads `add_FIB.py:22` first and skips if already `json.dumps` |

## Verification

- Engine unit tests in qti-package-maker:
  `source source_me.sh && pytest tests/` -- no-raw-high-byte assertion (M2), FIB
  JSON-valid array (M3), `embed_theme_css` both branches (M7-A).
- bp-website fast tests: `pytest tests/` (lint, manifest, naming) stay green.
- Visual end-to-end (primary look check): with the dev server on
  `127.0.0.1:8000`, `node tests/playwright/selftest_visual_survey.mjs` -- compare
  `test-results/selftest_survey/baseline/` vs
  `test-results/selftest_survey/after/` per question type, desktop 1280 and
  mobile 390, light and Material-slate dark; assert zero page console errors.
  Note: the harness MATCH simulation fix (workstream G) must be in place before
  the after-survey so the MATCH after-screenshots show readable text, not the
  CRC token.
- Byte check: a scan over the regenerated `selftest-*.html` finds zero bytes
  above 0x7F (this is the decisive mojibake-fixed signal; the baseline had
  266 of 278 files affected, 7661 `0xC2 0xA0` pairs alone).
- Functional spot-check: a FIB question typed correctly shows `CORRECT`, marks
  the badge complete, and fires sound/confetti; an answer containing a single
  quote does not throw a JS SyntaxError (M3).
- Regeneration check: `git diff --stat` over the regenerated fragments shows the
  expected uniform entity-substitution and CSS changes (inspection only; humans
  commit).

## Open decisions

- Dark-mode RDKit canvas treatment (M4): theme the canvas background to match the
  page versus wrapping the canvas in a themed container. Decide at M4 start from
  the dark screenshots; prefer the simpler page-matching background unless a
  legibility issue appears.
- Whether M5 dark-mode CSS ships embedded (M7-A on) or only via the vendored site
  stylesheet (flag off). Default: author the rules in the canonical asset so both
  paths carry them identically; the site serves the flag-off path.
- M7 packaging remains the recommended answer to the CSS-weight concern (engine
  asset as source of truth, default-on embed flag, vendored byte-identical site
  copy). Confirm at this pass's approval.

## Notes

- MATCH raw-ID is recorded in Non-goals as a TEST-HARNESS artifact, not an engine
  bug, per `match_raw_id_2026-06-08.md`. Workstream G corrects the harness; the
  engine is left unchanged on this axis.
- The M1 FIB f-string and result-color fix already landed (`add_FIB.py:30,33`);
  this pass does not redo it.

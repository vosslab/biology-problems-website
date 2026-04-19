# UI/UX review 2026-04-18 (second pass)

Fresh rendered-site review after the evening's emoji, LibreTexts, and Daily
Puzzles changes. Supersedes the deleted first-pass doc.

## Method

- Server: `mkdocs serve -a 127.0.0.1:8765 --strict` (zero broken-link warnings).
- Driver: [tests/ui_ux_review.mjs](../tests/ui_ux_review.mjs) at 1280x900
  (desktop) and 390x844 (mobile).
- Coverage: 30 URLs x 2 viewports = 60 visits. All non-generated pages
  (home, 5 daily puzzles, 4 tutorials, author, license) plus all 6 subject
  indexes plus a 1-2 topic sample per subject (11 of 42 generated topic
  pages), plus the search-results pseudo-page.
- Output: full-page screenshots in `test-results/ui_ux_review/` and
  `report.json` with per-page metrics (status, H1 count, image alt gaps,
  external `rel=noopener` gaps, table count).
- All 60 visits returned HTTP 200.

## What changed since the deleted first-pass review

- Subject-row LibreTexts `[logo] Chapter U.C` `.lt-link` anchor with brand
  blue `#127bc4`.
- Six subject labels carry emoji icons (biochem/genetics/lab/molbio/
  biostats/other).
- `navigation.sections` removed from theme features so subjects collapse
  again.
- New Daily Puzzles landing page using Material `grid cards` (md_in_html).
- `.lt-icon` scoped to text cap-height.

## Findings

### Major

(After source-code inspection, both initial Major findings turned out to be
false signals from over-broad harness checks; corrected and re-run with
zero remaining warnings. See "Resolved during this pass" below.)

### Resolved during this pass

- **Subject-index LibreTexts icons "missing alt"**: the source emitted
  `alt=""` (decorative) in both `bioproblems_site/subject_index.py:54`
  and `bioproblems_site/topic_page.py:659`, which the harness check
  `!i.getAttribute('alt')` was incorrectly flagging as missing. Two
  changes landed:
  1. Tightened the harness check to `i.getAttribute('alt') === null`
     so empty-string alts (the standard decorative marker) are not
     flagged.
  2. Changed the emitted alt from `""` to `"LibreTexts"` in both files.
     The aria-label sits on the `<a>`, not the `<img>`, so a
     defensive meaningful alt on the image survives any future
     refactor that drops or changes the wrapping anchor's label.
  Re-run: `noAlt=0` on every page; `alt="LibreTexts"` confirmed on 22
  icons across `/biochemistry/` and `/genetics/` after running
  `python3 generate_pages.py --indexes-only`.
- **`rel="noopener"` missing on author/topic external links**: every
  generated `target="_blank"` anchor (subject indexes, topic icon
  anchors, footer/social, image-source links) already carries
  `rel="noopener"` (or `noopener noreferrer`). The flagged links on
  `/author/` and the per-topic markdown text reference are bare same-tab
  links - `rel="noopener"` only matters with `target="_blank"`, so they
  do not need it. Tightened the harness `extNoRel` check to require both
  `target="_blank"` AND missing `rel`. Re-run: `extNoRel=0` on every page.
- **Dark-mode capture (harness)**: previous selector clicked the palette
  toggle but failed to flip the scheme because Material's palette JS
  reads `localStorage` at page load. Replaced with a fresh Playwright
  context using `colorScheme: 'dark'` plus an `addInitScript` that
  pre-seeds `localStorage.__palette = {index:1, scheme:"slate", ...}`
  before the page first paints. Re-run: `home_dark.png` and
  `subject_biochem_dark.png` now render the slate scheme correctly.

### Minor

1. **Per-question download row is dense on mobile, but intentional**
   Pages: any topic with many questions (`/genetics/topic11/` = 12,
   `/biochemistry/topic01/` = 8, `/biostatistics/topic05/` = 8). Each
   question shows a 4-button row (Blackboard Learn TXT, Blackboard
   Ultra QTI, Canvas/ADAPT QTI, Human-Readable TXT) that wraps to a
   2x2 grid at 390-wide. This is the primary action of the page -
   downloading the question into the reader's LMS - so collapsing the
   buttons would hide the point. Logged here only so future polish
   work knows the density is by design. If a tighter row is wanted
   later, options: icon-only buttons with on-tap labels, or a single
   horizontal-scroll row instead of 2x2 wrap. Screenshots:
   `topic_genetics11_mobile.png`, `topic_biochem01_mobile.png`.

2. **Daily Puzzles "Pick a puzzle" card label uses ASCII arrow**
   Page: `/daily_puzzles/`. Each card ends with `-> Play <Name>`. The
   `->` is fine but reads as code rather than UI; Material's `>` glyph
   or `&raquo;` would feel more like a CTA. Low impact, mostly polish.
   Screenshot: `daily_puzzles_index_*.png`.

3. **Search-results pseudo-page renders 11 H1s**
   Page: `/?q=enzyme`. Harness reports `h1count=11`. This is Material's
   search overlay listing matches; not a real page heading collision,
   but a future a11y audit might flag it. No action needed unless we
   add a header check to CI.

### Nit

4. **Mobile drawer footer crowds the social icons row**
   Page: `/author/` and others on mobile. The footer social row
   (GitHub, YouTube, Bluesky, LinkedIn, Facebook, Patreon, PayPal) sits
   tight against the copyright line. Padding is adequate; this is a
   "nice to have" line-height bump. Screenshot: `author_mobile.png`.

5. **`Other` subject rendered as a numbered list with one item**
   Page: `/other/`. The single "Cell Biology" topic appears as
   `1. Cell Biology  1 question`. Numbering a list of one feels
   over-formal; flatten to a single bulleted item until a second topic
   exists. Screenshot: `subject_other_desktop.png`.

## Known good (resolved since prior pass)

- LibreTexts label readability: `[logo] Chapter U.C` brand-blue anchor on
  hover-background reads as a clickable reference, no longer the bare
  logo image.
- Six subject labels have emoji icons; left rail no longer mixes
  unbranded plain text with FontAwesome utility rows.
- Daily Puzzles section has a real landing page with grid cards and a
  "How it works" explainer.
- Subject groups collapse again in the left rail (no more long
  always-expanded ladder).
- LibreTexts icon scoped to cap-height; no longer renders at natural
  pixel size next to body text.
- Home page Subjects vs Additional Topics split is intentional:
  Biochemistry and Genetics carry complete coverage; the other four
  subjects are partial and grouped under "Additional Topics" on purpose
  to set reader expectations. (Worth revisiting later: a small subtitle
  or one-line note on the home page would make this distinction
  legible to new readers - a previous attempt was deemed unnecessary
  but the reasoning could resurface.)
- All three tutorial pages (`bbq_tutorial`, `bbq_ultra_tutorial`,
  `canvas_tutorial`) ship with full alt text on every screenshot
  (35+18+21 imgs, 0 missing).
- `mkdocs build --strict` exits 0; zero broken subject-to-topic links.

## Harness drift

- Removed dead `biotechnology_orphan` row (orphan was deleted on
  2026-04-18).
- Expanded coverage from 17 to 30 URLs: added all daily puzzles, all
  tutorials, a 2nd topic per subject, search-results pseudo-page.
- Dark-mode capture (`home_dark.png`, `subject_biochem_dark.png`) is
  still firing the wrong selector; both PNGs render the light theme.
  Material's palette toggle uses two `<label>` elements (one hidden per
  scheme); the current selector clicks one but the click does not flip
  the scheme. Suggest replacing with
  `await page.evaluate(() => document.querySelector('[data-md-color-scheme]').setAttribute('data-md-color-scheme', 'slate'))`
  or driving the actual `<input>` checked state.

## Suggested follow-up plan

All three originally-approved fixes turned into harness-tightening (see
"Resolved during this pass"). No outstanding source changes from this
review. Future revisits to consider:

- A subtitle/one-liner on the home page explaining that Subjects =
  complete coverage and Additional Topics = partial coverage. Previously
  attempted and removed; legibility for new readers may justify a second
  try.

### Crucial finding for future agents

When the harness flags `imgsNoAlt` or `extNoRel`, **inspect the source
HTML before "fixing" the page generator**. In this pass:

- Every existing `target="_blank"` link in generated HTML already carries
  `rel="noopener"` (or `noopener noreferrer`).
- Every generated decorative `<img>` already carries `alt=""`.

The harness was over-broad: `!i.getAttribute('alt')` treated `alt=""` as
missing, and `extNoRel` flagged any external link regardless of `target`.
Both checks are now correct. If a future regression appears, the
generator code in `bioproblems_site/subject_index.py` and
`bioproblems_site/topic_page.py` is the right place to look, but verify
with `curl http://127.0.0.1:8765/<page>/ | grep '<a'` first.

## Artifacts

- Report: `test-results/ui_ux_review/report.json` (60 rows)
- Screenshots: `test-results/ui_ux_review/*.png` (60 PNGs + 2 dark-mode)
- Driver: [tests/ui_ux_review.mjs](../tests/ui_ux_review.mjs)

# UI/UX review 2026-04-18

Review of the rendered mkdocs site for `biology-problems-website`.
Driver: [devel/ui_ux_review.mjs](../devel/ui_ux_review.mjs). Screenshots:
`test-results/ui_ux_review/` (gitignored). Server: `mkdocs serve -a
127.0.0.1:8765`. Viewports: desktop 1280x900, mobile 390x844. Chromium via
Playwright 1.59.

Severity tags: `[blocker]` breaks primary task, `[major]` significant friction,
`[minor]` polish, `[nit]` cosmetic.

## Executive summary (top 5)

1. `[blocker]` **Broken subject-to-topic links.** Every subject index links to
   topic pages that do not exist. `mkdocs serve` emits 29 WARNINGs on build; in
   the browser, clicks on 25+ topic numbers 404. Examples:
   biochemistry/topic15, 17, 18, 19, 21; biostatistics/topic01-04, 07;
   all 7 biotechnology topics; laboratory/topic05-10, 12, 13;
   molecular_biology/topic01-03, 06, 10; other/topic02. Owning file:
   each `site_docs/<subject>/index.md`.
2. `[blocker]` **`biotechnology/` subject is orphaned.** The landing page
   renders at `/biotechnology/` and is reachable via broken-link guessing, but
   it is absent from `mkdocs.yml` nav and from the home page subject list. All
   of its topic links are 404. Either add it to nav + write its topic pages
   or remove the subject entirely.
3. `[major]` **LibreTexts chapter links stand out like a sore thumb.** The
   inline `(LibreTexts Unit X, Chapter Y [icon])` string repeats up to ~20
   times per subject index in small gray italic. The word "LibreTexts" is
   repeated on every row, it competes visually with the topic titles, and
   the styling is inconsistent (topics 1-14 on biochemistry have it,
   15-21 do not). Recommended fix: replace the text label with a compact
   LibreTexts favicon/logo link (e.g., 16px icon with
   `aria-label="LibreTexts Unit 1, Chapter 1"` for screen readers) rendered
   to the right of the topic title; drop the word "LibreTexts" from the
   visible label entirely. Secondary option: keep the text but pin it to a
   distinct color token (e.g., LibreTexts brand blue `#127bc4`) so it reads
   as "external reference" rather than muted afterthought. Owning files:
   `site_docs/assets/stylesheets/custom.css` for the styling,
   `site_docs/<subject>/index.md` and/or `generate_topic_pages.py` for the
   link template.
4. `[major]` **No question-count signal.** The site has no UI indicator of how
   many questions a topic contains. Combined with the 404 issue, users cannot
   tell the difference between "topic page missing" and "topic exists but has
   zero questions" until they click. Reintroducing a generated
   `topics_metadata.yml` (or equivalent single source) that records question
   counts would let `generate_topic_pages.py` suppress links to empty topics
   and surface counts as chips (e.g., `12 questions`).
5. `[major]` **Target=\_blank without `rel="noopener"`.** Author page has 8
   external links with `target="_blank"` and no `rel="noopener"`; biochemistry
   topic01, genetics topic01, daily_puzzles/peptidyle, and license each have
   1. Exposes the site to tabnabbing and leaks the opener window.

## What works well

- Material theme, green palette, and emoji subject icons give strong
  personality and clear subject identity.
- Image alt text is present on every image observed (35 tutorial screenshots,
  author photo, research collage) -- good accessibility baseline.
- Mobile navigation collapses cleanly into the hamburger drawer; content
  reflows without horizontal overflow on all pages reviewed.
- Download buttons (Blackboard Learn TXT, Blackboard Ultra QTI, Canvas QTI,
  Human-Readable TXT) are colored, iconic, and scannable -- a real strength
  of the topic pages. See [test-results/ui_ux_review/topic_lab01_desktop.png].
- Peptidyle daily puzzle has a clear "Next puzzle in HH:MM" cue and a
  collapsible help section that keeps the default view uncluttered.
- Home page scannable: subjects bulleted with one-sentence purpose each
  (light and dark palette both render with adequate contrast).

## Per-area findings

### Site chrome (header, nav, footer)

- `[minor]` Nav icons in `mkdocs.yml` mix FontAwesome markup (`<i class='fa
  ...'>`) and emoji (`🧪 Biochemistry`). The emoji render at a different
  baseline than FontAwesome glyphs and the mix is visually uneven. Pick one
  style. Owning file: `mkdocs.yml` lines 72-90.
- `[nit]` Footer `"Licensed under CC BY-SA 4.0"` is followed by three small
  gray Creative Commons icons on a dark green background; contrast is
  borderline. Owning file: `site_docs/assets/stylesheets/custom.css` or
  `mkdocs.yml` extra.

### Home page

- `[minor]` The "Additional Topics" section lists three subjects (Molecular
  Biology, Biostatistics, Laboratory) that are also listed under "Subjects"
  above. The split is confusing -- reads like Biochemistry and Genetics are
  primary while the rest are afterthoughts. Either merge into one "Subjects"
  list or relabel with clear criteria.
- `[nit]` Bullet phrase "a good general biology inheritance genetics course"
  under Genetics reads awkwardly.

### Subject landing pages (the pages that changed most recently)

- `[blocker]` Broken topic links (see summary item 1).
- `[major]` LibreTexts links (see summary item 3). Preferred: replace the
  repeated `(LibreTexts Unit X, Chapter Y)` text with a 16px LibreTexts
  logo icon, so the reference is a single glance-recognizable glyph and
  the word "LibreTexts" stops appearing 20 times per scroll.
- `[minor]` Topics with no external chapter should still have a
  consistent visible signal (e.g., badge `OER` or deliberately-empty slot)
  so readers know the absence is intentional, not a render bug.
- `[minor]` Topic numbering is sparse (biochemistry jumps 14 -> 15 -> 16 -> 17
  with 15/17/18/19/21 broken). Either hide missing numbers or renumber
  sequentially after the metadata cleanup.
- `[minor]` Subject index is the only entry to topic pages now that nav was
  collapsed (per CHANGELOG 2026-04-13). This is fine, but the index page
  would benefit from a sticky jump-to-topic TOC on the right rail (Material
  theme supports `toc.integrate`) -- 20+ topics is long scrolling.

### Topic pages (e.g., biochemistry/topic01, laboratory/topic01)

- `[major]` On mobile, each problem variant renders as a 4-button row
  (Blackboard Learn, Ultra QTI, Canvas QTI, Human-Readable TXT). Four
  buttons wrap to two lines per variant; with ~10 variants the page
  becomes a vertical wall of green buttons. Consider a single "Downloads"
  dropdown/button per variant on narrow viewports. Owning file: the
  generated topic page template in `generate_topic_pages.py`.
- `[minor]` Example-problem collapsibles use blue left-border admonitions
  identical to the daily-puzzle help admonition; users may not realize
  they are clickable. The `>` chevron helps but is small. Bumping the
  chevron or adding a hint like "click to expand" would help.
- `[minor]` Anchors for each variant heading are useful but the heading
  text duplicates the example-problem title below (e.g., `Chemical Bond
  Types and Characteristics` twice). Consider collapsing into one heading
  + download row + example.

### Daily puzzles (Peptidyle)

- `[major]` The guess area shows two empty white rectangles above "Next
  puzzle in HH:MM" with no visible cue that they accept input. A user
  who has not expanded "How to solve" may assume the game is broken.
  Add a placeholder like "type your first guess" or show an input
  cursor/keyboard hint.
- `[minor]` The two action buttons ("Peptide solving tips" and "I need
  help: show first letter (-1 guess)") compete for attention; the green
  one looks like the primary action but is a help lever. Swap visual
  weight so "Peptide solving tips" is primary or distinct.

### Tutorials

- Good. 35-image tutorial has alt text; headings scale well.
- `[nit]` On mobile, some Blackboard screenshots shrink to ~300px width
  and small UI labels become unreadable. A click-to-enlarge lightbox
  (Material `glightbox` plugin) would help.

### Author page

- `[major]` 8 external links open in new tab without `rel="noopener"` --
  fix with a global markdown extension or edit `site_docs/author.md` to
  add `{target=_blank rel=noopener}` via `attr_list`.
- `[nit]` "Support This Project" section lists Bitcoin + Cash App + 3 other
  methods without a short explanation of where funds go.

### License page

- Good. Plain-text license is long; a short plain-English preamble at the
  top (1-2 sentences) would help.

### Accessibility quick pass

- Headings: every page sampled has exactly one `<h1>` in article content.
- Color contrast: green accents on white pass visual gut-check AA for large
  text; the `0.8em` italic gray LibreTexts text is smaller than 16px and
  the gray-on-white contrast is borderline. Bump to body gray or add
  underline.
- Focus ring: Material theme provides it by default; not inspected in
  detail.
- `[minor]` No `aria-label` on the FontAwesome icons in nav entries
  (`<i class='fa fa-home'></i> Home`) -- screen readers read the text
  label but the icon adds noise.

### Performance smell

- Tutorial page loads 35 PNG screenshots inline with no lazy loading. On
  a slow connection this is ~1-5 MB. `attr_list` with `{loading=lazy}` on
  each image, or a `mkdocs-material` image plugin, would help.

## Suggested owners (by file)

| Issue area | Likely owning file |
| --- | --- |
| Broken topic links / empty topics | `generate_topic_pages.py` + per-subject `site_docs/<subject>/index.md` + (proposed) reintroduced `topics_metadata.yml` |
| Orphan biotechnology subject | `mkdocs.yml` nav + `site_docs/biotechnology/index.md` |
| LibreTexts link styling | `site_docs/assets/stylesheets/custom.css` |
| Mobile download-button wall | topic-page template in `generate_topic_pages.py` |
| `rel="noopener"` missing | `site_docs/author.md`, per-topic generator, mkdocs `markdown_extensions` |
| Home "Additional Topics" split | `site_docs/index.md` |
| Nav icon inconsistency | `mkdocs.yml` lines 72-90 |
| Lazy-load tutorial images | `site_docs/tutorials/*.md` |

## Recommendation on `topics_metadata.yml`

Bringing back a single source of truth for topic metadata is the right call.
It solves three issues at once: (a) lets the generator suppress links to
empty topics, (b) surfaces question-count chips, (c) re-enables LibreTexts
link uniformity without manually re-typing URLs in each subject index. The
CHANGELOG 2026-04-13 decision to move metadata into each subject's `index.md`
was motivated by "markdown was pleasant to edit" -- that benefit can be
preserved by authoring the markdown descriptions in `index.md` while
question counts and LibreTexts URLs live in a small generated YAML derived
from repo scans (problems per topic). This keeps the rich prose in markdown
and the machine-checkable facts in YAML.

## Verification

- `mkdocs serve` started cleanly at 127.0.0.1:8765 on 2026-04-18 (warnings
  above are content issues, not server failures).
- 32 page visits recorded in
  `test-results/ui_ux_review/report.json`; every target URL returned HTTP
  200 at both viewports.
- 33 screenshots saved under `test-results/ui_ux_review/` (desktop +
  mobile per page, plus home_dark.png and subject_biochem_dark.png).
- Every finding above cites an owning file and carries a severity tag.

## Artifacts

- `test-results/ui_ux_review/*.png` -- per-page screenshots (gitignored).
- `test-results/ui_ux_review/report.json` -- machine-readable metrics
  (status, H1 count, image count, missing-alt count, tables, external
  links missing rel=noopener).
- [devel/ui_ux_review.mjs](../devel/ui_ux_review.mjs) -- driver script;
  re-run with `node devel/ui_ux_review.mjs` while `mkdocs serve` is up.

# Human guidance

<!-- VENDORED HEADER: START -->
Record the durable guidance Neil Voss states, or approves for preservation here, in his own words:
first person or close paraphrase, one to three lines per bullet. Material he supplies as a source
may inform [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) once it is settled, and an entry of uncertain
origin belongs there too. Rules: [REPO_STYLE.md](REPO_STYLE.md).
[PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

## Decision priority

## Review expectations

- Curate problem-set titles for instructors browsing the corpus and considering whether
  to use the material in their courses.
- Question-type badges should be visually distinct from download buttons, using rectangular
  labels with colored side bars like the user-role badges. Use the existing colorwheel
  system for comparable badge saturation and lightness. Give MC, WOMC, TFMS, and
  Matching clearly distinct colors, reasonably separate from the download buttons.
- Put the type badge at the start of each download row for vertical scanning, with
  each badge only as wide as its label.
  Keep headings descriptive and place badges before linked titles in the All Questions index.
  Have the Python site build write badge markup; use CSS only for its visual layout.
- Identify the response type from each BBQ file's first record. Treat `FIB_PLUS` as the
  distinct `MULTI_FIB` type, and distinguish regular MC, WOMC, and TFMS banks.

## Working style

- I normally use Graphify update or fresh, sometimes context, and now the published map. Keep this
  command line to those recurring actions, with Ollama available when my Claude usage is maxed out.
- Let one Graphify run update or rebuild the data and publish `docs/GRAPHIFY.md` with its compact
  community SVG. Never put the full per-symbol export under `docs/`.
- Let Markdown link checks include newly created, nonignored untracked files for their first 24
  hours. Keep ignored files unavailable.

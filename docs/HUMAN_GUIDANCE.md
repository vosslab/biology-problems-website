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
- Make question-type badges visually distinct from download buttons: rectangular
  labels with colored side bars, using the existing colorwheel. Give MC, WOMC,
  TFMS, and Matching distinct colors.
- Put a label-width type badge at the start of each download row and before linked
  titles in the All Questions index. Keep headings descriptive. Have the Python
  site build write badge markup; use CSS only for layout.
- Identify the response type from each BBQ file's first record. Treat `FIB_PLUS` as the
  distinct `MULTI_FIB` type, and distinguish regular MC, WOMC, and TFMS banks.

## Working style

- Use the Codex backend by default for `build_site.py` title generation.
- I normally use Graphify update or fresh, sometimes context, and now the published map. Keep this
  command line to those recurring actions, with Ollama available when my Claude usage is maxed out.
- Let one Graphify run update or rebuild the data and publish `docs/GRAPHIFY.md` with its compact
  community SVG. Never put the full per-symbol export under `docs/`.
- Let Markdown link checks include newly created, nonignored untracked files for their first 24
  hours. Keep ignored files unavailable.

# Human guidance

<!-- VENDORED HEADER: START -->
Record the durable guidance Neil Voss states, or approves for preservation here, in his own words:
first person or close paraphrase, one to three lines per bullet. Material he supplies as a source
may inform [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) once it is settled, and an entry of uncertain
origin belongs there too. Rules: [REPO_STYLE.md](REPO_STYLE.md).
[PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

## Decision priority

- I want students to drop in, answer a few questions, and come back tomorrow.
  This is a self-test website, not an LMS.
- The questions are the main attraction. Progress and streaks are just
  encouragement to keep practicing.
- The BBQ filename is the unique identifier for a problem set. Track completion
  by filename, not by the CRC of a randomly generated question.
- Fix the design, not the symptom. Prefer durable fixes over quick patches
  when the durable fix is justified.
- For small banks, show question 1, then 2, then 3. Random selection is not
  needed when the site tracks what it has already shown.

## Review expectations

- Make Check Answer Roosevelt University green. Use compact button heights close to the
  completion badge and download links, give Show another question a dark fill with white text,
  and reduce MC/MA answer padding.
- Keep button spacing compact: enough separation to prevent touching, with only a little
  padding. Too much space is worse than too little.
- Feature Biochemistry and Genetics as complete courses developed with grant support. Use
  subjects for course areas and topics for chapters; label the other collections Additional
  Subjects. Make the homepage eye-catching while using space efficiently.
- Track question sets, not individual generated questions: generated quantity is arbitrary.
- Use emoji consistently for sidebar icons rather than mixing emoji and Font Awesome.
- Put Latest additions and Recently updated in separate links at the bottom of the sidebar,
  rather than nesting them under Collection activity.
- Reuse preselected subject emojis from MkDocs navigation on course cards instead of
  choosing a separate Font Awesome icon set.
- Use the course identities recorded in `~/nsh/syllabus/docs/COURSE_COLORS.md`:
  Biochemistry purple, Genetics blue, Biostatistics dark lime, and Biotechnology brick red.
- Extend that palette with magenta for Molecular Biology and teal green for Laboratory.
  Use Halloween/jack-o'-lantern orange for Other.
- In dark mode, use course-tinted card backgrounds with neutral descriptive text.
- Activity previews must lead to full Latest additions and Recently updated pages, then to
  the relevant collection's preview/download controls. Keep unknown history undated.
- Let task_files define the website inventory and query the source commands in biology-problems
  for history. Renaming generated website files must not erase the question history. An older
  source newly included on the website belongs under New to the site.

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

- Keep screenshot capture commands in `devel/`, with one executable
  `capture_screenshots.sh` to update the complete documentation corpus.
- Use WebP instead of PNG for documentation screenshots to save space.
- Use the Codex backend by default for `build_site.py` title generation.
- I normally use Graphify update or fresh, sometimes context, and now the published map. Keep this
  command line to those recurring actions, with Ollama available when my Claude usage is maxed out.
- Let one Graphify run update or rebuild the data and publish `docs/GRAPHIFY.md` with its compact
  community SVG. Never put the full per-symbol export under `docs/`.
- Let Markdown link checks include newly created, nonignored untracked files for their first 24
  hours. Keep ignored files unavailable.

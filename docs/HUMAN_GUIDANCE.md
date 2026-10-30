# Human guidance

<!-- VENDORED HEADER: START -->
Record the durable guidance Neil Voss states, or approves for preservation here, in his own words:
first person or close paraphrase, one to three lines per bullet. Material he supplies as a source
may inform [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) once it is settled, and an entry of uncertain
origin belongs there too. Rules: [REPO_STYLE.md](REPO_STYLE.md).
[PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

## Decision priority

- Classify question banks by filename; generated instances change. Run JEV in generation and
  indexing, using readable Python-generated questions and authored question YAML where appropriate.
- Keep `problem_set_bloom.yml` as one filename and one compact `Cognitive, Knowledge` value per
  entry, like the title map. Store experimental metadata in untracked files.
- Use an exploratory first pass and refinement to investigate coverage and classification quality;
  do not create a manual review queue for the corpus.

- Keep Bloom classification simple: do not maintain specialized visual conversion repairs for
  this secondary feature. Retain findings and document incomplete visual evidence.
- Apply KISS aggressively; add mechanisms and tests only for demonstrated needs.

- Use QPM for project-owned names. Reserve QTI for the interoperability standard and its
  format-specific identifiers. Do not retain project-owned compatibility aliases.
- Configure project-owned paths with explicit command-line arguments rather than custom
  environment variables.

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

- Give Show practice question and Show another question slightly different colors so the
  changed action is visible. Give Show another question a thin border that the initial
  button does not visibly have, while keeping the approved compact styling.
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

- Curate problem-set titles for instructors choosing questions for their classes. An instructor
  familiar with the chapter should recognize the specific problem set from its title.
- The website primarily serves instructors choosing question banks for their classes. Student
  self-testing and practice games are secondary uses.
- Add complexity when it provides a concrete benefit to the people using or maintaining the site;
  do not minimize implementation cost as an end in itself.
- Make question-type badges visually distinct from download buttons: rectangular
  labels with colored side bars, using the existing colorwheel. Give MC, WOMC,
  TFMS, and Matching distinct colors.
- Use three compact rows per bank: title; downloads; type, bank Bloom labels, completion and
  practice controls. Call the download Human-Readable and omit redundant practice hints/status.
  Keep type badges before linked titles in All Questions. Python owns badge markup; CSS owns layout.
- Identify the response type from each BBQ file's first record. Treat `FIB_PLUS` as the
  distinct `MULTI_FIB` type, and distinguish regular MC, WOMC, and TFMS banks.
- Have YORDER create both native ordering and Sequence MC banks, including the 16S workflow.
  Use "Selection of the Correct Sorting Sequence Multiple Choice" as the Sequence MC tooltip.
- On topic pages, keep breadcrumbs, the title, topic summary, and LibreTexts reference; remove
  chapter-top self-test progress and Bloom scales, reduce excess space, and number problem headings.
  Keep all per-bank downloads, labels, controls, questions, and grading intact. Apply the layout to
  every topic page; Topic 07 is an internal trial, not the stopping point.

## Multiple-answer question design

- Use MA when multiple correct answers arise naturally from one biological or mathematical
  problem. Students select multiple valid outcomes or properties of that problem, rather than
  independently judging several unrelated claims.
- Restriction fragment sizes: identify all fragments produced by one restriction digest.
- ABO blood types: identify all possible offspring or maternal blood types.
- Gene mapping: identify all recombinant or parental genotypes.
- Metabolic pathways: identify all supplements that rescue a mutant.
- Monosaccharide classification: identify all classifications that apply to one structure.
- Avoid MA banks that bundle independent true/false statements, even when each statement is
  scientifically valid. Assess those concepts separately rather than as an all-or-nothing
  combination that can deny credit for partial understanding.
- The combined dice chi-square MA bank is a poor fit: the separate dice banks already assess
  expected counts, degrees of freedom, chi-square calculations, and statistical significance.

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

- Task CSVs must never contain `-x` or `--max-questions`; reject them with an error.
  Set question limits on the build command, defaulting to 50 for every scope.
- This codebase is pre-production with no users. Prefer stronger foundational schemas, contracts,
  abstractions, and ownership boundaries over legacy compatibility when that improves the design.

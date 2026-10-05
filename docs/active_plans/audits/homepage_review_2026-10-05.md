# Homepage and activity review: 2026-10-05

## Outcome

The homepage now leads instructors to filtered question discovery, distinguishes
the two complete grant-supported courses from additional subjects, and shows a
real pedigree preview. Current inventory contains 476 question-set placements across
seven subjects and 57 topics. Cross-listed sets count in each subject. Individual
generated questions are no longer tracked: that quantity is an arbitrary build setting.

The activity workflow now includes dedicated Latest additions and Recently updated
pages. Homepage previews link through View all to complete dated family lists, then
directly to the relevant collection's preview/download controls. Latest additions
currently lists 20 dated families; the homepage shows five. Updated history remains
empty in the published artifacts until successful regeneration establishes provenance.

## Landing-page rubric

Adapted from the readme-docs rubric for an instructor-facing website. These are
editorial judgments, not automated acceptance thresholds. First success means
finding, previewing, and downloading a usable bank rather than installing software.

| Reader outcome | Before | After | Evidence and remaining improvement |
| --- | ---: | ---: | --- |
| Purpose, audience, value | 11/15 | 15/15 | Instructor audience and preview/download workflow lead the page. |
| Distinctive identity | 4/15 | 11/15 | Course accents, compact cards, and biology proof replace a list; a future second example could show another subject. |
| Proof and demonstration | 5/20 | 15/20 | Actual pedigree image links to its working self-test; no direct interactive question on the homepage. |
| Meaningful first success | 8/15 | 15/15 | Keyboard CTA, filtered search, question preview, and ZIP download verified together. |
| Conceptual orientation | 5/10 | 8/10 | Subjects, topics, sets, and grouped activity families distinguished; update history is intentionally incomplete for legacy banks. |
| Navigation | 8/10 | 10/10 | Featured courses, additional subjects, full activity pages, puzzles, and import guides have verified routes. |
| Adoption context | 4/5 | 5/5 | Free/open resources, author, license, complete-course status, and LMS import guides are explicit. |
| Presentation and currency | 5/10 | 8/10 | Responsive light/dark layout and build-derived counts; recent updates will populate as banks are regenerated with provenance. |
| Total | 50/100 | 87/100 | Stronger proof and a verified first-success path; no arbitrary score gate. |

## Verification

- Real subject/topic-scoped index-only build refreshed the global homepage and both
  full activity pages without regenerating banks. Normal builds use the same finalization.
- MkDocs rendered successfully. Desktop and phone layouts were inspected in light
  and dark themes; a 320-pixel viewport had no horizontal overflow.
- Every homepage link returned successfully, including the pedigree anchor.
  Keyboard activation opened Question Finder; searching for pedigrees reached
  the preview, and the download returned a ZIP archive.
- Relevant text color pairs passed WCAG AA contrast. Decorative accents and
  borders were not subjected to text contrast requirements.
- Course cards and chart labels/bars now follow `~/nsh/syllabus/docs/COURSE_COLORS.md`:
  Biochemistry purple, Genetics blue, Biostatistics dark lime, and Biotechnology brick red.
  Documented dark accents are reused; Biochemistry uses a locally reviewed `#d6a0eb`
  companion because the syllabus has none recorded. Unassigned subjects use site green.
  Both themes were rendered and inspected; course text contrast against its actual card
  and chart surfaces is at least 5.16:1. Color is supplementary to visible subject names.
- A real upstream generator produced two questions in a disposable directory.
  Its provenance retained the July 12 content revision through the October rename.
- Verified the complete Latest additions path: homepage View all, full page, exact
  bank anchor, expanded example, and valid ZIP download. All 20 listed anchors resolved.
- Verified Recently updated's deployed empty state and its Question Finder route.
  A separate temporary preview used real regeneration provenance to exercise the
  populated homepage preview, View all page, exact bank anchor, example, and ZIP download.
  No fixture dates or generated banks were added to published content.
- The Python suite passed 5,886 tests. Its default whitespace fixer touched three
  unrelated existing banks; those edits were restored. Focused temporary history
  checks and documentation-link checks passed, as did explicit linting of new modules.
- Follow-up verification passed 368 focused tests covering the build, history,
  documentation links, and source hygiene. Four new permanent tests protect set counts,
  rename lineage, provenance, and complete dated family lists without duplicate formats.
  Browser and integration checks were temporary.

Screenshots are local review artifacts under `test-results/homepage/` and
`test-results/activity/`, not tracked
site content. The actual pedigree image is tracked and can be recaptured with the
helper documented in [USAGE.md](../../USAGE.md).
Course-color captures are under `test-results/course-colors/`; no permanent color-value
tests were added.

The hero was subsequently reduced to about 215 pixels tall at a 1280-pixel desktop
viewport, with shorter copy and smaller padding/type. Light mode uses a pale green
surface and dark text; dark mode uses deep green and light text. Desktop and phone
captures are under `test-results/hero/`. Both themes were inspected, the keyboard
search action worked, and phones had no horizontal overflow. Relevant hero text
contrast remains at least 4.85:1. These were temporary presentation checks.

Course cards now read their subject emojis from the existing MkDocs navigation labels,
including the fly for Genetics and DNA for Molecular Biology. The separate Font Awesome
subject mapping was removed. Browser inspection confirmed all six card emojis render;
the capture is `test-results/subject-emoji.png`. Homepage and navigation checks passed.

Dark course cards now use course-tinted surfaces and borders with neutral descriptive
text. Molecular Biology extends the palette with magenta (`#a62178` light accent,
`#ee99ce` dark accent); Laboratory uses teal green (`#14756e`, `#7bd5cb`). These
identities also appear in the subject chart. Light/dark captures are
`test-results/light-card-tints.png` and `test-results/dark-card-tints.png`.
Relevant new text/background combinations were checked; no permanent color tests were added.

## Known limits

Legacy banks have no verified generation provenance, so Recently updated starts
empty. Two macromolecule inputs currently share one output filename; that bank is
counted once but its history remains unresolved until generation records its input.
Git rename detection is heuristic, and missing origins remain unknown. No historical
growth chart is inferred from today's inventory. Remote publication was not performed.

# Problem title abbreviations

Use these canonical abbreviations for question-format labels in
[problem_set_titles.yml](../problem_set_titles.yml) and newly generated titles.

For audience, wording, specificity, examples, and editorial review, follow
[PROBLEM_TITLE_STYLE.md](PROBLEM_TITLE_STYLE.md).

The cache stores plain titles with final format labels. Generated topic pages place the
type badge first in the download row; the All Questions index places it before each
linked title. The headings themselves contain only descriptive text. Both pages use
[problem_set_display.py](../bioproblems_site/problem_set_display.py). Other qualifiers
remain in the title. Each badge has its full format name as an abbreviation tooltip.
The rendered badge uses the response-type token at the start of that generated BBQ file;
the filename distinguishes MC subtypes. Colors support scanning in light and dark themes,
while the text labels identify formats independently of color.

| Abbreviation | Meaning |
| --- | --- |
| Matching | Matching questions; BBQ record type `MAT` |
| FiB | Fill in the Blank |
| MULTI_FIB | Multiple Fill in the Blanks; badge reads `Multi-FiB` |
| MC | Multiple Choice |
| WOMC | Which One Multiple Choice, drawn from matching content |
| TFMS | True/False Multiple-Choice Statements; badge reads `T/F Statements (MC)` |
| MA | Multiple Answer |
| NUM | Numeric |
| ORD | Ordering |

- Preserve the capitalization shown above, including `FiB`.
- Use format labels in parentheses, such as `Dipeptide Sequences from Structures (FiB)`
  and `Dipeptide Sequences from Structures (MC)`.
- Put the descriptive title first and the question type last in every cached title.
- Check the response format against the BBQ records: `MA`, `NUM`, and `ORD` use those
  labels; `MAT` displays as `Matching`; `FIB` displays as `FiB`; `FIB_PLUS` maps to
  the distinct `MULTI_FIB` type and displays as `Multi-FiB`.
- `MC` records use the filename to identify their subtype: `bbq-WOMC-` uses `WOMC`,
  `bbq-TFMS-` uses `TFMS`, and other MC filenames use `MC`.
- A shared cache title may use `MC/NUM` when the same generator filename produces
  different formats in different topic files. Each generated file is labeled with its
  actual response type, so its topic heading and catalog entry show one badge.
- Read the BBQ record type before the first tab on the first line (`MC`, `NUM`, `MAT`,
  `MA`, `FIB`, `FIB_PLUS`, or `ORD`). `WOMC` filenames identify which-one MC banks.
- `TFMS` identifies the generator family. Some TFMS stems ask students to identify
  examples or sequences; describe that assessed task in the base title.
- Keep paired titles parallel and retain qualifiers such as difficulty and choice counts.
- Write the matching format as `Matching`, such as `Amino Acid Properties (Matching)`
  alongside `Amino Acid Properties (WOMC)`.
- These spellings apply to display titles; filename identifiers keep their existing spelling.
- Badges are static metadata at a consistent starting edge, separate from title links
  and download actions. They use compact rectangles with pale fills, subtle outlines,
  and colored bars on both sides. They have no hover or pressed states.

### Badge colors

The fixed CSS colors come from the existing QTI package maker CAM16 color wheel.
Nine hues start at 22.5 degrees and advance by 40 degrees, with color variation
disabled. Light mode pairs `xdark` text with `xlight` fill; dark mode pairs
`light` text with `xdark` fill. The hue order is MC, Matching, NUM, MA, FiB,
MULTI_FIB, ORD, WOMC, TFMS. This gives the common MC, WOMC, TFMS, and Matching
badges distinct red, violet, magenta, and warm-brown colors. The generated
values are fixed in CSS so site builds do not depend on the colorwheel package.

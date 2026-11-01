# Genetics topic09 content selection

The chapter uses [genetics_topic09.csv](../task_files/genetics_topic09.csv), discovered by
the normal build. Its tasks moved out of [genetics_tasks2.csv](../task_files/genetics_tasks2.csv)
so this chapter can be reviewed and rebuilt independently.

## Deletion mapping

Publish four representative banks across four tiers instead of every label, gene-count, evidence,
and answer-format combination. The tier reflects the full task, including hints and response format.

| Tier | Genes | Labels | Evidence | Response | Support |
| --- | --- | --- | --- | --- | --- |
| Easy | 4 | Random letters | Deletion list | MC | First-gene hint |
| Medium | 5 or 6, mixed | Dictionary word | Deletion table | FiB | Word hint; no first-gene hint |
| Hard | 8 | Random letters | Deletion table | MC | No first-gene hint |
| Bonus | 12 | Random letters | Deletion list | FiB | No first-gene hint |

Titles use the shared base `Gene Order from Deletion Mutants`, with tier, gene count, labels,
evidence, hints, and response format in parentheses. `Deletion List` means uncovered-gene lists;
`Deletion Table` means the plus/minus experimental results, whose legend explains complementation.

The word and random-letter generators still accept both MC and FiB, gene-list or complementation
evidence, and custom gene counts. These alternatives remain available through the generators;
the catalog does not need to repeat every combination. Gene counts above six use the random-letter
generator so dictionary availability does not constrain the puzzle.
Larger maps scroll within their own panels on narrow screens, preserving readable gene labels.
The current word selector uses 25 five-letter words and 19 six-letter words. The word generator's
`--medium` randomly selects five or six genes per question and combines both sizes in one bank,
with no separate size-mixing option. It keeps the existing unique-letter/anagram filter;
eligible words require at least four
other dictionary anagrams. Deletion intervals and presentation also vary between questions.

## Other chapter content

- Keep the four distinct cytogenetic tasks: aneuploidy interpretation, band proximity,
  clinical-description-to-notation, and rearrangement notation. The file named
  `cytogenetic_notation-sub-band_notation.py` actually repeats aneuploidy interpretation;
  remove its misleading catalog entry without deleting the generator.
- Keep both Chromosomal Translocation Outcomes banks. Text and Chromosome Diagrams offer
  different representations of the same orientation problem; titles identify the difference.
- Keep balanced-translocation segregation and Robertsonian gametes: they assess meiotic
  products rather than fragment orientation.
- Keep both polyploid banks: gamete chromosome counts and the distinction between monoploid
  and haploid numbers. Website tasks select their scenarios randomly.
- Keep the existing Matching/WOMC pairs and the three visual chromosome-alteration formats.
  Their registrations and assessment behavior are preserved.
  The visual formats use full alteration names with consistent text colors and gene-order
  descriptions that identify centromeres and breaks.

## Missing question bank

The four-sex sparrow question belongs in this chapter as an application of chromosome
inversions. It appears in the past exams, including questions 62-63 of
`2025_genetics_final.md`, but has no generator or question bank in the current repository.
Its two original tasks ask for offspring stripe probability and the joint probability of
sex and stripe phenotype after a white-stripe male mates with a tan-stripe female.
Adding this content requires a new bank; it is not an existing task that can simply be moved.

## Rebuild and verification

From the website repository:

```bash
source source_me.sh && python3 build_site.py -S genetics -T topic09 --cli
source source_me.sh && python3 -m mkdocs build
```

Question limits belong to the build command; the default remains 50 per bank. Use `-x` on
`build_site.py` for a smaller local sample, rather than putting limits in task rows.
Use `-r` when every selected bank needs fresh randomized questions.

Task ownership, sample answer checks, and desktop/mobile render inspection are one-time audit
evidence. They do not create permanent snapshot, bank-count, or variant-matrix tests.

The initial 2026-11-01 audit rebuilt the selected banks and catalogs, producing 21 distinct question
sets. Eight deletion samples agreed with their diagrams and had unique orders up to reversal;
three monoploid/haploid keys were checked independently. Desktop and mobile previews were
inspected, including scrolling to the last gene, and the 8- and 12-gene FiB answers graded
correctly in the browser. Focused generator, site, and Markdown checks and the MkDocs build
passed. The existing Matching/WOMC banks were preserved. Full-suite and live LMS checks
were not run.

The earlier tier revision rebuilt the fixed 4-, 6-, 8-, and 12-gene banks. Two samples
per bank agreed with their maps and deletion evidence, and one question from each tier graded
correctly in BPW. Mobile previews of all four tiers and desktop previews of the two table
formats were inspected. Focused checks and the MkDocs build passed; these checks remain
one-time verification, with no new permanent tests.

Medium now uses one mixed five-/six-gene bank. A sample of each size agreed with its map,
experimental results, and answer key; both graded correctly in BPW at mobile width.
A focused generator test protects per-question size selection and matching evidence/key lengths.

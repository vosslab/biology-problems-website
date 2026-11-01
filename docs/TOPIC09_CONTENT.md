# Genetics topic09 content selection

The chapter uses [genetics_topic09.csv](../task_files/genetics_topic09.csv), discovered by
the normal build. Its tasks moved out of [genetics_tasks2.csv](../task_files/genetics_tasks2.csv)
so this chapter can be reviewed and rebuilt independently.

## Deletion mapping

Publish four representative banks instead of every label, gene-count, evidence, and answer-format
combination. The tier reflects the full task, including hints and response format.

| Tier | Genes | Labels | Evidence | Response | Support |
| --- | --- | --- | --- | --- | --- |
| Easy | 4 | Dictionary word | Uncovered-gene lists | MC | First-gene and word hints |
| Medium | 6 | Random letters | Uncovered-gene lists | MC | No first-gene hint |
| Hard | 8 | Random letters | Uncovered-gene lists | FiB | No first-gene hint |
| Bonus | 12 | Random letters | Complementation table | FiB | No first-gene hint |

The word and random-letter generators still accept both MC and FiB, gene-list or complementation
evidence, and custom gene counts. These alternatives remain available through the generators;
the catalog does not need to repeat every combination. Gene counts above six use the random-letter
generator so dictionary availability does not constrain the puzzle.
Larger maps scroll within their own panels on narrow screens, preserving readable gene labels.

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
- Keep the existing Matching/WOMC pairs and the three visual chromosome-notation formats.
  Their registrations and assessment behavior are preserved.

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

The 2026-11-01 audit rebuilt the selected banks and catalogs, producing 21 distinct question
sets. Eight deletion samples agreed with their diagrams and had unique orders up to reversal;
three monoploid/haploid keys were checked independently. Desktop and mobile previews were
inspected, including scrolling to the last gene, and the 8- and 12-gene FiB answers graded
correctly in the browser. Focused generator, site, and Markdown checks and the MkDocs build
passed. The existing Matching/WOMC banks were preserved. Full-suite and live LMS checks
were not run.

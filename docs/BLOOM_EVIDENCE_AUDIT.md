# Bloom evidence fidelity audit

## Main finding

HTML-to-text conversion erased essential question data in pedigrees, phylogenetic trees,
molecular canvases, box plots, and DNA fingerprint gels. A plausible Bloom label did not establish
that JEV had received the complete question. Some affected banks already received Analyze.

Prioritizing the largest compression percentages found additional defects beyond the initially
suspected pedigree diagrams. The experiment kept rubric version 2 and model `jev-1.14.0` unchanged.
It reclassified 78 filenames whose submitted evidence changes: 10 pairs change, while 68 remain
unchanged. Analyze increases from 30 to 32 banks. All 12 pedigree banks remain Understand /
Conceptual despite restoring their family relationships. Their original evidence was inadequate,
but this experiment does not establish that evidence loss caused those particular labels.

## Maintenance decision

The specialized visual parsers and their tests were removed after this experiment. Their limited
practical benefit did not justify ongoing maintenance for an approximate discovery feature. The
backend again uses simple HTML text extraction, table separators and image alternatives; the
small fix preserving decimal answer fields remains. Visual relationships may be missing from
future classification evidence. The reassessed filename labels and audit findings are retained.
This decision does not establish that the original labels were correct. Explicit future refreshes
use the simpler evidence and may produce different labels.

## Measurement definitions

The pre-repair census covers 414 unique filenames and 19,143 nonblank question records from the
same source placements selected by the classifier. Repeated website placements are not extra banks.
Every archived example was matched against its original record before the conversion changed.

- Original length: Unicode characters in a complete BBQ record, including HTML/CSS/scripts,
  response fields, answer keys/statuses, and tabs; excluding its trailing newline.
- Readable length: the same fields after the original converter, joined by tabs. JSON escaping,
  rubric text, and request metadata are excluded.
- Bank average: the arithmetic mean across that bank's records. Distributions and correlations
  give each filename equal weight, not each question or course placement.
- Compression percentage: `100 * (1 - readable_mean / original_mean)`. This ranks identically
  to original/readable ratio. A large percentage measures removed characters, not lost meaning.
- Actual submitted sample: five spread-out generated records, or one generated record alongside
  authored YAML. The 168 YAML-backed banks were primarily classified from authored YAML, so their
  generated-record length is not the length of their principal classification evidence.

The measurements below describe the original evidence and pre-repair labels. Their frozen
per-bank data remain available separately from the repaired evidence and current classifications.

## Length distributions before repair

Each entry is the median of bank averages, followed by the middle 50% in parentheses.
Characters cover complete question records, including response fields.

| Cognitive process | Banks | Original characters | Readable characters | Median retained |
| --- | ---: | ---: | ---: | ---: |
| Remember | 159 | 711 (517-1,030) | 395 (275-514) | 52.2% |
| Understand | 57 | 1,289 (484-7,420) | 289 (219-521) | 40.8% |
| Apply | 164 | 3,057 (1,210-10,051) | 740 (481-1,319) | 25.7% |
| Analyze | 30 | 8,486 (6,275-40,638) | 1,796 (1,070-3,850) | 11.9% |
| Evaluate | 4 | 3,605 (1,852-5,787) | 1,195 (993-1,464) | 38.5% |
| Create | 0 | No observations | No observations | No observations |

The actual submitted examples give similar readable medians: Remember 394, Understand 328,
Apply 738, Analyze 1,800, and Evaluate 1,186. The differences reflect sampling, particularly the
single generated example accompanying authored YAML. Evaluate has only four banks, and no
comparison involving observed Create questions is possible.

Across banks, readable averages range from 106 to 865 characters for Remember, 148 to 2,001 for
Understand, 172 to 3,277 for Apply, 345 to 5,144 for Analyze, and 899 to 1,759 for Evaluate.
There is overlap; length is not a category boundary.

## Correlations and confounding

Spearman rank correlation uses Remember through Create as ordered labels, without assuming equal
educational distances. Kendall tau-b provides a check that accounts for tied labels.

| Comparison | All 414 banks: Spearman | Kendall tau-b | Generated-only 246: Spearman |
| --- | ---: | ---: | ---: |
| Cognitive level vs original average | 0.625 | 0.475 | 0.267 |
| Cognitive level vs readable average | 0.563 | 0.431 | 0.543 |
| Cognitive level vs fraction retained | -0.481 | -0.360 | -0.023 |
| Cognitive level vs actual submitted readable average | 0.564 | 0.433 | 0.538 |

The apparent relationship between higher labels and more shortening largely disappears within
Python-generated banks. Source type is a major confounder: 146 of 168 YAML-backed banks received
Remember, while all 30 Analyze banks were Python-generated. Within YAML-backed banks, original
and readable length correlations are -0.048 and -0.139. Prompt-only readable length has a stronger
pooled correlation (0.762), illustrating sensitivity to what is counted.

These are descriptive associations in this corpus, not evidence that longer questions require
higher-level thinking. Related generator families are not independent observations. Existing
labels were assigned from the potentially incomplete representations being investigated; grouping
by them cannot reveal the true levels of questions whose evidence was lost. No accuracy estimate,
significance claim, or causal effect is inferred from these correlations.

## Highest compression first

The first 20 ranked filenames comprise all 12 pedigree banks, four box-plot banks, two hard DNA
fingerprint banks, and two genetic-code translation banks. The full ranking is retained locally.

| Ranked example or family | Original/readable ratio | Finding |
| --- | ---: | --- |
| Bonus autosomal pedigree | 231.9x (99.57% removed) | Sex, affected status, generations, and family links disappeared. |
| Pattern-to-pedigree, easy | 193.6x (99.48% removed) | Visually distinct answer pedigrees collapsed to separators. |
| Other pedigree banks | 31.0-172.0x | Same missing relationship data across all 12 banks. |
| Four box-plot banks | 38.6-51.7x | Quartiles, whiskers, median and mean positions vanished; choices retained axis labels only. |
| Hard crime-scene and paternity gels | 35.7x and 34.7x | Lane labels remained, but no bands were represented. |
| Two translation banks | About 31.5x | mRNA remained readable; merged codon/amino-acid associations were flattened. |

The wider targeted comparison also found tree branch lines missing, molecular structure fields
empty after removing drawing scripts, and pipette digits losing their decimal-place color cue.
By contrast, ordinary enzyme data tables and the examined linear/branched metabolic pathways kept
their values, metabolite labels, and arrow relationships. Compression alone cannot distinguish these.

## Repairs and reassessment

Experimental parsers read the known BPQ renderers before general text conversion:

- Pedigrees: anonymous person IDs, visible sex/status, parent-child families, displayed labels,
  and double partner lines. It does not import hidden genotypes or infer an inheritance answer.
- Trees: rooted nested descendant groups, taxon labels, and horizontal drawing coordinates.
  Coordinates are explicitly not asserted to be evolutionary distances.
- Molecular canvases: literal isomeric SMILES, preserving connectivity, charges and stereochemistry.
  Embedded JavaScript is parsed as data, never executed by the classifier.
- Box plots: plotted quartiles, median, mean and whisker endpoints calibrated to the shown axis.
- Horizontal DNA gels: lane names and aligned band positions, without calculating the matching lane.
- Genetic-code tables: all 64 displayed codon associations, respecting merged cells.
- Pipettes: red digits are explicitly identified in the text.

The converter also stops stripping numeric-looking prefixes. The former CRC-decoration regex
altered answer or tolerance fields in all 135 submitted examples from 27 unique NUM banks.
For example, `2300.00000000` became `0000`. The original question banks were never altered by this
bug; it affected classification evidence only. One additional MC bank also changes when this
stripping is removed.

Restoring meaning does not necessarily increase character count. For the same bank populations,
the median readable bank-average lengths change as follows:

| Family | Banks | Before | After |
| --- | ---: | ---: | ---: |
| Pedigrees | 12 | 213 | 2,310 |
| Trees | 9 | 3,112 | 2,916 |
| Box plots | 4 | 521 | 1,119 |
| DNA fingerprints | 6 | 1,614 | 1,439 |
| Genetic-code translation | 2 | 1,650 | 1,366 |

Tree and gel descriptions become shorter while restoring relationships: the old conversion
emitted many meaningless empty-cell separators. Compression is a useful inspection priority,
but increasing the retained percentage would be the wrong repair target.

All 78 affected banks were rerun with the same model, rubric, and example indices. Changes include:

- Easy and hard crime-scene gel banks: Apply to Analyze.
- Two tree-choice levels exchange Analyze/Apply assignments.
- Amino-acid identification from a structure: Remember to Understand in the fill-in version.
- Several molecular/gel banks change only their knowledge dimension.
- Pedigrees, box plots, numerical banks, and translation banks retain their cognitive labels.

One before/after call per bank cannot separate representation effects from ordinary model
variability. No label change is treated as a proven correction, and unchanged labels do not establish
that the original evidence was adequate. SMILES and textual relationships also change presentation:
they preserve underlying data but may not reproduce the effort of reading the original drawing.

## Historical experiment verification and limits

The initial audit captured 32 side-by-side browser comparisons, including the 20 largest
compression cases and additional representative visual banks. Molecular canvases were checked
for actual rendering. The pedigree reader additionally passed 80 independent round trips through
the BPQ source renderer, including both drawing orientations, with exact visible observations and
family links compared against the source model. The experimental tests covered numeric values, molecule
connectivity, pedigree relationships, tree branches, gel bands and plot coordinates.
All 19,143 question records converted successfully across the 414 banks; 398 focused
classification, typing, lint and documentation-link checks passed. The index-only build regenerates
57 topic pages and the Finder catalog from the reassessed compact map. Original BBQ banks remain
unchanged. These checks establish conversion and integration behavior, not educational accuracy.

The removed experimental implementation was a targeted fidelity repair, not a universal HTML
diagram interpreter. Fischer/Haworth
projections and colored protein-ladder diagrams were also unresolved in that experiment. The
restored simple pipeline again has the broader visual omissions described above. No specialized
parser maintenance or generator changes are required for this secondary feature. These evidence
limits should not be mistaken for failures of the Bloom rubric.

## Local experiment artifacts

Ignored `LOCAL_ONLY/visual_evidence_audit/` contains `compression_ranking.csv` (all 414 banks),
`bank_lengths.csv`, `length_statistics.json`, PNG/SVG distribution plots, exact archived requests,
HTML/screenshot comparisons, before/after evidence, and the pre-repair classification snapshot.
`bank_lengths_after.csv` records the repaired conversion separately. Exact live requests and
probabilities remain in ignored `LOCAL_ONLY/bloom_runs/` and `LOCAL_ONLY/bloom_metadata.json`.

Only the compact filename-to-pair map remains authoritative for the site. See
[BLOOM_COVERAGE.md](BLOOM_COVERAGE.md) for current coverage and
[BLOOM_FINDINGS.md](BLOOM_FINDINGS.md) for the earlier rubric experiment.

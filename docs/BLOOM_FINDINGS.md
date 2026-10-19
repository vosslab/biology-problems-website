# Bloom classification findings

## Instructor discovery

The exploratory run classified 414 unique filenames, appearing at 485 catalog placements.
The original refined-rubric run occupies 14 of the 24 cells. Its largest groups are Apply /
Procedural (119 banks) and Remember / Factual (102). No bank received Create or Metacognitive.
These are observed assignments, not proof that those educational tasks are absent.

The subsequent [BLOOM_EVIDENCE_AUDIT.md](BLOOM_EVIDENCE_AUDIT.md) experimentally restored missing visual
evidence, rerunning 78 affected banks without changing the rubric. Ten pairs change; Analyze rises
from 30 to 32. All 12 pedigree banks remain Understand / Conceptual after relationship data are
restored. Specialized parsers were subsequently removed to avoid maintenance overhead; the
reassessed labels remain cached and simple extraction may omit visual evidence. The historical rubric comparisons below remain separate from that evidence experiment.

[BLOOM_COVERAGE.md](BLOOM_COVERAGE.md) contains the complete matrices by subject and question type.
[bloom_catalog.csv](bloom_catalog.csv) lists the filenames behind the counts. Question Finder
supports both dimensions together and sorts cognitive labels in taxonomy order.

The later [BLOOM_EXTERNAL_VALIDATION.md](BLOOM_EXTERNAL_VALIDATION.md) records a blinded ISU
reference check and independent bank assessments. Agreement is limited; a small reasoning-first
candidate improves some cases but loses another. Keep version 2 without automatic upward ties.

## What refinement changed

The first pass used the source-grounded definitions in rubric version 1. A bounded examination of
representative bank prompts and 20 diagnostic biology examples identified three useful changes:

| Observation | Rubric refinement | Concrete result |
| --- | --- | --- |
| Familiar true/false propositions were sometimes treated as evaluation. | Require criteria-based judgment beyond recognizing a textbook statement. | Enzyme-equilibrium TFMS moved from Evaluate / Conceptual to Remember / Conceptual. |
| Method knowledge was confused with either isolated facts or any act of reasoning. | Distinguish knowledge of a method from reasoning about a biological model. | PCR-primer TFMS moved from Evaluate / Factual to Remember / Procedural. |
| Matching associations and categorizing new examples were not consistently distinguished. | Separate retrieval of taught associations from interpreting a new example. | Many Understand assignments moved to Remember; matching format alone determines neither label. |

The second corpus pass changed 108 pairs. The largest changes were Understand / Conceptual to
Remember / Conceptual (35), Understand / Factual to Remember / Factual (24), and Apply / Procedural
to Apply / Conceptual (10). These movements are sensitivity to a rubric revision, not counts of
proven corrected errors. Both passes used the same pinned JEV model, one bank per request, with
two Choice judgments. The credential-free request archives retain the actual evidence and criteria.

## Small diagnostic checks

The examples in [bloom_examples.yml](bloom_examples.yml) are agent-authored, source-grounded
working judgments. Their expected labels and rationales were written before the first requests.
They are not independently validated labels or a representative accuracy test. Development used
their mismatches; the table-interpretation case was moved into development after the first run.
Cases still marked held out were not used to write the revised boundaries. No expected label was
changed to agree with JEV. Expected labels and rationales were withheld from API requests.

| Check | First rubric | Refined rubric |
| --- | --- | --- |
| Cognitive labels agreeing with 20 provisional references | 20/20 | 20/20 |
| Knowledge labels agreeing with those references | 16/20 | 20/20 |
| Complete pairs agreeing with those references | 16/20 | 20/20 |
| Real-bank pairs unchanged in the evidence/presentation stress check | 16/25 | 23/25 |

The same 25 filenames were used for both stress checks: ten reproducibly sampled banks plus
targeted ambiguous or initially rare assignments. Python evidence increased from five to ten
spread-out examples and changed presentation order. YAML retained its authored content with a
different mapping order. This combined check cannot isolate sampling effects, presentation effects,
or model variability, and its targeted selection cannot estimate corpus-wide stability.

The reference examples include Create, Evaluate, and Metacognitive tasks, which JEV successfully
distinguished. This supports using the rubric for discovery without requiring the corpus to occupy
every category. Reference agreement and repeatability still do not establish educational accuracy.

## Remaining limitations

- Proofreading TFMS changed between Remember / Conceptual and Remember / Factual in the refined
  stress check. The bank mixes general principles and specific properties.
- Protein-versus-DNA gel WOMC changed between Understand / Factual and Understand / Conceptual.
  The boundary depends on whether particular properties or relationships are treated as dominant.
- Choosing a statistical test from a mixed bank of descriptions and scenarios can straddle
  Understand and Apply. Authored alternatives can demand different operations.
- The Hardy-Weinberg chi-square bank received Evaluate / Procedural. Its supplied test statistic
  and critical-value decision can also support Apply / Procedural if understood as executing a
  taught decision rule. This is a candidate for future boundary refinement, not a settled gold label.
- Five generated instances are a starting evidence sample, not a guarantee of capturing every
  task a bank can generate. Instructional history and missing visual meaning also limit inference.

Use these labels as approximate discovery aids. Further refinements should address a demonstrated
boundary issue and compare both category movements and representative question content. There is
no manual review queue, corpus-wide approval gate, or claim of measured corpus accuracy.

## Reproducing the exploration

Run `source source_me.sh` before the commands documented in
[BLOOM_TAXONOMY_GUIDE.md](BLOOM_TAXONOMY_GUIDE.md).

- `python3 -m devel.classify_bloom --action report` regenerates the coverage report from current labels.
- `python3 -m devel.evaluate_bloom` reruns the small live diagnostic without replacing bank labels.
- `python3 -m devel.classify_bloom --action refresh` explicitly replaces corpus labels with the current
  rubric; `--filenames` limits that operation to selected banks.
- `python3 build_site.py --indexes-only --cli` publishes the current map into local site sources.

Persistent labels live only in [../problem_set_bloom.yml](../problem_set_bloom.yml), one compact
value per filename. Baseline pairs, probabilities, model/rubric provenance, evaluation output, and
exact API request evidence remain in ignored `LOCAL_ONLY/` files. Those local experiment files are
not distributed with a checkout. The report preserves this run's aggregate findings.

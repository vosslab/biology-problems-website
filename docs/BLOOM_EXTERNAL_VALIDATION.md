# Bloom external reference check

## Decision

This small investigation evaluates the existing version 2 rubric without changing it or replacing
cached bank labels. Results support approximate instructor discovery, but do not establish reliable
classification across all 24 cells or consistent Apply/Analyze boundaries. Keep the rubric for
that limited use; do not describe these labels as validated educational measurements.

## Source and suitability

The [Iowa State CELT page](https://celt.iastate.edu/prepare-and-teach/design-your-course/blooms-taxonomy/)
links the official [Revised Blooms Handout PDF](https://iastate.app.box.com/s/z0otio95lflaii1l2ro3h42kp8q6fdmm).
Its third page contains 24 objectives, one per cognitive-process/knowledge combination. Rex Heer,
Iowa State CELT, created the model from Anderson and Krathwohl's 2001 revised taxonomy. The
[Oregon State mirror](https://ctl.oregonstate.edu/sites/ctl.oregonstate.edu/files/a_taxonomy_for_learning_teaching_and_assessing.pdf)
corroborates the example text and attribution; the current ISU-linked PDF is the source authority.
The two PDFs differ in revision/layout, so they are not claimed to be byte-identical.

An independent agent transcribed the cell positions and texts, and the manager inspected the grid.
The extracted reference has 24 unique pairs. All objectives were applicable as a taxonomy diagnostic;
none was discarded based on JEV's answer. These are intended learning outcomes, not exam questions
with response options, answer keys, instructional history, or student performance evidence.
Agreement with their labels is therefore reference agreement, not BPW classification accuracy.

## Small blinded experiment

On 2026-10-19, submit each objective unchanged in a `learning_objective` field, one API request per
objective. Use production rubric version 2 and `jev-1.14.0`, including the existing biology-bank
context. The request contains neither the reference pair nor its label-bearing archive ID. No
examples from this source are added to the rubric. Record exact requests and responses locally.

Separately, select six currently Apply/Analyze banks with the smallest absolute difference between
those two archived probabilities. Add the alphabetically first available chi-square and enzyme
banks as controls. This is a deliberately difficult sample, not a prevalence estimate. Two agents
independently assess the same frozen evidence before seeing stored labels, JEV outputs, or each
other's answers. A fresh agent then examines their disagreements with JEV.

## External reference results

| Comparison | Agreement |
| --- | ---: |
| Cognitive process | 18/24 (75.0%) |
| Knowledge dimension | 17/24 (70.8%) |
| Complete pair | 14/24 (58.3%) |
| Factual row: complete pair | 2/6 |
| Conceptual row: complete pair | 2/6 |
| Procedural row: complete pair | 5/6 |
| Metacognitive row: complete pair | 5/6 |

The ten disagreements are listed below. Topic descriptions are shortened identifiers, not
substitutes for the exact objective texts retained in the local reference artifact.

| Objective topic | ISU pair | JEV pair |
| --- | --- | --- |
| FAQ responses | Apply / Factual | Understand / Factual |
| Activity-list completeness | Analyze / Factual | Understand / Factual |
| Consistency across sources | Evaluate / Factual | Evaluate / Procedural |
| Daily activity log | Create / Factual | Create / Procedural |
| Exhaustion symptoms | Remember / Conceptual | Remember / Factual |
| Advice for novices | Apply / Conceptual | Create / Metacognitive |
| Cultural categories | Analyze / Conceptual | Understand / Conceptual |
| Expert team | Create / Conceptual | Create / Procedural |
| Regulatory compliance | Analyze / Procedural | Apply / Conceptual |
| Personal culture-shock response | Understand / Metacognitive | Apply / Conceptual |

## Disagreement assessment

Two fresh agents independently examined all ten ISU disagreements after the source extraction.
Both recommend retaining the production criteria. Most discrepancies involve sparse objectives:
recognizing symptoms can target details or a syndrome, and checking sources can target facts or
a method. They identified the novice-advice result as the clearest likely model overreach:
metacognition is not established merely by giving advice. Neither agent found a demonstrated
missing definition that justified adding a new rubric rule.

The agents differed on further calls: one recommended an objective-context check, while the other
considered additional responses unlikely to resolve missing context. The manager limited this to
four post-hoc calls. Replace only the biology-bank/full-credit and prompt/answer-key framing with
objective wording; retain all category definitions. FAQ responses moved to the ISU pair; novice
advice remained Create but changed from Metacognitive to Procedural; culture-shock prediction
remained Apply / Conceptual; the pH-testing control remained Apply / Procedural. This is not a new
validation score. Single responses cannot separate wording effects from ordinary model variability,
and objective framing alone did not resolve the disagreements.

A separate fresh bank adjudicator distinguished likely model misapplication from ambiguity.
Parental-class identification is a plausible overclassification: selecting the largest classes
is a familiar method. DNA melting comparisons and inverse epistasis remain sensitive to whether
the course teaches a routine rule or requires reconstruction of relationships. Missing tree/gel
information prevents evaluating those labels. These are provisional explanations, not proven
causes or new gold labels.

## Biology bank comparison

Both independent agents chose the same preferred pair for all eight banks. JEV matched three pairs;
among the six banks with usable textual evidence, it matched three. Agent agreement is not ground
truth: both assessors share a model family and may share misconceptions. Their alternatives and
reasoning are preserved separately. Tree and gel judgments are conditional on the intended task,
not confident judgments of complete submitted questions.

| Bank task | Both agents | Fresh JEV result | Interpretation |
| --- | --- | --- | --- |
| X-linked parental inference | Analyze / Conceptual | Analyze / Conceptual | Relationships among sex, offspring and inheritance. |
| DNA melting comparison | Understand / Conceptual | Apply / Conceptual | Interpretation versus executing a counting rule. |
| Tree from distance matrix | Analyze / Conceptual | Apply / Procedural | Tree topology missing from answer evidence. |
| Parental three-point classes | Apply / Procedural | Analyze / Procedural | Routine largest-count rule versus relational analysis. |
| Crime-scene DNA gel | Analyze / Procedural | Apply / Procedural | Bands missing; neither pair is validated by this input. |
| Inverse epistasis ratios | Apply / Conceptual | Analyze / Conceptual | Familiar class regrouping versus reconstructing relationships. |
| Chi-square calculation | Apply / Procedural | Apply / Procedural | Computing the statistic earns credit; optional reflection does not. |
| Replication enzyme matching | Remember / Factual | Remember / Factual | Retrieval of familiar enzyme/function associations. |

## Improving without automatic promotion

The user proposed investigating borderline promotion. The observed directions do not support a
uniform upward correction. Relative to ISU, cognitive labels were lower in four cases, equal in
18 and higher in two. Relative to the independent bank assessments, the six original usable banks
had zero lower, three equal and three higher labels. Remember/Understand prevalence alone is not
evidence of downward bias.

A single candidate adds required-operation and nearest-alternative comparisons to the existing
context, emphasizing that incidental intermediate steps do not automatically raise the level.
Category definitions stay unchanged. It explicitly rejects corpus-balancing and automatic upward
ties. Freeze that candidate before fresh assessments or outputs; do not tune it again in this run.
The ISU examples are not reused to claim independent validation of the candidate.

Two new agents independently assessed six fresh text/table banks, blind to labels and candidate
wording. They agreed on all six pairs. These cases were held out of this candidate's wording
selection, not certified independent of all earlier project experiments or model training.
The hand-selected cases cover recall, calculation, interpreting data and judging a flawed method.
Run baseline and candidate once each, counterbalancing request order. No production files change.

| Comparison with agent pairs | Baseline | Candidate |
| --- | ---: | ---: |
| Original six usable development banks | 3/6 | 4/6 |
| Six fresh banks | 4/6 | 5/6 |
| Fresh cognitive labels: lower / equal / higher | 1 / 4 / 1 | 1 / 5 / 0 |

The candidate resolves the parental-class and inverse-epistasis development disagreements but
moves X-linked inference from Analyze to Apply, losing an agreement. On fresh banks, it changes
wild-type identification in a growth table from Analyze to Understand, matching both agents: the
actual question identifies the row with growth everywhere, not the pathway order. Both versions
remain Understand for inhibition identification from enzyme data, while both agents prefer
Analyze / Conceptual. The operation, rather than the generator topic, is the useful distinction.

Using cognitive ranks only as descriptive category steps, mean absolute distance falls from 0.50
to 0.33 in development and from 0.67 to 0.33 in the fresh set. These ranks are not equal educational
intervals. Small gains from one response per condition cannot establish a causal improvement or
robustness; the candidate also loses a defensible Analyze assignment. Do not pool development
results into an independent validation score.

**Final decision:** keep version 2 and cached labels. Do not add an upward tie-breaker, adopt this
candidate, or reclassify the corpus. The candidate is promising but has not earned added production
complexity. Retain its exact wording and contrasts as local evidence for any future justified
revision. The practical improvement is a clearer diagnosis of where current labels are approximate,
not making the distribution look balanced. No further tuning or human review is required for this
investigation.

## Reproduction and limits

Ignored `LOCAL_ONLY/bloom_validation/` contains the source PDFs, rendered grid, `isu_reference.json`,
`protocol.json`, rubric snapshot/hash, bank selection and evidence, independent assessments, exact
credential-free JSONL requests/responses, and comparisons. The one-off runner uses the existing
production client and never saves to the classification map. From the repository root:

```bash
source source_me.sh
PYTHONPATH=. python3 LOCAL_ONLY/bloom_validation/run_validation.py isu
PYTHONPATH=. python3 LOCAL_ONLY/bloom_validation/run_validation.py banks
```

The runner resumes its archived IDs; use a copy with empty request archives for a fresh replication.
Archived payloads are the exact reproducible inputs. Live model outputs need not be identical.
The optional context and candidate experiments are recorded in `objective_context_requests.jsonl`
and `candidate_requests.jsonl`; their one-off scripts sit alongside the main runner. Frozen
`candidate_context.txt` and `fresh_bank_evidence.json` support replay of the follow-up comparison.
These local scripts and metadata remain untracked; no permanent validation framework is introduced.

The investigation made 56 calls: 24 original objectives, eight initial banks, four context probes,
eight candidate development banks and 12 paired fresh-bank calls. Each condition has one response
per case; this is not a repeatability or accuracy study. Public examples may have been
in model training data despite labels being withheld in these requests. The reference is balanced
by construction while BPW is not. The bank sample overrepresents ambiguity, and two visual cases
have incomplete evidence. Neither set supports a corpus-wide error rate. The experiment does not
measure whether instructors actually find questions faster or whether students learn more.

The specialized visual converters and their tests remain removed. Simple extraction, the decimal
answer-field fix, existing classifications, and the historical
[BLOOM_EVIDENCE_AUDIT.md](BLOOM_EVIDENCE_AUDIT.md) remain. No new conversion code, review queue,
API workflow, classifier abstraction, or persistent experimental metadata is required.

# Bloom taxonomy guide

BPW uses revised Bloom labels to help instructors discover and sort question banks. Each exact
BBQ filename receives an estimated dominant cognitive process and knowledge type. Randomized
instances inherit that pair. Labels describe assessed tasks, not difficulty or teaching quality.

## Classification criteria

The source framework is Anderson and Krathwohl's *A Taxonomy for Learning, Teaching, and
Assessing* (2001), particularly chapters 4-6. The
[Iowa State model](https://celt.iastate.edu/prepare-and-teach/design-your-course/blooms-taxonomy/)
summarizes its knowledge subtypes and 19 cognitive subprocesses. The
[model PDF](https://ctl.oregonstate.edu/sites/ctl.oregonstate.edu/files/a_taxonomy_for_learning_teaching_and_assessing.pdf)
provides examples of learning objectives, not mandatory question templates.

| Cognitive process | Required performance |
| --- | --- |
| Remember | Recognize or recall taught information. |
| Understand | Interpret, exemplify, classify, summarize, infer, compare, or explain meaning. |
| Apply | Execute a familiar procedure or implement/select/adapt one for an unfamiliar situation. |
| Analyze | Differentiate relevant parts, organize relationships, or attribute underlying structure. |
| Evaluate | Check or critique against criteria or standards. |
| Create | Generate, plan, or produce a coherent new solution or product. |

| Knowledge type | Assessed knowledge |
| --- | --- |
| Factual | Terminology and specific details or elements. |
| Conceptual | Categories, principles, generalizations, theories, models, and systems. |
| Procedural | Subject-specific skills, algorithms, techniques, methods, and selection criteria. |
| Metacognitive | General learning strategies, cognitive tasks and their conditions, and self-knowledge. |

These are two classification dimensions, not a promise of statistical independence or uniform
coverage. A biology assessment study found associations between the dimensions and found that
prompt verbs alone did not determine cognitive categories.
[Larsen et al., 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9727608/).

## Decide from the task

1. Read the prompt, response format, answer key, and representative authored alternatives.
2. Identify the mental operation necessary for full credit.
3. Identify the knowledge acted upon, independently of the operation.
4. Check the nearest alternative category and state why it fits less well.
5. Summarize the dominant bank task; do not select the hardest possible variant.

Assume an undergraduate prepared in the relevant subject, without assuming memorization of these
exact items. Unknown instructional history makes some pairs approximate. A bank mixing genuinely
different tasks can be poorly summarized by one pair; record that limitation in the findings.

## Easily confused categories

- Recognizing taught terminology or a definition can be Remember even in a matching exercise.
  Classifying a new example using defining features can be Understand.
- Apply includes unfamiliar implementations and adapted procedures. Novelty alone does not imply
  Analyze. Analysis requires separating/organizing relationships.
- Inferring an explanation can be Understand; judging whether evidence warrants a conclusion
  against standards can be Evaluate. A word such as "best" does not settle the distinction.
  Selecting a true or false textbook statement can be Remember or Understand; truth selection
  alone does not establish Evaluate.
- Selecting an existing experimental design does not itself constitute Create. Producing a design
  or plan can.
- A question mentioning a laboratory method may assess terminology, a causal principle, or a
  procedure. Identify what knowledge earns credit rather than classifying the topic.
- Metacognitive knowledge concerns cognition itself, including general strategies. Thinking hard,
  checking a biological calculation, or solving a complex problem does not automatically assess it.
- Conceptual knowledge can be recalled; procedural knowledge can be remembered or understood.
  Neither knowledge type forces a particular cognitive process.
- Numerical responses and multiple-choice responses can require the same reasoning. Compare the
  actual task and available cues before treating two formats as equivalent.

## Backend workflow

The executable criteria live in
[../bioproblems_site/bloom_rubric.py](../bioproblems_site/bloom_rubric.py).
Normal generation and index-only builds classify missing filenames. Existing labels persist,
including manual edits. Both fields must form a complete valid pair.

- Python banks supply five complete, evenly spread readable generated records by default,
  including response fields and answer keys. This is a starting evidence sample, not a taxonomy rule.
- Authored YAML banks supply semantic YAML content with presentation substitutions removed, plus
  one generated example to identify the actual output format. Supporting YAML data used by a Python
  generator does not turn it into a YAML question bank.
- Simple HTML extraction retains text, table row/cell separators and image alternatives, while
  removing scripts and styles. Visual relationships may be incomplete. Specialized diagram
  parsers are intentionally excluded to limit maintenance. See
  [BLOOM_EVIDENCE_AUDIT.md](BLOOM_EVIDENCE_AUDIT.md) for the experiment and known limitations.
- One JEV request supplies the two Choice judgments for one filename.
- The API key stays in `~/.config/jev/jev-api-key.txt`. Missing credentials or failed requests leave
  existing labels intact and pending banks unclassified. The browser never contacts JEV.
- Exact credential-free requests and results are retained in `LOCAL_ONLY/bloom_runs/`, outside
  the published site and Git. The editable filename map is
  [../problem_set_bloom.yml](../problem_set_bloom.yml).

The persistent map follows the title-map convention: one filename and one compact value,
such as `bbq-example-questions.txt: Apply, Procedural`. The first value is the cognitive process;
the second is the knowledge type. Model, rubric, probabilities, and experiment results belong
only in ignored files under `LOCAL_ONLY/`; they are not part of the published classification map.

Normal builds classify missing filenames automatically. Run through the repository environment:

```bash
source source_me.sh
python3 build_site.py --indexes-only --cli
python3 -m devel.classify_bloom --action refresh --filenames bbq-example-questions.txt
python3 -m devel.classify_bloom --action refresh
python3 -m devel.classify_bloom --action report
```

The developer utility is retained for explicit refreshes and coverage reports.
The example filename above is a placeholder; refresh requires an actual catalog filename.
Refresh deliberately replaces selected labels. Ordinary builds preserve them.

## Exploration and refinement

[BLOOM_COVERAGE.md](BLOOM_COVERAGE.md) counts unique filenames overall, by subject, and by response
type. A zero means no bank was assigned there, not a proven educational gap. Coverage need not be
uniform. Subject groups can overlap.
[BLOOM_FINDINGS.md](BLOOM_FINDINGS.md) records the exploratory comparison and remaining limitations.
[BLOOM_EXTERNAL_VALIDATION.md](BLOOM_EXTERNAL_VALIDATION.md) records the independent external
reference and bank checks. These do not establish corpus accuracy or justify promoting labels
to balance the distribution.

[bloom_examples.yml](bloom_examples.yml) contains provisional diagnostic judgments and rationales.
These source-grounded examples are not independently certified ground truth. They cover boundary
distinctions, including categories that may not occur in BPW. Synthetic examples never enter corpus
coverage. Some examples are reserved from rubric refinement.

Use `python3 -m devel.evaluate_bloom` for a bounded live check of those examples and a reproducible
random/targeted selection of real banks. It records evidence and results without replacing current
bank labels. Keep live LLM checks outside offline pytest.

Compare reference agreement, sample/presentation stability, and changes after rubric refinement
separately. Inspect high-confidence cases too. JEV returns choices and distributions, not narrative
rationales. Confidence is derived from its probabilities and is not demonstrated accuracy:
[JEV confidence documentation](https://docs.typesafe.ai/confidence).

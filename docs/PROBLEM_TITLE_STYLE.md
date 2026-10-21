# Problem-set title style guide

Titles help instructors choose questions for their classes. An instructor familiar with the
chapter should recognize the specific problem set from its title.

**Use the shortest title that uniquely identifies the problem set to that instructor.**
Preserve meaningful detail rather than optimizing for a word count.

This is the editorial guide for [problem_set_titles.yml](../problem_set_titles.yml) and the
generation prompt in [problem_set_title.py](../bioproblems_site/problem_set_title.py).
[PROBLEM_TITLE_ABBREVIATIONS.md](PROBLEM_TITLE_ABBREVIATIONS.md) owns format labels and badges.

## Identify the specific set

- **Specific:** distinguish the set from others in the same chapter.
- **Descriptive:** name what students actually determine, calculate, identify, or compare.
- **Concise:** remove filler while retaining details that distinguish the set.
- **Recognizable:** use the scientific and teaching terms instructors associate with the task.

Include the biological context, mathematical concept, application, or input where it helps
identify the set. For example, `Offspring Phenotype Probabilities for Independent Births (MC)`
distinguishes independence questions from binomial offspring counts and probability-table tasks.

Name the assessed decision rather than one possible conclusion. The dice interpretation bank
asks whether deviations are statistically significant, whether or not the data support die bias.
Its title is `Statistical Significance of Dice Roll Deviations (MC)`.

## Use direct wording

- Prefer concrete noun phrases: `Null Hypothesis Rejection Criteria (TFMS)` and
  `Chi-Square Process Error Identification (MC)`.
- Remove generic introductions such as `Completing a`, `Evaluating a`, `Choosing the`,
  `Reviewing a`, and `When to`. Keep task words such as `Calculations`, `Decisions`, and
  `Error Identification` when they distinguish what students must do.
- Lead with the distinguishing content. A chapter name such as `Chi-Square` belongs where
  it identifies the task; it need not begin every title in that chapter.
- Use familiar task terms instead of vague umbrellas such as `Process Evaluation`. A concise
  combined-task title works when it identifies the set; retain specific components where they
  are needed to distinguish it from its neighbors.
- Treat `Result from Input` as a useful pattern, not a required sentence template.
- Use Title Case, ASCII characters, and no final punctuation. Preserve scientific notation
  such as `pH`, `p-Values`, and `5'/3'`.

## Examples from title review

| Less useful | Preferred | Distinction preserved |
| --- | --- | --- |
| Chi-Square Tests (TFMS) | Null Hypothesis Rejection Criteria (TFMS) | The decision rule being assessed |
| Completing a Dice Chi-Square Calculation (MC) | Chi-Square Calculations for Dice Rolls (MC) | Calculation task and dice context |
| Evidence of Die Bias from Goodness-of-Fit Results (MC) | Statistical Significance of Dice Roll Deviations (MC) | Significance assessment rather than a possible outcome |
| Errors in Chi-Square Calculations and Hypothesis Decisions (MC) | Chi-Square Process Error Identification (MC) | Error identification across the test process |
| Hypothesis Pair Error Identification for Genetic Crosses (MC) | Null and Alternative Hypothesis Error Identification for Genetic Crosses (MC) | Which hypotheses students inspect |
| Offspring Probability and Independence (MC) | Offspring Phenotype Probabilities for Independent Births (MC) | Biological context and independence application |

Shortening can misstate scope. Use `Chi-Square Calculations for Dice Rolls (MC)` rather than
`Chi-Square Totals from Dice Rolls (MC)` because that bank asks for both individual contributions
and totals. Verify every proposed simplification against the questions.

## Keep related titles parallel

Use the same base title for equivalent content in different formats, such as
`Chi-Square Terms from Definitions (Matching)` and
`Chi-Square Terms from Definitions (WOMC)`.

Different tasks need different identifying details, even when they share a topic:

- `Offspring Phenotype Probabilities for Independent Births (MC)`
- `Binomial Probabilities for Offspring Phenotype Counts (2-4 Offspring, MC)`
- `Binomial Probabilities for Offspring Sex Counts (MC)`
- `Offspring Sequences with Exact or Minimum Phenotype Counts (MA)`
- `Offspring Phenotype Count Probabilities from Tables (Matching)`

Keep meaningful variant details in parentheses, ending with the format label. Order applicable
qualifiers consistently: difficulty, size or count, representation or label type, `With Hint`,
then format. Use consistent spellings such as `Word Labels`, `Directionless`, and `5'/3' Labels`.

Preserve explicit difficulty labels: `Easy`, `Medium`, `Hard`, `Rigorous`, and `Bonus`.
Shared scientific assumptions do not replace them. Replace opaque generator labels or course
codes with verified distinctions, such as `3 Taxa` instead of `Level 1` when that is its meaning.

## Review against the questions

1. Read representative questions across the bank and inspect the generator when scope is unclear.
   Identify the actual task, inputs, and meaningful variants; verify the response format.
2. Describe the scope of the set. Include an organism, disorder, or value only when it defines
   that scope. Keep random examples and correct answers out of the title.
3. Compare every title with its chapter neighbors in [sitemap.md](../site_docs/sitemap.md).
   An instructor should recognize each set without opening its questions or reading a filename.
   Confirm that combined tasks remain distinguishable from their component tasks.
4. Remove filler and repeated context, then check that the title still identifies the same set.
   Retain information that affects course selection, including prerequisites and representation;
   support every difficulty or scope claim with the material.
5. Edit the shared title cache while preserving keys, metadata, and format labels. Refresh affected
   topic pages and catalogs through the index workflow in [USAGE.md](USAGE.md), including any
   other topic that uses the same bank. Verify that displayed titles agree with the cache.

The generation prompt should carry these rules and representative examples. Prompt construction
checks verify the instructions supplied to the model; evaluating generated title quality requires
reviewing actual model output against the questions and neighboring titles.

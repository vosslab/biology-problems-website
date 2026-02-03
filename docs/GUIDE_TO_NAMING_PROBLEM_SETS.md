# Guide to naming problem sets

This guide defines how to name entries in `problem_set_titles.yml` so titles are
consistent, informative, and easy to scan.

## Core format
- Use `Task + Topic + Key Detail`.
- Use Title Case for the full title.
- Keep titles plain text with no markdown, quotes, HTML, or trailing punctuation.
- Keep titles concise while still conveying the main task and what is being
  distinguished.

## Task verbs
Use one of these verbs as the first word in the title, aligned to question type:

| Question type | Task verb |
| --- | --- |
| MC, MA | Identifying |
| FIB, MULTI_FIB | Identifying |
| MATCH | Matching |
| NUM, NUMERIC | Calculating |
| ORDERING | Determining |
| TF, TFMS | Determining |

If the question type is unclear, infer it from the filename and pick the best
fit from the list above.

## Key detail guidance
- Include the distinguishing detail that makes the set specific.
- Prefer parentheses for structured details like counts or difficulty levels.
- Use consistent phrasing for repeated formats.

Examples of key details:
- `(EASY, 4 Suspects)`
- `(6 Choices)`
- `(4 Metabolites)`
- `(10 Length, 3 Sites)`
- `(Cis vs. Trans)`

## Examples
- Identifying RFLP Forensic DNA Analysis Results (EASY, 4 Suspects)
- Matching Macromolecule Types to Structures or Functions
- Calculating pH Using the Henderson-Hasselbalch Equation
- Determining Gene Configuration (Cis vs. Trans) in Two-Point Test Crosses
- Identifying Amino Acids from Chemical Structures (7 Choices)

## Updating timestamps
When a `problem_set_titles.yml` file is updated, refresh the `last edit` entry
to reflect the current time.

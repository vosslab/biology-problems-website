# Guide to naming problem sets

This guide defines how to name entries in `problem_set_titles.yml` so titles are
consistent, informative, and easy to scan.

Titles are topic labels, not instructions. Question type is handled elsewhere,
so do not encode it in the title text.

## Core rule
- Titles must begin with the primary noun phrase that names the concept,
  object, or system being tested.
- Do not begin with a task or action verb.

## Structure
- Use `Concept or Entity + Qualifier + Context or Constraint`.
- Use Title Case for the full title.
- Keep titles plain text with no markdown, quotes, HTML, or trailing punctuation.
- Keep titles concise while still conveying the main task and what is being
  distinguished.

## Verb handling
- Do not include leading task verbs such as "Identifying", "Determining",
  "Calculating", "Matching", or "Construct".
- Verbs are allowed later in the title only when they name a biological or
  chemical process, not a student action.

## Scope and detail
- Include the distinguishing detail that makes the set specific.
- Prefer parentheses for structured details like counts or difficulty levels.
- Use consistent phrasing for repeated formats.
- Avoid filler phrases like "Using" unless they name a required method or
  equation.

## Consistency rules
- Prefer singular concept names unless plurality is essential.
- Use the same phrasing for repeated patterns across topics.
- Keep titles short enough to scan in a list without truncation.

Examples of key details:
- `(EASY, 4 Suspects)`
- `(6 Choices)`
- `(4 Metabolites)`
- `(10 Length, 3 Sites)`
- `(Cis vs. Trans)`

## Examples
- RFLP Forensic DNA Analysis Results (EASY, 4 Suspects)
- Macromolecule Types to Structures or Functions
- pH Using the Henderson-Hasselbalch Equation
- Gene Configuration (Cis vs. Trans) in Two-Point Test Crosses
- Amino Acids from Chemical Structures (7 Choices)

## Updating timestamps
When a `problem_set_titles.yml` file is updated, refresh the `last edit` entry
to reflect the current time.

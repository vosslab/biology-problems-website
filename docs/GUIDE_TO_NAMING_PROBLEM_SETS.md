# Guide to naming problem sets

This guide defines how to name entries in `problem_set_titles.yml` so titles are
consistent, informative, and easy to scan.

Titles are topic labels rather than student instructions. Most titles emphasize
the concept first. Matching and true/false multiple-statement sets are useful
exceptions because their formats distinguish them from nearby problem sets.

## Core rule

- Titles must begin with the primary noun phrase that names the concept,
  object, or system being tested.
- Do not begin general titles with task phrases such as "Determining",
  "Identifying", or "Calculating".
- Begin Blackboard matching titles with "Matching".
- Begin TFMS titles with "True/False Statements About".

## Structure
- Use `Concept or Entity + Qualifier + Context or Constraint`.
- Use Title Case for the full title.
- Keep titles plain text with no markdown, quotes, HTML, or trailing punctuation.
- Keep titles concise while still conveying the main task and what is being
  distinguished.

## Format cues

- Write MATCH titles as `Matching A to B` so students can distinguish them
  from multiple-choice sets covering the same content.
- Write TFMS titles as `True/False Statements About X`.
- Give WOMC titles natural, concept-focused wording. Do not force a common
  prefix because their tasks vary.
- Use format suffixes such as `(Multiple Choice)` and `(Numeric)` when sibling
  sets otherwise have the same title.

## Verb handling

- Do not include leading task verbs such as "Identifying", "Determining",
  "Calculating", or "Construct" in general titles.
- Verbs are allowed later in the title only when they name a biological or
  chemical process, not a student action.

## Scope and detail

- Include the distinguishing detail that makes the set specific.
- Prefer parentheses for structured details like counts or difficulty levels.
- Surface meaningful generator parameters when similar sets appear together.
  Examples include difficulty, item count, marker count, color mode, answer
  format, layout, label type, and course-specific scope.
- Use consistent phrasing for repeated formats.
- Avoid filler phrases like "Using" unless they name a required method or
  equation.

## Consistency rules

- Prefer singular concept names unless plurality is essential.
- Use the same phrasing for repeated patterns across topics.
- Give the same BBQ filename key the exact same title wherever it appears.
- Keep titles short enough to scan in a list without truncation.

Examples of key details:
- `(EASY, 4 Suspects)`
- `(6 Choices)`
- `(4 Metabolites)`
- `(10 Length, 3 Sites)`
- `(Cis vs. Trans)`
- `(2 Markers, Black)`
- `(2 Markers, Color)`
- `(3 Markers, Color)`

## Examples

- RFLP Forensic DNA Analysis Results (EASY, 4 Suspects)
- Matching Macromolecule Types to Structures or Functions
- Macromolecule Types from Structures or Functions
- True/False Statements About Enzyme Kinetics
- pH Using the Henderson-Hasselbalch Equation
- Gene Configuration (Cis vs. Trans) in Two-Point Test Crosses
- Amino Acids from Chemical Structures (7 Choices)
- Offspring HLA Genotypes (2 Markers, Black)
- Offspring HLA Genotypes (2 Markers, Color)
- Offspring HLA Genotypes (3 Markers, Color)

## Updating timestamps

When a `problem_set_titles.yml` file is updated, refresh the `last edit` entry
to reflect the current time.

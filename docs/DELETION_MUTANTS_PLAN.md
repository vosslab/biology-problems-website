# Deletion mutant daily puzzle plan

## Goal

Build a new daily puzzle (similar in spirit to `Peptidyle`) where a player deduces the linear order of genes on a
chromosome using deletion mutant evidence.

The original reference implementation is Python under `site_docs/daily_puzzles/deletetions_source/` and generates HTML
for LMS imports. The daily puzzle must run in-browser using JavaScript + CSS inside MkDocs.

## Non-goals

- Do not depend on `qti_package_maker` at runtime (browser cannot import it).
- Do not break the existing `Peptidyle` page while refactoring shared code.
- Do not introduce new third-party JS dependencies unless there is a strong reason.

## Constraints and conventions

- Must work as static site content (MkDocs `site_docs/`).
- Prefer deterministic "daily" behavior based on a UTC day key.
- Persist stats in `localStorage` with a per-game key (avoid collisions).
- Keep CSS self-contained under a root element (like `#pw-root` in Peptidyle).
- ASCII only in content.

## Proposed user experience

- Player sees a table of deletions (rows) vs. unknown gene positions (columns).
- Each row indicates which genes are uncovered by that deletion (colored blocks).
- Player enters a proposed gene order (letters) and gets immediate feedback.
- Optional hints:
  - "first gene is X" (mirrors `--first-letter` behavior in the Python generator)
  - "answer is an English word" (when we use a word bank)
- Game ends on correct solution or after a fixed number of guesses.

## Data model (browser)

- `num_genes`: typically 4 to 6 (start with 5 as default).
- `answer_gene_order`: an array of letters, e.g. `["S","T","A","R","E"]`.
- `deletions_list`: list of deletions, each deletion is an array of letters, e.g. `["S","T","A"]`.
- `deletion_colors`: mapping from a stable deletion key (sorted letters joined) to a hex color.

## Implementation phases

### Phase 1: Understand and freeze puzzle rules

- Review Python functions in `deletionlib.py`:
  - `generate_deletions()`, `generate_deletions_sub()`, `add_new_pairs()`
  - `make_html_table()` (for rendering intent)
  - `write_question_text()` (for wording and hints)
- Decide the exact rules for the web puzzle:
  - Guess format (typed string, drag-and-drop, or both)
  - Max guesses
  - Feedback style:
    - full Wordle-style positional feedback, or
    - adjacency feedback (neighbors), or
    - correctness only (simple)
- Decide default difficulty presets (match Python: easy 4, medium 5, rigorous 6).

Deliverable:
- A short written spec embedded in the final daily puzzle page describing rules and hints.

## Status (2026-01-05)

- Implemented a working in-browser version of the deletion mutant daily puzzle page.
- Added shared daily puzzle utilities and reused them for this puzzle and Peptidyle.
- Updated light/dark mode styling and aligned the keyboard and stats display across the puzzles.
- Added a first-gene hint behind a guess penalty and made it consistent across both daily puzzles.
- Embedded a filtered unique-letter word bank for deletion mutants (no runtime fetch of `real_wordles.txt`).

## Notes on word lists

- The live browser puzzle uses an embedded word list inside:
  - `site_docs/assets/scripts/deletion_mutants_words.js`
- Refresh the embedded word list using:
  - `build_deletion_mutants_wordbank.py`
  - optionally with `--src PATH/TO/real_wordles.txt` if your word list is not at the default location.

### Phase 2: Port Python deletion logic to JavaScript

Port the core algorithm from `deletionlib.py`:

- `generate_deletions_sub()` and `add_new_pairs()` to JS.
- Ensure output is deterministic for a given daily seed.
- Add guardrails to avoid infinite loops:
  - max iterations, retry with a new seed stream, or widen deletion size bounds.

Deliverable:
- `site_docs/assets/scripts/deletion_mutants_logic.js` that can produce:
  - `answer_gene_order`
  - `deletions_list`

### Phase 3: QA and maintainability

- Run `tests/run_pyflakes.sh` when Python scripts change.
- Manually test in browser:
  - desktop + mobile layout
  - light/dark theme
  - localStorage stats update once per day
  - deterministic daily puzzle (same day, same puzzle)

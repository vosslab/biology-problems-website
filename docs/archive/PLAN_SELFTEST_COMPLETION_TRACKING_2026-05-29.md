# Self-test Completion Tracking Plan

Status: implemented and verified on 2026-05-29.

## Goal

Add local, browser-only completion tracking for embedded self-test HTML
questions. A question is marked complete only after one fully correct answer.
Wrong answers, attempts, and accuracy are not stored.

This is intentionally lighter than Khan Academy mastery. User-facing labels use
completion language (`Completed`, `Not completed`, `Topic complete`) rather
than implying repeated-evidence mastery.

## Product Rules

- The scoring unit for v1 is the individual self-test question.
- The v1 question ID is the existing `hhhh_hhhh` CRC code.
- The browser stores only completed question IDs and first-correct timestamps.
- Incorrect and partially correct answers do not change stored progress.
- Topic completion means every reachable self-test question on that topic page
  is complete.
- Progress is local to the browser profile through `localStorage`.
- If storage is unavailable or corrupt, answer checking still works and the
  progress UI shows a non-blocking warning instead of silently pretending to
  save progress.

## Source Of Truth

The manifest source of truth is the MkDocs student-facing navigation:

1. Read topic pages reachable from `mkdocs.yml` nav.
2. Follow self-test `{% include ... %}` references from those pages.
3. Extract real `question_html_hhhh_hhhh` containers from the included HTML.
4. Exclude generated self-test files that are not reachable from a topic page.

This avoids counting archived, hidden, duplicate, or generated-but-unused
questions in the dashboard.

## Question Identity

There are 4,294,967,296 possible CRC codes. The current corpus scale is small
relative to that space, but v1 still validates duplicate CRCs and fails loudly.

The manifest stores:

- `questionId`: the CRC code, used by local storage.
- `crc`: the CRC code, duplicated for readability and validation.
- `pagePath`: the reachable topic page that owns the question.
- `selftestPath`: the included self-test HTML file.
- `subjectKey`, `topicKey`, and `topicTitle`: dashboard grouping metadata.
- `questionFingerprint`: a diagnostic hash to flag suspicious future reuse.

If a future collision or content-reuse issue appears, the manifest has enough
metadata to detect it before old completion data is silently attached to the
wrong question.

## Correctness Contract

The runtime wrapper calls the generated `checkAnswer_<crc>()` function first,
then inspects the matching `result_<crc>` element. A question is completed only
when the rendered result clearly represents full correctness.

The accepted contract is fixture-tested in JavaScript:

- Full-correct result states mark completion.
- Partial-credit states do not mark completion.
- Incorrect states do not mark completion.
- Missing or ambiguous result elements do not mark completion.

This keeps broad fallback matching out of the production path. If a generated
question type changes its result wording or DOM convention, the contract tests
must be updated with real fixtures before broadening runtime behavior.

## Implementation Workstreams

### Manifest And Generator Integration

Owner: manifest/generator coder.

- Add a manifest builder under `bioproblems_site/`.
- Integrate manifest generation into `generate_pages.py` through the existing
  pipeline module.
- Write `site_docs/assets/data/selftest_question_manifest.json`
  deterministically.
- Validate duplicate CRCs and malformed included self-test HTML.
- Reserve `progress/` so the dashboard page is not treated as a metadata
  subject.

Acceptance:

- Generated manifest has one row per reachable self-test question.
- Orphan generated self-test files are excluded.
- Duplicate CRCs fail loudly.
- Manifest regeneration is deterministic.

### Browser Runtime

Owner: browser JS coder.

- Add `site_docs/assets/scripts/selftest_progress.js`.
- Load it through `mkdocs.yml` `extra_javascript`.
- Support both normal `DOMContentLoaded` and MkDocs Material `document$`
  navigation lifecycle.
- Wrap generated answer-check functions idempotently.
- Store only first-correct completion data in `localStorage`.
- Expose a small `window.SelfTestProgress` API for tests and future UI work.
- Avoid storing wrong answers, attempts, elapsed time, or accuracy.

Acceptance:

- Correct answers mark completion once.
- Incorrect and partial answers do not store anything.
- Re-running a correct check does not change the first-correct timestamp.
- Storage failures do not break generated answer checking.

### UI And Dashboard

Owner: UI coder.

- Add a progress dashboard page at `site_docs/progress/index.md`.
- Add nav and homepage links.
- Add per-topic summaries and per-question status badges at runtime.
- Use completion labels instead of mastery labels.
- Add reset behavior with confirmation.
- Disable reset when storage is unavailable.

Acceptance:

- Dashboard aggregates completion by subject and topic.
- Topic pages show local progress for their visible questions.
- The UI remains usable with storage unavailable or empty.
- Reset clears self-test progress only and does not affect daily puzzle data.

### Tests And Verification

Owner: test owner.

- Add Python manifest tests.
- Add metadata regression tests for the `progress/` nav path.
- Add Node-based browser runtime tests.
- Run MkDocs build.
- Run `mkdocs serve` and verify live pages and JSON assets over HTTP.

Required checks:

- `node tests/selftest_progress_storage_test.mjs`
- `node tests/selftest_correctness_contract_test.mjs`
- `node tests/selftest_progress_dom_test.mjs`
- `/opt/homebrew/opt/python@3.12/bin/python3.12 -m pytest tests/test_selftest_manifest.py tests/test_mkdocs_metadata_sync.py tests/test_pyflakes_code_lint.py`
- `source source_me.sh && /opt/homebrew/opt/python@3.12/bin/python3.12 -m mkdocs build --strict`
- `source source_me.sh && /opt/homebrew/opt/python@3.12/bin/python3.12 -m mkdocs serve -a 127.0.0.1:8765`

The live server check must verify:

- `/progress/` returns HTTP 200 and contains the dashboard container.
- `/biochemistry/topic01/` returns HTTP 200 and contains self-test question
  containers.
- `/assets/data/selftest_question_manifest.json` returns HTTP 200 JSON.

### Documentation

Owner: documentation owner.

- Document the local-only storage model.
- Document that wrong answers are not stored.
- Document that first-correct timestamps are stored.
- Document the generated manifest.
- Update the changelog.
- Archive this plan under `docs/archive/`.

## Reviewer Gate Resolution

- Result parsing gate: resolved with a fixture-tested correctness contract
  instead of untested broad text matching.
- Manifest source-of-truth gate: resolved by using reachable MkDocs topic
  pages, not all generated files.
- Question identity gate: v1 uses CRCs with duplicate validation and diagnostic
  fingerprints.
- Generator integration gate: manifest writing is integrated into the existing
  generation pipeline.
- Tooling gate: Python commands use the repo-required Homebrew Python 3.12;
  Node is used only for standalone browser-JS tests.
- Storage unavailable gate: storage failures show a warning and do not block
  answer checking.
- UI validation gate: MkDocs build and live `mkdocs serve` HTTP checks cover
  the dashboard, topic page, and manifest asset.
- Rollback gate: remove the script include, dashboard nav/page, generated
  manifest, runtime script, CSS additions, and pipeline manifest hook.

## Verification Result

Implemented as planned. The final manifest currently serves 262 reachable
self-test questions, including the regenerated Life Molecules topic self-tests.


# Self-test progress

The 2026-10-09 Phase 2 runtime report records a passing real-WASM A/B/A journey and
complete rollout of 482 self-tests, topic wrappers, and manifest banks. Existing v1
completion records and timestamps remain intact. Final fresh post-KISS reviews are
pending; the synthetic CRC finding remains upstream-owned. See
[the Phase 2 acceptance report](active_plans/reports/optimized_spindle_phase2_acceptance.md).

How local self-test completion tracking works, for authors adding questions and
for anyone debugging the dashboard. Implementation lives in
[selftest_manifest.py](../bioproblems_site/selftest_manifest.py) (build side) and
[selftest_progress.js](../site_docs/assets/scripts/selftest_progress.js) (browser
side). See also [CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md) for the data flow and
[USAGE.md](USAGE.md) for the user-facing summary.

## Model

- The scoring unit is a single self-test question, identified by its `hhhh_hhhh`
  CRC code.
- A question is marked complete only after one fully correct answer.
- Each variant has its own completion record. Completing variant A does not
  complete variant B in the same bank.
- A reroll resets the answer controls and feedback to provide a fresh attempt.
  If the reroll shows a variant already completed, its CRC-specific completion
  record remains; a previously unseen CRC starts incomplete.
- Bank identity routes and groups variants for fetching. It does not own,
  aggregate, or migrate completion records.
- Wrong answers, partial credit, attempts, and accuracy are never stored.
- Progress is local to the browser profile in `localStorage`. There is no server
  and no account.

## Browser storage

Key: `selftest_progress_v1`. The value is a versioned envelope containing a
`completed` object that maps completed question CRCs to their first-correct
timestamp. Only completed questions appear. Bank completion is not stored, and
there is no bank-level migration.

```json
{
  "version": 1,
  "completed": {
    "1a2b_3c4d": { "firstCorrectAt": "2026-05-29T15:04:05.000Z" },
    "9f8e_7d6c": { "firstCorrectAt": "2026-05-29T15:09:12.000Z" }
  }
}
```

If `localStorage` is unavailable or corrupt, answer checking still works and the
dashboard shows a non-blocking warning instead of pretending to save progress.

## Generated manifest

The unified `build_site.py` workflow writes
[selftest_question_manifest.json](../site_docs/assets/data/selftest_question_manifest.json)
through the pipeline. The build reads topic pages reachable from the
[mkdocs.yml](../mkdocs.yml) nav, follows their self-test `{% include ... %}`
references, extracts `question_html_hhhh_hhhh` container IDs, and rejects
duplicate CRCs. Files that are generated but not reachable from a topic page are
excluded.

Each manifest row has these fields:

| Field | Meaning |
| --- | --- |
| `questionId` | CRC code; the key used in `localStorage`. |
| `crc` | The same CRC, kept for readability and DOM-id lookups. |
| `pagePath` | Reachable topic page that owns the question. |
| `bankId` | Bank routing/grouping key; it does not identify or aggregate completion. |
| `selftestPath` | Included self-test HTML file. |
| `subjectKey` | Subject grouping key (for the dashboard). |
| `topicKey` | Topic grouping key (for the dashboard). |
| `topicTitle` | Human-readable topic title. |
| `questionFingerprint` | Short content hash, a diagnostic to flag CRC reuse. |

## Adding a new self-test question

1. Author the question HTML with a `question_html_hhhh_hhhh` container and the
   matching `checkAnswer_<crc>()` / `result_<crc>` elements (the standard
   generated self-test shape).
2. Reference it from a topic `index.md` reachable in the mkdocs nav via a
   `{% include "downloads/selftest-....html" %}` tag.
3. Regenerate: `source source_me.sh && ./build_site.py`.
4. Confirm the new CRC appears in the manifest JSON and that the build did not
   raise on a duplicate CRC.

## When a CRC changes

A question's CRC is derived from its content, so editing the question changes its
CRC. Old completion data keyed on the previous CRC becomes orphaned (the question
shows as not completed again). `questionFingerprint` exists so a future tool can
detect content reuse before old progress is attached to the wrong question.

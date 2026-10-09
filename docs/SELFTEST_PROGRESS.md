# Self-test progress

How local self-test completion tracking works for authors adding question banks
and for anyone debugging the dashboard. The browser starts each page visit with
a fresh generated first question, while completion remains a lightweight record
of past success. Implementation lives in
[selftest_manifest.py](../bioproblems_site/selftest_manifest.py) (build side),
[selftest_reroll.js](../site_docs/assets/scripts/selftest_reroll.js) (question
lifecycle), and [selftest_progress.js](../site_docs/assets/scripts/selftest_progress.js)
(browser progress). See [CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md) for the data
flow and [USAGE.md](USAGE.md) for the user-facing summary.

## Model

- The completion unit is one BBQ problem set, identified directly by its
  filename basename, such as `bbq-fret_overlap_colors-questions.txt`.
- A set used in several topics shares one achievement. Overall and subject
  totals count each filename once; each topic shows the sets it contains.
- A problem set is marked complete after one fully correct answer to any
  generated version. Completing version A therefore completes version B from
  the same source bank.
- A generated question's `hhhh_hhhh` CRC still identifies its generated DOM,
  answer checker, and result element. It is not persistent progress identity.
- Requesting a new version replaces only that container's answers and feedback.
  The problem set remains completed during later rerolls and visits.
- Wrong answers, partial credit, attempts, and accuracy are never stored.
- Progress is local to the browser profile in `localStorage`. There is no server
  and no account.

## Browser storage

Key: `selftest_progress_v2`. The value is a versioned envelope containing a
`completed` object that maps BBQ filename basenames to their first-correct
timestamp. Only completed problem sets appear. The former CRC-keyed v1 data is
not migrated; it may be discarded.

```json
{
  "version": 2,
  "completed": {
    "bbq-fret_overlap_colors-questions.txt": {
      "firstCorrectAt": "2026-05-29T15:04:05.000Z"
    }
  }
}
```

If `localStorage` is unavailable or corrupt, answer checking still works and the
dashboard shows a non-blocking warning instead of pretending to save progress.
Daily streaks continue to use their separate `selftest_streak_v1` storage and
existing rules.

## Generated manifest

The unified `build_site.py` workflow writes
[selftest_question_manifest.json](../site_docs/assets/data/selftest_question_manifest.json)
through the pipeline. The build reads topic pages reachable from the
[mkdocs.yml](../mkdocs.yml) nav, finds their `.qti-selftest` containers, follows
each `data-selftest` path to its standalone artifact, extracts
`question_html_hhhh_hhhh` container IDs, and records a sample CRC for
diagnostics. Files that are generated but not declared by a reachable topic
container are excluded. The manifest envelope is version 2.

Each manifest row has these fields:

| Field | Meaning |
| --- | --- |
| `questionId` | BBQ filename basename; the key used in `localStorage`. |
| `crc` | Sample generated CRC, retained for diagnostics and DOM-id lookups. |
| `pagePath` | Reachable topic page that owns the question. |
| `selftestPath` | Standalone sample self-test HTML file. |
| `subjectKey` | Subject grouping key (for the dashboard). |
| `topicKey` | Topic grouping key (for the dashboard). |
| `topicTitle` | Human-readable topic title. |
| `questionFingerprint` | Short content hash, a diagnostic to flag CRC reuse. |

## Adding a new self-test question

1. Generate the standalone self-test artifact with its
   `question_html_hhhh_hhhh`, `checkAnswer_<crc>()`, and `result_<crc>` elements.
2. Let the topic-page build create its `.qti-selftest` container with
   `data-bbq` and `data-selftest` attributes.
3. Regenerate: `source source_me.sh && ./build_site.py`.
4. Confirm the BBQ filename appears as `questionId` in the manifest JSON.

## When a CRC changes

A question's CRC is derived from its generated content, so it may change when
the source bank is edited or a different version is generated. Completion stays
with the BBQ filename, so those changes do not remove earned problem-set credit.
The manifest fingerprint and sample CRC are diagnostic data only.

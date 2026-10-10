# BPW flat HTML cleanup and WASM updater audit

Date: 2026-10-09

Six fresh independent passes reviewed the uncommitted changes against
`6d6c5f8e947c24929f2dae137718ab20e8883f4e`: Plan, Test, Style, Docs, Legacy,
and Comment. Scope covered flat HTML/native-converter retirement, the direct
manifest, retained build behavior, tests, documentation, and the WASM updater.
QPM renderer parity and upstream implementation were outside the audit.

## Findings and disposition

| Severity | Finding | Disposition |
| --- | --- | --- |
| Validation blocker | The shared vendored header collector opens deleted Git-listed files before checking existence. Full pytest in this unstaged checkout stops on the retired native README. | Left the shared harness unchanged. Its owner should move the existence filter before the content filter, then rerun full pytest. Current-file checkout validation is recorded separately below. |
| Medium | `test:survey` and two Playwright survey tools still target retired standalone HTML. | Removed the entrypoint, `selftest_visual_survey.mjs`, and `capture_all_fragments.mjs`. Existing dynamic-WASM tests remain. |
| Medium | Live usage text still describes self-test-only builds. | Removed the obsolete clause in [USAGE.md](../../USAGE.md). |
| Low | The new updater command example omits the project environment. | Added `source source_me.sh &&` in [FILE_STRUCTURE.md](../../FILE_STRUCTURE.md). |
| Low | The new bank-validation function lacks the required separator. | Added the separator in [selftest_manifest.py](../../../bioproblems_site/selftest_manifest.py). |

The Test pass called the collection failure a blocker. It blocks the standard
test command in this unstaged checkout; it is not evidence of a BPW runtime
failure. Neither the shared collector nor the user's Git index was modified.
Evidence is the content filter in
[test_vendored_headers.py](../../../tests/test_vendored_headers.py), line 66,
called before the missing-file check in
[file_utils.py](../../../tests/file_utils.py), lines 753-756.

The Style pass initially flagged `QPM_ROOT` as newly introduced configuration,
then withdrew that finding after checking HEAD: both implementation and docs
already supported it. No override or replacement option was added during audit.

## Coverage and test judgment

- Plan: no findings. The retained manifest fields, identities, envelope and order
  match the baseline. The one-time equivalence check implements the user's
  migration requirement and does not add a permanent inventory or byte gate.
- Test: retained manifest, build, orphan, and browser tests protect meaningful
  behavior. Deleted native tests and temporary updater probes were appropriately
  removed. No new permanent test was recommended or added.
- Style, Docs, Legacy, Comment: findings above were corrected. Historical plans
  and changelog descriptions remain historical records.
- No second independent review was performed after these low-risk corrections.

## Verification

- Fresh focused Python run: 64 passed.
- Fresh Node progress/storage/correctness checks: all three passed.
- Fresh changed-production Pyflakes, updater Bandit, and `git diff --check` passed.
- Fresh MkDocs build passed. This is build evidence, not browser appearance evidence.
- Main-checkout full pytest: collection failed as described above.
- After the fixes, all 3,257 tests passed in a temporary checkout containing the
  current working files, with only that temporary checkout's index updated.
  No test was skipped or patched. This verifies the intended file set while
  keeping the original checkout's collection limitation visible. The temporary
  checkout was removed after validation.
- `npm run` lists only the retained screenshot, UI, and smoke commands.

The earlier browser and updater results are separate evidence: see
[BPW_FLAT_HTML_RETIREMENT.md](../../BPW_FLAT_HTML_RETIREMENT.md) for Chromium,
Firefox, and migration checks. The updater's real compilation and WASM
conversion passed in a temporary BPW destination, preserving installed assets.
No browser rerun or deployment was performed during this audit.

# Optimized Spindle Phase 3b publication migration

Date: 2026-10-09. Permanent topic-page migration and prebuilt-format cleanup PASS.
The manager released the migration after the real three-bank corpus checks and all 14
native/final visual pairs passed. Fresh final integration browser acceptance also PASS.

## Permanent publication changes

The GitHub Pages workflow builds committed `site_docs` with MkDocs. This migration copied
57 canonical rendered topic indexes into that publication input, using the previously
isolated `RenderOptions(regenerate_selftests=False)` output. At execution, all 73 source
receipt hashes and 482 BBQ inputs matched current live files. Every page comparison was
identical outside its download button rows. Existing headings, descriptions, selftest
includes, bank identities, question selections, and WeBWorK links were preserved.

The 57 pages now contain 1,440 browser-generated export controls:

| Format | Controls | Retired regular files | Retired bytes |
| --- | ---: | ---: | ---: |
| Blackboard Ultra ZIP | 479 | 479 | 509,256,126 |
| Canvas/ADAPT QTI v1.2 | 479 | 479 | 7,218,103 |
| Human-Readable HTML | 482 | 466 | 43,190,836 |
| Total | 1,440 | 1,424 | 559,665,065 |

Controls cover 482 banks; eligibility differs by format. All 482 selftest bank wrappers
remain. The controls use their existing bank's BBQ source and the canonical converter
filename. Human-readable exports remain controlled by the writer's supported content.

These old public URL patterns are retired:

- `<subject>/topicNN/downloads/blackboard_export_zip-*.zip`
- `<subject>/topicNN/downloads/canvas_qti_v1_2-*.zip`
- `<subject>/topicNN/downloads/human_readable-*.html`

The replacement action is the corresponding export control on the same topic/bank row.
Downloaded filenames retain the respective canonical prefixes. No redirect was added.

## Reversible cleanup and preservation

Removed files were moved, with their relative paths retained, to:
`/private/tmp/optimized_spindle_phase3_migration_20261009/backup/site_docs/`.
The same backup contains the 57 topic pages as they existed immediately before migration.
Every backup file matched its recorded SHA256. The backup is outside the published tree.

All 1,400 protected `site_docs` files matched their pre-migration SHA256 after migration
and after MkDocs acceptance. This includes all 482 BBQ sources, 482 selftest HTML files,
183 PGML files, 73 PG files, authored assets, catalogs, and the current question manifest.
Existing question selections and CRCs remain unchanged because both selftests and their
manifest were preserved byte for byte. No selftest was regenerated.

The manifest SHA256 is
`346d282c3e74f93c0930864b521efa0fda8545c36386f344c6fa66ca2fc289a0`.
Full per-file and aggregate preservation receipts live in the evidence directory below.

Measured regular-file bytes in `site_docs`:

| Before | After | Net reduction |
| ---: | ---: | ---: |
| 760,890,085 | 201,127,738 | 559,762,347 |

The net reduction includes 559,665,065 removed export bytes and 97,282 fewer topic-page
bytes. This measures the live publication input, excluding its external temporary backup
and isolated built output; it does not measure Git object history or remote storage.

## Actual deployment-input acceptance

Ran `source source_me.sh && python3 -m mkdocs build --site-dir
/private/tmp/optimized_spindle_phase3_migration_20261009/site` from the live checkout.
MkDocs PASS in 3.66 seconds. This follows the publication workflow's static-build path;
remote publication was not performed. The build reports the existing vendored
`assets/package_render/README.md` outside navigation as informational output.

The resulting built output passed all 57-page mapping checks: all 1,440 controls refer
to existing BBQ sources and canonical filenames; all 482 bank wrappers remain; all 722
retained BBQ/PGML/PG download links resolve; package-download script inclusion is present;
zero retired static export files or links remain. All protected hashes still match.
The final integration owner ran the two package and three reroll browser checks against
this exact post-cleanup output: all five PASS in 3.1 seconds. Browser evidence is
`browser_tests.log` and `browser_test_outputs/` in the evidence root. Its server on port
8851 was stopped after acceptance.

Focused affected checks PASS: 30 tests in 0.41 seconds across
`test_topic_page_generate_downloads.py`, `test_build_site_workflow.py`, and
`test_selftest_manifest.py`. The manager's preceding full source-suite result is a
separate acceptance lane; this migration did not repeat or replace it.

## Evidence and handoff

Temporary evidence root: `/private/tmp/optimized_spindle_phase3_migration_20261009/`.
It contains `before.json`, `prepared.json`, `migration.json`, `preservation_receipt.json`,
`static_acceptance.json`, `mkdocs.log`, `browser_tests.log`, and the temporary verification
scripts.
The final built site is its `site/` directory. This report and the 57 pages plus 1,424
removed downloads are the permanent changes owned by this migration. Source code,
manual documentation/changelog, Git/index operations, and final integration remain with
their assigned owners.

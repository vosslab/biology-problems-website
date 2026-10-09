# Optimized spindle Phase 1 output baseline

Captured 2026-10-09 before the native build validation run. This baseline is the reference for
Phase 1 output comparison in [the plan](../i-want-to-explore-optimized-spindle.md).

## Starting checkout state

Site repository: `/Users/vosslab/nsh/PROBLEMS/biology-problems-website`

- HEAD: `ab15effe34d3cbc23787cf2ee805a1932eef27c8`
- `git status --short --branch`:

  ```text
  ## main...origin/main
  A  docs/active_plans/i-want-to-explore-optimized-spindle.md
  ?? docs/active_plans/reports/
  ```

Rust repository: `/Users/vosslab/nsh/PROBLEMS/qti-package-maker-rs`

- HEAD: `3ad5a72c37be06b88112b8cbfb78be90fb453dd9`
- `git status --short --branch`:

  ```text
  ## main...origin/main
  ```

The site status above predates creation of this report and the ignored baseline directory. No
build was run during capture.

## Downloadable outputs

The capture covered regular `.zip` and `.html` files below `site_docs/**/downloads/`.
It also recorded SHA-256 hashes, byte lengths, and paths for all 482 `bbq-*-questions.txt`
source banks (162,827,406 bytes) in `bbq_source_inventory.jsonl`; this is the pre-regeneration
source reference for identifying skipped or changed outputs:

- 958 ZIP files, 516,474,229 bytes total.
- 948 HTML files, 56,697,940 bytes total.
- 1,906 files total.
- 62,485 non-directory ZIP members were recorded.

`download_inventory.jsonl` has one row per downloadable file with relative path, byte length,
kind, and SHA-256. `zip_members.jsonl` has one row per non-directory member with its ZIP path,
member path, byte length, and SHA-256. XML members also have an `xml_c14n_sha256` value from
ElementTree canonicalization with `strip_text=False`; this normalizes XML serialization details
such as attribute ordering while preserving text and whitespace. ZIP container hashes will change
when timestamps change, so member hashes and canonical XML hashes provide the content comparison.

Ten full artifacts are retained under `representative/`: six Blackboard/Canvas ZIPs, including
five PNG-rich Blackboard ZIPs, and four `human_readable`/`selftest` HTML files. Their source paths
and SHA-256 values are in `representative_manifest.json`. The ZIP copies are about 28.3 MB total.
No existing Phase 3a spike corpus was present when this snapshot was made.

## Timing reference

The plan's roughly 1183-second baseline is present in the pre-existing root `build_timing.jsonl`.
The complete timing log was copied to this baseline directory. Its completed build record is:

- Run ID: `aba70fff18134379a6d103b9844ff1c8`
- Started: `2026-10-02T03:00:40.048399+00:00`
- Completed: `2026-10-02T03:20:22.906472+00:00`
- Elapsed: `1182.8516623749747` seconds
- Stages: BBQ 1069.268 s; downloads 108.537 s; selftests 3.978 s; topic pages 0.366 s;
  indexes 0.677 s.

This run included 47 planned operations across all five stages. Later log entries are partial
runs for topic pages and indexes, so they are not comparable full-build timings. During post-build
acceptance, report elapsed wall time together with each stage's `executed` value and actual rebuilt
operation counts. A cached or no-op stage does not demonstrate a speedup; compare runtime for
operations that actually regenerated outputs against this complete-build reference.

## Reproduction and comparison

The capture used the repository Python environment (`source source_me.sh && python3`) and read
all files under `site_docs/**/downloads/` and all BBQ source banks. Downloadable files were
hashed in 1 MiB blocks; each BBQ source file was hashed from its bytes. ZIP members were read
from Python's `zipfile` module and hashed in sorted member-path order. XML was
UTF-8 decoded (allowing a UTF-8 BOM) and passed to `xml.etree.ElementTree.canonicalize` with
`strip_text=False` before hashing. The untouched timing log was copied byte-for-byte.

For post-build comparison, regenerate a JSONL inventory with the same fields and hash procedure,
then compare by relative path. Raw SHA-256 mismatches on ZIP containers are expected where ZIP
metadata timestamps changed; compare member rows and XML canonical hashes to distinguish content
changes. HTML raw hashes should match unless the documented selftest variant changed. Preserve
missing/added paths as explicit findings. Do not delete or rewrite the retained baseline during
comparison.

Baseline artifacts are in the ignored `output_rust_qpm_validation/baseline_2026-10-09/` directory.
`git check-ignore -v output_rust_qpm_validation` confirmed the directory is ignored.

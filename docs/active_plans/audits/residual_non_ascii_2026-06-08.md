# Residual non-ASCII selftest fragments audit (2026-06-08)

## Summary

The 6 files do NOT bypass `escape_non_ascii`. They are STALE: they were last
generated BEFORE the escape fix shipped and were never regenerated, because the
bp-website bbq pipeline skips any selftest output file that already exists on
disk. The fixed engine code never ran on them.

## The 6 files

All scans use Latin-1 / backslash-escape so the mojibake byte
A-circumflex + following byte is shown as `\xc2\xXX`. `\xc2\xa0` is a UTF-8
encoded non-breaking space (U+00A0); `\xc2\xb0` is a UTF-8 encoded degree sign
(U+00B0).

| File | Offending bytes (context) |
| --- | --- |
| site_docs/biochemistry/topic02/downloads/selftest-chemical_group_pka_forms.html | `\xc2\xa0` at `font-family: monospace;">\xc2\xa0</div>` (result-div footer) |
| site_docs/biochemistry/topic06/downloads/selftest-free_energy_keq_relationship.html | `\xc2\xb0` at `&#916;G\xc2\xb0&#8242;` (degree sign between escaped delta and prime); `\xc2\xa0` in footer |
| site_docs/biochemistry/topic06/downloads/selftest-thermodynamics_system_laws.html | `\xc2\xa0` in footer |
| site_docs/genetics/topic04/downloads/selftest-MATCH-mendel_four_principles.html | `\xc2\xa0` at `Law of Independent\xc2\xa0Assortment` and `Principle of Paired\xc2\xa0Factors`; `\xc2\xa0` in footer |
| site_docs/genetics/topic09/downloads/selftest-letter_translocation_problem_color-black.html | `\xc2\xa0` in footer |
| site_docs/laboratory/topic11/downloads/selftest-kaleidoscope_ladder_mapping.html | `\xc2\xa0` at `></span>\xc2\xa0colored band</td>` (5 rows) plus footer |

Total scanned: 278 fragments. 6 contain a byte > 0x7F; 272 are clean ASCII.

## Bypass mechanism

There is no live bypass in the engine. Every render path is ASCII-safe:

- qti_package_maker/engines/html_selftest/write_item.py:14-17 -- every type
  helper (MC, MA, MATCH, NUM, FIB, MULTI_FIB, ORDER) returns
  `_wrap_selftest_html(html_text)`, and `_wrap_selftest_html` ends with
  `return html_functions.escape_non_ascii(wrapped)`. The escape wraps the
  ENTIRE fragment (theme CSS + body), so no byte > 0x7F can survive.
- qti_package_maker/engines/html_selftest/html_functions.py:25-41 --
  `escape_non_ascii` is `html_text.encode("ascii", "xmlcharrefreplace")
  .decode("ascii")`. Bulletproof on any Python `str`.
- qti_package_maker/engines/html_selftest/engine_class.py:30-39 --
  `save_package` writes the already-ASCII string with `open(outfile, "w")`.
  No re-encode, no post-wrap concatenation.

The real mechanism is a regeneration SKIP on the bp-website side:

- run_bbq_tasks.py:484-493 -- `output_exists(output_path, workdir)` returns
  `True` when the target file already exists on disk (`os.path.isfile`).
- The bbq task runner is existence-gated, not content/mtime-gated and not
  forced. When the escape fix shipped and the site was regenerated, the 272
  fragments that changed (or were rebuilt) picked up the new ASCII footer
  `&#160;`; the 6 pre-existing fragments already had files on disk and were
  left untouched.

Decisive evidence (byte scan + git log):

- All 272 clean files contain the post-fix footer `&#160;`.
- All 6 dirty files LACK `&#160;` entirely and instead carry the old raw
  `\xc2\xa0` footer -- the literal pre-fix output shape.
- Git last-commit dates of the 6: 2026-03-30 through 2026-04-19. A clean file
  (selftest-MATCH-bond_types.html) is 2026-05-29. The escape fix and the
  bulk regeneration land on the later date; the 6 predate it.

## Why escape_non_ascii missed it

It did not miss it -- it never ran on these 6 files. The bytes in the 6 files
are the raw output of the OLD engine (before `escape_non_ascii` was applied to
the full fragment). Because the output files already existed, the
existence-gated runner skipped re-rendering, so the fixed code path was never
invoked for these items. The `\xc2\xb0` degree sign in the free-energy file is
consistent with old raw UTF-8 source text flowing straight to disk under the
old engine; it is not a new injection past the escape.

## Recommended fix

Single location / approach: force regeneration of these 6 fragments (or all
selftest fragments) so the fixed engine re-renders them through
`escape_non_ascii`.

- Cleanest one-time fix: delete the 6 stale files and re-run the bbq pipeline,
  OR add a `--force` / overwrite path so existence does not short-circuit.
- Durable fix (fix the design, not the symptom): change the skip gate at
  run_bbq_tasks.py:484 (`output_exists`) from pure existence to a freshness
  check (regenerate when the source/generator is newer than the output, or
  always regenerate selftest HTML), so an engine fix automatically propagates
  to already-existing fragments instead of being silently skipped.

No engine change is needed -- the engine is already correct. No upstream
source cleanup is required for the non-breaking spaces; regeneration alone
converts them to `&#160;`. The lone `\xc2\xb0` will likewise become `&#176;`
once the free-energy fragment is re-rendered, so source normalization is
optional, not required.

## Confidence

High. The engine path is provably ASCII-only (three file:line checkpoints),
and the 272-vs-6 footer split (`&#160;` vs raw `\xc2\xa0`) plus the
before/after git dates pin the cause to a skipped regeneration, not a code
bypass.

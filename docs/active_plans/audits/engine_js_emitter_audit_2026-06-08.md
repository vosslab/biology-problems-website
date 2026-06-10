# Engine JS-emitter hazard audit (html_selftest)

Date: 2026-06-08
Scope: read-only audit of every JS/HTML emitter in
`qti-package-maker/qti_package_maker/engines/html_selftest/`.
Files reviewed: add_FIB.py, add_MA.py, add_MATCH.py, add_MC.py,
add_MULTI_FIB.py, add_NUM.py, add_ORDER.py, engine_class.py,
html_functions.py, javascript_functions.py, write_item.py, __init__.py.

This audit hunts the bug family flagged in the FIB review:

1. Non-f-string lines containing `{...}` placeholders meant to be substituted
   (the original FIB ReferenceError bug).
2. Python `repr` (`!r`) or `str(list)` injected into emitted JS/JSON.
3. Manual quote concatenation that breaks if content contains the quote char.
4. Python list/dict interpolated directly into a `<script>` block.
5. f-strings emitting unescaped content text into a JS string context.

## Summary

Count by severity:

- High: 1
- Medium: 2
- Low: 3

Runtime-error-class confirmation: The previously fixed add_FIB.py line
(`const fibAnswers_... = {normalized_answers!r}`) is now a correct f-string, so
the literal-placeholder ReferenceError no longer fires. NO other
runtime-error-class instance of the exact FIB literal-placeholder bug exists:
every `{crc16_text}`/`{idx}`-style token in the engine sits inside an f-string
(verified by full read plus regex sweep). However, one NEW
runtime-error-capable hazard remains in add_FIB.py line 22: the surviving
`{normalized_answers!r}` repr injection can emit syntactically invalid JS
(a JS `SyntaxError` at parse time, which disables the whole item's script,
same blast radius as the original bug) whenever an answer contains a single
quote or a backslash. This is classed High.

## Findings

| file:line | hazard class | severity | runtime-error-possible | note |
| --- | --- | --- | --- | --- |
| add_FIB.py:22 | 2 (repr into JS array) | high | yes | `f"const fibAnswers_{crc16_text} = {normalized_answers!r};"` injects a Python list repr into a JS array literal. ASCII answers are fine, but an answer containing a single quote (`it's`), a backslash, or non-ASCII produces invalid JS (Python repr uses single quotes and Python escape rules, not JS/JSON). Result is a parse-time JS SyntaxError that kills the item script. Fix-note: replace with `json.dumps(normalized_answers)` like add_MULTI_FIB.py:11 already does. |
| add_MATCH.py:221,224 | 5 (unescaped content into HTML attr / text) | medium | no | choice_text and clean_title are interpolated into `title="{clean_title}"` and `<span>...{choice_text}</span>`. A double quote in clean_title closes the attribute early; raw `<`/`>` in choice_text can break markup. clean_title comes from make_question_pretty (some sanitizing), but no quote/attribute escaping is guaranteed. Breaks only on unusual input. Fix-note: HTML-escape attribute values (html.escape with quote=True) for the title attribute. |
| add_MATCH.py:185 / add_ORDER.py:141 | 5 (unescaped content into HTML) | medium | no | prompt_text / choice_text interpolated raw into table cells and list spans. HTML context, not JS, and downstream lxml formatting plus escape_non_iso_8859_1 reduce risk, but embedded quotes/angle brackets in source content can still distort layout. Breaks only on unusual input. Fix-note: escape content before interpolation, or confirm upstream sanitization is mandatory. |
| add_MC.py:43 / add_MA.py:45 | 5 (unescaped content into HTML) | low | no | `<span>{choice_text}</span>` raw interpolation. Pure HTML body context (not attribute, not JS); a stray `<`/`>` could break rendering but cannot cause a JS runtime error. Fix-note: escape if choice_text may contain markup; acceptable if upstream guarantees safe HTML. |
| add_NUM.py:27,28 | 4-adjacent (Python value into script) | low | no | `const numAnswer_... = {answer_float}` and `{tol}` interpolate Python floats directly into JS. Safe for normal floats; only `float('nan')`/`inf` would emit a bare `nan`/`inf` token (JS ReferenceError). Inputs are typed float and realistically finite, so risk is low. Fix-note: guard against non-finite values or emit via json.dumps. |
| add_FIB.py:24 / add_MULTI_FIB.py:71 / add_MATCH.py:128 / add_ORDER.py (various) | 3 (manual quote concatenation in JS) | low | no | Several lines build JS with mixed string-concatenation and quote styles (for example `'result_'+crc16_text`). crc16_text is a CRC16 hex token (controlled, alphanumeric), so the concatenation cannot break. No content data flows through these joins. Style note only, not a content-safety hazard. |

## Non-findings (checked, clean)

- Hazard class 1 (non-f-string with live placeholder): NONE. Regex sweep
  plus full read confirms every `{crc16_text}`/`{idx}`/`{normalized_answers}`
  token is inside an f-string. add_FIB.py:22 is now an f-string.
- html_functions.py:222-228 builds a `<style>` injection using
  `json.dumps(css)` for the textContent. This is the CORRECT pattern
  (json.dumps, not repr) and is safe.
- add_MULTI_FIB.py:11 uses `json.dumps(answers)` into a `data-answers`
  attribute and parses it back with `JSON.parse` in JS. This is the
  reference-correct approach the FIB fix should copy.
- javascript_functions.py and the drag/drop scripts only interpolate
  crc16_text (controlled hex), no content data.

## Recommended remediation order

1. add_FIB.py:22 (HIGH, runtime-error-capable): switch `{normalized_answers!r}`
   to `json.dumps(normalized_answers)`. This is the only remaining
   runtime-error-class hazard and the direct continuation of the fixed bug.
2. add_MATCH.py:221,224 (MEDIUM): escape the `title` attribute value to
   prevent attribute-breakout on quotes in content.
3. add_MATCH.py:185 / add_ORDER.py:141 (MEDIUM): escape prompt/choice text
   interpolated into HTML cells and spans.
4. add_MC.py:43 / add_MA.py:45 (LOW): escape choice_text in span bodies, or
   document upstream HTML-safety guarantee.
5. add_NUM.py:27,28 (LOW): guard non-finite floats.
6. Manual-quote-concatenation lines (LOW): leave as-is or normalize to
   f-strings for consistency; no content-safety impact.

## Runtime-error-class conclusion (explicit)

The fixed add_FIB.py literal-placeholder line is the ONLY instance of the exact
original FIB bug (non-f-string emitting a literal `{...}` token), and it is
already fixed. There are NO other lines of that exact class. There IS one other
hazard that can produce a runtime JS error of equivalent blast radius:
add_FIB.py:22's surviving `{normalized_answers!r}` repr-into-JS injection,
which emits invalid JS (parse-time SyntaxError) on quote/backslash/non-ASCII
answers. It should be remediated next.

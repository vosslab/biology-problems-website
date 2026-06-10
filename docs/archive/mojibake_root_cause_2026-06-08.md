# Mojibake root cause: A-circumflex in self-test HTML

Read-only investigation, 2026-06-08. The mojibake character is written
throughout this report as the literal phrase "A-circumflex" (capital A with a
circumflex accent, Unicode U+00C2), never as a raw non-ASCII byte.

## Summary

The verdict is the ENGINE. The byte signature of every mojibake instance is a
UTF-8-encoded Latin-1-range character: `0xC2` followed by a second byte in the
`0xA0`-`0xBE` range. The most common case is `0xC2 0xA0` (UTF-8 for a
non-breaking space, U+00A0). The engine function
`escape_non_iso_8859_1` in
`html_functions.py`
only escapes characters ABOVE U+00FF; it deliberately passes through every
character in U+0080-U+00FF (non-breaking space U+00A0, plus-minus U+00B1,
middle dot U+00B7, degree U+00B0, fractions U+00BC-U+00BE) as a raw Latin-1
byte. `save_package` then writes the file with Python's default UTF-8 encoding
(`open(outfile, "w")`), so each raw Latin-1 byte becomes a two-byte UTF-8
sequence beginning with `0xC2`. When a consumer decodes that fragment as
Latin-1 (the manifest reader already opens these files with
`encoding="iso8859-1"`), the leading `0xC2` byte renders as A-circumflex and
the second byte renders as the trailing symbol. A full site scan found 266 of
278 self-test files affected, with 7661 occurrences of the `0xC2 0xA0` pair
alone.

## Evidence

### Byte sequences (ground truth)

A Python byte scan over all 278 `selftest-*.html` files under `site_docs/`
returned:

```
total selftest files: 278
affected (any high byte): 266
C2-pair counts: {
  (0xC2,0xA0): 7661,   # non-breaking space  U+00A0
  (0xC2,0xB2): 72,     # superscript two     U+00B2
  (0xC2,0xB3): 11,     # middle dot/sup three region
  (0xC2,0xB0): 19,     # degree sign         U+00B0
  (0xC2,0xBD): 38,     # one half            U+00BD
  (0xC2,0xBE): 4,      # three quarters      U+00BE
  (0xC2,0xBC): 4       # one quarter         U+00BC
}
```

Encoding round-trip confirmation (run locally, then deleted):

```
"a\xa0b\xb1c\xb7d".encode("utf-8")      -> b'a\xc2\xa0b\xc2\xb1c\xc2\xb7d'
"a\xa0b\xb1c\xb7d".encode("iso-8859-1") -> b'a\xa0b\xb1c\xb7d'
locale.getpreferredencoding(False)      -> UTF-8
```

So a single Latin-1 `0xA0` character, written through the UTF-8 default of
`open(..., "w")`, lands on disk as `0xC2 0xA0`. Decoding those bytes back as
Latin-1 yields A-circumflex plus non-breaking space, which is exactly the
trailing artifact.

### The trailing stray (below the buttons)

The trailing A-circumflex sits in the result placeholder div emitted by
`add_result_div`. Hexdump of
`site_docs/biochemistry/topic03/downloads/selftest-WOMC-amino_acids_properties.html`
at offset 7863:

```
6d 6f 6e 6f 73 70 61 63 65 3b 22 3e c2 a0 3c 2f 64 69 76 3e 0a 3c 2f 66 6f 72 6d 3e
m  o  n  o  s  p  a  c  e  ;  "  >  ..  ..  <  /  d  i  v  >  \n <  /  f  o  r  m  >
```

The placeholder is the very last child before `</form>`, so the artifact
renders on its own line just below the Check Answer and Reset buttons. The
emitter is
`html_functions.py`:

```
html_content = f"<div id='result_{crc16_text}' {style}>&nbsp;</div>\n"
```

Note the engine SOURCE for this div is the ASCII entity `&nbsp;`. Running the
current engine directly (probe run locally, then deleted) confirms
`add_result_div` and `escape_non_iso_8859_1` both leave the literal string
`&nbsp;` untouched. Yet the on-disk WOMC file carries a raw `0xC2 0xA0` in that
exact slot while the FIB file
(`selftest-which_amino_acid-FIB.html`) still carries the literal ASCII
`&nbsp;`. The difference proves that the affected files passed through an
entity-decoding step (an HTML parse round-trip or `html.unescape`) somewhere in
their generation, which turned `&nbsp;` into a raw U+00A0 character before the
UTF-8 save. Decoder candidates inside qti-package-maker:
`common/string_functions.py` line 409 (`html.unescape`) and lines 462-466
(`lxml.html.fromstring` + `lxml.etree.tostring(encoding="unicode")`). The
result is the same byte pattern regardless of which one ran.

### The inline corruption

Inline cases share the identical mechanism but originate in the upstream
`question_text` rather than the engine. The plus-minus, middle dot, and degree
symbols in question content are Latin-1-range Unicode characters (U+00B1,
U+00B7, U+00B0). `escape_non_iso_8859_1` passes them through unescaped:

```
escape_non_iso_8859_1("polar covalent bond +/- O-H middle-dot O")
   leaves U+00A0, U+00B1, U+00B7 as raw single bytes
```

(In the probe the input non-breaking space, plus-minus, and middle dot all
survived as raw `\xa0`, `\xb1`, `\xb7`.) A representative inline hit, in
`site_docs/laboratory/topic02/downloads/selftest-solution-molarity-mol_weight-numeric.html`,
again shows the result-div `0xC2 0xA0`, and the numeric tolerance messages add
`0xC2 0xB1` from the upstream `question_text`.

### Charset / serving

`mkdocs.yml` adds no charset override and uses the mkdocs-material default
`<meta charset="utf-8">`, so the BUILT page is UTF-8. The corruption is baked
into the fragment bytes on disk before the build, not introduced by the served
charset. The contributing inconsistency is that
`bioproblems_site/selftest_manifest.py` line 127 opens these same files with
`encoding="iso8859-1"`, confirming the project treats the fragments as Latin-1
in at least one path while the engine wrote them as UTF-8. That mismatch is the
classic decode-as-Latin-1 trigger that turns `0xC2` into A-circumflex.

## Root cause

ENGINE. Two engine-side defects combine:

1. Escaping gap: `escape_non_iso_8859_1`
   (`html_functions.py`)
   escapes only characters above U+00FF, leaving the entire U+0080-U+00FF
   Latin-1 block (non-breaking space, plus-minus, middle dot, degree,
   fractions) as raw characters.
2. Encoding mismatch: `save_package`
   (`engine_class.py`)
   writes with the platform default (UTF-8). The escape function is named and
   designed for an ISO-8859-1 byte stream, but the file is saved as UTF-8, so
   the surviving Latin-1 characters become `0xC2`-prefixed UTF-8 sequences.

The upstream question CONTENT supplies the inline Latin-1 characters, and an
upstream entity-decode step supplies the result-div non-breaking space, but
neither would surface as mojibake if the engine escaped the full Latin-1 block
or wrote a consistent charset. The engine is the correct single place to fix.

## Recommended fix location

`qti_package_maker/engines/html_selftest/html_functions.py`, function
`escape_non_iso_8859_1`, lines 25-31 (specifically the encode target on line
31). Escape the full non-ASCII range to numeric entities instead of only
characters above U+00FF, for example by encoding to ASCII with
`xmlcharrefreplace` so that U+00A0, U+00B1, U+00B7 and friends become
`&#160;`, `&#177;`, `&#183;`. That keeps the on-disk bytes pure ASCII and
makes them charset-agnostic, which neutralizes both the trailing and inline
artifacts in one change. Pair it with making `save_package`
(`engine_class.py` line 37) declare an explicit encoding so intent is no longer
left to the platform default.

## Secondary contributors

- The result-div placeholder literal `&nbsp;`
  (`html_functions.py`)
  is decoded to a raw non-breaking space by an upstream entity-decoding pass
  (`html.unescape` at `common/string_functions.py` line 409, or the lxml
  round-trip at lines 462-466). Emitting `&#160;` instead of `&nbsp;`, or
  avoiding the decode pass on self-test HTML, removes the trailing artifact at
  its source even before the escape fix.
- `bioproblems_site/selftest_manifest.py` line 127 reads the fragments with
  `encoding="iso8859-1"`, a Latin-1 assumption that conflicts with the engine's
  UTF-8 write and demonstrates the decode-as-Latin-1 path that renders
  A-circumflex.
- Upstream question generators that embed raw U+00B1, U+00B7, U+00B0, and
  fraction characters in `question_text` are the source of the inline
  corruption; once the engine escapes the full Latin-1 block they become
  harmless numeric entities, but using ASCII entities at authoring time is the
  cleaner long-term posture.

## Confidence and what would raise it

Confidence is HIGH for the byte mechanism and the engine fix location. The
byte scan, the encode round-trip, and the direct hexdump of the trailing token
are all decisive and reproducible. What would raise it from high to certain:
add a unit-level reproduction that feeds a non-breaking space, plus-minus, and
middle dot through `escape_non_iso_8859_1` and asserts the output is pure ASCII
(it currently is not), and a `git log -p` trace pinning the exact upstream
entity-decode call that converts the result-div `&nbsp;` to a raw character in
the generation pipeline.

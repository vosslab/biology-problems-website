# BPW flat self-test retirement

Date: 2026-10-09

## Result

BPW builds no longer generate standalone self-test HTML. The manifest reads
reachable topic-page `data-bbq` declarations and validates the corresponding
nonempty banks. Browser WASM rendering, grading, completion storage, and package
downloads retain their existing implementation.

Removed 482 flat HTML files (16,031,024 bytes), the unused native QPM bundle,
conversion stages and timing entries, and `-H/--selftests-only`.
`-I/--indexes-only` retains subject/topic selection and dry-run behavior.
The WASM refresh helper now copies only the browser distribution.

## One-time migration verification

Baseline BPW revision: `6d6c5f8e947c24929f2dae137718ab20e8883f4e`.

Before deleting any artifacts, the replacement manifest matched the baseline
after projecting every row to `questionId`, `pagePath`, `subjectKey`,
`topicKey`, and `topicTitle`. Comparison included the envelope and row order:
482 placements, 411 bank identities, and 57 topics. Version remains 2 and source
remains `reachable-topic-pages`. Unused `crc`, `questionFingerprint`, and
`selftestPath` fields were intentionally removed.

SHA256 of the complete projected manifest serialized with
`json.dumps(manifest, sort_keys=True).encode()`:

`505a5d99b3863bdd6093a3d90bb7fe666e811488f489aebdf858e64b18c934bf`

The same comparison passed after global and scoped index regeneration.
All 57 regenerated topic pages differ only by removal of `data-selftest`.
Hashes of 760 BBQ, PGML, companion, and vendored WASM files remained unchanged.
The source tree and built site contain no retired flat HTML files or references.

The original manifest, artifact inventory, hash inventory, native bundle, and
standalone reference HTML were saved outside the site before deletion:

`/var/folders/32/jn37sr213255rv_yn8l58gnh0000gn/T/bpw-flat-retirement-o4ho6n_o`

The baseline files also remain recoverable from the Git revision above.

These comparisons proved this migration; their counts and hashes are not
permanent test expectations. Scoped builds retain other topics' existing rows
directly. The committed manifest was regenerated, so merges need no legacy-field
stripping. Bank checks cover readable question data and valid declarations;
the local build adds no separate symlink policy for repository-owned inputs.

## Validation

- Global and scoped `build_site.py -I` builds passed without native QPM or flat HTML.
- Both normal and index-only CLI dry runs preserved all tracked bytes and mtimes.
- A normal forced build of one genetics CSV row passed in an isolated checkout,
  including BBQ/PGML generation, topic rendering, reconciliation, manifest output,
  and row-completion timing. It produced no flat self-test HTML.
- Before the KISS review below, all 3,270 Python tests passed in an isolated copy.
  The original checkout's vendored header collector cannot handle an unstaged
  deleted Markdown file: it opens the removed vendor README before checking
  existence. The isolated copy's index includes only current files; the user's
  Git index was left untouched.
- Three Node progress/storage/correctness checks and the orphan-reconciliation
  end-to-end check passed.
- All seven Chromium lifecycle and package-download tests passed serially and
  with four workers. The default Python development server reset asset connections
  under concurrent load; the parallel acceptance run used a temporary server with
  `ThreadingHTTPServer.request_queue_size = socket.SOMAXCONN`.
- Fresh Firefox contexts with cache disabled passed MATCH selection, feedback,
  Reset, and New version at 1280 px and 390 px, in light and dark modes. No page
  errors or horizontal overflow were observed. Screenshots and results were
  retained under `/var/folders/32/jn37sr213255rv_yn8l58gnh0000gn/T/bpw_fresh_firefox_0GAXEU`.

These checks justified no additional BPW rendering changes. QPM Python/Rust
parity remains a separate upstream responsibility. No remote publication or
commit was performed.

## KISS review

Removed the unused artifact-naming wrapper and 14 permanent cases covering
duplicate naming, already-covered filesystem behavior, and a speculative symlink
restriction. Removed legacy-field stripping and redundant sorting. No new options,
abstractions, or permanent tests were added.

After simplification, 64 focused permanent tests passed. One temporary check in
`tests/_temp/` confirmed that global generation and a scoped dry run both reproduce
the current manifest and leave the output untouched; the check was then removed.
Pyflakes and `git diff --check` passed. The broader build and browser results above
precede this review; rendering code was unchanged.

# Phase 1 and 2 integration

Source plan: [i-want-to-explore-optimized-spindle.md](../i-want-to-explore-optimized-spindle.md).
Decisions: [optimized_spindle_execution.md](optimized_spindle_execution.md).

## Decision

Accept the current combined Phase 1/2 source integration. Fresh isolated canonical generation,
full topic/manifest composition, MkDocs build, and all three retained browser checks pass.
This decision combines the earlier successful full-export evidence with the new source/runtime
acceptance below; it does not repeat the full exporter benchmark or full pytest suite.

The earlier integration rejection is superseded. The user confirms intentionally restoring
`site_docs` generated outputs for code-only review. The missing wrappers and bank metadata in
that snapshot therefore do not establish a source regression or a defective default writer.
Earlier recovery occurred before that clarification. This fresh acceptance writes no live
`site_docs` outputs and makes no claim that the intentionally restored live generated tree is
currently deployable. Regenerating/publishing it remains a separate action.

Acceptance covers Phases 1 and 2 only. Phase 3a scientific gallery acceptance, browser packaging,
and Blackboard Ultra import/grading remain separate gates. Phase 3b has not started.

## Earlier evidence retained

[optimized_spindle_build_validation.md](optimized_spindle_build_validation.md) establishes:

- The initial default build returned zero but failed 13 Blackboard renderer launches. Its
  unrestricted retry completed those 13 exports with zero artifact failures and 25 legitimate
  unsupported text skips. The 94.099-second retry includes cached work and does not establish
  whole-build speedup against the historical 1183-second workload.
- Matched unchanged-source measurement covers eight banks, 370 questions, four formats,
  and three alternating rounds. Native median 12.115 seconds versus Python 21.810 seconds
  means about 44.5% less converter elapsed time on that workload. Unsupported text pairs
  are excluded symmetrically. All 96 generated ZIPs have clean CRCs, parsed XML, matching
  question counts, and successful package checks.
- Scientific question bodies, choices, grading associations, numeric tolerances, and FIB
  answers are preserved. Raw XML inspection confirms all 50 MATCH items despite inspection
  reader aggregation deduplicating one item. This does not justify CRC equality as a gate.
- The recorded fresh full pytest execution reports 6075 passed in 5.49 seconds. This review
  reads that receipt; it does not run a second full suite.

[optimized_spindle_phase2_acceptance.md](optimized_spindle_phase2_acceptance.md) records the
complete earlier 482-bank rollout, real-WASM A/B/A grading/completion journey, no WASM before
click, retained v1 records, external dependency readiness/retry, and one-time reload/multi-slot
probes. Those broader probes remain separate earlier evidence; they are not repeated here.
Fresh Phase 1/2 specification and quality reviews are separately manager-owned.

D8's synthetic prefixed-choice CRC discrepancy remains upstream-owned because the real website
inventory finds no affected choices. Rust QPM remains the canonical grading/identifier owner.
No website CRC translation or completion compensation is introduced.

## Isolation and consumed source

Evidence root: `/private/tmp/optimized_spindle_phases12_20261009/`.
Project copy: `biology-problems-website/` beneath that root.
`copy_receipt.json` records the input scope: current Python source/configuration/task inputs,
current site assets, 482 BBQ banks, and 482 existing native selftest HTML files. ZIPs,
human-readable/PG/PGML downloads, `.git`, and ignored spike outputs are omitted.
The copied permanent browser spec is unchanged. The copy's `node_modules` and sibling Rust
checkout are read-only dependency links; generated content and test outputs stay isolated.

`source_identity.json` confirms all 70 copied production Python modules/build entrypoint,
site JavaScript files, and browser spec match current live source bytes after acceptance.
Native binary SHA256 remains
`03c04dde59037d6ba860674388ddb2f17f852c5a6598eaa8131fedf6466364f3`.
The 18-file vendored distribution matches its consumed-file SHA256 receipt. `sourceCommit`
remains null with its provenance qualification. Hashes identify consumed bytes rather than
create compatibility or equivalence requirements. This review consumes the already rebuilt
native/WASM artifacts documented in the Phase 2 report; it does not rebuild them again.

## Canonical generation and MkDocs

From the isolated project directory, run:

```bash
source source_me.sh && python3 build_site.py -H -S genetics -T topic01 --cli
source source_me.sh && python3 isolated_indexes.py
source source_me.sh && python3 isolated_inventory.py
source source_me.sh && mkdocs build
```

The scoped `-H` exits 0 and regenerates all three real Genetics Topic 01 selftests through
current native `bbq-converter`; it also finalizes the scoped manifest. Receipt:
`selftests_scoped.log`. All other selftests are existing copied inputs, not newly generated
by this acceptance.

Initial unadapted `build_site.py -I --cli` reaches homepage finalization but exits 1 because
Git history is unavailable in the deliberately Git-free copy. Receipt: `indexes_all.log`.
`isolated_indexes.py` is a temporary runner that redirects only `source_history.git` lookups
for the copy to the live checkout read-only, then invokes unchanged `build_site.main(["-I",
"--cli"])`. Repository discovery and all generation paths still target the isolated project.
This is an isolation accommodation for homepage history, not a production workaround.

That full index run exits 0: 57 topic pages and 15 metadata outputs in 21 seconds.
`indexes_all_with_history.log` records its result. The existing ambiguous macromolecule-bank
homepage warning remains non-fatal. Native includes remain direct include directives.
MkDocs exits 0 and builds the isolated static site in 3.58 seconds; `mkdocs_build.log` is the
receipt. Omitted download packages are outside this narrow composition/runtime acceptance.

`composition_inventory.json` and its temporary `isolated_inventory.py` producer record:

| Contract | Fresh isolated result |
| --- | --- |
| Topic pages generated | 57 |
| Reroll wrappers | 482 |
| Manifest question rows | 482 |
| Missing manifest bank IDs | 0 |
| Wrapper/manifest bank sets | Exactly equal |
| Missing BBQ sources or native includes | 0 |
| Native question CRC/manifest mapping mismatches | 0 |
| Wrapper bank URI/include mapping mismatches | 0 |

The inventory parses wrapper attributes and direct include paths, checks every mapped bank
and native CRC, and verifies the vendored file receipt. Counts describe this snapshot;
they do not introduce permanent inventory thresholds.

## Fresh browser acceptance

Serve the already built isolated site, then run the unchanged permanent spec directly:

```bash
source source_me.sh && python3 -m http.server 8847 --bind 127.0.0.1 --directory site
source source_me.sh && PORT=8847 npx playwright test tests/playwright/selftest_reroll.spec.ts --workers=1
```

The managed Playwright configuration reuses this explicitly built isolated HTTP site.
Initial sandbox launch fails before assertions with Chromium MachPortRendezvous permission
denied (1100); `playwright_isolated.log` records that infrastructure failure. The authorized
unrestricted rerun exits 0: **3 passed in 2.1 seconds**.
Receipt: `playwright_isolated_unrestricted.log`. The HTTP server is stopped after acceptance.

The real published-bank/real-WASM journey verifies no WASM request before click; conversion
and correct A grading; distinct B initially incomplete with unchecked controls and blank
feedback; incorrect B with no stored completion; correct B with separate A/B records under
`selftest_progress_v1`; and return to completed A with fresh answer controls/feedback.
No page errors occur in that journey. The two separate dependency checks verify ordered
external-script readiness and failure/retry through converter stubs; they do not claim another
real-WASM grading journey.

## Boundaries and closeout

This review changes only this report plus isolated temporary evidence. No live generated
pages, assets, banks, packages, production code, permanent tests, human guidance, or Git/index
state are changed. The manager's documentation owner records the report edit in the changelog.
The complete prior export/suite evidence and fresh isolated source composition/runtime result
support Phase 1/2 acceptance. Whole-plan completion still requires the named Phase 3 gates.

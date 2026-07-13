# Release history

## v26.07 - 2026-07-12

### Highlights

- Expanded the curated BBQ task controls to 432 placements across supported subjects.
- Added root-level batch coordination with deterministic task discovery and runtime
  reporting.
- Added a Playwright smoke suite that discovers and validates every rendered route.
- Added standalone self-test regeneration and browser-local completion tracking.

### Notable fixes

- Reviewed all 500 problem-set titles and made matching, TFMS, and parameterized
  variants easier to distinguish.
- Restored omitted genetics variants and replaced bare defaults with explicit gene-tree,
  deletion-mutant, DNA-profiling, and test-cross configurations.
- Consolidated the shell environment around `source source_me.sh && python3`.

### Validation

- The repository Python suite covers code quality, metadata, navigation, rendering,
  reconciliation, and documentation links.
- The Playwright smoke suite checks the MkDocs shell and interactive self-tests across
  all sitemap routes.

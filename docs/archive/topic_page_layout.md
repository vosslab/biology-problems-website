# Topic page layout

## Outcome

Make every topic page use the same compact chapter header followed by clearly separated,
numbered problem-set sections. Keep breadcrumbs, title, topic summary, LibreTexts reference, and
all existing bank controls and question content.

## Approved scope

- Remove chapter-top self-test progress and Bloom scale panels.
- Reduce excess space around the breadcrumbs, title, summary, and LibreTexts reference.
- Number problem headings while preserving existing heading anchors and links.
- Keep problem-bank downloads, type labels, Bloom labels, completion and practice controls,
  questions, and grading behavior intact. Adjust only numbered headings and quiet sheets around
  them.
- Apply the same layout to all topic pages. Topic 07 is an internal trial, not a stopping point.

## Ownership and decisions

- Renderer: `render_topic_sheets`; correction: `fix_sheet_containment`.
- CSS and spacing: `style_topic_sheets`; correction: `correct_topic_spacing`.
- Browser review: `browser_layout_review`; manager coordinated and reviewed browser evidence.
- Documentation closeout: `layout_docs` and `layout_docs_closeout`.
- Independent reviews: `corrected_spec_review`, `layout_quality_review`, and
  `layout_integration_review` passed. Integration review confirmed all 57 pages, 499 bank
  sections, 556 heading IDs, 499 download containers, focused checks, and composed screenshots,
  with no findings or architecture drift.
- Decision: keep the generated bank interface intact and limit its visual change to numbered
  headings and separation between bank sections. The shared layout applies to all topic pages.
- No human approval or interaction milestone is required.

## Markup contract

The shared outer `.topic-page` contains `.topic-introduction` and the problem-set sections.
Numbered headings retain their existing IDs and link targets. Styles own layout; renderer output owns
semantic headings and bank content.

## Verification and status

- Shared renderer covers all 57 topic pages and 499 bank sections. Temporary census checks confirm
  every bank remains inside its section; 556 heading IDs and all 499 download targets are preserved.
- No question-bank, cached-title, or metadata sources changed. Bank controls, labels, questions, and
  grading behavior remain intact; hidden boolean serialization was normalized equivalently.
- Baseline and final MkDocs builds pass. The targeted Python suite passes 542 checks; the Chromium
  suite passes 93 tests. Node progress-storage and DOM checks pass.
- Reproduce Python verification with:

  ```bash
  source source_me.sh && python3 -m mkdocs build
  source source_me.sh && python3 -m pytest \
    tests/test_topic_page_generate_downloads.py \
    tests/test_generated_title.py \
    tests/test_selftest_manifest.py \
    tests/test_mkdocs_metadata_sync.py \
    tests/test_mkdocs_nav.py \
    tests/test_markdown_links.py \
    tests/test_import_requirements.py \
    tests/test_function_typing.py \
    tests/test_pyflakes_code_lint.py -q
  ```

- Reproduce browser and Node verification with:

  ```bash
  bash devel/run_playwright_tests.sh selftest_reroll.spec.ts selftest_clear.spec.ts \
    package_download.spec.ts smoke.spec.ts
  node tests/selftest_progress_storage_test.mjs
  node tests/selftest_progress_dom_test.mjs
  ```

  Browser run: 93 passed. Python suite: 542 passed. The local run used the repository bootstrap
  and an already-running helper server because the standalone MkDocs command selected Python
  without the required plugin.
- Browser review covers desktop, light and dark themes, 390px mobile, 200% text, actual deep links
  and downloads, completion persistence, clear, answer, reroll, and wide tables. No overflow or
  browser errors; existing heading font and control styles are preserved. Unrelated home,
  Genetics landing, and Finder geometry remain unchanged.
- Fresh specification, layout-quality, and integration reviews pass. Integration review confirms
  all-page and bank-section coverage, preserved heading IDs and download containers, focused checks,
  and composed screenshots, with no findings or architecture drift.

**Status: complete.** Closeout evidence is recorded in [CHANGELOG.md](../CHANGELOG.md). This item
is archived after completion.

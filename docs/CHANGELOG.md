# Changelog

## 2026-04-30

### Behavior or Interface Changes
- Added two short path aliases to
  [bbq_control/bbq_settings.yml](../bbq_control/bbq_settings.yml):
  `bp_mcs` (resolves to `{bp_root}/multiple_choice_statements`) and
  `bp_match` (resolves to `{bp_root}/matching_sets`). Replaced the older
  long-named `multiple_choice_statements` and `matching_sets` aliases (the
  `script_aliases` and `pgml_script_map` blocks now reference the short
  names). Substituted `{bp_root}/multiple_choice_statements` -> `{bp_mcs}`
  and `{bp_root}/matching_sets` -> `{bp_match}` across
  [bbq_control/task_files/biochem_tasks1.csv](../bbq_control/task_files/biochem_tasks1.csv),
  [bbq_control/task_files/biochem_tasks2.csv](../bbq_control/task_files/biochem_tasks2.csv),
  and [bbq_control/task_files/biochem_tasks3.csv](../bbq_control/task_files/biochem_tasks3.csv)
  to shorten frequent path prefixes. No code changes were required because
  `resolve_alias_map` in
  [bbq_control/run_bbq_tasks.py](../bbq_control/run_bbq_tasks.py)
  already supports recursive `{key}` expansion.

### Developer Tests and Notes
- Verified with `python3 bbq_control/run_bbq_tasks.py -t
  bbq_control/task_files/biochem_tasks1.csv -s bbq_control/bbq_settings.yml
  -n -F -l 3` that the dry-run resolves task paths to the expected
  absolute filesystem locations under
  `~/nsh/PROBLEMS/biology-problems/problems/...`.

## 2026-04-22

### Fixes and Maintenance
- Updated [bbq_control/task_files/biochem_tasks1.csv](../bbq_control/task_files/biochem_tasks1.csv)
  and [bbq_control/task_files/biochem_tasks3.csv](../bbq_control/task_files/biochem_tasks3.csv)
  to match the 2026-04-22 biology-problems changelog entry that moved lipid
  generators into `problems/biochemistry-problems/lipids/` and replaced
  `fatty_acid_naming.py` with four new generators
  (`fatty_acid_{naming,match}_{omega,delta}.py`). Repathed
  `which_hydrophobic-simple.py`, `which_lipid-chemical_formula.py`, and
  `quick_fatty_acid_colon_system.py` under `lipids/`, and replaced the
  retired `fatty_acid_naming.py` topic12 row with the four new generator rows.

## 2026-04-18

### Behavior or Interface Changes
- Redesigned the `generate_pages.py` CLI from two mutually-exclusive mode flags to three composable build-axis flags plus one alias. Old flags removed: `--indexes-only`, `--topics-only`, `--adopt-existing`. New flags: `-S`/`--subject-indexes`, `-T`/`--topic-pages`, `-G`/`--generate-downloads`, `--full`. The default (no flag) is now the fast subject-indexes + nav path (was: full run). Migration mapping: old `./generate_pages.py` full run -> `./generate_pages.py --full`; old `--indexes-only` -> bare `./generate_pages.py` (or `-S`); old `--topics-only` -> `-T -G`. Net-new workflow: bare `-T` regenerates `topic??/index.md` layout without rebuilding any download artifact files (fast middle path that did not exist before). `-G` without `-T` and `--full` combined with any of `-S`/`-T`/`-G` are hard argparse errors. Wired via [generate_pages.py](../generate_pages.py), [bioproblems_site/pipeline.py](../bioproblems_site/pipeline.py), [bioproblems_site/topic_page.py](../bioproblems_site/topic_page.py). Rationale: the old `--indexes-only`/`--topics-only` pair hid the real cost axes, and the old default always paid for the slow download-artifact regeneration even for routine top-level maintenance.

### Fixes and Maintenance
- Dropped the `adopt_existing` kwarg from `bioproblems_site.pipeline.run` and `_write_subject_index`. All 6 live subject `index.md` files now carry the generated marker, so the one-shot migration escape hatch has no remaining use. The marker check still fires if a future hand-authored subject index appears; its error now points at "delete and regenerate" rather than the removed flag.
- Also gated the per-BBQ selftest HTML regen in [bioproblems_site/topic_page.py](../bioproblems_site/topic_page.py) `update_index_md` on `generate_downloads`. It was unconditionally removing + re-invoking `bbq_converter.py` on every run, which dominated `-T` runtime. Now it reuses the existing selftest file when present (only rebuilds if missing, so the `{% include %}` on line 717 never breaks); `-STG` / `--full` still force the rebuild.
- Replaced the unused `RenderOptions.no_downloads` field in [bioproblems_site/topic_page.py](../bioproblems_site/topic_page.py) with `generate_downloads: bool = False` (opposite polarity, matches the new CLI flag). Threaded through `render_all` -> `update_index_md` -> `generate_download_button_row` as a keyword argument. When `False`, the per-format loop skips buttons for missing files and never calls `create_downloadable_format` (including the stale-source rebuild path).

### Decisions and Failures
- Picked `--generate-downloads` (positive form, default off) over `--no-generate` / `--no-downloads`. "Downloads" alone reads like "fetch from the internet"; the flag is about locally generating downloadable artifact files. Default off matches the measured timing: the bare run is under a second, download generation dominates the slow path.
- Chose a CLI break over a soft-landing deprecation. The new `--full` alias is what users who ran bare `./generate_pages.py` should use instead; the explicit error on `-G` without `-T` is preferred over a silent ignore.

### Developer Tests and Notes
- Added [tests/test_topic_page_generate_downloads.py](../tests/test_topic_page_generate_downloads.py): one minimal pytest that pre-seeds a topic folder and asserts `generate_download_button_row(..., generate_downloads=False)` writes no files. Pins the one behavior that actually matters for the new `-T` (without `-G`) fast path.
- Full pyflakes gate (`pytest tests/test_pyflakes_code_lint.py`) green after the refactor.

### Additions and New Features
- Added [docs/UI_UX_REVIEW_2026-04-18b.md](UI_UX_REVIEW_2026-04-18b.md), a fresh rendered-site UI/UX pass after the evening's emoji/LibreTexts/Daily Puzzles changes (supersedes the deleted first-pass doc). Net result: zero outstanding source changes from this review; both initially flagged "Major" findings (subject-index images missing `alt`, external links missing `rel="noopener"`) turned out to be over-broad harness checks - the generated HTML was already correct. Two minor follow-ups remain (ASCII arrow on Daily Puzzles cards, single-item numbered list on `/other/`) plus a "worth revisiting" note about adding a small subtitle on the home page to explain the Subjects-vs-Additional-Topics distinction (Biochemistry/Genetics are complete; the rest are partial).
- Expanded [tests/ui_ux_review.mjs](../tests/ui_ux_review.mjs) coverage from 17 to 30 URLs (60 visits across desktop+mobile): all hand-authored pages (home, 4 daily puzzles + landing, 3 tutorials + landing, author, license) plus a 1-2 topic sample per subject (11 of 42 generated topics) plus the search-results pseudo-page. Removed the dead `biotechnology_orphan` row (orphan was deleted earlier today). All 60 visits return HTTP 200.

### Fixes and Maintenance
- Tightened three checks in [tests/ui_ux_review.mjs](../tests/ui_ux_review.mjs) that were producing false-positive findings:
  - `imgsNoAlt` now requires the `alt` attribute to be truly absent (`getAttribute('alt') === null`); empty-string `alt=""` is the standard decorative-image marker and was being mis-flagged. Re-run: `noAlt=0` on every page.
- Changed the LibreTexts icon `alt` from `""` (decorative) to `"LibreTexts"` in both [bioproblems_site/subject_index.py](../bioproblems_site/subject_index.py) and [bioproblems_site/topic_page.py](../bioproblems_site/topic_page.py). The aria-label sits on the `<a>` not the `<img>`, so a meaningful image alt is more defensive (survives refactors that drop or change the anchor label). Regenerated subject indexes via `generate_pages.py --indexes-only`; 22 icons updated across biochem/genetics.
  - `externalNoRel` now requires both `target="_blank"` AND a missing `noopener` rel; `rel="noopener"` only matters for new-tab links. Re-run: `extNoRel=0` on every page.
  - Dark-mode capture now uses a fresh Playwright context with `colorScheme: 'dark'` plus an `addInitScript` that pre-seeds `localStorage.__palette` (Material's palette JS reads localStorage at page load before paint, so per-page evaluate-then-reload was always too late). `home_dark.png` and `subject_biochem_dark.png` now render the slate scheme correctly.
- Added `visibleTables` and `detailsBlocks` metrics to [tests/ui_ux_review.mjs](../tests/ui_ux_review.mjs) so the report distinguishes on-load tables from tables nested inside collapsed `<details>` panels. Confirmed `visibleTables=0` on every topic page; the prior alarm about 88-table mobile overflow was a false signal from counting hidden example tables.

### Decisions and Failures
- **Crucial finding for future agents**: when the harness flags `imgsNoAlt` or `extNoRel`, inspect the source HTML before "fixing" the page generator. Every existing `target="_blank"` link in generated HTML already carries `rel="noopener"` (or `noopener noreferrer`), and decorative `<img>` tags carry an `alt` attribute (now `"LibreTexts"` for the LibreTexts icon). Verify with `curl http://127.0.0.1:8765/<page>/ | grep '<a'` before changing source.
- The per-question 4-button download row (Blackboard Learn TXT, Blackboard Ultra QTI, Canvas/ADAPT QTI, Human-Readable TXT) on long topic pages is dense on mobile, but it is the page's primary action - downloading the question into the reader's LMS - and is intentional. Logged as Minor in the review for future polish work, not as a bug to hide.
- The Subjects vs Additional Topics split on `site_docs/index.md` is intentional: Biochemistry and Genetics carry complete coverage; the other four subjects are partial. A previous attempt to add an explanatory subtitle was deemed unnecessary and removed; the review notes this is worth revisiting later for new-reader legibility.

### Additions and New Features
- Added [site_docs/daily_puzzles/index.md](../site_docs/daily_puzzles/index.md), a landing page for the Daily Puzzles section with a Material grid-card overview of the four puzzles (Peptidyle, Deletion mutants, Mutant screen, Biomacromolecules) plus a short "How it works" section covering the local-midnight rotation and browser-local stats storage. Wired it into the Daily Puzzles nav group in [mkdocs.yml](../mkdocs.yml) as the first child so Material's `navigation.indexes` uses it as the section landing page. Also added the new URL to the page list in [tests/ui_ux_review.mjs](../tests/ui_ux_review.mjs).
- Added a `_subject_display_labels` test to [tests/test_mkdocs_nav.py](../tests/test_mkdocs_nav.py) covering the new list-shape path (value is a list whose first entry is the subject index), so icons in subject labels stay preserved across nav regeneration.

### Behavior or Interface Changes
- Restored emoji icons on the six subject labels in [mkdocs.yml](../mkdocs.yml) (`🧪 Biochemistry`, `🪰 Genetics`, `🔬 Laboratory`, `🧬 Molecular Biology`, `🎲 Biostatistics`, `📚 Other`) so every top-level nav entry has a glyph, matching the FontAwesome prefixes already on Home / Daily Puzzles / Tutorials / Author / License. Fixes the [minor] "unbranded subjects" finding from [docs/UI_UX_REVIEW_2026-04-18.md](UI_UX_REVIEW_2026-04-18.md).
- Reworked the LibreTexts link in [bioproblems_site/subject_index.py](../bioproblems_site/subject_index.py) `_libretexts_icon_anchor`: it now renders as `[logo] Chapter U.C` (e.g. `Chapter 1.2`) inside an `<a class="lt-link">` with LibreTexts brand blue (`#127bc4`), a hover background, a "Open on LibreTexts (new tab)" tooltip, and `rel="noopener noreferrer"`. Replaces the prior logo-only anchor that readers could not interpret. New `.lt-link` CSS in [site_docs/assets/stylesheets/custom.css](../site_docs/assets/stylesheets/custom.css). All subject indexes regenerated via `generate_pages.py --indexes-only`.
- Added `md_in_html` to `markdown_extensions` in [mkdocs.yml](../mkdocs.yml) so the Daily Puzzles landing page can use Material's `grid cards` layout (Markdown inside HTML blocks).

### Fixes and Maintenance
- Generalized `_subject_display_labels` in [bioproblems_site/mkdocs_nav.py](../bioproblems_site/mkdocs_nav.py) to read subject labels from both shapes (string-valued `{"Biochemistry": "biochemistry/index.md"}` and list-valued `{"Biochemistry": ["biochemistry/index.md", ...]}`). The prior string-only path silently dropped hand-authored icons whenever `navigation.indexes` listed subject children.

### Decisions and Failures
- Chose "emoji on subjects, FontAwesome on utility rows" over uniform FontAwesome after user preference. Accepts a minor mixed-style cost on the top-level nav in exchange for keeping the existing personality (🧪, 🪰, 🔬, 🧬, 🎲, 📚) that readers in earlier commits had internalized.

### Behavior or Interface Changes
- Removed `navigation.sections` from [mkdocs.yml](../mkdocs.yml) `theme.features` so subject groups (Biochemistry, Genetics, Laboratory, Molecular Biology, Biostatistics, Other) render as collapsible sections again rather than a long always-expanded left rail.
- Scoped the `.lt-icon` CSS rule in [site_docs/assets/stylesheets/custom.css](../site_docs/assets/stylesheets/custom.css) to `.md-typeset img.lt-icon` with `height: 1em; max-height: 1.2em;` so the LibreTexts icon renders at text cap-height instead of full natural size; Material's `.md-typeset img` rule no longer wins on specificity.
- Topic pages (e.g., `/biochemistry/topic01/`) now render the LibreTexts icon (`.lt-icon`) next to the `**LibreTexts reference:**` link, matching the subject-index convention. Code in [bioproblems_site/topic_page.py](../bioproblems_site/topic_page.py).

### Fixes and Maintenance
- Dropped dead parameters in [bioproblems_site/topic_page.py](../bioproblems_site/topic_page.py): `get_topic_title(folder_path)` and `get_libretexts_link(topic_folder)` no longer accept the previously-ignored `topic_number` / `relative_topic_name` arguments. Single in-module caller updated.
- Dropped the never-used `save_prompt` argument from `generate_title_prompt` and `get_problem_title_from_file` in [bioproblems_site/problem_set_title.py](../bioproblems_site/problem_set_title.py) and removed the associated dead `with open('prompt.txt', 'w')` branch.

### Decisions and Failures
- Considered consolidating the three trailing boolean kwargs of `_write_subject_index` (`adopt_existing`, `dry_run`, `verbose`) into a new `WriteFlags` dataclass module; skipped because both call sites are already explicit and a dataclass only moves the keyword-arg typing around. Plan file: [conduct-a-deep-review-partitioned-pony.md](../../.claude/plans/conduct-a-deep-review-partitioned-pony.md) (WP-3c was gated as conditional).

### Developer Tests and Notes
- `pytest tests/ -q` green (1103 passed) after the cleanup.

### Additions and New Features
- Added `bioproblems_site/llm_helpers.py` (project-local seam over the vendored `local_llm_wrapper.llm` facade), mirroring `validate_ollama_model` and `create_llm_client` from the sibling `biology-problems` repo.
- Added `-O/--ollama` and `-m/--model MODEL` flags to `generate_pages.py`. `--model` implies `--ollama`; when set, `validate_ollama_model` runs once at startup before any topic page is rendered. The pipeline builds a single `LLMClient` and threads it through `RenameOptions.llm_client` -> `update_index_md(client=...)` -> `get_problem_set_title(client, ...)` -> `get_problem_title_from_file(client, ...)`. No per-call client cache; one client per `generate_pages.py` run.
- Added [devel/ui_ux_review.mjs](../devel/ui_ux_review.mjs), a Playwright driver that visits key mkdocs pages at desktop and mobile viewports, captures full-page screenshots into `test-results/ui_ux_review/`, and writes `report.json` with per-page metrics (status, H1 count, image count, missing alt text, tables, external links missing `rel=noopener`).
- Added [docs/UI_UX_REVIEW_2026-04-18.md](UI_UX_REVIEW_2026-04-18.md) capturing the findings of a rendered-site UI/UX pass against the Material theme.

### Behavior or Interface Changes
- Replaced ad-hoc `bioproblems_site/llm_wrapper.py` with the vendored `local_llm_wrapper` package (also on PyPI as `local-llm-wrapper`). `source_me.sh` now appends `~/nsh/local-llm-wrapper` to `PYTHONPATH` (after `source ~/.bashrc`, which clears it). Default LLM transport is now Apple Intelligence (matches sibling repo); Ollama is opt-in via `-O/--ollama` or `-m/--model`. Title generation is now capped at `max_tokens=200` -- intentional behavior change suitable for short titles; the old wrapper used the Ollama default.
- Added `test-results/` and `node_modules/` to `.gitignore` so Playwright screenshots and npm deps stay out of git.
- Initialized root `package.json` and installed `playwright` as a dev dependency (plus `chromium` browser via `npx playwright install chromium`) so the review script can run locally per [docs/PLAYWRIGHT_USAGE.md](PLAYWRIGHT_USAGE.md).

### Decisions and Failures
- User feedback during review: the repeated `(LibreTexts Unit X, Chapter Y)` labels on each subject index "stand out like a sore thumb"; findings doc now recommends replacing the text label with a compact LibreTexts logo icon (or a distinct brand-blue color if text is kept) so the word "LibreTexts" is not repeated ~20 times per page.
- Review flagged 25+ broken subject-to-topic links (`mkdocs serve` already warns about them), an orphan `biotechnology/` subject not in `mkdocs.yml` nav, inconsistent LibreTexts link styling across subject indexes, mobile download-button wall on generated topic pages, and missing `rel=noopener` on several `target=_blank` anchors (8 on `site_docs/author.md`, plus 1 each on a few topic and puzzle pages).
- Recommendation documented: reintroduce a generated `topics_metadata.yml` (question counts + LibreTexts URLs) alongside the existing subject `index.md` prose, so the generator can suppress links to empty topics and surface question-count chips. See findings doc for the full rationale.

### Developer Tests and Notes
- Ran `node devel/ui_ux_review.mjs` against `mkdocs serve -a 127.0.0.1:8765`; 32 page visits, all HTTP 200, 33 screenshots saved under `test-results/ui_ux_review/`.
- Applied reviewer-driven style/test fixes to the `bioproblems_site/` reorg: removed mutable module-level `BASE_DIR` global in `topic_page.py` (now threaded via `base_dir` parameter), removed re-export aliases for `git_paths` helpers, dropped dead commented-out code. Narrowed `llm_wrapper.get_vram_size_in_gb` try/except to not swallow broad exceptions; moved module-level asserts into `tests/test_llm_wrapper.py`. Converted `problem_set_title.py` to a library-only module (removed argparse, `main()`, `if __name__ == '__main__'`). Tightened `metadata._validate_libretexts` to use direct key access for required keys. Moved `detect_formats` filesystem scanning out of `formats.py` (now pure registry) into `scanner._detect_formats`. Replaced brittle exact-count assertion in `test_scanner.py` with behavioral property (more files -> higher count); converted `test_subject_index_render.py` helper into `@pytest.fixture` and switched to `startswith` check; passed explicit paths in `test_mkdocs_metadata_sync.py` to avoid CWD coupling. Deleted obsolete `tests/test_topic_page_parity.py`.
- Executed M1-M4 of the pipeline reorg plan. `pytest tests/test_metadata_loader.py tests/test_mkdocs_metadata_sync.py tests/test_scanner.py tests/test_subject_index_render.py tests/test_pyflakes_code_lint.py` is green (42 tests). `mkdocs build --strict` exits 0 with zero broken-link warnings. `python generate_pages.py --indexes-only` is idempotent.

### Additions and New Features
- Added `topics_metadata.yml` at repo root as the single source of truth for subject and topic metadata.
- Added the `bioproblems_site/` package with submodules `metadata`, `formats`, `scanner`, `subject_index`, `topic_page`, `pipeline`, `llm_wrapper`, `problem_set_title`. Importable logic lives here; no helper modules remain at the repo root.
- Added `generate_pages.py` at the repo root as the single page-generation CLI entrypoint. Thin argparse (83 lines); delegates to `bioproblems_site.pipeline.run`. Supports `--subject`, `--topic`, `--indexes-only`, `--topics-only`, `--adopt-existing`, `--use-icon`/`--legacy-libretexts-text`, `--dry-run`, `-q`/`-v`.
- Added `site_docs/assets/images/libretexts.png` (LibreTexts chapter icon) plus `.lt-icon` CSS. The generated subject indexes now render a compact icon anchor per topic instead of the repeated `(LibreTexts Unit N, Chapter M)` text. Icon anchors carry `aria-label` and `rel="noopener"`.
- Added per-topic `N questions` chip via a new `.topic-count` CSS class; chips derive from `bbq-*-questions.txt` scan at generation time, not mkdocs render time.

### Behavior or Interface Changes
- Enabled Material for MkDocs theme features `navigation.path`, `navigation.indexes`, `navigation.sections`, and `navigation.top` in `mkdocs.yml`. Breadcrumbs, collapsible subject sections, and back-to-top come from the theme, not generator-emitted HTML.
- Added `bioproblems_site/mkdocs_nav.py` plus a `tests/conftest.py` that puts the repo root on `sys.path` so `pytest tests/` works without `source source_me.sh`.
- Generated `site_docs/<subject>/index.md` pages are now authoritative and carry a generated-file marker as their first line; the generator refuses to overwrite a file without this marker unless `--adopt-existing` is passed.
- Subject index generation intentionally omits topics with zero questions (no `bbq-*-questions.txt` on disk), so broken subject-to-topic links caught by the UI/UX review are no longer possible in generated output. `mkdocs build --strict` now exits with zero missing-target warnings.

### Removals and Deprecations
- Deleted `bioproblems_site/llm_wrapper.py` outright (no deprecation stub; this repo's only caller, `problem_set_title.py`, was migrated in the same change). `Colors`, `extract_xml_tag`, `select_ollama_model`, `query_ollama_model`, `list_ollama_models`, `extract_response_text`, `get_vram_size_in_gb` are gone from this repo -- use `local_llm_wrapper.llm` (`extract_xml_tag_content`, `choose_model`, `LLMClient`, `get_vram_size_in_gb`) instead.
- Deleted `site_docs/biotechnology/` (orphan subject, not in `mkdocs.yml` nav, no topic pages). `grep -rn biotechnology site_docs/ mkdocs.yml` returns zero hits.
- Deleted root `generate_topic_pages.py` (replaced by `generate_pages.py`). The markdown-index parser, `_TOPIC_HEADING_RE`, `_LIBRETEXTS_RE`, `_DESCRIPTION_RE`, and `--metadata-source` argparse flag are all gone. YAML is the sole metadata source.
- Moved `llm_wrapper.py` -> `bioproblems_site/llm_wrapper.py` and `llm_generate_problem_set_title.py` -> `bioproblems_site/problem_set_title.py` via `git mv`. Neither is run directly.

### Decisions and Failures
- Picked Branch A of the M4 decision gate (theme breadcrumbs via `navigation.path`) and shipped the generated subject nav block in the same session. `bioproblems_site.mkdocs_nav` rewrites only the region between `# BEGIN GENERATED SUBJECT NAV` and `# END GENERATED SUBJECT NAV` markers in `mkdocs.yml`; the rest of the config is hand-authored. Guardrails: markers must appear exactly once, file is restored from backup if the rewrite would break YAML parsing, second run produces zero diff. Topic pages are back in nav so Material's `navigation.path` breadcrumb renders the full Home -> Subject -> Topic trail.
- Genetics topics render as `(LibreTexts Chapter N)` (no unit label); the YAML schema was relaxed to allow libretexts with `url` + `chapter` but no `unit` so chapter-only books round-trip correctly.
- Pyflakes caught an unused scanner import in `bioproblems_site/subject_index.py`; removed.

## 2026-04-13

### Additions and New Features
- Added `load_subject_topics()` parser to `generate_topic_pages.py` that reads `site_docs/<subject>/index.md` and extracts topic title, description, and LibreTexts link (URL, unit, chapter) per topic, with module-level caching.
- Added `_derive_libretexts_title()` helper that recovers chapter titles from LibreTexts URL slugs so the generated per-topic pages keep the "Unit X, Chapter Y: Chapter Title" link text.

### Behavior or Interface Changes
- `get_topic_title()`, `get_topic_description()`, and `get_libretexts_link()` in `generate_topic_pages.py` now read from the parsed subject `index.md` instead of `mkdocs.yml` / `topics_metadata.yml`. Source of truth for topic metadata is now the per-subject markdown file.
- Shrunk `mkdocs.yml` nav: each subject is one entry pointing at `<subject>/index.md`. Individual topic pages are reached via the subject landing page rather than an expanded sidebar tree.

### Removals and Deprecations
- Removed `topics_metadata.yml` (data now lives in each `site_docs/<subject>/index.md`).
- Removed `generate_subject_indexes.py` (previously generated subject index pages from the removed YAML; subject pages are now authored directly).

### Decisions and Failures
- Chose to make `site_docs/<subject>/index.md` the single source of truth for topic titles, descriptions, and LibreTexts links instead of keeping a parallel YAML. Rationale: the markdown already held the richest copy and was most pleasant to edit; the YAML was a mirror that kept drifting.

## 2026-03-30

### Additions and New Features
- Added `unit` and `chapter` fields to `topics_metadata.yml` for all biochemistry and genetics topics, matching the current LibreTexts course structure (Unit 1 Proteins, Unit 2 Enzymes, Unit 3 Macromolecules, Unit 4 Senses).
- Updated `build_link_markup()` in `generate_subject_indexes.py` to display "(LibreTexts Unit X, Chapter Y)" or "(LibreTexts Chapter Y)" on subject index pages, using the new YAML fields.
- Updated `get_libretexts_link()` in `generate_topic_pages.py` to return and display unit/chapter info in individual topic page LibreTexts reference links.
- Added `copy_sister_pgml()` function to `bbq_control/run_bbq_tasks.py` that automatically copies sister `.pgml`/`.pg` files from the source script directory to `{output_dir}/downloads/` after successful task execution.

### Behavior or Interface Changes
- Updated all biochemistry LibreTexts URLs to the new unit-based URL structure (e.g., `/01%3A_Unit_1_-_Proteins/1.01%3A_Molecules_of_Life`).
- Expanded biochemistry from 11 to 14 topics: split Enzyme Regulation into Enzyme Inhibition (topic08) and Enzyme Allostery (topic09), renumbered Carbohydrates to topic10, Nucleic Acids to topic11, added Lipids (topic12), Membranes and Membrane Proteins (topic13), and moved Human Senses to topic14.
- Updated `mkdocs.yml` nav section for the new 14-topic biochemistry structure.
- Supports exact basename match and normalized match (lowercase + hyphens to underscores, e.g., `michaelis_menten_table-Km.py` finds `michaelis_menten_table_km.pgml`).
- Skips tasks that already have `pgml_info` (handled by the existing `run_pgml_generation` mechanism).

## 2026-02-25

### Additions and New Features
- Switched LLM title prompt in `llm_generate_problem_set_title.py` to request XML `<title>` tags, parsed via `llm_wrapper.extract_xml_tag()`, with fallback to legacy `###` markdown parsing for backward compatibility.
- Added download freshness check in `generate_topic_pages.py`: stale download files (where the source `bbq-*-questions.txt` is newer) are now automatically rebuilt instead of skipped.

### Fixes and Maintenance
- Added `is_valid_title()` validation to `generate_topic_pages.py` that rejects titles over 140 characters, containing "thinking" (LLM reasoning leaks), or non-ASCII characters.
- Updated `get_problem_set_title()` to validate cached YAML titles and regenerate bad ones, with up to 3 retries for freshly generated titles.
- Cleaned LLM chain-of-thought "Thinking..." text from `problem_set_titles.yml` in topic06 (all entries), topic07 (1 entry), and topic02 (1 entry plus removed stale uppercase EQUATION key with no matching file).

- Added `pgml_script_map` to `bbq_control/bbq_settings.yml` mapping BBQ scripts to their PGML generator equivalents.
- Updated `bbq_control/run_bbq_tasks.py` to load `pgml_script_map`, attach `pgml_info` to tasks with PGML generators, and run PGML generation after successful BBQ task completion.
- Added `run_pgml_generation()` function to `bbq_control/run_bbq_tasks.py` for generating WeBWorK PGML files from YAML inputs.
- Added a 5th "WeBWorK PGML" download button to `generate_topic_pages.py` that appears when a `.pgml` or `.pg` file exists for a problem set.
- Added `find_pgml_file()` function to `generate_topic_pages.py` that searches `downloads/` and the topic folder for PGML files matching BBQ core names.
- Added `.webwork_pgml` button style and `fa-code` icon to `site_docs/assets/stylesheets/custom.css`.

## 2026-02-24
- Added 4th daily puzzle: Biomacromolecules - shows a 2D chemical structure and asks the player to identify its macromolecule category (Carbohydrate, Lipid, Nucleic Acid, Protein), then subcategory for fun.
- Created build script `tools/build_biomacromolecule_data.py` that merges macromolecules.yml with pubchem data into `biomacromolecule_data.js` (326 molecules).
- Added guard in `showGameEndModal` to skip guess distribution chart when `maxGuesses <= 1`.
- Consolidated shared CSS into `daily_puzzle.css` for all four puzzles: root container, stats, message, toast, instructions, canvas display, keyboard, board/cell, hint-area, and accessibility styles.
- Added `#ms-root` to all shared selectors in `daily_puzzle.css` - mutant screen now uses shared keyboard, board, cell, and hint-area styles instead of duplicated rules.
- Stripped ~200 lines of duplicated CSS from puzzle-specific files (`peptidyle_formatting.css`, `deletion_mutants_formatting.css`, `mutant_screen_formatting.css`, `biomacromolecule_formatting.css`).
- Switched biomacromolecule rendering from SVG to canvas (800x450) matching peptidyle dimensions, with shared gray background and dark mode styling.
- Moved biomacromolecule name-reveal button into the shared hint-area alongside the help button, matching the layout of the other three puzzles.
- Added `explicitMethyl: true` to biomacromolecule RDKit rendering to match peptidyle.
- Added pastel category colors to Biomacromolecule buttons (sky blue for Carbohydrate, orange for Lipid, red for Nucleic Acid, green for Protein) with dark mode variants.
- Added detailed identification guide table in instructions, adapted from `which_macromolecule.py`, including phosphate group tip.
- Added Wordle-style game-end modal with guess distribution chart, win percentage, streak indicators, and next-puzzle timer to all three daily puzzles (Peptidyle, Deletion Mutants, Mutant Screen).
- Redesigned stats bar from horizontal pill layout to card-style grid with large values on top and labels below.
- Extended stats data model with `guessDistribution` array; backward-compatible with old localStorage data.
- Added fire emoji indicator for active streaks.

## 2026-02-06
- Updated `bbq_control/run_bbq_tasks.py` to append `--no-hidden-terms --allow-click` to every task command so website batch runs disable bptools anti-cheat filters globally.
- Updated `bbq_control/source_me.sh` to fall back to `~/nsh/PROBLEMS/qti_package_maker` (and repo-parent `qti_package_maker`) when `paths.qti_package_maker` points to a missing location.
- Updated `bbq_control/source_me.sh` to fall back to `~/nsh/PROBLEMS/biology-problems/problems` (and repo-parent equivalent) when `paths.bp_root` points to a missing location.
- Simplified `bbq_control/source_me.sh` to derive paths directly from `bbq_control/../..` (`biology-problems/problems` and `qti_package_maker`) instead of YAML-based path resolution.
- Updated `bbq_control/bbq_settings.yml` path aliases to `~/nsh/PROBLEMS/...` and made `bbq_control/run_bbq_tasks.py` ignore stale non-existent configured `bp_root` values during PYTHONPATH validation.
- Updated `bbq_control/run_bbq_tasks.py` PYTHONPATH validation to require repo presence (`biology-problems` and `qti_package_maker`) by path components instead of exact absolute configured paths.
- Updated `bbq_control/run_bbq_tasks.py` output auto-detection for `yaml_which_one_mc_to_bbq.py` to match legacy `bbq-WOMC-<input>-questions.txt` output naming in addition to `bbq-MC-...`.
- Updated `bbq_control/run_bbq_tasks.py` with a fallback output detector that scans recent `bbq-*.txt` files and selects the closest filename match when the expected output pattern is missing after a successful task run.

## 2026-02-04
- Reframed `docs/GUIDE_TO_NAMING_PROBLEM_SETS.md` around noun-first titles and removed leading task-verb guidance.
- Removed leading task verbs from `problem_set_titles.yml` titles across `site_docs/` and refreshed timestamps.
- Refined `problem_set_titles.yml` titles across `site_docs/` to remove matching-style "to" phrasing and other leftover action wording.
- Made `generate_topic_pages.py` locate `bbq_converter.py` from repo or sibling `qti_package_maker` paths when the old symlink target is missing.
- Fixed case mismatches in `site_docs/biochemistry/topic02/index.md` to match the tracked Henderson-Hasselbalch download filenames.
- Taught `generate_topic_pages.py` to resolve case mismatches using Git-tracked paths and warn when files differ only by case.
- Updated `generate_topic_pages.py` to remove case-mismatched download files before generating new outputs, keeping BBQ filename casing authoritative.
- Aligned `generate_topic_pages.py` with Git-tracked BBQ filename casing when generating links and downloads.

## 2026-02-03
- Added argparse options, per-format logging, and summary stats to `generate_topic_pages.py`.
- Added laboratory subject navigation, metadata, and topic index pages.
- Linked the laboratory subject from `site_docs/index.md`.
- Added the microscope emoji to the Laboratory nav entry in `mkdocs.yml`.
- Standardized problem set titles to a plain-text Task + Topic + Key Detail format with consistent verbs.
- Fixed corrupted laboratory problem set titles and updated topic title timestamps.
- Updated the problem set title LLM prompt to return plain-text titles with deterministic verb guidance.
- Added `docs/GUIDE_TO_NAMING_PROBLEM_SETS.md` to document problem set title conventions.

## 2026-02-02
- Made missing or mismatched PYTHONPATH a hard error that exits in `bbq_control/run_bbq_tasks.py`.
- Allowed BBQ output auto-detection to use YAML input basenames for `yaml_match_to_bbq.py` and `yaml_which_one_mc_to_bbq.py`.
- Added YAML input basenames to task labels for `yaml_match_to_bbq.py` and `yaml_which_one_mc_to_bbq.py` in `bbq_control/run_bbq_tasks.py`.
- Updated YAML MC statements aliasing to use `yaml_mc_statements_to_bbq.py` and included it in input-basename output detection and task labels.
- Moved `run_bbq_tasks.py` argparse into `parse_args()` and stopped attaching derived runtime state to `args`.
- Switched `run_bbq_tasks.py` to raise a ValueError on non-zero exit from `main()`.
- Removed the output_file column from `bbq_control/bbq_tasks.csv` and `bbq_control/sub_bbq_tasks.csv`.
- Updated `bbq_control/run_bbq_tasks.py` and `bbq_control/bbq_sync_tasks.py` to auto-detect new bbq-*.txt outputs and move them into the site_docs topic folders.
- Updated `bbq_control/USAGE.md` and `flow_for_html_generation.txt` to document the new CSV format and output auto-detection.
- Added a YMATCH script alias that runs both matching-set generators on the same input file.
- Replaced YMWOMC usages in `bbq_control/bbq_tasks.csv` with YMATCH.
- Tightened output auto-detection to match `bbq-<script_name>*-problems.txt` (with a questions.txt fallback).
- Added a PYTHONPATH check in `bbq_control/run_bbq_tasks.py` and skip dry-run cleanup when it is missing.
- Updated `bbq_control/USAGE.md` to reflect YMATCH and the output naming pattern.
- Allowed `bp_root`/`BP_ROOT` to override path aliases and use that value to build PYTHONPATH for BBQ runs.
- Added a dedicated `bbq_generation_errors.log` for failed task output in `bbq_control/run_bbq_tasks.py`.
- Included the full command in `bbq_generation_errors.log` entries for easier debugging.
- Removed rotation for `bbq_generation_errors.log` and delete it at the start of each run.
- Updated `ignore_gen_content.sh` to remove untracked `bbq-*-questions.txt` files under `site_docs/`.

## 2026-01-19
- Switched ASCII compliance file skips to a regex list (currently `human_readable-*.html`).
- Replaced box-drawing characters in the README ASCII tree guidance with codepoint text.
- Reapplied the topic page summary line fix to avoid trailing whitespace in generated index pages.
- Updated `bbq_control/source_me.sh` to prepend `biology-problems` to PYTHONPATH instead of `bbq_control`.
- Added `qti_package_maker` to `bbq_control/bbq_settings.yml` and used BBQ settings to derive PYTHONPATH in `bbq_control/source_me.sh` and `bbq_control/bbq_sync_tasks.py`.
- Updated `bbq_control/USAGE.txt` to reference `bbq_settings.yml` and the new qti path entry.
- Changed `bbq_control/run_bbq_tasks.py` so `-x/--limit` caps task count and `--max-questions` is the global questions flag.
- Added `--shuffle` to `bbq_control/run_bbq_tasks.py` to randomize task order before applying `-x/--limit`.
- Added a pre-run input YAML existence check in `bbq_control/run_bbq_tasks.py` with a clear missing-file message.
- Added a pre-run script existence check in `bbq_control/run_bbq_tasks.py` to avoid running missing generators.
- Updated `bbq_control/run_bbq_tasks.py` to always overwrite existing outputs when moving generated files.
- Added colored TUI status labels in `bbq_control/run_bbq_tasks.py` for pending/running/ok/failed.
- Switched the TUI task table to update cells by row/column keys to avoid invalid coordinates.

## 2026-01-16
- Updated `README.md` to a concise overview with documentation links and a verified quick start.
- Added minimal `docs/INSTALL.md` and `docs/USAGE.md` stubs based on repo evidence.
- Added an ASCII repository structure snippet to `README.md`.
- Added `docs/CODE_ARCHITECTURE.md` and `docs/FILE_STRUCTURE.md` with repo layout and flow notes.
- Documented the ASCII-only tree rule and example in the `README.md` repository structure section.

## 2026-01-15
- Improved `bbq_control/run_bbq_tasks.py` settings lookup to search CWD, repo root, and script directory using `git rev-parse --show-toplevel`.
- Fixed `{bp_root}` alias expansion in task CSV files.
- Renamed `bbq_config.yml` to `bbq_settings.yml` and changed argparse flags: `-t/--tasks` for CSV, `-s/--settings` for YAML.
- Simplified argparse options: removed `--print-only`, `--log`, `--shuffle`, `--sort`, `--seed`, `--duplicates`, and `--no-duplicates` flags.
- Changed `-d` (duplicates) to auto-calculate as `ceil(max_questions * 1.1)` when `-x` is set, otherwise defaults to 99.
- Changed log output to `bbq_generation.log` in CWD with numbered rotation (.1, .2, .3, .4, .5) and a startup message when rotated.
- Added line count to non-TUI task completion output (e.g., `DONE script.py (99 lines)`).

## 2026-01-09
- Added the new daily puzzle page `site_docs/daily_puzzles/mutant_screen.md` based on Beadle and Tatum *Neurospora* auxotroph experiments.
- Added mutant screen puzzle JS assets: `mutant_screen_words.js`, `mutant_screen_logic.js`, `mutant_screen_game.js`, and `mutant_screen_bootstrap.js`.
- Added `site_docs/assets/stylesheets/mutant_screen_formatting.css` for growth table and puzzle styling.
- Shuffled both rows (mutant classes) and columns (metabolites) in the growth table so the answer cannot be read directly from the table.
- Updated `mkdocs.yml` nav to include the mutant screen puzzle.
- Updated `site_docs/index.md` to link to the mutant screen puzzle.

## 2026-01-05
- Added `docs/DELETION_MUTANTS_PLAN.md` outlining the deletion mutant daily puzzle port.
- Added the new daily puzzle page `site_docs/daily_puzzles/deletion_mutants.md`.
- Added short "why this matters" blurbs to the daily puzzle pages for Peptidyle and deletion mutants.
- Added shared browser utilities `site_docs/assets/scripts/daily_puzzle_core.js` and `site_docs/assets/scripts/daily_puzzle_stats.js`.
- Added deletion mutant puzzle JS/CSS assets under `site_docs/assets/scripts/` and `site_docs/assets/stylesheets/`.
- Tweaked deletion mutant UI: stronger table borders, visible empty guess grid, and an optional first-gene hint with a guess penalty.
- Tweaked daily puzzle UI: shared pill-style stats/streak display and deletion-table styling closer to the original deletion mutant tables.
- Refined deletion mutant daily puzzle styling: pastel deletions in light mode, dark deletions in dark mode, better empty-cell fills, hint button styling, and reduced perceived whitespace around the game area.
- Reduced the size of the "I need help" hint UI in the deletion mutant daily puzzle.
- Widened deletion mutant table columns for readability.
- Refactored deletion mutant theme switching to use MkDocs Material `data-md-color-scheme` CSS variables (no JS re-render on toggle).
- Improved daily puzzle theme integration: scheme-aware deletion colors via CSS, Material token-based surfaces/borders, focus-visible outlines, and reduced-motion scrolling.
- Updated invalid (red) on-screen keyboard keys to render as dark red in dark mode.
- Added shared `site_docs/assets/scripts/daily_puzzle_keyboard.js` and refactored both daily puzzles to use it.
- Added shared physical keyboard input controller `site_docs/assets/scripts/daily_puzzle_input.js` and refactored both puzzles to use it.
- Hardened `site_docs/assets/scripts/daily_puzzle_input.js` to avoid duplicate listeners across reloads and to ignore contenteditable ancestors (e.g. MkDocs search/widgets).
- Made `site_docs/assets/scripts/daily_puzzle_input.js` merge install options to avoid accidental handler loss; strengthened slate-mode keyboard key foreground in `site_docs/assets/stylesheets/daily_puzzle.css`.
- Added a shared "next puzzle" countdown timer under both daily puzzle keyboards (updates once per minute; `aria-live="off"`).
- Improved deletion mutant layout: responsive table+legend columns, continuous deletion bars, and a non-reserved guess board to reduce whitespace before play.
- Moved the deletion mutant help button into the same control row as the first-gene hint.
- Updated the shared on-screen keyboard: renamed disabled keys from `invalid` to `disabled`, added an option to soft-disable keys, and drove disabled-key colors via theme-switched CSS variables.
- Fixed deletion mutants page HTML rendering by removing leading indentation that caused Markdown to treat the UI as a code block.
- Fixed dark mode keyboard foreground and disabled-key dimming via shared keyboard CSS variables.
- Increased light-mode deletion bar saturation by using the light palette (instead of extra-light) for table fills.
- Improved deletion legend wrapping (flex rows with fixed labels) and made light-mode deletion colors more saturated.
- Added hard overrides to force keyboard glyph colors to switch correctly in slate mode (including Safari `-webkit-text-fill-color`).
- Fixed theme selector mismatch by switching MkDocs Material scheme selectors from `:root/html[...]` to `body[data-md-color-scheme=...]`.
- Aligned Peptidyle keyboard styling with the deletion mutants keyboard (container box + key borders).
- Added shared `site_docs/assets/scripts/daily_puzzle_ui.js` and shared `site_docs/assets/stylesheets/daily_puzzle.css`.
- Moved shared daily puzzle stats/keyboard/control-bar CSS out of `site_docs/assets/stylesheets/custom.css`.
- Updated Peptidyle UI: moved tips controls above the peptide image and added a first-letter hint with a 1-guess penalty.
- Updated both puzzles so the -1 first-letter hint consumes a visible guess row (first letter in green, rest blank) and is disabled when only 1 guess remains.
- Added the deletion mutant puzzle to `mkdocs.yml` nav and linked it from `site_docs/index.md`.
- Migrated Peptidyle stats to `site_docs/assets/scripts/daily_puzzle_stats.js` and removed `site_docs/assets/scripts/peptidyle_stats.js`.
- Renamed `site_docs/assets/scripts/deletion_mutants_colors.js` to `site_docs/assets/scripts/daily_puzzle_colors.js` for reuse across daily puzzles.
- Added `site_docs/assets/scripts/daily_puzzle_wordle.js` (shared Wordle scoring, board rendering, and toast helper) and refactored both daily puzzles to use it.
- Unified -1 hint behavior across both puzzles: hint is only available before the first guess, requires an empty current guess, consumes a guess via a visible penalty row, and pre-fills the current guess with the revealed first letter.
- Updated `site_docs/assets/scripts/peptidyle_words.js` to use `site_docs/assets/scripts/daily_puzzle_core.js` for daily selection/hashing (no duplicate hashing implementation).
- Added shared Wordle cell/board styling to `site_docs/assets/stylesheets/daily_puzzle.css` so both puzzles render the guess grid consistently (and the deletion mutant board has visible boxes).
- Increased light-mode deletion mutant palette saturation in `site_docs/assets/scripts/daily_puzzle_colors.js`.
- Extended `site_docs/assets/scripts/daily_puzzle_keyboard.js` click handling to support optional soft-disabled key toasts.
- Added `build_deletion_mutants_wordbank.py` and embedded the filtered unique-letter deletion-mutants word list directly in `site_docs/assets/scripts/deletion_mutants_words.js` (no runtime fetch required).

## 2026-01-03
- Added `bbq_control/bbq_config.yml` for path aliases, script aliases, and input defaults.
- Added an `input` column to `bbq_control/bbq_tasks.csv` and `bbq_control/sub_bbq_tasks.csv`.
- Updated BBQ task runners to expand aliases and attach input files from the new columns.
- Added `bbq_control/usage.txt` with BBQ task runner usage notes.
- Switched the main path alias to `{bp_root}` for shorter CSV entries.
- Allowed basename-only `input` values for YMWOMC/YMCS/YMMS tasks.
- Removed the `input_flag` column (inputs always use `-y`).

## 2025-12-27
- Added `bbq_sync_tasks.py` to sync BBQ outputs from biology-problems scripts with a task state CSV.
- Moved MkDocs content from `docs/` to `site_docs/` and set `docs_dir` in `mkdocs.yml`.
- Updated path references to the MkDocs content in `README.md`, `bbq_control/bbq_tasks.csv`, and helper scripts.
- Simplified `bbq_control/bbq_tasks.csv` to `chapter,topic,output_file,script,flags,notes` and updated runners to build output paths from chapter/topic.
- Added `--limit`, `--sort`, `--shuffle`, and `--seed` options to `run_bbq_tasks.py`.
- Updated the Textual TUI layout to put the task table full-width with a top metrics/log row.
- Fixed DataTable updates in the TUI to avoid row/column lookup errors.
- Adjusted TUI labels to show script names, tightened the metrics layout, and reduced the top row height.
- Moved the TUI "Press q to quit" prompt into the dashboard panel.
- Removed the TUI header bar and added a dashboard title line.
- Increased the TUI top row height to scale with terminal size while keeping a larger minimum height.
- Added `-x/--max-questions` to append a global max-questions flag to all scripts.
- Added a validation check that fails when a max-questions run produces too many lines.
- Truncate `logs/bbq_generation.log` at the start of each run.
- Added `-d/--duplicates` (default 99) and `--no-duplicates` to control global duplicate runs.
- Fixed dry-run validation to count lines from the newly generated output in the working directory.
- Clean up dry-run generated `bbq*.txt` outputs to avoid accumulation.
- Read the MkDocs `docs_dir` from `mkdocs.yml` when generating subject indexes and topic pages.
- Routed LLM title generation through `llm_wrapper.py` with quiet model calls.
- Removed shell-based subprocess usage from topic page generation.
- Removed unused imports flagged by pyflakes.
- Added `--no-tui` to force plain mode.
- Added `pip_requirements.txt` with `textual`.
- Fixed `run_bbq_tasks.py` to guard TUI class definitions when Textual is unavailable.
- Updated BBQ task runners to fail when outputs are missing or mismatched.

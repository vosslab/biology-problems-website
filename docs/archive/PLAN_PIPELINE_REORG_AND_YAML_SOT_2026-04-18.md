# Plan: Pipeline reorg + topics_metadata.yml as source of truth (v4)

Status: Revised 2026-04-18 after four rounds of reviewer feedback.

The six in-scope subjects (from `mkdocs.yml` nav) are: `biochemistry`,
`genetics`, `laboratory`, `molecular_biology`, `biostatistics`, `other`.
`biotechnology` is present on disk but not in nav and is deleted in M2
(see below).
Supersedes
[docs/active_plans/PLAN_PIPELINE_REORG_AND_YAML_SOT_2026-04-18.md](../../nsh/PROBLEMS/biology-problems-website/docs/active_plans/PLAN_PIPELINE_REORG_AND_YAML_SOT_2026-04-18.md),
which will be rewritten to match on plan approval.

## Context

The UI/UX review on 2026-04-18 found 25+ broken subject-to-topic links, an
orphan `biotechnology/` subject, and inconsistent LibreTexts link styling.
Root cause: topic metadata lives hand-authored in each
`site_docs/<subject>/index.md` after the 2026-04-13 removal of
`topics_metadata.yml` and `generate_subject_indexes.py`. The existing
`generate_topic_pages.py` at repo root is a 968-line mix of argparse,
git-path helpers, download-button HTML, and LLM title lookup, so helpers
are not discoverable and the operator has no single page-generation
command.

This plan reintroduces `topics_metadata.yml` as authoritative, consolidates
page generation into one root entrypoint `generate_pages.py`, and moves all
importable logic into `bioproblems_site/`.

## Design philosophy

1. **One source of truth per fact.** Title, LibreTexts URL, and
   description live in `topics_metadata.yml`. Subject index pages and
   topic pages are generated.
2. **Derive, do not author, question counts.** Counts come from
   scanning `site_docs/<subject>/topic<NN>/bbq-*-questions.txt` **when
   the generator runs** (`python generate_pages.py`), before MkDocs
   build or serve. mkdocs does not recompute counts;
   `mkdocs serve` and `mkdocs build` treat `site_docs/` as already
   rendered content. The word "build time" never means mkdocs build
   anywhere in this plan.
3. **Links follow content.** A subject index never links to a topic
   whose directory is absent or whose question count is zero. This is a
   generation-time filter inside `generate_pages.py` (not a browser- or
   mkdocs-render-time filter).
4. **One page-generation command.** The operator runs exactly one
   script to regenerate all site markdown: `generate_pages.py`. It
   regenerates subject indexes and topic pages together, so the repo
   cannot end up with mismatched pages.
5. **Root is for entrypoints, not helpers.** Python files at the repo
   root must be directly-runnable argparse scripts. Import-only helpers
   live under `bioproblems_site/`. New generation logic must not be
   added at repo root except for the primary CLI entrypoint.
6. **Additive rollout, bounded deletion.** Old parser code survives
   behind an argparse flag through M1-M2 and is deleted in M3 only
   after YAML is authoritative for all six subjects.

## Root-file policy

After this reorg, the repo root Python surface is intentionally tiny:

| Stay at root | Why |
| --- | --- |
| `generate_pages.py` | Single operator-facing page-generation entrypoint. Thin argparse; delegates to `bioproblems_site.pipeline`. |
| `bbq_converter.py` | Symlink into `../qti-package-maker`; established root command; out of scope to move. |

Moved out of root in this plan:

| Move | To | Why |
| --- | --- | --- |
| `generate_topic_pages.py` | renamed + shrunk to `generate_pages.py` (root) plus `bioproblems_site/` submodules | Single entrypoint; logic in package. |
| `llm_wrapper.py` | `bioproblems_site/llm_wrapper.py` | Imported only by `llm_generate_problem_set_title.py`; not user-run. |
| `llm_generate_problem_set_title.py` | `bioproblems_site/problem_set_title.py` | Neil confirmed it is not invoked directly; currently imported by `generate_topic_pages.py`. Becomes internal helper used by `bioproblems_site.topic_page`. |
| ~900 lines of helpers | `bioproblems_site/{metadata,scanner,subject_index,topic_page,download_buttons,git_paths,pipeline,formats}.py` | All importable logic. |

Files removed:

- Old `generate_topic_pages.py` (replaced by `generate_pages.py`).
- No separate `generate_subject_indexes.py` is ever created. Subject
  indexes are one phase of the unified `generate_pages.py` pipeline.

## YAML path and schema

- **Path:** `topics_metadata.yml` at repo root.
- **Subject order:** read from `mkdocs.yml` nav; YAML keys may appear
  in any order.
- **Topic order:** numeric ascending by zero-padded suffix of the
  topic key (`topic01`, `topic02`, ...).
- **Hand edits forbidden** on generated files. Every generated
  `index.md` begins with:
  `<!-- GENERATED FROM topics_metadata.yml BY bioproblems_site.subject_index -- DO NOT EDIT -->`
  (The marker names the component, not the CLI filename, so CLI renames
  do not invalidate existing files.)
- **Migration exception for first write.** The current six
  `site_docs/<subject>/index.md` files are hand-authored and do not
  carry the marker. The first M2 run overwrites them via the argparse
  flag `--adopt-existing`, which is only honored when the target path
  matches a known-expected generated output
  (`site_docs/<subject>/index.md` for the six in-scope subjects).
  After that commit lands, `--adopt-existing` is no longer needed and
  subsequent runs enforce the strict marker check. The flag stays in
  the argparse surface as a clearly-documented escape hatch (e.g., for
  a future seventh subject) but is never the default.

### Canonical schema example

```yaml
# topics_metadata.yml
# Single source of truth for subject and topic metadata.
# Question counts are NOT stored here; they are scanned from disk by
# generate_pages.py at generation time.

biochemistry:
  title: Biochemistry                    # required; string
  description: |                          # required; subject landing-page intro, may span lines
    Biochemistry is the study of chemical substances and vital
    processes in living organisms.
  topics:
    topic01:
      title: Life Molecules               # required; string, topic heading minus the number
      description: |                      # required; may use inline markdown
        Students categorize biomolecules into major classes
        (proteins, carbohydrates, lipids, nucleic acids) and
        distinguish hydrophobic from hydrophilic molecules.
      libretexts:                         # optional; omit to render no external link
        url: https://bio.libretexts.org/Courses/Roosevelt_University/BCHM_355_455_Biochemistry_(Roosevelt_University)/01%3A_Unit_1_-_Proteins/1.01%3A_Molecules_of_Life
        unit: 1                           # required when libretexts is present; int >= 1
        chapter: 1                        # required when libretexts is present; int >= 1
      visible: true                       # optional; default true. Set false to hide intentionally.
    topic15:
      title: Digestion
      description: "Students trace the digestion of proteins..."
      visible: false                      # hide from generated index even if files exist
```

### Keeping `mkdocs.yml` and `topics_metadata.yml` in sync

Two files hold overlapping facts: `mkdocs.yml` owns subject display
labels and subject ordering, `topics_metadata.yml` owns every other
topic/subject fact. Drift between them is exactly the class of bug that
created the `biotechnology/` orphan. Mitigation has three layers:

1. **One-way dependency.** `topics_metadata.yml` never duplicates
   mkdocs labels/icons/order. The generator reads subject order from
   `mkdocs.yml` nav and everything else from YAML. No field is written
   to both files.

2. **Fail-fast validator in `bioproblems_site.metadata`.** On load,
   `load_topics_metadata()` also parses `mkdocs.yml` and asserts:
   - `set(yaml_subject_keys) == set(nav_subject_keys)` where
     `nav_subject_keys` is the set of `<key>` such that some nav entry
     points at `<key>/index.md`. A mismatch raises
     `MetadataMkdocsMismatchError` naming the extra/missing keys and
     points the operator at the offending file.
   - Every YAML subject key resolves to exactly one nav entry.
   - Reserved top-level nav slots (`Home`, `Daily Puzzles`, `Tutorials`,
     `Author`, `License`) are ignored by the check.
   The validator runs on every `python generate_pages.py` invocation --
   the operator sees the mismatch before any file is written.

3. **Pytest gate.** `tests/test_mkdocs_metadata_sync.py` asserts the
   same invariant as a unit test, so CI (and the pyflakes/smoke runner)
   catches drift even when the generator is not re-run.

Adding a new subject requires edits to both files in the same patch:
the YAML entry + the `mkdocs.yml` nav line. Removing a subject (as with
biotechnology in M2) also requires both, which is why M2 bundles the
delete with the nav-cleanup grep gate.

Schema rules enforced by `bioproblems_site.metadata`:

- Subject key matches `^[a-z_]+$`; topic key matches `^topic\d{2}$`.
- `title` is required non-empty string on both subjects and topics.
- `description` is required non-empty string on both subjects and
  topics. No markdown-fallback path; YAML is the sole source of truth
  for topic and subject descriptions. No `icon` or `mkdocs_label`
  fields; display labels in the nav are sourced from `mkdocs.yml`
  only (not duplicated here).
- `libretexts.url` (when present) starts with `https://bio.libretexts.org/`.
- `libretexts.unit` and `.chapter` are integers >= 1; both present or
  both absent, never one without the other.
- Unknown keys raise an error.

## Scanner format values

`bioproblems_site.scanner.scan_topic(dir) -> TopicScan` returns:

- `questions: int` -- `len(glob("bbq-*-questions.txt"))` in the topic
  directory. Missing directory returns 0.
- `formats: frozenset[str]` -- one value per download-format file group
  discovered under `downloads/`. Allowed values come from
  `bioproblems_site.formats.FORMAT_KEYS`:
  - `"bb_text"` -- Blackboard Learn TXT
  - `"bb_qti"` -- Blackboard Ultra QTI v2.1
  - `"canvas_qti"` -- Canvas/ADAPT QTI v1.2
  - `"human_read"` -- Human-Readable TXT
  - `"webwork_pgml"` -- WeBWorK PGML

`bioproblems_site.formats` is the neutral registry. Both `scanner` and
`download_buttons` import from it. Scanner contains no HTML concerns;
`download_buttons` contains no filesystem discovery. Adding a format
touches `formats.py` (key + file-glob pattern) and `download_buttons.py`
(human label + button HTML), and no other file.

## Parity contract (two phases)

- **M1 parity (topic pages only).** With argparse flag
  `--metadata-source=yaml`, topic `index.md` output for a pinned
  sample is byte-identical to the current markdown-source code path.
  Tested by pytest diff.
- **M2 divergence (subject indexes).** Regenerated
  `site_docs/<subject>/index.md` intentionally differs from
  hand-authored files. Expected diffs:
  - topics with `questions == 0`, missing directory, or
    `visible: false`: removed,
  - `N questions` chip added after each title,
  - LibreTexts text label replaced by icon anchor with `rel="noopener"`
    and `aria-label`,
  - generated-file marker at top.
  M2 parity test: generated links are a **strict subset** of current
  links (no new broken links).

## Architecture: one entrypoint, one package

### Pipeline flow

```
   +-------------------------+
   |  generate_pages.py      |   <-- root entrypoint, argparse only
   |  (<= 60 lines)          |
   +-----------+-------------+
               |
               v
   +-------------------------+
   | bioproblems_site.       |
   |   pipeline.run(args)    |   <-- orchestrates the full generation
   +-----------+-------------+
               |
   +-----------+-----------------------------+
   |                                         |
   v                                         v
   metadata.load_topics_metadata()           scanner.scan_all()
               \                            /
                v                          v
               subject_index.render_all()
                    |
                    v
               topic_page.render_all()
                    |
                    v
               files written under site_docs/<subject>/
```

mkdocs is not in the picture. `mkdocs serve` / `mkdocs build` runs later,
separately, and treats everything under `site_docs/` as already rendered.

### Component map

| Component | File | Role |
| --- | --- | --- |
| `bioproblems_site.metadata` | `bioproblems_site/metadata.py` | Load + validate `topics_metadata.yml`; cross-check `mkdocs.yml`. `Subject`, `Topic` dataclasses. |
| `bioproblems_site.formats` | `bioproblems_site/formats.py` | Neutral format registry: `FORMAT_KEYS` + file-glob patterns. No HTML, no filesystem walk. |
| `bioproblems_site.scanner` | `bioproblems_site/scanner.py` | Scan topic directory for question count + format set. Imports `formats`. |
| `bioproblems_site.subject_index` | `bioproblems_site/subject_index.py` | Render one subject `index.md` from metadata + scan. |
| `bioproblems_site.topic_page` | `bioproblems_site/topic_page.py` | Render per-topic `index.md`. |
| `bioproblems_site.download_buttons` | `bioproblems_site/download_buttons.py` | Human labels + button-row HTML. Imports `formats` for keys. No FORMAT_KEYS duplication. |
| `bioproblems_site.git_paths` | `bioproblems_site/git_paths.py` | Git-tracked-path helpers. |
| `bioproblems_site.llm_wrapper` | `bioproblems_site/llm_wrapper.py` | Moved from root in M3. |
| `bioproblems_site.problem_set_title` | `bioproblems_site/problem_set_title.py` | Moved from root `llm_generate_problem_set_title.py` in M3. Internal helper to `topic_page`. |
| `bioproblems_site.pipeline` | `bioproblems_site/pipeline.py` | Orchestration entrypoint called by the root script. |
| `bioproblems_site.breadcrumbs` (conditional) | `bioproblems_site/breadcrumbs.py` | Only created if M4 decision gate chooses "topic pages stay out of nav" and theme breadcrumbs therefore fail on topic pages. Otherwise not written. |
| `generate_pages.py` | repo root | argparse only. Thin. The only page-generation Python file at the repo root after M3. |

### Reference implementation

Neil restored the previously-removed `generate_subject_indexes.py`
(183 lines) as a read-only reference. Mine it for:

- `write_subject_index` (lines 124-162): the output-shape pattern for
  `bioproblems_site.subject_index.render_subject_index`.
- `build_link_markup` (lines 107-121): the exact LibreTexts HTML string
  that ships today and that M4 replaces with an icon.
- `load_yaml_file` (lines 43-50): matches the validator stance of the
  new `metadata.py` (FileNotFoundError on missing, ValueError on
  non-mapping root; no silent defaults).

Differences to carry into the new design:

- The old script derived topic order from `mkdocs.yml` nav entries.
  That is no longer valid because the 2026-04-13 nav collapse removed
  per-topic nav entries. The new pipeline derives topic order from
  `topics_metadata.yml` keys (zero-padded numeric ascending).
- The old script only handled `biochemistry` and `genetics`. The new
  pipeline handles all six in-scope subjects uniformly.
- The old script writes with `"\n".join(lines).rstrip() + "\n"`. Keep
  that trailing-newline convention in the new renderer.

The file itself is not revived or edited; `bioproblems_site.subject_index`
replaces it.

### Entrypoint CLI

```
python generate_pages.py --all                                  # default
python generate_pages.py --subject biochemistry
python generate_pages.py --subject biochemistry --topic topic01
python generate_pages.py --indexes-only                         # debugging
python generate_pages.py --topics-only                          # debugging
python generate_pages.py --metadata-source {markdown,yaml}      # M1-M2 only
python generate_pages.py --dry-run
```

The `--metadata-source` flag is deleted at M3 close. `--indexes-only`
and `--topics-only` stay only if they prove useful during M2-M3
iteration; otherwise they are dropped before M4.

## Milestone plan

Milestone narrative: M1 is transitional -- patches land against the
existing `generate_topic_pages.py` so YAML and the old parser run side
by side (argparse flag). M2 introduces the new unified
`generate_pages.py` entrypoint and makes YAML authoritative for
generation output. M3 deletes the old entrypoint and parser code. M4
is polish and nav/theme work.

### M1: YAML + metadata loader + topic-page parity gate (transitional)

- **Depends on:** none.
- **Deliverables:**
  - `topics_metadata.yml` at repo root, populated from current
    `site_docs/<subject>/index.md` for all six nav subjects.
  - `bioproblems_site/__init__.py` (empty docstring only).
  - `bioproblems_site/metadata.py` with loader, dataclasses, validator.
  - argparse flag `--metadata-source {markdown,yaml}` added to the
    existing `generate_topic_pages.py` (not renamed yet). Default
    `markdown`.
  - Unit tests under `tests/test_metadata_loader.py`.
  - Parity pytest: with `--metadata-source=yaml`, topic `index.md`
    output for biochem/topic01, genetics/topic01, laboratory/topic01 is
    byte-identical to the markdown-source path.
- **Exit:**
  - `pytest tests/test_metadata_loader.py tests/test_topic_page_parity.py`
    green.
  - `mkdocs serve` warnings unchanged (no regression).

### M2: Unified pipeline + scanner + subject index (intentional divergence)

- **Depends on:** M1 (`metadata` loader).
- **Deliverables:**
  - `bioproblems_site/scanner.py` + tests.
  - `bioproblems_site/subject_index.py` + tests.
  - `bioproblems_site/pipeline.py` with `run(args)` orchestrating
    metadata load + scan + subject-index render + topic-page render.
  - New root entrypoint `generate_pages.py` (argparse only, <=60
    lines). Existing `generate_topic_pages.py` stays in parallel during
    M2 so both code paths can be diffed; it is deleted in M3.
  - Regenerated `site_docs/<subject>/index.md` for all six subjects,
    carrying the generated-file marker.
  - Biotechnology decision executed at M2 start in a single patch that
    includes all three cleanup actions:
    1. `git rm -r site_docs/biotechnology/` (delete the directory),
    2. `topics_metadata.yml` does not contain a `biotechnology:` key,
    3. any reference in `mkdocs.yml`, home-page `site_docs/index.md`,
       or other cross-links is removed. `grep -rn biotechnology
       site_docs/ mkdocs.yml` must return zero hits when the patch
       lands. Reversed only if Neil opts in before M2 begins.
- **Exit:**
  - `mkdocs build --strict` exits 0.
  - `python generate_pages.py --all` is idempotent (second run: zero
    git diff).
  - Subject-index parity test: generated links are a strict subset of
    current links.
  - `node devel/ui_ux_review.mjs`: all targets HTTP 200.

### M3: Extract topic-page logic, move llm_wrapper, delete old code

- **Depends on:** M2 (subject pages already flow through the new
  pipeline; otherwise the markdown parser cannot be removed safely).
- **Deliverables:**
  - Move helpers from `generate_topic_pages.py` into
    `bioproblems_site/{git_paths,download_buttons,topic_page}.py`.
  - `bioproblems_site.pipeline.run` now invokes
    `bioproblems_site.topic_page.render_all` directly.
  - `git rm generate_topic_pages.py`. `generate_pages.py` is the sole
    page-generation entrypoint.
  - `git mv llm_wrapper.py bioproblems_site/llm_wrapper.py`.
  - `git mv llm_generate_problem_set_title.py
    bioproblems_site/problem_set_title.py`; update the import chain so
    `bioproblems_site.topic_page` calls the moved module.
  - Delete `load_subject_topics()`, `_TOPIC_HEADING_RE`,
    `_LIBRETEXTS_RE`, `_DESCRIPTION_RE`, and the
    `--metadata-source` argparse flag.
- **Exit:**
  - `pytest tests/` green, including topic-page byte-diff parity
    against a pre-M3 fixture and the title-generation path test.
  - `wc -l generate_pages.py` <= 60.
  - No root-level `llm_wrapper.py` or
    `llm_generate_problem_set_title.py` remain (`ls *.py`).
  - Root contains no import-only Python files.
  - (Developer check, not a gate) `grep -r "import llm_wrapper"
    --include='*.py' .` returns zero hits outside
    `bioproblems_site/`.

### M4: Close-out -- icon, breadcrumbs, rel=noopener, docs

- **Depends on:** M3.
- **Deliverables:**
  - `site_docs/assets/images/libretexts.svg` (16px, `currentColor`).
  - `.lt-icon` CSS in `site_docs/assets/stylesheets/custom.css`.
  - `bioproblems_site/subject_index.py` emits the icon anchor with
    `aria-label` and `rel="noopener"`.
  - `rel="noopener"` sweep across `site_docs/author.md` and any other
    hand-authored markdown with `target="_blank"`.
  - **Breadcrumb navigation, theme-driven.** Topic pages reach 3+
    levels deep (Home -> Subject -> Topic, occasionally -> Downloads
    or a helper subpage). Breadcrumbs are owned by the theme, not the
    generator. Add the following to `theme.features` in `mkdocs.yml`:
    - `navigation.path` -- breadcrumb line above the page title.
    - `navigation.indexes` -- subject `index.md` becomes the clickable
      landing page for the subject section (matches existing layout).
    - `navigation.top` -- "back to top" button on long pages.
    - `navigation.sections` -- considered if, after reinstating topic
      pages in nav (see next bullet), the left sidebar becomes too
      long. Not enabled in the first cut; revisit after Playwright
      verification.

    No breadcrumb HTML is generated into page content. No breadcrumb
    metadata is added to `topics_metadata.yml`. The nav path is the
    structural source.

  - **M4 decision gate: topic pages in nav.** (Elevated from open
    questions.) This is a formal gate, decided before any M4 patch
    lands. Exactly one branch is taken:

    **Branch A (default): reinstate topic pages in `mkdocs.yml` nav,
    theme owns breadcrumbs.** Motivation for the 2026-04-13 collapse
    (sidebar too long) is addressed by `navigation.sections` +
    `navigation.indexes`. The generator owns a clearly-marked nav
    block inside `mkdocs.yml` directly, not a separate file and not
    an include-plugin. Shape:
    ```yaml
    # === BEGIN GENERATED SUBJECT NAV -- bioproblems_site.pipeline ===
    - "🧪 Biochemistry":
      - biochemistry/index.md
      - "01: Life Molecules": biochemistry/topic01/index.md
      - "02: Water and pH":   biochemistry/topic02/index.md
      ...
    # === END GENERATED SUBJECT NAV ===
    ```
    `bioproblems_site.pipeline` rewrites only the text between these
    two markers and aborts if either marker is missing (same strict
    stance as the generated-`index.md` marker). Anything outside the
    markers (theme config, plugins, Home/Tutorials/Author/License nav
    entries, etc.) is never touched. `bioproblems_site.subject_index`
    emits the per-subject fragment; `pipeline` stitches them in
    `mkdocs.yml` nav order.

    **Branch B: topic pages stay out of nav, generator-owned
    breadcrumb module activates.** Chosen only if Neil explicitly
    opts for the post-2026-04-13 collapsed nav shape. Creates
    `bioproblems_site/breadcrumbs.py` + `.bp-breadcrumb` CSS; subject
    indexes still use the theme breadcrumb via `navigation.indexes`.
    `mkdocs.yml` is not auto-rewritten.

    The choice must be explicit before M4 Patch 7 starts. The plan
    defaults to Branch A if no decision is recorded.
  - `docs/CODE_ARCHITECTURE.md`, `docs/FILE_STRUCTURE.md`,
    `docs/USAGE.md`, new `docs/YAML_FILE_FORMAT.md` updated to describe
    the single entrypoint and `bioproblems_site/` package.
  - CHANGELOG entries per patch.
  - Plan moved to `docs/archive/`.
- **Exit:**
  - `node devel/ui_ux_review.mjs`: `report.externalNoRel == 0` on every
    page.
  - Manual pass: LibreTexts icon shows on every topic row with a URL;
    no visible "LibreTexts" text label remains.

## Critical files

- `topics_metadata.yml` (new, root).
- `bioproblems_site/__init__.py` (new).
- `bioproblems_site/metadata.py` (new).
- `bioproblems_site/formats.py` (new; neutral format registry).
- `bioproblems_site/scanner.py` (new).
- `bioproblems_site/subject_index.py` (new).
- `bioproblems_site/topic_page.py` (new; receives
  `generate_topic_pages.py:373-881`).
- `bioproblems_site/download_buttons.py` (new; receives
  `generate_topic_pages.py:470-645`; `FORMAT_KEYS` lives in
  `formats.py`, not here).
- `bioproblems_site/git_paths.py` (new; receives
  `generate_topic_pages.py:57-112`).
- `bioproblems_site/pipeline.py` (new).
- `bioproblems_site/llm_wrapper.py` (moved from root in M3).
- `bioproblems_site/problem_set_title.py` (moved from root
  `llm_generate_problem_set_title.py` in M3).
- `bioproblems_site/breadcrumbs.py` (conditional; only if M4 Branch B).
- `generate_pages.py` (new root entrypoint; argparse only).
- `generate_topic_pages.py` (deleted in M3 after replacement).
- `llm_wrapper.py` and `llm_generate_problem_set_title.py` (both
  deleted from root in M3 after the `git mv` into the package).
- `mkdocs.yml` (M4 Branch A: generated nav block with BEGIN/END markers
  maintained by `bioproblems_site.pipeline`; theme features updated).
- `site_docs/<subject>/index.md` x6 (overwritten as generated files).
- `site_docs/assets/images/libretexts.svg` (new).
- `site_docs/assets/stylesheets/custom.css` (add `.lt-icon`;
  `.bp-breadcrumb` only if M4 Branch B).

Reused existing helpers (kept, not duplicated):

- `generate_topic_pages.py:260` `_derive_libretexts_title` -- moves
  into `bioproblems_site.metadata` as a private fallback.
- `generate_topic_pages.py:215` `get_repo_root` and `:230`
  `find_bbq_converter` -- move into `bioproblems_site.git_paths`.
- `generate_topic_pages.py:408` `get_download_js_string` and `:470`
  `generate_download_button_row` -- move into
  `bioproblems_site.download_buttons`.

## Verification

- `source source_me.sh && python -m pytest tests/` -- unit tests green.
  New files:
  - `tests/test_metadata_loader.py`
  - `tests/test_mkdocs_metadata_sync.py`
  - `tests/test_scanner.py`
  - `tests/test_subject_index_render.py`
  - `tests/test_topic_page_parity.py`
- `source source_me.sh && python -m pytest tests/test_mkdocs_strict.py
  -m smoke` -- marked `@pytest.mark.smoke`; runs
  `mkdocs build --strict`; excluded from the default fast subset via
  `-m "not smoke"` in `pytest.ini`.
- `source source_me.sh && python generate_pages.py --all` --
  idempotent; second run produces zero git diff.
- `source source_me.sh && python generate_pages.py --dry-run
  --subject biochemistry` -- prints planned changes without touching
  files.
- `source source_me.sh && mkdocs serve -a 127.0.0.1:8765` (background)
  + `node devel/ui_ux_review.mjs` -- every page 200;
  `report.externalNoRel == 0`; no 404 topic links.
- `tests/test_pyflakes_code_lint.py` and
  `tests/test_ascii_compliance.py` stay green at every milestone close.

## Rollback path

If M2 regeneration reveals bad YAML:

1. `git restore site_docs/<subject>/index.md` to undo the generator
   output.
2. Keep `--metadata-source=markdown` as the default on the old
   `generate_topic_pages.py` (do not advance M3).
3. Fix the YAML; rerun `python generate_pages.py --subject <name>`;
   re-diff.
4. M3 is gated on zero rollback events across the six subjects in the
   last M2 run.

The `--metadata-source` argparse flag is the single rollback lever
until M3 deletes it.

## Open questions

1. **LibreTexts icon source.** Default if undecided by M4:
   FontAwesome `fa-book` with a small `fa-external-link-alt` overlay,
   brand blue `#127bc4`. If Neil supplies or approves an official
   LibreTexts logo before M4, we use it instead.

The previously-open questions about `llm_generate_problem_set_title.py`
placement, topic-description markdown fallback, and topic-pages-in-nav
are now decided above (M3 moves the script into `bioproblems_site/`;
YAML is the sole source of truth for descriptions with no fallback;
topic-pages-in-nav is the M4 decision gate with Branch A as default).

Everything else called out by the reviewer (YAML path, schema shape,
scanner formats, subject ordering, generated-file marker, feature-flag
form, smoke-test marking, biotechnology default, root-file policy,
`llm_wrapper` move, rollback path, single entrypoint, `bioproblems_site`
package name, count-timing clarification) is decided above.

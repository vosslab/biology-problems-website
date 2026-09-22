# File structure

## Top-level layout

- [build_site.py](../build_site.py): primary unified site-build CLI.
- [source_me.sh](../source_me.sh): Python and sibling-repository environment contract.
- [topics_metadata.yml](../topics_metadata.yml): subject and topic source of truth.
- [bbq_settings.yml](../bbq_settings.yml): BBQ path and script aliases.
- [task_files/](../task_files/): per-subject BBQ task CSV inputs.
- [mkdocs.yml](../mkdocs.yml): MkDocs configuration and generated navigation.
- [bioproblems_site/](../bioproblems_site/): reusable site and BBQ package logic.
- [site_docs/](../site_docs/): MkDocs content root and generated question artifacts.
- [docs/](.): documentation and repository standards.
- [devel/](../devel/): maintainer command surfaces and propagated repository helpers.
- [tools/](../tools/): independent utilities with no repository-package imports.
- [tests/](../tests/): fast pytest, end-to-end, and Playwright verification.

## Script inventory

This is the authoritative inventory of tracked Python and shell scripts outside
`tests/`, `site_docs/`, and `bioproblems_site/`. Root scripts are primary
workflow surfaces; package modules own reusable behavior; `devel/` owns
maintenance and test orchestration; `tools/` remains standalone.

### Root

| Path | Purpose | Invocation |
| --- | --- | --- |
| [build_site.py](../build_site.py) | Unified content build | `source source_me.sh && ./build_site.py` |
| [source_me.sh](../source_me.sh) | Shell environment contract | `source source_me.sh` |

### `tools/`

| Path | Purpose | Invocation |
| --- | --- | --- |
| [tools/csv_topic_sorter.py](../tools/csv_topic_sorter.py) | Sort task CSV rows by metadata topic order | `./tools/csv_topic_sorter.py -i task_files/FILE.csv` |
| [tools/ultra_transfer_audit.py](../tools/ultra_transfer_audit.py) | Audit Ultra transfer artifacts | `python3 tools/ultra_transfer_audit.py` |

### `devel/` repository-owned

| Path | Purpose | Invocation |
| --- | --- | --- |
| [devel/site_maint.py](../devel/site_maint.py) | Topics CSV, question counts, two data builds, and generated reset | `python3 devel/site_maint.py COMMAND` |
| [devel/run_playwright_tests.sh](../devel/run_playwright_tests.sh) | Playwright preflight and runner wrapper | `bash devel/run_playwright_tests.sh` |
| [devel/setup_playwright.sh](../devel/setup_playwright.sh) | Install or verify Playwright tooling | `bash devel/setup_playwright.sh` |

### `devel/` propagated

These are shared repository-maintenance helpers for versioning, changelog,
release, graphify, cleanup, and Markdown maintenance. They are not primary site
application commands.

| Path | Purpose |
| --- | --- |
| [devel/bump_version.py](../devel/bump_version.py) | Update project version |
| [devel/changelog_lib.py](../devel/changelog_lib.py) | Changelog library |
| [devel/changelog_parse.py](../devel/changelog_parse.py) | Parse changelog entries |
| [devel/clean_build.sh](../devel/clean_build.sh) | Clean build artifacts |
| [devel/commit_changelog.py](../devel/commit_changelog.py) | Commit changelog changes |
| [devel/dist_clean.sh](../devel/dist_clean.sh) | Clean distribution artifacts |
| [devel/flatten_broken_md_links.py](../devel/flatten_broken_md_links.py) | Repair broken Markdown links |
| [devel/graphify_context_lib.py](../devel/graphify_context_lib.py) | Graphify context helpers |
| [devel/graphify_docs_lib.py](../devel/graphify_docs_lib.py) | Graphify documentation helpers |
| [devel/graphify_map_repo.py](../devel/graphify_map_repo.py) | Map repository graph |
| [devel/graphify_prune_tests.py](../devel/graphify_prune_tests.py) | Prune graphify tests |
| [devel/make_release.py](../devel/make_release.py) | Prepare a release |
| [devel/markdown_section_sizes.py](../devel/markdown_section_sizes.py) | Report Markdown section sizes |
| [devel/query_changelog.py](../devel/query_changelog.py) | Query changelog entries |
| [devel/rotate_changelog.py](../devel/rotate_changelog.py) | Rotate changelog sections |
| [devel/version_files.py](../devel/version_files.py) | Locate version files |
| [devel/version_lib.py](../devel/version_lib.py) | Versioning library |

## Key content trees

Each subject under [site_docs/](../site_docs/) contains `topicNN/` pages and
question-source text files. The generated [sitemap.md](../site_docs/sitemap.md)
lists all problem-set titles for browser searching. Generated downloads live under each topic's
`downloads/` directory. The page pipeline reconciles generated artifacts with
the live `bbq-*-questions.txt` files and writes the self-test manifest at
`site_docs/assets/data/selftest_question_manifest.json`.

## Documentation map

- [README.md](../README.md): project landing page.
- [INSTALL.md](INSTALL.md): installation and verification.
- [USAGE.md](USAGE.md): site, page, BBQ, and maintainer commands.
- [CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md): components and data flow.
- [BBQ_TASK_CSV_FORMAT.md](BBQ_TASK_CSV_FORMAT.md): task CSV schema.
- [TOPICS_METADATA_FORMAT.md](TOPICS_METADATA_FORMAT.md): metadata and aliases.
- [REPO_STYLE.md](REPO_STYLE.md): repository conventions.
- [PYTHON_STYLE.md](PYTHON_STYLE.md): Python conventions.
- [PYTEST_STYLE.md](PYTEST_STYLE.md): test policy and lanes.

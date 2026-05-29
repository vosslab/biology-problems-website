# File structure

## Top-level layout

- [AGENTS.md](../AGENTS.md): Agent workflow and environment rules.
- [README.md](../README.md): Project overview and quick start.
- [mkdocs.yml](../mkdocs.yml): MkDocs configuration and site navigation.
- [generate_pages.py](../generate_pages.py): Page-generation entrypoint for
  subject indexes, topic pages, the generated nav block, and the self-test
  manifest.
- [run_bbq_tasks.py](../run_bbq_tasks.py): BBQ batch task runner (imports
  `bioproblems_site`).
- [topics_metadata.yml](../topics_metadata.yml): Topic descriptions, aliases,
  and links.
- [bioproblems_site/](../bioproblems_site/): Importable generator package for
  metadata, scanning, rendering, nav updates, and self-test manifest creation.
- [site_docs/](../site_docs/): MkDocs content root for pages and assets.
- `site/`: Built site output (generated, git ignored).
- [docs/](.): Repo documentation and standards.
- [bbq_control/](../bbq_control/): BBQ batch runner scripts and task configs.
- [tools/](../tools/): Helper scripts for content generation tasks.
- [devel/](../devel/): Developer utilities (versioning, changelog tooling).
- [tests/](../tests/): Lint, ASCII compliance, and unit/E2E tests.

## Key subtrees

- [site_docs/assets/](../site_docs/assets/): Shared CSS, JS, fonts, images, and generated data.
- [site_docs/assets/scripts/selftest_progress.js](../site_docs/assets/scripts/selftest_progress.js): Browser self-test completion tracking.
- [site_docs/progress/](../site_docs/progress/): Self-test progress dashboard page.
- [site_docs/biochemistry/](../site_docs/biochemistry/): Biochemistry topic pages and assets.
- [site_docs/genetics/](../site_docs/genetics/): Genetics topic pages and assets.
- [site_docs/daily_puzzles/](../site_docs/daily_puzzles/): Daily puzzle pages and scripts.
- [site_docs/tutorials/](../site_docs/tutorials/): BBQ and LMS import tutorials.
- [bioproblems_site/selftest_manifest.py](../bioproblems_site/selftest_manifest.py): Builds the self-test question manifest.
- [bbq_control/](../bbq_control/): CSV task lists, YAML settings, and runner scripts.

## Generated artifacts

Git-ignored outputs and local-only files are listed in [.gitignore](../.gitignore),
including the built `site/` directory, `report_*.txt` lint reports,
`bbq_generation.log*` files, and the `bbq_converter.py` symlink.

## Documentation map

- [docs/CHANGELOG.md](CHANGELOG.md): Chronological changes.
- [docs/INSTALL.md](INSTALL.md): Setup steps and verification.
- [docs/USAGE.md](USAGE.md): MkDocs usage and build flow.
- [docs/REPO_STYLE.md](REPO_STYLE.md): Repo conventions and naming rules.
- [docs/MARKDOWN_STYLE.md](MARKDOWN_STYLE.md): Markdown style guide.
- [docs/PYTHON_STYLE.md](PYTHON_STYLE.md): Python style guide.
- [docs/AUTHORS.md](AUTHORS.md): Maintainers and contributors.
- [docs/DELETION_MUTANTS_PLAN.md](DELETION_MUTANTS_PLAN.md): Puzzle planning notes.

## Where to add new work

- New site content: [site_docs/](../site_docs/).
- New docs: [docs/](.).
- New scripts: repo root for small tools or [tools/](../tools/).
- New tests: [tests/](../tests/).

# File structure

## Top-level layout

- [AGENTS.md](../AGENTS.md): Agent workflow and environment rules.
- [README.md](../README.md): Project overview and quick start.
- [mkdocs.yml](../mkdocs.yml): MkDocs configuration and site navigation.
- [site_docs/](../site_docs/): MkDocs content root for pages and assets.
- [site/](../site/): Built site output (generated, git ignored).
- [docs/](../docs/): Repo documentation and standards.
- [bbq_control/](../bbq_control/): BBQ batch runner scripts and task configs.
- [tools/](../tools/): Helper scripts for content generation tasks.
- [devel/](../devel/): Developer utilities and scratch resources.
- [tests/](../tests/): Lint and ASCII compliance scripts.
- [topics_metadata.yml](../topics_metadata.yml): Topic descriptions and links.
- [generate_subject_indexes.py](../generate_subject_indexes.py): Subject index generator.
- [generate_topic_pages.py](../generate_topic_pages.py): Topic page generator.
- [llm_generate_problem_set_title.py](../llm_generate_problem_set_title.py): LLM title helper.
- [llm_wrapper.py](../llm_wrapper.py): Local LLM selection and invocation helper.

## Key subtrees

- [site_docs/assets/](../site_docs/assets/): Shared CSS, JS, fonts, and images.
- [site_docs/biochemistry/](../site_docs/biochemistry/): Biochemistry topic pages and assets.
- [site_docs/genetics/](../site_docs/genetics/): Genetics topic pages and assets.
- [site_docs/daily_puzzles/](../site_docs/daily_puzzles/): Daily puzzle pages and scripts.
- [site_docs/tutorials/](../site_docs/tutorials/): BBQ and LMS import tutorials.
- [bbq_control/](../bbq_control/): CSV task lists, YAML settings, and runner scripts.

## Generated artifacts

Git-ignored outputs and local-only files are listed in [.gitignore](../.gitignore),
including [site/](../site/), [pyflakes.txt](../pyflakes.txt),
[ascii_compliance.txt](../ascii_compliance.txt), `bbq_generation.log*`, and
[bbq_converter.py](../bbq_converter.py).

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
- New docs: [docs/](../docs/).
- New scripts: repo root for small tools or [tools/](../tools/).
- New tests: [tests/](../tests/).

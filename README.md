# Biology Problems OER

This repository contains the MkDocs site content and supporting scripts for Biology Problems OER, a free and open collection of biochemistry, genetics, and related problem sets for students and educators. The live site is at [https://biologyproblems.org](https://biologyproblems.org).

## Documentation

- [docs/CHANGELOG.md](docs/CHANGELOG.md): Chronological record of repo changes.
- [docs/INSTALL.md](docs/INSTALL.md): Setup steps and verification.
- [docs/USAGE.md](docs/USAGE.md): MkDocs usage and build flow.
- [docs/REPO_STYLE.md](docs/REPO_STYLE.md): Repo conventions for files, naming, and docs.
- [docs/MARKDOWN_STYLE.md](docs/MARKDOWN_STYLE.md): Markdown rules for this repo.
- [docs/PYTHON_STYLE.md](docs/PYTHON_STYLE.md): Python coding rules for scripts in this repo.
- [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md): High-level components and flows.
- [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md): Directory map and file placement notes.
- [docs/AUTHORS.md](docs/AUTHORS.md): Maintainers and contributors.

## Quick start

1. Install dependencies:
   ```bash
   python3.12 -m pip install -r pip_requirements.txt
   ```
2. Serve the site locally:
   ```bash
   mkdocs serve
   ```
3. Open your browser to `http://127.0.0.1:8000/`.

Site content lives under [site_docs/](site_docs/) and is configured by [mkdocs.yml](mkdocs.yml).

## Repository structure

When showing a directory tree, use ASCII only. Do not use box drawing characters.

- Allowed: `|`, `+-`, `` `-``, spaces
- Not allowed: box-drawing characters (for example U+2500, U+2502, U+2514, U+251C)

Example (ASCII only):

```text
site_docs/
+- index.md                    # Main landing page
+- biochemistry/               # Biochemistry topics
|  `- topic01/                 # Topic 1
|     `- index.md              # Topic 1 content
`- genetics/                   # Genetics topics
   `- topic01/                 # Topic 1
      `- index.md              # Topic 1 content
mkdocs.yml                     # Configuration for MkDocs
```

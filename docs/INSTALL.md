# Install

This repo is a MkDocs site. An install is complete when you can run MkDocs to
serve or build the site from [site_docs/](../site_docs/) using
[mkdocs.yml](../mkdocs.yml).

## Requirements
- Python 3.12.
- pip for installing dependencies from [pip_requirements.txt](../pip_requirements.txt).

## Install steps
1. Clone the repository.
2. From the repo root, install dependencies:
   ```bash
   python3.12 -m pip install -r pip_requirements.txt
   ```

## Verify install
Run:
```bash
python3.12 -m mkdocs --version
```

## Known gaps
- Confirm whether a virtual environment is required or preferred.
- Confirm any non-Python system dependencies beyond pip packages.

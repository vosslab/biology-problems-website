# Install

This repo is a MkDocs site. An install is complete when you can run MkDocs to
serve or build the site from [site_docs/](../site_docs/) using
[mkdocs.yml](../mkdocs.yml).

## Requirements

- Python 3.12.
- pip for installing dependencies from [pip_requirements.txt](../pip_requirements.txt).
- Node.js and npm for Playwright tests and documentation screenshots.
- Playwright Chromium for Blackboard Ultra ZIP downloads containing HTML tables.

## Install steps

1. Clone the repository.
2. From the repo root, install dependencies:
   ```bash
   python3.12 -m pip install -r pip_requirements.txt
   ```
3. For browser tests and screenshot capture, install the development packages and
   Chromium:
   ```bash
   npm install
   npx playwright install chromium
   ```
4. For Blackboard ZIP table screenshots, install the Python Playwright browser:
   ```bash
   source source_me.sh && python3 -m playwright install --only-shell chromium
   ```

## Verify install

Run:

```bash
python3.12 -m mkdocs --version
```

## Known gaps

- Confirm whether a virtual environment is required or preferred.

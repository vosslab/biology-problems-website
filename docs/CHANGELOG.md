# Changelog

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
- Added `--no-tui` to force plain mode.
- Added `pip_requirements.txt` with `textual`.
- Fixed `run_bbq_tasks.py` to guard TUI class definitions when Textual is unavailable.
- Updated BBQ task runners to fail when outputs are missing or mismatched.

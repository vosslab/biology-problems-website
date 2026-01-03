# Changelog

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

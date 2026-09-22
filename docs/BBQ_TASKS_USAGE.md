# BBQ task usage

## Run one task file

From the repository root, source the environment and run the application CLI:

```bash
source source_me.sh && python3 bioproblems.py bbq \
  --flat --max-questions 199 \
  --settings bbq_settings.yml \
  --tasks task_files/biochem_tasks1.csv
```

The `--flat` option selects plain terminal output. Without it, an interactive
Textual dashboard is used when stdout is a terminal.

## Run every task file

The batch mode runs each `task_files/*.csv` file in filename order, with one
isolated application process per CSV:

```bash
source source_me.sh && python3 bioproblems.py bbq --all-tasks
```

Use `--list-tasks` to verify discovery without generating output:

```bash
source source_me.sh && python3 bioproblems.py bbq --list-tasks
```

Batch mode applies a default maximum of 199 questions per task. Pass
`--max-questions`, `--limit`, `--dry-run`, or `--shuffle` to change a trial.
Shuffle is opt-in. A batch reports the ten slowest tasks after all CSV files
finish.

## Key files

- `bioproblems.py`: primary `pages` and `bbq` application CLI.
- `topics_metadata.yml`: site-wide subject and topic metadata source.
- `bbq_settings.yml`: BBQ path and script aliases.
- `task_files/`: per-subject task CSV files.
- `bioproblems_site/bbq_*.py`: package-owned configuration, execution, output,
  TUI, and batch behavior.

## CSV format

- Columns: `subject,topic,script,flags,input,notes` (optional: `output`).
- The `topic` cell may be a canonical `topicNN` key or a per-subject alias
  from `topics_metadata.yml`.
- Output files are auto-detected from newly generated
  `bbq-<script_name>*-problems.txt` files and moved to the matching
  `site_docs/<subject>/<topicNN>/` directory.
- If auto-detection is ambiguous, add an `output` column with a full or
  relative path.
- `script` can be a full path, a relative path, or a configured script alias.
- `flags` holds extra CLI flags. `input` supplies a required input file and is
  added as `-y` by default.
- For `YMATCH`, `YMCS`, and `YMMS`, `input` may be only the YAML basename.

## Sort a task CSV

Use the standalone metadata-driven sorter to regroup a CSV by subject and topic
order while preserving every nonblank task row:

```bash
source source_me.sh && ./tools/csv_topic_sorter.py \
  -i task_files/molecular_bio_tasks.csv
```

## Example row

```text
biochemistry,topic01,YMATCH,,macromolecules.yml,
```

## Config format

`bbq_settings.yml` contains `paths`, `script_aliases`, and optional
`pgml_script_map` sections. Use `{alias}` placeholders in CSV fields to avoid
repeating external repository paths. Export `bp_root` or `BP_ROOT` to override
the configured biology-problems path for a local run.

Failed script output is appended to `bbq_generation_errors.log` in the current
working directory.

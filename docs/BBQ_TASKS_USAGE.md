# BBQ task usage

## Run one task file

From the repository root, source the environment and run the unified build:

```bash
source source_me.sh && ./build_site.py \
  --tasks task_files/biochem_tasks1.csv
```

The selected BBQ work automatically triggers the affected self-test, topic-page,
download, and index/navigation stages.

## Run every task file

Without a scope option, the unified workflow loads every `task_files/*.csv` in
filename order and runs stale configured tasks in one coordinator process. It
does not use the former per-CSV `build_site.py` subprocess path for a normal
build:

```bash
source source_me.sh && ./build_site.py
```

Only an unrestricted all-task run receives the 199-question maximum. A selected
CSV (`--tasks`) keeps each configured generator's own question limit; scoped
`--subject` and `--limit` runs do not receive the all-task default. The public
command accepts `--subject`, `--tasks`, `--limit`, `--shuffle`, `--dry-run`,
`--full`, and `--model`.

Use `--shuffle --limit N` to sample N task rows in random order during
development. Shuffling is opt-in and happens before the limit is applied.

## Key files

- `build_site.py`: primary content-build CLI.
- `topics_metadata.yml`: site-wide subject and topic metadata source.
- `bbq_settings.yml`: BBQ path and script aliases.
- `task_files/`: per-subject task CSV files.
- `bioproblems_site/bbq_*.py`: package-owned configuration, task selection,
  execution, and output behavior.

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

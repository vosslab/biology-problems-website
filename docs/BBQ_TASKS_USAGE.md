# BBQ task usage

## Run one task file

From the repository root, source the environment and run the unified build:

```bash
source source_me.sh && ./build_site.py \
  --task task_files/biochem_tasks1.csv
```

Each selected CSV row automatically triggers its self-test and download work
before the next row starts. After the selected rows finish, each affected topic
page is rendered once with the available links, followed by index/navigation
updates. A failed conversion stops the build before the page is published.

Combine a subject and topic filter for a focused run:

```bash
source source_me.sh && ./build_site.py -S genetics -T topic01
```

`--topic` accepts a canonical `topicNN` key and requires `--subject`. When used
with `--task`, it selects only that subject/topic's rows from the chosen CSV.

## Run every task file

Without a scope option, the unified workflow loads every `task_files/*.csv` in
filename order and runs stale configured tasks in one coordinator process. It
does not use the former per-CSV `build_site.py` subprocess path for a normal
build:

```bash
source source_me.sh && ./build_site.py
```

Only an unrestricted all-task run receives the 199-question maximum. A selected
CSV (`--task`) keeps each configured generator's own
question limit; scoped `-S/--subject` and `-l/--limit` runs do not receive the
all-task default. The public command accepts `-S/--subject`, `-t/--task`,
`-l/--limit`, `-R/--shuffle`, `-b/--backend`, `-n/--dry-run`, `-F/--full`, and
`-m/--model`. Use
`--backend codex` to generate page titles through the configured Codex CLI
instead of Ollama.

Use `-R -l N` to sample N task rows in random order during development.
Shuffling is opt-in and happens before the limit is applied.

## Key files

- `build_site.py`: primary content-build CLI.
- `topics_metadata.yml`: site-wide subject and topic metadata source.
- `bbq_settings.yml`: BBQ path and script aliases.
- `task_files/`: per-subject task CSV files.
- `bioproblems_site/bbq_*.py`: package-owned configuration, task selection,
  execution, and output behavior.

## CSV format

- Columns: `subject,topic,script,flags,input,notes` (optional: `output`).
- The `topic` cell must use a per-subject alias when one is defined in
  `topics_metadata.yml`; otherwise, use the canonical `topicNN` key.
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

For each build run with pending tasks, the runner starts one fresh
`bbq_generation.log` in the current working directory. It contains progress and
failure details for every selected CSV row; numbered backups and the former
`bbq_generation_errors.log` are cleared at startup. An invalid, empty, or
oversized generated candidate is rejected; the previous configured output is
restored when generation fails. A failed task stops the current build before
its downstream stages and later CSV rows run; completed earlier rows remain
published. Self-test conversion stages its HTML and replaces the previous file
only after a successful, nonempty conversion.

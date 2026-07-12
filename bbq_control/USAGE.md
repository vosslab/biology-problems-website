# BBQ control usage

## Run all task files

From the repository root, run:

```bash
./bbq_control/all_tasks.py
```

The command finds the Git repository root, runs every
`bbq_control/task_files/*.csv` file in filename order, and invokes the root
`run_bbq_tasks.py` with absolute paths. It sources the root `source_me.sh` for
each CSV run, so it does not depend on the directory from which it is called.

Use `--list` to verify file discovery without generating any output:

```bash
./bbq_control/all_tasks.py --list
```

For a limited trial, `--limit` applies to each CSV and `--no-shuffle` keeps
the source order:

```bash
./bbq_control/all_tasks.py --limit 1 --no-shuffle --max-questions 1
```

`all_tasks.sh` remains a compatibility launcher for the Python command.

## Run one task file

Use the root runner directly when you want one CSV:

```bash
source source_me.sh && /opt/homebrew/opt/python@3.12/bin/python3.12 run_bbq_tasks.py \
  --flat --max-questions 199 \
  --settings bbq_control/bbq_settings.yml \
  --tasks bbq_control/task_files/biochem_tasks1.csv
```

## Key files

- `run_bbq_tasks.py`: Root runner that executes one task CSV and writes outputs.
- `topics_metadata.yml`: Root site-wide subject and topic metadata source.
- `bbq_control/all_tasks.py`: Root-aware batch coordinator for every task CSV.
- `bbq_control/bbq_settings.yml`: BBQ path and script aliases.
- `bbq_control/task_files/`: Per-subject task CSV files.

## CSV format

- Columns: subject,topic,script,flags,input,notes (optional: output).
- The `topic` cell may be either a canonical `topicNN` key or a
  per-subject alias from `topics_metadata.yml`; aliases resolve to
  `topicNN` at load time.
- Output files are auto-detected from newly generated
  `bbq-<script_name>*-problems.txt` files in CWD and moved to
  `site_docs/<subject>/<topicNN>/` using the detected filename.
- If auto-detection is ambiguous, add an output column with a full or relative path.
- script can be a full path, a relative path, or a script alias.
- flags holds any extra CLI flags for the script.
- input lets you pass a required input file path (added as -y).
- For YMATCH, YMCS, and YMMS, you can set input to just the YAML basename.

## Example row
```text
biochemistry,topic01,YMATCH,,macromolecules.yml,
```

## Config format (bbq_control/bbq_settings.yml)
- paths: Named path aliases you can use as {alias} in CSV fields.
- script_aliases: Short names for long script paths.

## Example config
```yaml
paths:
  bp_root: "~/nsh/biology-problems/problems"
  qti_package_maker: "~/nsh/qti_package_maker"
  matching_sets: "{bp_root}/matching_sets"
  multiple_choice_statements: "{bp_root}/multiple_choice_statements"
script_aliases:
  YMATCH:
    - "{matching_sets}/yaml_match_to_bbq.py"
    - "{matching_sets}/yaml_which_one_mc_to_bbq.py"
  YMCS: "{multiple_choice_statements}/yaml_mc_statements_to_bbq.py"
  YMMS: "{matching_sets}/yaml_make_match_sets.py"
```

## Notes
- If input is set, leave -y out of flags.
- Use {bp_root} in script paths to avoid repeating the full root.
- YMATCH runs both matching-set generators on the same input file.
- You can override bp_root by exporting `bp_root` or `BP_ROOT` in your shell.
- Failed script output is appended to `bbq_generation_errors.log` at the repo root.

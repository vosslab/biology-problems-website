# BBQ control usage

## Quick start
- Edit `bbq_control/bbq_settings.yml` to point bp_root to your local
  biology-problems checkout.
- Edit `bbq_control/bbq_tasks.csv` to add or adjust tasks.
- Run: `python3 bbq_control/run_bbq_tasks.py --config bbq_control/bbq_tasks.csv`
- For sync mode: `python3 bbq_control/bbq_sync_tasks.py --config bbq_control/bbq_tasks.csv`
  - To limit tasks during testing: add `-x 5` (runs the first 5 tasks).
  - To randomize task order for testing: add `--shuffle` (use with `-x` for a random subset).
  - To append max-questions to each task: add `--max-questions 5`.

## Key files
- `bbq_control/run_bbq_tasks.py`: Runs task list and writes outputs.
- `bbq_control/bbq_sync_tasks.py`: Regenerates outputs only when inputs change.
- `bbq_control/bbq_tasks.csv`: Full task list.
- `bbq_control/sub_bbq_tasks.csv`: Subset task list.
- `bbq_control/sub_biochem.csv`: Biochemistry subset for quick testing.
- `bbq_control/bbq_settings.yml`: Path aliases and script aliases.

## CSV format (bbq_tasks.csv)
- Columns: chapter,topic,script,flags,input,notes (optional: output).
- Output files are auto-detected from newly generated
  `bbq-<script_name>*-problems.txt` files in CWD and moved to
  `site_docs/<chapter>/<topic>/` using the detected filename.
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
- Use --bbq-config to point at a different config file.
- YMATCH runs both matching-set generators on the same input file.
- You can override bp_root by exporting `bp_root` or `BP_ROOT` in your shell.
- Failed script output is appended to `bbq_generation_errors.log` in the current
  working directory.

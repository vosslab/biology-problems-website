# BBQ task CSV format

BBQ task CSV files under [bbq_control/task_files/](../bbq_control/task_files/)
drive [run_bbq_tasks.py](../run_bbq_tasks.py) (located at the repo
root). Each row describes one generation task: which script to run,
which inputs to pass, and where the output belongs.

This document describes the column schema and how the `topic` column
resolves through the alias system defined in
[docs/TOPICS_METADATA_FORMAT.md](TOPICS_METADATA_FORMAT.md). For
operational usage of the runner, see
[bbq_control/USAGE.md](../bbq_control/USAGE.md).

## Header row

CSVs are plain RFC 4180 with a header row. The supported columns are:

| Column        | Required | Notes                                                              |
| ---           | ---      | ---                                                                |
| `subject`     | yes      | Canonical subject key (e.g. `biochemistry`).                       |
| `topic`       | yes      | Topic alias when defined; otherwise the canonical `topicNN`.       |
| `script`      | yes      | Path to the generator script, or a `script_aliases` key from settings. |
| `flags`       | no       | Extra CLI flags passed to the script (parsed with `shlex`).        |
| `input`       | no       | Path to the input YAML or other input file, if any.                |
| `notes`       | no       | Free-text comment; ignored by the runner.                          |
| `program`     | no       | Interpreter; defaults to `python3`.                                |
| `output`      | no       | Explicit output path; usually omitted (auto-derived).              |
| `output_file` | no       | Output basename; combined with the auto-derived output dir.        |

The runner reads these columns in `load_tasks_csv` in
[run_bbq_tasks.py](../run_bbq_tasks.py); see the row loop near the
`csv.DictReader` block for the exact field handling.

## Subject and topic resolution

The `subject` column holds the canonical subject key. Subjects are not
aliased; the value must match a top-level key in
[topics_metadata.yml](../topics_metadata.yml).

The `topic` column holds the topic alias when the topic has one
defined. The runner calls
`bioproblems_site.topic_aliases.resolve_topic_key(subject, raw_topic, alias_map, source=csv_path, row_number=...)`
on every non-blank row. The resolver:

- Strips surrounding whitespace only (does not lowercase).
- Rejects empty cells, uppercase, and any character outside `[a-z0-9_]`.
- Looks the alias up under the row's `subject`. Returns the canonical
  `topicNN` on hit.
- For an aliased topic, raises if the author wrote the raw `topicNN`
  literal; the alias must be used instead.
- Raises with a precise message that names the CSV path, row number,
  subject, the offending cell, and (when possible) a suggestion or the
  list of available aliases for that subject.

Output paths use the resolved canonical id, not the alias:

```text
csv row:           biochemistry, amino_acids, ...
resolved topic:    topic03
output dir:        site_docs/biochemistry/topic03/
```

See [docs/TOPICS_METADATA_FORMAT.md](TOPICS_METADATA_FORMAT.md) for the
canonical-id vs alias rules and for the topic key contract.

## Path and script aliases from bbq_settings.yml

Cells in `script` and `input` may contain `{name}` placeholders that
expand against the `paths` and `script_aliases` maps in
[bbq_control/bbq_settings.yml](../bbq_control/bbq_settings.yml).

Common path aliases:

| Placeholder    | Meaning                                              |
| ---            | ---                                                  |
| `{bp_root}`    | Root of the `biology-problems` problems tree.        |
| `{bp_match}`   | `{bp_root}/matching_sets`.                           |
| `{bp_mcs}`     | `{bp_root}/multiple_choice_statements`.              |

Common script aliases:

| Alias    | Resolves to                                                    |
| ---      | ---                                                            |
| `YMATCH` | A pair of YAML-to-BBQ scripts under `{bp_match}` (one row in, two scripts run). |
| `YMCS`   | `{bp_mcs}/yaml_mc_statements_to_bbq.py`.                       |
| `YMMS`   | `{bp_match}/yaml_make_match_sets.py`.                          |

A `script` cell that exactly matches a `script_aliases` key (for
example `YMATCH`) expands to the configured script (or list of
scripts). Otherwise the cell is treated as a path with `{...}`
expansion. This is implemented by `resolve_script_alias` and
`apply_aliases` in [run_bbq_tasks.py](../run_bbq_tasks.py).

## Blank-row separator

A row whose `script` and `flags` cells are both empty is treated as a
visual separator and skipped at parse time. Use blank rows to group
related tasks (typically per topic) and keep the CSV scannable. The
resolver is never asked to validate the topic cell on a separator row.

## Examples

The examples below mirror real rows in
[bbq_control/task_files/biochem_tasks1.csv](../bbq_control/task_files/biochem_tasks1.csv).

```csv
subject,topic,script,flags,input,notes
biochemistry,biomolecules,{bp_root}/biochemistry-problems/PUBCHEM/MACROMOLECULE_CATEGORIZE/which_macromolecule.py,,{bp_root}/biochemistry-problems/PUBCHEM/MACROMOLECULE_CATEGORIZE/simple_macromolecules.yml,
biochemistry,biomolecules,YMATCH,,{bp_match}/biochemistry/macromolecules.yml,
,,,,,
biochemistry,ph_buffers,{bp_root}/biochemistry-problems/buffers/Henderson-Hasselbalch.py,--mc --pH,,
biochemistry,ph_buffers,{bp_root}/biochemistry-problems/buffers/optimal_buffering_range.py,,,
,,,,,
biochemistry,amino_acids,{bp_root}/biochemistry-problems/PUBCHEM/AMINO_ACIDS/alanine_protonation_states.py,,,
```

Things to notice:

- The `topic` column uses aliases (`biomolecules`, `ph_buffers`,
  `amino_acids`), not `topic01`/`topic02`/`topic03`.
- `YMATCH` in the `script` column is a script alias from
  `bbq_settings.yml`; it expands into two scripts and the runner
  emits one task per expanded entry.
- `{bp_root}` and `{bp_match}` expand against the path aliases.
- Blank rows separate topic blocks for readability.

## CLI cross-reference

The same alias system is used by `generate_pages.py -t/--topic`. The
runner and the CLI share
[bioproblems_site/topic_aliases.py](../bioproblems_site/topic_aliases.py)
so the rules are identical.

The preferred CLI form is `subject:alias`, which is always
unambiguous:

```bash
source source_me.sh && python3 generate_pages.py -t biochemistry:amino_acids
```

Other accepted CLI forms:

- `biochemistry:topic03` -- canonical pair; raises if the topic has an
  alias defined (must use the alias instead).
- `amino_acids` -- bare alias; valid only if exactly one subject
  defines that alias. Ambiguous matches raise with the candidate
  `subject:alias` list.
- `topic03` -- bare canonical; valid only if exactly one subject
  defines `topic03` and that topic has no alias. Most subjects share
  `topic03`, so this form usually raises; this is intentional and
  steers authors toward `subject:alias`.

## See also

- [docs/TOPICS_METADATA_FORMAT.md](TOPICS_METADATA_FORMAT.md) -- alias
  rules, topic key contract, hidden topics.
- [bbq_control/USAGE.md](../bbq_control/USAGE.md) -- how to run the
  BBQ task runner end-to-end.
- [bbq_control/bbq_settings.yml](../bbq_control/bbq_settings.yml) --
  path and script alias definitions.
- [run_bbq_tasks.py](../run_bbq_tasks.py) -- CSV row loop and
  resolver wiring.

# topics_metadata.yml format

`topics_metadata.yml` at the repo root is the single source of truth for
subject and topic metadata. It is loaded by every program that needs to
know what subjects and topics exist: `generate_pages.py`,
`run_bbq_tasks.py`, and the `bioproblems_site/` package modules.

This document describes the file's schema and the canonical-id vs alias
contract. The companion document
[docs/BBQ_TASK_CSV_FORMAT.md](BBQ_TASK_CSV_FORMAT.md) describes how the
`topic` column in BBQ task CSVs uses these aliases. Operational usage of
the BBQ runner is in [bbq_control/USAGE.md](../bbq_control/USAGE.md).

## Top-level structure

The file is a YAML mapping of `subject_key -> Subject`. Each `Subject`
contains a `topics` mapping of `topic_key -> Topic`.

```yaml
biochemistry:           # subject_key
  title: Biochemistry
  description: ...
  topics:
    topic01:            # topic_key (canonical id)
      alias: biomolecules
      title: Life Molecules
      description: ...
    topic02:
      alias: ph_buffers
      title: Water and pH
      description: ...
```

Subject keys match `[a-z_]+`. Topic keys match exactly `^topic\d{2}$`
(see "Topic key contract" below).

## Subject keys per Subject

| Key           | Required | Type    | Notes                                   |
| ---           | ---      | ---     | ---                                     |
| `title`       | yes      | string  | Display name; non-empty.                |
| `description` | yes      | string  | May be empty string but must be a string. |
| `topics`      | yes      | mapping | Mapping of `topic_key -> Topic`.        |

Subjects do NOT have aliases. Subject keys are already short, canonical,
human-meaningful names (`biochemistry`, `genetics`, `molecular_biology`).

## Keys per Topic

| Key           | Required | Type    | Notes                                              |
| ---           | ---      | ---     | ---                                                |
| `title`       | yes      | string  | Display name; non-empty.                           |
| `description` | yes      | string  | Non-empty after trim.                              |
| `libretexts`  | no       | mapping | External link block; see below.                    |
| `visible`     | no       | bool    | Defaults to `true`. Hidden topics still resolvable. |
| `alias`       | no       | string  | Author-facing slug; charset `[a-z0-9_]+`.          |

The `libretexts` block (when present) requires `url` (must start with
`https://bio.libretexts.org/`) and `chapter` (integer, 1 or greater).
`unit` is optional and defaults to `0`. Note: `libretexts.chapter` is
LibreTexts' own external chapter number; it is unrelated to the retired
internal "chapter" terminology mentioned under "Hierarchy" below.

## Canonical id vs author-facing alias

There are two names for every topic, used at different layers:

- `topicNN` is the canonical id. It is the YAML mapping key, the
  on-disk folder name (`site_docs/<subject>/topicNN/`), the mkdocs nav
  segment, the URL segment, and the sort order.
- `alias` is the author-facing input form. Authors type the alias (for
  example `amino_acids`) into BBQ task CSVs and into
  `generate_pages.py -t/--topic`. The resolver in
  `bioproblems_site/topic_aliases.py` converts the alias back to the
  canonical `topicNN` at input time.

Aliases are unique within a subject. The same alias text MAY repeat
across different subjects. For example, both `biochemistry` and
`molecular_biology` could legally define an alias `nucleic_acids` on
different topic numbers; the subject context disambiguates.

Once a topic has an alias defined, all author-facing input MUST use
the alias. Passing the raw `topicNN` for an aliased topic raises a
loud error with the alias to use. This keeps author input consistent
across the codebase.

## URL and folder mapping

Aliases are NOT used in mkdocs URLs or in `site_docs/` folder paths.
The site continues to serve `/<subject>/<topicNN>/`. Every link, nav
entry, and folder name remains canonical.

The alias resolves at input time only. The full path for the amino
acids topic is:

```text
author input:    biochemistry:amino_acids
internal:        biochemistry / topic03
on disk:         site_docs/biochemistry/topic03/
served URL:      /biochemistry/topic03/
```

Adding an alias does not move folders, rename URLs, or change the
mkdocs nav. Renaming an alias has zero effect on the rendered site.

## Hierarchy

The hierarchy is exactly two levels: subjects at the top, topics
underneath. There is no third "textbook" or "chapter" level; legacy
code that used those terms (`chapter` for what is now `subject`,
`subject` for what is now `topic`) has been retired. The
`libretexts.chapter` field is a different concept: it refers to
LibreTexts' external chapter number for cross-referencing, not to any
internal hierarchy.

Subjects are already named (`biochemistry`, `genetics`,
`molecular_biology`, ...) and are never aliased. Only topics get
aliases.

## Topic key contract

Topic keys match exactly `^topic\d{2}$`: the literal string `topic`
followed by exactly two digits. The following are all rejected at
load time:

- `topic1` (one digit)
- `topic001` (three digits)
- `Topic03` (uppercase)
- `topic_03` (underscore)

The canonical key form is also rejected as an alias value, so an
author cannot define `alias: topic15` and collide with a future
canonical id.

## Alias stability

Aliases are part of the public author-facing contract. They appear
verbatim in BBQ task CSVs, in CLI invocations, and in author memory.

- Do NOT rename an alias casually as part of a metadata cleanup pass.
- A rename is a deliberate, scripted CSV migration: update
  `topics_metadata.yml`, then rewrite every matching cell in
  `bbq_control/task_files/*.csv` in the same patch.
- Adding a new alias to a topic that did not have one is also a
  contract change; expect to update CSVs in the same patch.

## Hidden topics

Topics with `visible: false` are still first-class metadata entries.
They remain referenceable by both BBQ task CSVs and the
`generate_pages.py -t/--topic` filter. The resolver does not filter on
`visible`; visibility only affects rendering (subject index, nav).

This lets you keep a topic in the metadata file (for BBQ generation,
for archive, for in-progress work) without exposing it on the public
site.

## Example

```yaml
biochemistry:
  title: Biochemistry
  description: |
    Study of molecular processes in living systems.
  topics:
    topic01:
      alias: biomolecules
      title: Life Molecules
      description: Categorize biomolecules by class and polarity.
      libretexts:
        url: https://bio.libretexts.org/Courses/Example/01%3A_Unit_1/1.01%3A_Molecules
        unit: 1
        chapter: 1
    topic02:
      title: Water and pH
      description: Buffer and pKa calculations.
      visible: false
```

Notes on the example:

- `topic01` has an alias; authors must write `biochemistry:biomolecules`
  in CSVs and on the CLI. Writing `biochemistry,topic01` raises.
- `topic02` has no alias; authors may still write `biochemistry,topic02`
  directly. Adding an alias later is fine but is a CSV migration event.
- `topic02` is hidden from the rendered site but remains a valid target
  for BBQ tasks and the CLI topic filter.

## See also

- [docs/BBQ_TASK_CSV_FORMAT.md](BBQ_TASK_CSV_FORMAT.md) -- BBQ task CSV
  schema and how the `topic` column resolves.
- [bbq_control/USAGE.md](../bbq_control/USAGE.md) -- how to run the
  BBQ task runner.
- [bioproblems_site/metadata.py](../bioproblems_site/metadata.py) --
  schema validator and loader.
- [bioproblems_site/topic_aliases.py](../bioproblems_site/topic_aliases.py)
  -- pure resolver helpers used by every alias-aware caller.

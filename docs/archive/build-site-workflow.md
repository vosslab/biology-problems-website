# Plan: Consolidate the site build workflow

## Context

The repository currently has a root `bioproblems.py` application CLI with separate `pages` and `bbq` commands. That reflects the implementation split, but it makes the user remember which generated artifacts become stale after question generation.

The intended architecture keeps those implementation responsibilities separate while giving the maintainer one normal command:

```text
BBQ generation
    -> affected subjects/topics
    -> self-tests
    -> topic pages
    -> download artifacts
    -> subject indexes and MkDocs navigation
```

The root executable should be renamed to `build_site.py`. The `bioproblems_site/` package must not be renamed; it owns the reusable implementation and is intentionally distinct from the executable name.

The existing package already contains separate BBQ, page, topic, output, and configuration code. The implementation should extract the smallest useful contracts from that code rather than creating a new framework. Existing line ranges are discovery evidence only. Before dispatch, verify ownership from call relationships, inputs, outputs, and state dependencies.

MkDocs already has `site_url: https://biologyproblems.org/` and owns final static-site generation, including `sitemap.xml`. This build pipeline generates source and derived content needed by MkDocs; it must not add sitemap generation.

## Objectives

- Make `./build_site.py` the normal site-maintenance command.
- Run BBQ generation and all affected downstream work in dependency order.
- Propagate structured information about what BBQ actually changed.
- Keep stale checks local to the stage that owns each output.
- Use existing files, mtimes, and known direct input/output relationships; do not add persistent build state.
- Keep the coordinator small enough that its code reads like the dependency pipeline.
- Preserve the package boundary: `bioproblems_site/` remains the implementation package.
- Preserve the user’s ability to restrict work to one subject, one task CSV, or a development limit.
- Make `--full` bypass stale checks while respecting the requested scope.
- Make `--dry-run` report planned work without invoking generators, LLM calls, or writing generated files.
- Regenerate inexpensive subject indexes and MkDocs navigation unconditionally on normal runs unless repository evidence proves that this is materially expensive.
- Leave final static-site output, including the SEO sitemap, to `mkdocs build`.

## Design philosophy

Use a simple dependency pipeline, not separate user-sequenced commands and not a generalized workflow engine.

Each stage should answer two questions:

1. `needs_run(...)`: is this stage’s output missing, stale relative to its direct inputs, or forced by `--full`?
2. `run(...)`: what does this stage write, and what structured result should it return to the next stage?

The coordinator owns order and propagation of affected topics. It does not own BBQ generation details, page rendering details, download naming rules, or stale-detection rules belonging to another stage.

Do not add a build database, cache manifest, hash store, generalized DAG engine, or other persistent state. Prefer a one-second unconditional rebuild of a cheap global index over new state and dependency bookkeeping.

The extraction is behavior-preserving except for the explicitly requested interface and workflow changes: the root command is renamed and simplified, downstream stages become automatic, stale work is skipped, structured change information is returned, and the listed option/default behavior is clarified. Do not describe moved code as having unchanged bodies when these changes are made.

## Scope

- Rename the root executable from `bioproblems.py` to `build_site.py`.
- Remove the normal-user `pages` and `bbq` subcommand boundary.
- Keep `bioproblems_site/` and its package-owned implementation.
- Add a small root CLI that parses the public build options and delegates to the package coordinator.
- Add a small coordinator module, preferably `bioproblems_site/build_coordinator.py`, if existing `pipeline.py` cannot remain equally clear after simplification.
- Introduce a structured BBQ result equivalent to:

  ```python
  @dataclass
  class BuildChanges:
      changed_topics: set[str]
      changed_subjects: set[str]
      changed_files: set[Path]
  ```

- Ensure BBQ task configuration supplies canonical subject/topic keys to the result-producing code instead of requiring downstream code to infer them by parsing arbitrary paths.
- Give BBQ, self-test, topic-page, download, and subject-index stages small local stale checks.
- Ensure the topic-page stage does not secretly create self-tests or download artifacts as a side effect of rendering a page. Those are separate stages in the coordinator even if they continue to share low-level helpers.
- Document and test the new command contract.
- Record documentation changes in `docs/CHANGELOG.md` when implementation begins.

## Non-goals

- Do not rename `bioproblems_site/`.
- Do not retain root `pages` or `bbq` commands as aliases.
- Do not keep user-facing sequencing flags merely because the old implementation has them.
- Do not add sitemap generation to `build_site.py`.
- Do not make `build_site.py` invoke `mkdocs build` or `mkdocs serve` unless a separate requirement is approved.
- Do not add a persistent dependency database, cache manifest, hash manifest, or generalized DAG scheduler.
- Do not redesign BBQ question generation, title generation, or page content unrelated to the workflow contract.
- Do not perform security-hardening work unrelated to this low-security MkDocs maintenance refactor.
- Do not implement the separate user-visible problem index in this change unless explicitly added to the implementation scope later.

## Current state summary

Verify these facts against the current checkout before implementation rather than assuming that historical line numbers remain exact:

- The root CLI currently dispatches `pages` and `bbq` subcommands.
- `bioproblems_site/bbq_cli.py` owns the current BBQ argument surface and delegates into BBQ runner/batch code.
- `bioproblems_site/pages_cli.py` owns the current page-generation argument surface and delegates into the existing pipeline.
- `bioproblems_site/pipeline.py` currently exposes several booleans for subject indexes, topic pages, downloads, and self-tests. Those booleans are implementation-era controls, not the desired public contract.
- `bioproblems_site/topic_page.py` currently combines topic-page rendering with self-test and download-related behavior. Verify the call graph and split the side effects at semantic ownership boundaries.
- `bioproblems_site/bbq_config.py` already loads task CSVs and resolves subject/topic information. Extend that contract only as needed for structured change reporting.
- `mkdocs.yml` already declares `site_url`, so MkDocs should remain the owner of the generated SEO sitemap.

Before dispatch, the manager must inspect call relationships and state dependencies for BBQ runner, BBQ outputs, BBQ configuration, topic pages, self-tests, downloads, and subject indexes. Old line ranges may guide discovery but must not dictate module boundaries.

## Architecture boundaries and ownership

### Mapping

| Boundary | Owns | Must not own |
| --- | --- | --- |
| `build_site.py` | Public argument parsing, repository-root startup, exit-code translation | Generation logic, stale checks, page rendering, BBQ details |
| `build_coordinator.py` or a simplified existing coordinator | Scope normalization, stage order, propagation of `BuildChanges`, aggregate reporting | Individual generator commands, filename conventions, hidden stage side effects |
| BBQ configuration and runner modules | Task selection, task invocation, output detection, subject/topic/file change reporting | Self-test/page/download generation |
| Self-test module or existing semantic owner | Self-test input/output mapping and stale checks | Topic-page orchestration and unrelated BBQ scheduling |
| Topic-page module | Topic metadata/page rendering and topic-page stale checks | Creating downloads or silently regenerating self-tests |
| Download/output module | Expected download filenames, source/output stale checks, artifact creation | Deciding which tasks should run |
| Subject-index/nav owner | Subject indexes and MkDocs nav generation | BBQ generation and topic-page domain logic |
| MkDocs | Final static site, `sitemap.xml`, theme output | Source/generated-content dependency decisions |

Do not create `bbq_runner`, `bbq_outputs`, and `bbq_config` circular imports by slicing the old module mechanically. If a current module already owns a semantic responsibility, retain it and add a narrow result type or helper at the least-coupled boundary.

### Structured change contract

The BBQ stage must return a structured result, not only an exit code:

```python
@dataclass(frozen=True)
class BuildChanges:
    changed_topics: set[str]
    changed_subjects: set[str]
    changed_files: set[Path]
```

Use canonical subject/topic identifiers consistently. If a task can affect several generated files, add every actually changed file to `changed_files` and add the task’s canonical topic and subject to the corresponding sets. If a dry run cannot know actual post-run changes, return the planned scope in a clearly documented dry-run result rather than pretending that files were written.

The coordinator should pass this object directly to downstream stages. Do not make every downstream stage rescan the repository to guess what BBQ changed.

## User-facing command contract

The supported normal commands are:

```text
./build_site.py
./build_site.py --subject genetics
./build_site.py --tasks task_files/genetics_tasks.csv
./build_site.py --subject genetics --dry-run
./build_site.py --full
```

The normal run must:

1. Select configured BBQ work within the requested scope.
2. Run only BBQ tasks whose direct outputs are missing/stale, unless `--full` is set.
3. Return the subjects, topics, and files actually changed or planned.
4. Regenerate self-tests for affected topics when their direct inputs require it.
5. Regenerate affected topic pages when their direct inputs require it.
6. Generate missing/stale download artifacts for affected topics.
7. Regenerate subject indexes and the MkDocs nav block. If this is cheap, do it unconditionally on every normal run.

The root CLI should keep these options because they have clear demonstrated uses:

| Option | Contract |
| --- | --- |
| `--subject SUBJECT` | Restrict every stage to one subject, such as `genetics`. |
| `--tasks CSV` | Run one BBQ task CSV instead of all configured task files. Validate that it is inside the supported task-file scope. |
| `--limit N` | Limit BBQ work during development/testing; downstream work is limited to the topics reported by that BBQ run. |
| `--dry-run` | Report planned stages and outputs without generator/LLM execution or file writes. |
| `--full` | Bypass stale checks and rebuild everything in the selected scope. |

Review the following options individually against current repository usage and documented workflows before deciding their final location:

- `--max-questions`: retain only if development or documented generation workflows use it; otherwise make it an internal runner parameter.
- `--shuffle`: retain only if task-order randomization is an active development workflow; otherwise make it internal.
- `--flat`: retain only if the non-TUI batch mode is actively used; otherwise keep it internal.
- `--settings`: retain only if alternate BBQ settings files are used in real workflows; otherwise use the repository default internally.
- `--model`: retain only if switching Ollama models is a demonstrated workflow.
- `--quiet`: retain only if scripts or documented workflows consume it. It is not a primary architecture option.

Remove the normal-user sequencing options `--subject-indexes`, `--topic-pages`, `--generate-downloads`, `--selftests`, and `--no-selftests`. Remove old `pages`/`bbq` command syntax and do not add compatibility aliases.

Unless repository evidence says otherwise, apply `--full` as “ignore stale checks within the selected scope” while still respecting `--subject`, `--tasks`, and `--limit`. A limited full run should not silently become an all-repository run.

## Coordinator contract

The coordinator should remain small and readable. Its shape should be equivalent to this, adapted to the actual repository APIs:

```python
def build_site(scope: BuildScope) -> BuildReport:
    changes = bbq_runner.run_if_needed(scope)

    affected_topics = set(changes.changed_topics)
    if scope.full:
        affected_topics = all_topics(scope.subject)

    for topic in affected_topics:
        if selftests.needs_run(topic, scope, changes):
            selftests.run(topic, scope)
        if topic_pages.needs_run(topic, scope, changes):
            topic_pages.run(topic, scope)
        if downloads.needs_run(topic, scope, changes):
            downloads.run(topic, scope)

    subject_indexes.run(scope)
    return report
```

The actual ordering must account for the fact that a newly generated self-test may be a direct input to a topic page and a newly generated topic page may reference downloads. The implementation should either update each stage’s input model or run the stages in the order that makes those relationships explicit. The coordinator must not hide those dependencies in a monolithic `run()` function.

`--dry-run` must use the same selection and stale-check logic but stop before subprocesses, LLM calls, and writes. Its report should make clear which stages would run and why.

## Stale-check contract

Each check must be local, deterministic, and based on direct known relationships.

### BBQ task output

Run a task when any of the following is true:

- `--full` is set.
- An expected output is missing.
- A direct task input, generator source, or relevant configuration is newer than the expected output.
- The requested development options explicitly force the task to run.

The runner must identify the output files it inspected and report files that were created or changed. Avoid broad repository scans and avoid inferring the topic from output-path string conventions when task configuration already knows it.

### Self-test

Run a topic self-test when:

- `--full` is set.
- The self-test HTML is missing.
- Its direct `bbq-*.txt` source is newer than the self-test HTML.
- The BBQ result says that the relevant source changed.

Keep self-test regeneration separate from topic-page rendering. If the current implementation has a helper that builds a self-test while writing `index.md`, split the orchestration while preserving shared formatting helpers.

### Topic page

Run a topic page when:

- `--full` is set.
- `index.md` is missing.
- Topic metadata or other direct source inputs are newer than `index.md`.
- A changed self-test, BBQ output, or other known generated input belongs to that topic.

The page stage may update links and content that refer to downloads, but it must not create download files as a hidden side effect.

### Download artifacts

Run download generation when:

- `--full` is set.
- An expected artifact is missing.
- Its direct BBQ/source input is newer than the artifact.
- The affected-topic result identifies the source as changed.

Reuse the existing output naming and format ownership. Do not duplicate expected filename logic in the coordinator.

### Subject indexes and nav

First measure the current index/nav generation cost. If it is inexpensive, always regenerate the subject indexes and MkDocs nav on a normal run. Only add membership/title/order change detection if unconditional work is demonstrably expensive or has an observable side effect that makes it unsuitable.

## Milestone plan

### Milestone 1: Repository and call-graph reconnaissance

Inspect the current entrypoints, task CSV schema, output naming, self-test inputs, topic-page inputs, index/nav writers, and all executable configuration formats. Include `*.csv`, `*.yaml`, `*.yml`, `*.json`, shell files, and other repository-local operational inputs in stale-reference searches.

**Exit gate:** a written ownership map identifies each stage’s direct inputs, outputs, and side effects; no module split is justified only by old line ranges.

### Milestone 2: Public CLI and root rename

Create `build_site.py` as the only root application executable, move/reuse the existing dispatch entrypoint, and remove the old subcommand parser. Keep the root file thin: parse options, construct scope, call the coordinator, and return its exit status.

**Exit gate:** the five supported example commands parse correctly; old `pages` and `bbq` forms fail clearly; invalid arguments return nonzero status.

### Milestone 3: Structured BBQ changes

Add the `BuildChanges` contract and thread it through task selection and execution. Preserve batch behavior, but make the runner report canonical subjects, topics, and changed files rather than only an integer status.

**Exit gate:** a focused test demonstrates that one changed task yields the expected subject/topic/file sets, while an unchanged task yields no false downstream topic.

### Milestone 4: Semantic stage boundaries

Refactor only where needed so self-tests, topic pages, downloads, and indexes have explicit stage entrypoints and local stale checks. Confirm the ownership map before creating new modules. Avoid circular imports and avoid making `build_site.py` or the coordinator the new home for domain logic.

**Exit gate:** each stage can be tested with a temporary input/output tree; a topic-page render does not unexpectedly create self-test or download files.

### Milestone 5: Coordinator integration

Implement the dependency order, scope propagation, full-mode behavior, dry-run behavior, reporting, and unconditional cheap index/nav regeneration. Make the coordinator call stage APIs rather than embedding generation details.

**Exit gate:** representative changed/unchanged/full/limited/subject-scoped runs show the expected stage decisions and writes.

### Milestone 6: Documentation and removal audit

Update usage and architecture documentation, record the change in `docs/CHANGELOG.md`, remove obsolete entrypoints only after equivalence checks, and audit all source/config formats for stale references.

**Exit gate:** no references remain to removed root scripts or old subcommand forms in Python, Markdown, shell, YAML, JSON, CSV, TOML, Makefiles, CI configuration, or other executable configuration.

## Work packages

### WP1: Root CLI

**Owner:** application entrypoint.

**Touchpoints:** `build_site.py`, existing CLI helpers only where their parsing logic is reusable.

**Acceptance:** one root command, no subcommands, no legacy aliases, thin parsing/orchestration surface, correct help and exit codes.

### WP2: Scope and change contract

**Owner:** package-level build contracts and BBQ runner boundary.

**Touchpoints:** new narrow result module if needed, `bbq_config.py`, `bbq_runner.py`, `bbq_batch.py`, task selection helpers.

**Acceptance:** canonical subject/topic propagation, changed file reporting, dry-run semantics, preserved batch invocation behavior.

### WP3: Stage-local stale checks

**Owner:** the semantic module that owns each output.

**Touchpoints:** self-test, topic-page, download/output, and index/nav code identified during WP1 reconnaissance.

**Acceptance:** checks use direct inputs and outputs, `--full` bypasses them, no persistent state is introduced, and hidden cross-stage writes are removed.

### WP4: Coordinator

**Owner:** small package coordinator.

**Touchpoints:** coordinator plus stage entrypoints.

**Acceptance:** order is BBQ -> self-tests -> topic pages -> downloads -> indexes/nav; affected-topic propagation is direct; subject/task/limit scope is preserved; coordinator remains orchestration-only.

### WP5: Documentation and removal

**Owner:** repository maintenance.

**Touchpoints:** README/usage docs, architecture/file-layout docs if applicable, `docs/CHANGELOG.md`, stale-reference audit.

**Acceptance:** documented examples work, old entrypoints are removed only after checks, and CSV/config references are covered.

## Acceptance criteria and gates

- `./build_site.py -h` describes the unified workflow and does not advertise `pages` or `bbq`.
- `./build_site.py` runs the normal dependency pipeline.
- `./build_site.py --subject genetics` restricts BBQ, downstream topics, and indexes to the intended subject scope.
- `./build_site.py --tasks task_files/genetics_tasks.csv` selects the requested task CSV and propagates its affected topics.
- `./build_site.py --subject genetics --dry-run` performs no generator, LLM, subprocess, or file-write side effects.
- `./build_site.py --full` bypasses stale checks but honors the selected subject/task/limit scope.
- A fresh normal run skips unchanged expensive stages while still performing cheap unconditional index/nav work if that measurement supports the choice.
- Touching or changing one task input causes only its reported topic and required downstream artifacts to be selected.
- Missing self-test and download outputs are recreated without requiring user sequencing flags.
- A page build does not silently create unrelated output files outside its stage contract.
- Representative invalid arguments and generator failures produce nonzero exit codes and useful messages.
- Old `bioproblems.py`/`generate_pages.py`/other removed entrypoint references are absent from source and operational configuration, including CSV files.
- `mkdocs build --strict` still succeeds and generates the final `sitemap.xml` through MkDocs using the configured `site_url`.
- The full repository test suite and focused workflow tests pass.

## Test and verification strategy

### Focused unit tests

- Parse and validate the unified CLI, including representative valid/invalid arguments and exit-code behavior.
- Test `BuildChanges` construction and canonical subject/topic propagation.
- Test each stage’s `needs_run()` with missing outputs, older outputs, newer direct inputs, and `full=True`.
- Test dry-run reports without invoking subprocesses, generators, LLMs, or writes.
- Test coordinator order with stub stages and verify that `changed_topics` flows only to the correct downstream stages.
- Test subject and task-file scope boundaries.

### Repository-level checks

- Run the existing focused BBQ/task smoke tests with a small limit and dry-run/flat mode as appropriate.
- Run the full pytest suite using the repository’s documented Python environment.
- Run static checks required by the repository style rules.
- Run `git diff --check`.
- Run `mkdocs build --strict` and inspect that the generated static site contains the sitemap and expected representative pages.
- Audit removed names and command forms across Python, Markdown, shell, YAML/YML, JSON, TOML, CSV, Makefiles, CI files, and other executable configuration formats.

### Old/new entrypoint equivalence before deletion

Before deleting old scripts or old implementation entrypoints, compare old and new behavior for representative cases. The comparison must include:

- default invocation;
- one subject filter;
- one task CSV;
- a limited BBQ run;
- a full run;
- dry-run behavior;
- missing or malformed task/settings paths;
- invalid numeric values;
- generator failure and nonzero exit propagation;
- help output and exit codes.

For the former `generate_pages.py` path in particular, test parser normalization and defaults explicitly: subject/topic filters, default stage selection, self-test defaults, download generation behavior, model selection, and malformed combinations. Do not delete it based only on a successful happy-path replacement.

## Risk register

| Risk | Evidence to collect | Mitigation |
| --- | --- | --- |
| The coordinator becomes a new monolith | Coordinator line count and imports; domain logic in its functions | Keep stage APIs narrow; reject generation logic in coordinator review |
| Topic-page code retains hidden self-test/download writes | Temporary-tree test and output diff | Separate stage calls and preserve only shared low-level helpers |
| BBQ reports the wrong topic | Task CSV schema and generated output mapping | Carry canonical keys from configuration; test one-task propagation |
| Batch default changes single-task behavior | Parser tests for batch and single-task modes | Apply the special `199` default only in batch normalization, not in the shared parser default |
| `--full` escapes requested scope | Subject/task/limit integration tests | Treat full as stale-check bypass, not scope expansion |
| Dry run still triggers side effects | Subprocess/LLM/write spies and temporary tree | Make dry-run a first-class scope property checked before stage execution |
| Mtime resolution causes an unexpected skip | Tests with controlled timestamps and missing-output cases | Use missing output as authoritative; ensure writes update output mtimes; avoid persistent state |
| Index/nav change detection adds needless complexity | Measured generation time and side effects | Prefer unconditional regeneration when cheap |
| Old references survive in task CSVs/config | Format-inclusive audit output | Search operational inputs before deletion; include CSV explicitly |
| MkDocs sitemap responsibility is duplicated | `mkdocs build --strict` output and config inspection | Keep sitemap generation entirely in MkDocs |

## Rollout and release checklist

1. Complete call-graph and ownership reconnaissance.
2. Add focused tests for the new contracts before deleting old entrypoints.
3. Implement the root rename and unified parser.
4. Implement structured BBQ results.
5. Implement stage-local stale checks and explicit stage boundaries.
6. Implement the coordinator and dry-run/full scope behavior.
7. Run representative old/new checks, focused tests, full tests, static checks, and strict MkDocs build.
8. Run the all-format stale-reference audit, including CSVs.
9. Update usage/architecture documentation and `docs/CHANGELOG.md`.
10. Remove obsolete scripts only after the gates pass.

## Documentation close-out requirements

Document the following as the user-facing contract:

- `./build_site.py` is the normal maintenance command.
- `--subject`, `--tasks`, `--limit`, `--dry-run`, and `--full` examples.
- The program automatically propagates BBQ changes through self-tests, topic pages, downloads, and indexes/nav.
- `mkdocs build` produces the final static site and sitemap.
- Advanced options, if retained, are explicitly labeled maintainer/development controls rather than required sequencing steps.

Document the architecture briefly for maintainers: the coordinator owns order, each stage owns its stale check and outputs, and BBQ returns structured affected-scope information.

## Patch plan and reporting format

Each implementation patch should report:

- files changed and the ownership boundary each file serves;
- whether behavior changed beyond the explicitly approved CLI/workflow changes;
- stale-check rules implemented for each stage;
- focused tests run and their results;
- full-suite and MkDocs validation status;
- old/new equivalence cases covered;
- stale-reference audit scope and result;
- any unresolved option-retention decision.

Keep patches small enough that a reviewer can distinguish CLI changes, structured BBQ reporting, stage-boundary changes, coordinator integration, and cleanup.

## Open questions and decisions needed

- Verify whether subject indexes/nav are cheap enough for unconditional regeneration. The default recommendation is yes if measurement is around the current one-second scale.
- Verify which advanced BBQ options have active repository usage before exposing them in the unified command.
- Verify whether the current `pipeline.py` can become the coordinator without becoming a large mixed-responsibility module, or whether a new thin coordinator is clearer.
- Verify semantic ownership before splitting or merging BBQ modules; do not use historical line ranges as the design.
- Decide whether `--limit` on a full run means “full rebuild of the topics selected by the limited BBQ scope.” The recommended interpretation is yes.
- Keep the user-visible problem index/SEO sitemap enhancement as a separate follow-up. The current site can support a generated, searchable problem-set index using existing titles and human-readable links, but that is not required to implement this build pipeline.

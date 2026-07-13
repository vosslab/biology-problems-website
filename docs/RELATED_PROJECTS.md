# Related projects

These projects supply the question sources, conversion pipeline, local title support,
and site framework used by Biology Problems OER.

## Confirmed related projects

### biology-problems

- Relationship: upstream question-generator collection
- Link: [github.com/vosslab/biology-problems](https://github.com/vosslab/biology-problems)
- Evidence: `bbq_control/bbq_settings.yml` points task rows at this repository, and
  the public project contains the biology generators represented on this site.

### qti-package-maker

- Relationship: direct conversion dependency
- Link: [github.com/vosslab/qti-package-maker](https://github.com/vosslab/qti-package-maker)
- Evidence: `source_me.sh` adds the local package to `PYTHONPATH`, and the site
  pipeline uses it to produce Blackboard, Canvas, human-readable, and self-test files.

### local-llm-wrapper

- Relationship: direct title-generation dependency
- Link: [github.com/vosslab/local-llm-wrapper](https://github.com/vosslab/local-llm-wrapper)
- Evidence: `source_me.sh` exposes the package and
  `bioproblems_site/problem_set_title.py` imports its LLM client and XML helpers.

### MkDocs

- Relationship: direct site-generation dependency
- Link: [github.com/mkdocs/mkdocs](https://github.com/mkdocs/mkdocs)
- Evidence: `mkdocs.yml`, the deployment workflow, and `pip_requirements.txt` define
  the repository as an MkDocs static site.

### Material for MkDocs

- Relationship: direct theme dependency
- Link: [github.com/squidfunk/mkdocs-material](https://github.com/squidfunk/mkdocs-material)
- Evidence: `mkdocs.yml` selects the Material theme and configures its palette,
  navigation, search, and social links.

## Evidence notes

Relationships are confirmed from imports, manifests, configuration paths, and the
public project repositories. Web discovery was limited to the named dependencies
already present in this checkout.

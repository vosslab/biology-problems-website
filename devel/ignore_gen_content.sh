#!/bin/bash
# Reset all generated content under site_docs/ back to HEAD.
# Tracked generated files are restored with `git checkout`; newly
# created (untracked) generated files are removed with `git clean`.
# Source files (problem_set_titles.yml, subject-level index.md, hand
# written .md) are intentionally NOT touched.

# Restore tracked generated files to their committed state.
git checkout -- \
	":(glob)site_docs/**/downloads/*" \
	":(glob)site_docs/*/topic*/index.md" \
	":(glob)site_docs/**/bbq-*-questions.txt" \
	site_docs/assets/data/selftest_question_manifest.json

# Remove untracked generated files (new selftest-*.html, zips, pgml,
# pg, and freshly added bbq question sets).
git clean -f -- \
	":(glob)site_docs/**/downloads/*" \
	":(glob)site_docs/**/bbq-*-questions.txt"

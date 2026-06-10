"""Unit tests for bioproblems_site.orphan_prune.

Covers download detection and pure naming, in-file pruners (index includes
and title cache), pgml/pg mapping and topic-master quarantine, and the
dry-run no-op guarantee of reconcile_topic. Git helper integration is
covered by the E2E test, not here.
"""

# Standard Library
import os
import pathlib

# PIP3 modules
import yaml
import pytest

# local repo modules
import bioproblems_site.orphan_prune as orphan_prune
import bioproblems_site.topic_page as topic_page


#============================================
# pure_download_basename equivalence with get_outfile_name

# The 4 download format keys as (prefix, extension) pairs.
DOWNLOAD_FORMAT_CASES = [
	("selftest", "html"),
	("blackboard_qti_v2_1", "zip"),
	("canvas_qti_v1_2", "zip"),
	("human_readable", "html"),
]

# Cores exercising the naming branches: normal, MATCH-*, already-prefixed.
EQUIVALENCE_CORES = [
	"chemical_group_pka_forms",
	"MATCH-amino_acid_codes",
	"selftest-already_prefixed",
]


@pytest.mark.parametrize("core", EQUIVALENCE_CORES)
@pytest.mark.parametrize("prefix,ext", DOWNLOAD_FORMAT_CASES)
def test_pure_download_basename_matches_get_outfile_name(tmp_path, core, prefix, ext):
	# Build a bbq path under tmp_path that encodes the target core
	bbq_path = os.path.join(str(tmp_path), f"bbq-{core}-questions.txt")
	expected_path = topic_page.get_outfile_name(bbq_path, prefix, ext)
	expected_basename = os.path.basename(expected_path)
	pure_basename = orphan_prune.pure_download_basename(core, prefix, ext)
	assert pure_basename == expected_basename


#============================================
# find_orphan_downloads orphan vs unmanaged classification

def _make_downloads(tmp_path, names):
	"""Create a downloads/ subdir with empty files for each name."""
	downloads_dir = os.path.join(str(tmp_path), "downloads")
	os.makedirs(downloads_dir)
	for name in names:
		# Use pathlib touch for empty-file creation (no bare open needed)
		pathlib.Path(os.path.join(downloads_dir, name)).touch()
	return downloads_dir


def test_find_orphan_downloads_flags_prefixed_and_pgml_orphans(tmp_path):
	live_cores = {"alpha"}
	# A live artifact, two ghost orphans, and one unmanaged support file
	names = [
		"selftest-alpha.html",
		"blackboard_qti_v2_1-ghost.zip",
		"ghost.pgml",
		"random_support.txt",
	]
	_make_downloads(tmp_path, names)
	result = orphan_prune.find_orphan_downloads(str(tmp_path), live_cores)
	orphan_basenames = {os.path.basename(p) for p in result["orphans"]}
	assert orphan_basenames == {"blackboard_qti_v2_1-ghost.zip", "ghost.pgml"}


def test_find_orphan_downloads_keeps_live_and_ignores_unmanaged(tmp_path):
	live_cores = {"alpha"}
	names = [
		"selftest-alpha.html",
		"random_support.txt",
	]
	_make_downloads(tmp_path, names)
	result = orphan_prune.find_orphan_downloads(str(tmp_path), live_cores)
	# The live artifact is not an orphan; the unmanaged file is report-only
	assert result["orphans"] == []
	unmanaged_basenames = {os.path.basename(p) for p in result["unmanaged"]}
	assert "random_support.txt" in unmanaged_basenames


#============================================
# expected_source_basenames prefix branches

SOURCE_MAP_CASES = [
	("MATCH-foo", "foo-matching"),
	("WOMC-foo", "foo-which_one"),
	("MC-foo", "foo-which_one"),
	("TFMS-foo", "foo"),
	("foo", "foo"),
]


@pytest.mark.parametrize("core,stem", SOURCE_MAP_CASES)
def test_expected_source_basenames_branches(core, stem):
	expected = {f"{stem}.pgml", f"{stem}.pg"}
	assert orphan_prune.expected_source_basenames(core) == expected


#============================================
# find_orphan_sources topic-dir scoping

def test_find_orphan_sources_live_not_orphan(tmp_path):
	# A topic-level master whose mapped core is live is not an orphan
	pathlib.Path(os.path.join(str(tmp_path), "foo.pgml")).touch()
	live_cores = {"foo"}
	assert orphan_prune.find_orphan_sources(str(tmp_path), live_cores) == []


def test_find_orphan_sources_absent_core_is_orphan(tmp_path):
	pathlib.Path(os.path.join(str(tmp_path), "foo.pgml")).touch()
	live_cores = {"bar"}
	orphans = orphan_prune.find_orphan_sources(str(tmp_path), live_cores)
	orphan_basenames = {os.path.basename(p) for p in orphans}
	assert orphan_basenames == {"foo.pgml"}


#============================================
# quarantine_dest mapping and collision

def test_quarantine_dest_maps_site_docs_to_orphaned(tmp_path):
	# Build a synthetic site_docs subtree entirely under tmp_path
	repo_root = str(tmp_path)
	src_path = os.path.join(repo_root, "site_docs", "biochem", "topic07", "foo.pgml")
	dest_path = orphan_prune.quarantine_dest(src_path, repo_root=repo_root)
	# Quarantine is FLAT: only the basename lands under orphaned/, no nesting
	expected = os.path.join(repo_root, "orphaned", "foo.pgml")
	assert dest_path == expected


def test_quarantine_dest_raises_on_existing_dest(tmp_path):
	# Build a synthetic site_docs subtree entirely under tmp_path
	repo_root = str(tmp_path)
	src_basename = "collision_master.pgml"
	src_path = os.path.join(repo_root, "site_docs", "subj", "topic01", src_basename)
	# Pre-create the FLAT destination under tmp_path so the mapping hard-fails
	dest_path = os.path.join(repo_root, "orphaned", src_basename)
	os.makedirs(os.path.dirname(dest_path), exist_ok=True)
	pathlib.Path(dest_path).touch()
	with pytest.raises(FileExistsError):
		orphan_prune.quarantine_dest(src_path, repo_root=repo_root)


#============================================
# strip_orphan_includes exact-line removal

def _write_index(tmp_path, lines):
	index_path = os.path.join(str(tmp_path), "index.md")
	with open(index_path, "w") as index_file:
		index_file.write("".join(lines))
	return index_path


def test_strip_orphan_includes_removes_only_orphan_line(tmp_path):
	lines = [
		"# Topic title\n",
		"\n",
		'{% include "downloads/selftest-alpha.html" %}\n',
		'{% include "downloads/selftest-ghost.html" %}\n',
		"Some prose stays here.\n",
	]
	index_path = _write_index(tmp_path, lines)
	removed = orphan_prune.strip_orphan_includes(index_path, {"alpha"}, dry_run=False)
	assert removed == 1
	with open(index_path, "r") as index_file:
		remaining = index_file.read()
	# The orphan include is gone, the live include and prose remain
	assert "selftest-ghost.html" not in remaining
	assert "selftest-alpha.html" in remaining
	assert "Some prose stays here." in remaining


def test_strip_orphan_includes_dry_run_no_write(tmp_path):
	lines = ['{% include "downloads/selftest-ghost.html" %}\n']
	index_path = _write_index(tmp_path, lines)
	removed = orphan_prune.strip_orphan_includes(index_path, set(), dry_run=True)
	assert removed == 1
	with open(index_path, "r") as index_file:
		# Dry-run reports the count but leaves the file unchanged
		assert "selftest-ghost.html" in index_file.read()


#============================================
# prune_title_cache key dropping

def test_prune_title_cache_drops_stale_keeps_live_and_meta(tmp_path):
	cache = {
		"bbq-alpha-questions.txt": "Alpha title",
		"bbq-ghost-questions.txt": "Ghost title",
		"last edit": "some-timestamp",
	}
	yaml_path = os.path.join(str(tmp_path), "problem_set_titles.yml")
	with open(yaml_path, "w") as yaml_file:
		yaml.dump(cache, yaml_file)
	live = {"bbq-alpha-questions.txt"}
	dropped = orphan_prune.prune_title_cache(yaml_path, live, dry_run=False)
	assert dropped == 1
	with open(yaml_path, "r") as yaml_file:
		result = yaml.safe_load(yaml_file)
	assert "bbq-ghost-questions.txt" not in result
	assert "bbq-alpha-questions.txt" in result
	assert "last edit" in result


#============================================
# reconcile_topic dry-run performs no mutation

def test_reconcile_topic_dry_run_no_mutation(tmp_path):
	topic_folder = str(tmp_path)
	# Live bbq file plus a dead include, dead artifact, and stale cache key
	pathlib.Path(os.path.join(topic_folder, "bbq-alpha-questions.txt")).touch()
	_make_downloads(tmp_path, ["selftest-ghost.html"])
	index_lines = ['{% include "downloads/selftest-ghost.html" %}\n']
	index_path = _write_index(tmp_path, index_lines)
	yaml_path = os.path.join(topic_folder, "problem_set_titles.yml")
	with open(yaml_path, "w") as yaml_file:
		yaml.dump({"bbq-ghost-questions.txt": "x", "last edit": "now"}, yaml_file)

	# Capture file contents before the dry_run call
	with open(index_path, "r") as index_file:
		index_before = index_file.read()
	with open(yaml_path, "rb") as yaml_file:
		yaml_before = yaml_file.read()

	plan = orphan_prune.reconcile_topic(topic_folder, {"alpha"}, set(), dry_run=True)

	# The plan reports the orphan download and the stripped include
	delete_basenames = {os.path.basename(p) for p in plan["delete_downloads"]}
	assert "selftest-ghost.html" in delete_basenames
	# No mutation: the ghost artifact file still exists
	assert os.path.isfile(os.path.join(topic_folder, "downloads", "selftest-ghost.html"))
	# No mutation: index.md is byte-identical after dry_run
	with open(index_path, "r") as index_file:
		assert index_file.read() == index_before
	# No mutation: problem_set_titles.yml is byte-identical after dry_run
	with open(yaml_path, "rb") as yaml_file:
		assert yaml_file.read() == yaml_before

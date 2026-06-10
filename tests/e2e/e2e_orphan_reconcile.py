#!/usr/bin/env python3
"""E2E reconcile check for bioproblems_site.orphan_prune in a tmp git repo.

Builds a throwaway git repo with one topic that has a live bbq file, its 4
generated download artifacts, a downloads/ pgml copy, a TOPIC-LEVEL pgml
master, an index.md self-test include, and a problem_set_titles.yml cache
key. After committing so everything is tracked, the bbq source file is
deleted and reconcile is run. The check asserts the locked file-class
policy end to end:

  - the 4 downloads artifacts AND the downloads pgml copy are git-rm staged
    (gone from worktree, staged as deletions),
  - the TOPIC-LEVEL pgml master is git-mv staged to the FLAT orphaned/
    folder (present there, not deleted),
  - the orphan self-test include line is stripped from index.md,
  - the stale key is dropped from problem_set_titles.yml,
  - a second reconcile that would collide with an existing orphaned/<name>
    raises FileExistsError,
  - a dry-run leaves index.md / yml / artifact bytes+mtimes unchanged and
    stages nothing.

Everything happens inside a tempfile dir; the real repo is never touched.
The script exits 0 on success and non-zero with a clear stderr message on
failure.
"""

# Standard Library
import os
import sys
import shutil
import tempfile
import subprocess

# local repo modules
import bioproblems_site.git_paths as git_paths
import bioproblems_site.orphan_prune as orphan_prune


#============================================
CORE = "alpha_topic"
BBQ_NAME = f"bbq-{CORE}-questions.txt"
PGML_NAME = f"{CORE}.pgml"
SELFTEST_NAME = f"selftest-{CORE}.html"
ARTIFACT_NAMES = (
	SELFTEST_NAME,
	f"blackboard_qti_v2_1-{CORE}.zip",
	f"canvas_qti_v1_2-{CORE}.zip",
	f"human_readable-{CORE}.html",
)


#============================================
def run_git(repo_root: str, *args: str) -> str:
	"""Run a git command inside repo_root and return its stdout.

	Args:
		repo_root (str): The working directory for the git call.
		args (str): The git arguments after the git binary.

	Returns:
		str: The command stdout.
	"""
	result = subprocess.run(
		["git", *args],
		cwd=repo_root,
		capture_output=True,
		text=True,
		check=True,
	)
	return result.stdout


#============================================
def write_file(path: str, text: str) -> None:
	"""Write text to a path, creating parent directories as needed.

	Args:
		path (str): The destination file path.
		text (str): The file contents.
	"""
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w") as file_pointer:
		file_pointer.write(text)


#============================================
def build_repo(repo_root: str) -> dict:
	"""Build the tmp git repo fixture and return key paths.

	Args:
		repo_root (str): The tmp repo root directory.

	Returns:
		dict: Named paths used by the assertions.
	"""
	topic_dir = os.path.join(repo_root, "site_docs", "subj", "topic01")
	downloads_dir = os.path.join(topic_dir, "downloads")
	os.makedirs(downloads_dir, exist_ok=True)

	# The live bbq source file (its deletion triggers the orphan state)
	bbq_path = os.path.join(topic_dir, BBQ_NAME)
	write_file(bbq_path, "1. question alpha\n")

	# The 4 generated download artifacts for the core
	for artifact_name in ARTIFACT_NAMES:
		write_file(os.path.join(downloads_dir, artifact_name), "artifact\n")

	# A mapped pgml copy in downloads/ (reproducible -> delete on orphan)
	downloads_pgml = os.path.join(downloads_dir, PGML_NAME)
	write_file(downloads_pgml, "DOCUMENT();\n")

	# The TOPIC-LEVEL pgml master (quarantined, never deleted, on orphan)
	topic_pgml = os.path.join(topic_dir, PGML_NAME)
	write_file(topic_pgml, "DOCUMENT(); master\n")

	# index.md self-test include for the core
	index_path = os.path.join(topic_dir, "index.md")
	index_text = (
		"# Topic title\n"
		"\n"
		'{% include "downloads/' + SELFTEST_NAME + '" %}\n'
		"Some prose stays here.\n"
	)
	write_file(index_path, index_text)

	# problem_set_titles.yml cache with the bbq key plus the meta key
	yaml_path = os.path.join(topic_dir, "problem_set_titles.yml")
	yaml_text = (
		f"{BBQ_NAME}: Alpha title\n"
		"last edit: 2026-06-09\n"
	)
	write_file(yaml_path, yaml_text)

	# Initialize git and commit everything so all paths are tracked
	run_git(repo_root, "init", "--quiet")
	run_git(repo_root, "config", "user.email", "e2e@example.com")
	run_git(repo_root, "config", "user.name", "e2e")
	run_git(repo_root, "add", "-A")
	run_git(repo_root, "commit", "--quiet", "-m", "fixture")

	return {
		"topic_dir": topic_dir,
		"downloads_dir": downloads_dir,
		"bbq_path": bbq_path,
		"downloads_pgml": downloads_pgml,
		"topic_pgml": topic_pgml,
		"index_path": index_path,
		"yaml_path": yaml_path,
	}


#============================================
def staged_status(repo_root: str) -> dict:
	"""Return {relative_path: status_code} from git status porcelain.

	Args:
		repo_root (str): The tmp repo root directory.

	Returns:
		dict: Mapping of path to its two-char porcelain status.
	"""
	out = run_git(repo_root, "status", "--porcelain")
	status_by_path = {}
	for line in out.splitlines():
		if not line:
			continue
		code = line[:2]
		rest = line[3:]
		# A rename line is "R  old -> new"; record the new path
		if " -> " in rest:
			rest = rest.split(" -> ", 1)[1]
		status_by_path[rest] = code
	return status_by_path


#============================================
def reset_git_caches() -> None:
	"""Clear git_paths lru_caches so the tmp repo root is rediscovered."""
	git_paths.get_repo_root.cache_clear()
	git_paths.get_git_tracked_paths.cache_clear()


#============================================
def check_dry_run(repo_root: str, paths: dict) -> None:
	"""Run reconcile with dry_run=True and assert nothing changed.

	Args:
		repo_root (str): The tmp repo root directory.
		paths (dict): Named fixture paths.
	"""
	index_path = paths["index_path"]
	yaml_path = paths["yaml_path"]
	# Capture content and mtimes before the dry-run
	with open(index_path, "rb") as index_file:
		index_before = index_file.read()
	with open(yaml_path, "rb") as yaml_file:
		yaml_before = yaml_file.read()
	index_mtime_before = os.stat(index_path).st_mtime_ns
	yaml_mtime_before = os.stat(yaml_path).st_mtime_ns
	status_before = staged_status(repo_root)

	site_docs_dir = os.path.join(repo_root, "site_docs")
	reset_git_caches()
	orphan_prune.reconcile_all(site_docs_dir, dry_run=True, verbose=False)

	# Content and mtimes must be unchanged after a dry-run
	with open(index_path, "rb") as index_file:
		assert index_file.read() == index_before, "dry-run mutated index.md"
	with open(yaml_path, "rb") as yaml_file:
		assert yaml_file.read() == yaml_before, "dry-run mutated yml"
	assert os.stat(index_path).st_mtime_ns == index_mtime_before, "dry-run touched index.md"
	assert os.stat(yaml_path).st_mtime_ns == yaml_mtime_before, "dry-run touched yml"
	# All artifacts still present after a dry-run
	for artifact_name in ARTIFACT_NAMES:
		artifact_path = os.path.join(paths["downloads_dir"], artifact_name)
		assert os.path.isfile(artifact_path), f"dry-run removed {artifact_name}"
	assert os.path.isfile(paths["topic_pgml"]), "dry-run moved topic pgml master"
	# Dry-run stages nothing: git status is identical
	assert staged_status(repo_root) == status_before, "dry-run staged changes"


#============================================
def check_live_run(repo_root: str, paths: dict) -> None:
	"""Run reconcile for real and assert the locked policy outcome.

	Args:
		repo_root (str): The tmp repo root directory.
		paths (dict): Named fixture paths.
	"""
	site_docs_dir = os.path.join(repo_root, "site_docs")
	reset_git_caches()
	orphan_prune.reconcile_all(site_docs_dir, dry_run=False, verbose=False)

	status = staged_status(repo_root)

	# The 4 download artifacts and the downloads pgml copy are git-rm staged
	deleted_basenames = list(ARTIFACT_NAMES) + [PGML_NAME]
	for basename in deleted_basenames:
		worktree_path = os.path.join(paths["downloads_dir"], basename)
		assert not os.path.exists(worktree_path), f"{basename} still in worktree"
		rel = os.path.relpath(worktree_path, repo_root)
		assert rel in status, f"{rel} not staged"
		assert status[rel].startswith("D"), f"{rel} not staged as deletion ({status[rel]})"

	# The topic-level pgml master is git-mv staged to FLAT orphaned/<basename>
	flat_dest = os.path.join(repo_root, "orphaned", PGML_NAME)
	assert os.path.isfile(flat_dest), "quarantined master missing from orphaned/"
	assert not os.path.exists(paths["topic_pgml"]), "topic pgml master still in topic dir"
	# Confirm flatness: no subject/topic nesting under orphaned/
	nested_dest = os.path.join(repo_root, "orphaned", "subj", "topic01", PGML_NAME)
	assert not os.path.exists(nested_dest), "quarantine is nested, expected flat"
	dest_rel = os.path.relpath(flat_dest, repo_root)
	assert dest_rel in status, "quarantined master not staged"

	# The orphan self-test include line is stripped from index.md
	with open(paths["index_path"], "r") as index_file:
		index_after = index_file.read()
	assert SELFTEST_NAME not in index_after, "orphan selftest include not stripped"
	assert "Some prose stays here." in index_after, "prose was lost"

	# The stale bbq key is dropped from problem_set_titles.yml
	with open(paths["yaml_path"], "r") as yaml_file:
		yaml_after = yaml_file.read()
	assert BBQ_NAME not in yaml_after, "stale title key not dropped"
	assert "last edit" in yaml_after, "meta key was lost"


#============================================
def check_collision(repo_root: str) -> None:
	"""Assert a reconcile colliding with an existing orphaned/<name> raises.

	A fresh topic-level master with the SAME basename as the already
	quarantined file must hard-fail because orphaned/<basename> exists.

	Args:
		repo_root (str): The tmp repo root directory.
	"""
	topic_dir = os.path.join(repo_root, "site_docs", "subj", "topic01")
	# Re-create a topic-level master with the same basename, no live core
	colliding_master = os.path.join(topic_dir, PGML_NAME)
	write_file(colliding_master, "DOCUMENT(); second master\n")

	site_docs_dir = os.path.join(repo_root, "site_docs")
	reset_git_caches()
	raised = False
	try:
		orphan_prune.reconcile_all(site_docs_dir, dry_run=False, verbose=False)
	except FileExistsError:
		raised = True
	assert raised, "expected FileExistsError on quarantine collision"


#============================================
def main() -> None:
	"""Build the fixture, exercise reconcile, and assert the policy."""
	# Resolve any symlink in the temp root (macOS /tmp -> /private/tmp) so
	# the glob-derived abspaths match git rev-parse's realpath repo root.
	work_root = os.path.realpath(tempfile.mkdtemp(prefix="e2e_orphan_reconcile_"))
	original_cwd = os.getcwd()
	try:
		repo_root = os.path.join(work_root, "repo")
		os.makedirs(repo_root)
		# git_rm/git_mv and get_repo_root resolve against the process cwd
		os.chdir(repo_root)
		paths = build_repo(repo_root)

		# Delete the bbq source to create the orphan state
		os.remove(paths["bbq_path"])

		# A dry-run must not mutate anything or stage changes
		check_dry_run(repo_root, paths)
		# The real run enacts the locked file-class policy
		check_live_run(repo_root, paths)
		# A second run colliding on the flat dest must hard-fail
		check_collision(repo_root)

		print("e2e_orphan_reconcile: PASS")
	finally:
		os.chdir(original_cwd)
		shutil.rmtree(work_root, ignore_errors=True)


#============================================
if __name__ == "__main__":
	try:
		main()
	except AssertionError as failure:
		sys.stderr.write(f"e2e_orphan_reconcile: FAIL: {failure}\n")
		sys.exit(1)

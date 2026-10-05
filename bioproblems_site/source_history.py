"""Read authored-source lineage and task admission dates without running generators."""

import csv
import io
import hashlib
import subprocess
from pathlib import Path

import bioproblems_site.bbq_config as bbq_config


#============================================
def git(repo: Path, *arguments: str) -> str:
	"""Run a read-only Git query with separate arguments (ASVS 1.2.5)."""
	result = subprocess.run(
		["git", "-C", str(repo), *arguments], check=True, capture_output=True, text=True,
	)
	return result.stdout


#============================================
def fingerprint(path: Path) -> str:
	"""Identify exact source or bank bytes independently of file timestamps."""
	digest = hashlib.sha256(path.read_bytes()).hexdigest()
	return digest


#============================================
def parse_lineage(log: str) -> dict:
	"""Follow Git's detected lineage; unchanged renames do not advance revision dates."""
	aliases = set()
	revisions = []
	origin = None
	for block in log.split("\x1e"):
		lines = [line for line in block.strip().splitlines() if line]
		if not lines:
			continue
		commit, date = lines[0].split("\t")
		changed = False
		for line in lines[1:]:
			status, *paths = line.split("\t")
			aliases.update(paths)
			if status != "R100":
				changed = True
			if status == "A":
				origin = {"commit": commit, "path": paths[0], "date": date[:10]}
		if changed:
			revisions.append({"commit": commit, "date": date[:10]})
	result = {"aliases": sorted(aliases), "revisions": revisions, "origin": origin}
	return result


#============================================
def source_history(path: Path) -> dict | None:
	"""Return committed lineage plus whether the working source matches HEAD."""
	if not path.is_file() or not any((parent / ".git").exists() for parent in path.parents):
		return None
	root = Path(git(path.parent, "rev-parse", "--show-toplevel").strip())
	relative = path.resolve().relative_to(root).as_posix()
	log = git(root, "log", "--follow", "--format=%x1e%H%x09%cI", "--name-status", "-M", "--", relative)
	history = parse_lineage(log)
	if history["origin"] is None or not history["revisions"]:
		return None
	origin = history["origin"]
	# Include the origin path: a single commit can introduce many independent banks.
	history["id"] = origin["commit"] + ":" + origin["path"]
	history["path"] = relative
	history["root"] = root
	history["fingerprint"] = fingerprint(path)
	history["clean"] = not git(root, "status", "--porcelain", "--", relative).strip()
	return history


#============================================
def authored_source(task: dict) -> Path:
	"""YAML input owns bank content; otherwise the configured generator does."""
	# Input is optional for standalone commands; script is always required.
	source = task.get("input_path", "") or task["script"]
	path = Path(source).resolve()
	return path


#============================================
def task_admissions(repo: Path, settings: dict, histories: dict[Path, dict]) -> dict:
	"""Recover first source-family admission, excluding the initial task inventory."""
	aliases = bbq_config.apply_env_overrides(bbq_config.resolve_alias_map(settings["paths"]))
	aliases["repo_root"] = str(repo)
	path_ids = {}
	for history in histories.values():
		for alias in history["aliases"]:
			path = (history["root"] / alias).resolve()
			path_ids.setdefault(path, set()).add(history["id"])
	log = git(repo, "log", "--reverse", "--format=%H%x09%cI", "--", "task_files")
	admissions = {}
	for index, line in enumerate(log.splitlines()):
		commit, date = line.split("\t")
		paths = git(repo, "ls-tree", "-r", "--name-only", commit, "--", "task_files").splitlines()
		for path in paths:
			if not path.endswith(".csv"):
				continue
			content = git(repo, "show", f"{commit}:{path}")
			reader = csv.DictReader(io.StringIO("\n".join(
				line for line in content.splitlines() if line.strip() and not line.startswith("#")
			)))
			for row in reader:
				if not row.get("subject") or not row.get("script"):
					continue
				source = (row.get("input") or row["script"]).strip()
				expanded = bbq_config.expand_text(source, aliases)
				if "{" in expanded or not expanded.startswith("/"):
					continue
				identities = path_ids.get(Path(expanded).resolve(), set())
				if len(identities) != 1:
					continue
				identity = next(iter(identities))
				if identity not in admissions:
					admissions[identity] = {"date": date[:10], "baseline": index == 0}
	return admissions

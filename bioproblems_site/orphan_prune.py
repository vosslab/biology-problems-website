"""Reconcile bbq-derived state against the live bbq-core set per topic.

GitHub Pages deploys break when a `bbq-*-questions.txt` source file is
deleted but its generated artifacts, include lines, and cache keys are
left behind. This module detects those orphans -- files, include lines,
and cache keys whose encoded core is no longer in the topic's live
bbq-core set -- and reconciles them per the locked file-class policy:

- generated `downloads/*` artifacts and reproducible `downloads/*.pgml`
  / `*.pg` copies are deleted (git rm if tracked, else os.remove),
- orphan `selftest-<core>` include lines in `index.md` are stripped,
- orphan keys in `problem_set_titles.yml` are dropped (keep `last edit`),
- orphan TOPIC-LEVEL `.pgml` / `.pg` masters are quarantined by git mv to
  a FLAT `orphaned/<basename>` at the repo root (never deleted).

Detection is forward-only and decidable: the expected name set is built
FROM the live cores, and real files are matched against it. A file whose
name does not decidably encode a bbq core is classified UNMANAGED and is
reported only -- it is never deleted or moved.
"""

# Standard Library
import os
import re
import glob

# PIP3 modules
import yaml

# local repo modules
import bioproblems_site.git_paths as git_paths
import bioproblems_site.topic_page as topic_page


#============================================
# Pure naming and detection constants

# The four prefixed download artifacts generated from each bbq file.
# Each entry mirrors topic_page.get_outfile_name(bbq, prefix, ext) output
# but without that function's remove_case_mismatched_files side effect.
# Equivalence is proven by snapshot test, not by calling get_outfile_name.
DOWNLOAD_ARTIFACTS = (
	("selftest", "html"),
	("blackboard_qti_v2_1", "zip"),
	("canvas_qti_v1_2", "zip"),
	("human_readable", "html"),
)

# Include line basename anchor: mirrors selftest_manifest.INCLUDE_RE so the
# strip path removes only a self-test include, never an unrelated include.
INCLUDE_RE = re.compile(r'{%\s*include\s+"([^"]*selftest[^"]*\.html)"\s*%}')

# Title-cache meta key that is never a bbq basename and must be preserved.
TITLE_CACHE_META_KEY = "last edit"

# Quarantine root folder name at the repo root (outside docs_dir).
# The quarantine layout is FLAT: a moved master lands at orphaned/<basename>
# with no subject/topic nesting.
QUARANTINE_ROOT = "orphaned"


#============================================
# Download artifact detection and pure naming

#============================================
def pure_download_basename(core: str, prefix: str, ext: str) -> str:
	"""Return the download artifact basename for a core, prefix, and ext.

	Pure reimplementation of the naming in topic_page.get_outfile_name,
	without the remove_case_mismatched_files filesystem side effect.
	Mirrors the startswith(prefix) guard so a core that already begins
	with a known prefix (for example a MATCH-* core) is not double
	prefixed.

	Args:
		core (str): The bbq core name (from extract_core_name).
		prefix (str): The generated-artifact prefix.
		ext (str): The file extension without a leading dot.

	Returns:
		str: The basename, for example selftest-foo.html.
	"""
	# Prefix the core unless it already starts with the prefix
	basename = core
	if not basename.startswith(prefix):
		basename = f"{prefix}-{basename}"
	# Append the extension unless it is already present
	if not basename.endswith("." + ext):
		basename += "." + ext
	return basename


#============================================
def expected_download_basenames(core: str) -> set:
	"""Return the set of 4 prefixed download artifact basenames for a core.

	Args:
		core (str): The bbq core name.

	Returns:
		set: The 4 expected generated-artifact basenames.
	"""
	expected = set()
	# Build one basename per generated download format
	for prefix, ext in DOWNLOAD_ARTIFACTS:
		expected.add(pure_download_basename(core, prefix, ext))
	return expected


#============================================
def _live_download_basenames(live_cores: set) -> set:
	"""Return every legit download basename across all live cores.

	Combines the 4 prefixed artifacts with the pgml/pg copies so a file
	matching any live core is recognized as not-orphan.

	Args:
		live_cores (set): Cores backed by a live bbq file.

	Returns:
		set: All expected download basenames for the live cores.
	"""
	live_basenames = set()
	# Accumulate prefixed artifacts and pgml/pg copies for each live core
	for core in live_cores:
		live_basenames |= expected_download_basenames(core)
		live_basenames |= expected_source_basenames(core)
	return live_basenames


#============================================
def _decodes_to_core(basename: str) -> bool:
	"""Return True if a download basename decidably encodes a bbq core.

	A basename is managed (decidable) when it carries one of the 4 known
	generated prefixes, or when it is a pgml/pg copy. Any other file is
	UNMANAGED and is never a deletion candidate.

	Args:
		basename (str): The download file basename.

	Returns:
		bool: True if the basename maps to a bbq core class.
	"""
	# A known generated prefix makes the basename decidable
	for prefix, ext in DOWNLOAD_ARTIFACTS:
		if basename.startswith(prefix + "-") and basename.endswith("." + ext):
			return True
	# A pgml/pg copy is decidable (its core is resolved via the live map)
	if basename.endswith(".pgml") or basename.endswith(".pg"):
		return True
	return False


#============================================
def find_orphan_downloads(topic_folder: str, live_cores: set) -> dict:
	"""Find orphan and unmanaged files under a topic's downloads/ folder.

	A download file is an orphan only if its name decidably encodes a bbq
	core (a known generated prefix, or a pgml/pg copy) AND that name is not
	in the live expected set. A file that does not decidably encode a core
	is classified UNMANAGED: it is reported for human awareness but drives
	NO deletion.

	Args:
		topic_folder (str): Path to the topic directory.
		live_cores (set): Cores backed by a live bbq file.

	Returns:
		dict: {"orphans": [paths to delete], "unmanaged": [paths to report]}.
	"""
	downloads_dir = os.path.join(topic_folder, "downloads")
	orphan_paths = []
	unmanaged_paths = []
	if not os.path.isdir(downloads_dir):
		empty_result = {"orphans": orphan_paths, "unmanaged": unmanaged_paths}
		return empty_result
	# Precompute every legit download basename across the live cores
	live_basenames = _live_download_basenames(live_cores)
	# Classify each file in downloads/ as orphan, live, or unmanaged
	for entry in sorted(os.listdir(downloads_dir)):
		entry_path = os.path.join(downloads_dir, entry)
		if not os.path.isfile(entry_path):
			continue
		# A name that does not encode a core is unmanaged, never deleted
		if not _decodes_to_core(entry):
			unmanaged_paths.append(entry_path)
			continue
		# A decidable name not in the live set is an orphan to delete
		if entry not in live_basenames:
			orphan_paths.append(entry_path)
	result = {"orphans": orphan_paths, "unmanaged": unmanaged_paths}
	return result


#============================================
# Source pgml/pg mapping and topic-master quarantine

#============================================
def expected_source_basenames(core: str) -> set:
	"""Return the expected pgml/pg basenames for a core.

	Forward mirror of topic_page.find_pgml_file's prefix mapping
	(topic_page.py:269-285). Shared by download detection for the
	downloads-copy delete path and by topic-master quarantine.

	Mapping:
		MATCH-x        -> x-matching.{pgml,pg}
		WOMC-x / MC-x  -> x-which_one.{pgml,pg}
		TFMS-x         -> x.{pgml,pg}
		default        -> <core>.{pgml,pg}

	Args:
		core (str): The bbq core name.

	Returns:
		set: The expected pgml and pg basenames.
	"""
	# Resolve the yaml base stem per the find_pgml_file prefix branches
	if core.startswith("MATCH-"):
		stem = core[len("MATCH-"):] + "-matching"
	elif core.startswith("WOMC-"):
		stem = core[len("WOMC-"):] + "-which_one"
	elif core.startswith("MC-"):
		stem = core[len("MC-"):] + "-which_one"
	elif core.startswith("TFMS-"):
		stem = core[len("TFMS-"):]
	else:
		stem = core
	# Both extensions are valid source/copy names for the stem
	return {f"{stem}.pgml", f"{stem}.pg"}


#============================================
def _live_source_basenames(live_cores: set) -> set:
	"""Return every legit pgml/pg basename across all live cores.

	Args:
		live_cores (set): Cores backed by a live bbq file.

	Returns:
		set: All expected pgml/pg basenames for the live cores.
	"""
	live_basenames = set()
	for core in live_cores:
		live_basenames |= expected_source_basenames(core)
	return live_basenames


#============================================
def find_orphan_sources(topic_folder: str, live_cores: set) -> list:
	"""Find orphan topic-level pgml/pg masters to quarantine.

	Scans the TOPIC DIRECTORY ONLY -- downloads/ pgml/pg orphans are
	deleted by find_orphan_downloads, not quarantined. A topic-level
	pgml/pg file whose mapped core is not live is an orphan master.

	Args:
		topic_folder (str): Path to the topic directory.
		live_cores (set): Cores backed by a live bbq file.

	Returns:
		list: Paths to topic-level pgml/pg masters to quarantine.
	"""
	orphan_paths = []
	live_basenames = _live_source_basenames(live_cores)
	# Inspect only direct topic-dir entries, skipping the downloads/ subdir
	for entry in sorted(os.listdir(topic_folder)):
		entry_path = os.path.join(topic_folder, entry)
		if not os.path.isfile(entry_path):
			continue
		# Only pgml/pg masters are quarantine candidates
		if not (entry.endswith(".pgml") or entry.endswith(".pg")):
			continue
		# A master not matching any live core is an orphan to quarantine
		if entry not in live_basenames:
			orphan_paths.append(entry_path)
	return orphan_paths


#============================================
def quarantine_dest(src_path: str, repo_root: str = None) -> str:
	"""Map a topic-level source path to its FLAT quarantine destination.

	A master at site_docs/<subject>/<topic>/<basename> maps to exactly
	orphaned/<basename> at the repo root. The quarantine folder is FLAT:
	there is NO subject/topic nesting under orphaned/.

	Hard-fails if the destination already exists (collision), so an
	orphaned master never silently overwrites a prior quarantine.

	Args:
		src_path (str): Path to the topic-level source file.
		repo_root (str): Optional repo root override; defaults to
			git_paths.get_repo_root() for production callers.

	Returns:
		str: The flat quarantine destination path orphaned/<basename>.

	Raises:
		FileExistsError: When the destination already exists.
	"""
	# Default to the real repo root for production callers
	if repo_root is None:
		repo_root = git_paths.get_repo_root()
	# Flat quarantine: only the basename lands under the orphaned/ folder
	basename = os.path.basename(src_path)
	dest_path = os.path.join(repo_root, QUARANTINE_ROOT, basename)
	# A pre-existing destination is a hard-fail collision
	if os.path.exists(dest_path):
		raise FileExistsError(dest_path)
	return dest_path


#============================================
# In-file pruners: index includes and title cache

#============================================
def strip_orphan_includes(index_md_path: str, live_cores: set, dry_run: bool) -> int:
	"""Strip orphan selftest include lines from a topic index.md.

	Removes ONLY a line whose included basename is selftest-<core>.html
	for a core not in live_cores. Other includes, headings, blank lines,
	and prose are left untouched. Mirrors selftest_manifest INCLUDE_RE.

	Args:
		index_md_path (str): Path to the topic index.md.
		live_cores (set): Cores backed by a live bbq file.
		dry_run (bool): When True, count but do not write changes.

	Returns:
		int: Number of orphan include lines removed.
	"""
	with open(index_md_path, "r") as index_md_file:
		lines = index_md_file.readlines()
	kept_lines = []
	removed_count = 0
	# Keep every line except an include that points at an orphan selftest
	for line in lines:
		match = INCLUDE_RE.search(line)
		if match is not None:
			included_basename = os.path.basename(match.group(1))
			# The included core is the selftest-<core>.html stem
			core = _selftest_include_core(included_basename)
			if core is not None and core not in live_cores:
				removed_count += 1
				continue
		kept_lines.append(line)
	# Only rewrite the file outside of dry-run when something changed
	if not dry_run and removed_count > 0:
		with open(index_md_path, "w") as index_md_file:
			index_md_file.writelines(kept_lines)
	return removed_count


#============================================
def _selftest_include_core(included_basename: str) -> str | None:
	"""Return the core encoded in a selftest-<core>.html basename.

	Args:
		included_basename (str): The included file basename.

	Returns:
		str: The core name, or None if the basename is not a selftest.
	"""
	prefix = "selftest-"
	suffix = ".html"
	# A selftest include decidably encodes its core between prefix/suffix
	if included_basename.startswith(prefix) and included_basename.endswith(suffix):
		return included_basename[len(prefix):-len(suffix)]
	return None


#============================================
def prune_title_cache(yaml_path: str, live_bbq_basenames: set, dry_run: bool) -> int:
	"""Drop non-live keys from a problem_set_titles.yml cache.

	Every top-level key is either a bbq-*-questions.txt basename or the
	meta key last edit. Non-live bbq-basename keys are dropped; the
	last edit meta key and live keys are preserved.

	Args:
		yaml_path (str): Path to problem_set_titles.yml.
		live_bbq_basenames (set): Basenames of live bbq files.
		dry_run (bool): When True, count but do not write changes.

	Returns:
		int: Number of stale cache keys dropped.
	"""
	with open(yaml_path, "r") as yaml_file:
		cache_data = yaml.safe_load(yaml_file)
	# An empty or absent cache has nothing to prune
	if not cache_data:
		return 0
	stale_keys = []
	# A key is stale when it is neither the meta key nor a live bbq basename
	for key in cache_data:
		if key == TITLE_CACHE_META_KEY:
			continue
		if key not in live_bbq_basenames:
			stale_keys.append(key)
	# Remove the stale keys from the in-memory cache
	for key in stale_keys:
		del cache_data[key]
	# Only rewrite the file outside of dry-run when something changed
	if not dry_run and stale_keys:
		with open(yaml_path, "w") as yaml_file:
			yaml.dump(cache_data, yaml_file)
	return len(stale_keys)


#============================================
# Topic reconcile driver

#============================================
def compute_live_state(topic_folder: str) -> tuple:
	"""Compute the live cores and bbq basenames for a topic.

	Args:
		topic_folder (str): Path to the topic directory.

	Returns:
		tuple: (live_cores set, live_bbq_basenames set).
	"""
	live_cores = set()
	live_bbq_basenames = set()
	bbq_glob = os.path.join(topic_folder, "bbq-*-questions.txt")
	# Each live bbq file contributes one core and one basename
	for bbq_path in glob.glob(bbq_glob):
		live_cores.add(topic_page.extract_core_name(bbq_path))
		live_bbq_basenames.add(os.path.basename(bbq_path))
	return live_cores, live_bbq_basenames


#============================================
def reconcile_topic(
		topic_folder: str,
		live_cores: set,
		tracked_set: set,
		dry_run: bool,
	) -> dict:
	"""Reconcile every bbq-derived target for one topic against live cores.

	Composes the four reconcile targets:
	  1. delete orphan downloads/ artifacts and pgml/pg copies,
	  2. strip orphan selftest includes from index.md,
	  3. drop stale problem_set_titles.yml keys,
	  4. quarantine orphan topic-level pgml/pg masters.

	With dry_run=True this performs read-only scans only and returns the
	risk-grouped planned action list without any write, remove, move, or
	git-staging operation. The tracked_set is injected, so this function
	makes no git call to decide tracked-vs-untracked.

	Args:
		topic_folder (str): Path to the topic directory.
		live_cores (set): Cores backed by a live bbq file.
		tracked_set (set): Absolute paths git currently tracks.
		dry_run (bool): When True, plan only; perform no mutation.

	Returns:
		dict: Risk-grouped action plan with keys delete_downloads,
			strip_includes, drop_cache_keys, quarantine_sources, and
			unmanaged.
	"""
	# Recompute live bbq basenames locally for the title-cache prune
	_, live_bbq_basenames = compute_live_state(topic_folder)

	plan = {
		"delete_downloads": [],
		"strip_includes": [],
		"drop_cache_keys": [],
		"quarantine_sources": [],
		"unmanaged": [],
	}

	# Target 1: orphan downloads/ artifacts and pgml/pg copies -> delete
	download_result = find_orphan_downloads(topic_folder, live_cores)
	plan["unmanaged"] = list(download_result["unmanaged"])
	for orphan_path in download_result["orphans"]:
		plan["delete_downloads"].append(orphan_path)
		if not dry_run:
			_delete_path(orphan_path, tracked_set)

	# Target 2: orphan selftest include lines in index.md -> strip
	index_md_path = os.path.join(topic_folder, "index.md")
	if os.path.isfile(index_md_path):
		removed = strip_orphan_includes(index_md_path, live_cores, dry_run)
		if removed > 0:
			plan["strip_includes"].append({"path": index_md_path, "removed": removed})

	# Target 3: stale problem_set_titles.yml keys -> drop
	yaml_path = os.path.join(topic_folder, "problem_set_titles.yml")
	if os.path.isfile(yaml_path):
		dropped = prune_title_cache(yaml_path, live_bbq_basenames, dry_run)
		if dropped > 0:
			plan["drop_cache_keys"].append({"path": yaml_path, "dropped": dropped})

	# Target 4: orphan topic-level pgml/pg masters -> quarantine (never delete)
	for src_path in find_orphan_sources(topic_folder, live_cores):
		dest_path = quarantine_dest(src_path)
		plan["quarantine_sources"].append({"src": src_path, "dest": dest_path})
		if not dry_run:
			_quarantine_path(src_path, dest_path, tracked_set)

	return plan


#============================================
def reconcile_all(site_docs_dir: str, dry_run: bool, verbose: bool) -> dict:
	"""Reconcile every topic under a site_docs dir against its live cores.

	Builds the git tracked-set once, globs the same topic-folder shape as
	topic_page.render_all (*/topic??/), computes live cores per topic, and
	runs reconcile_topic for each. The per-topic plans are aggregated into a
	single combined plan. With dry_run=True no mutation occurs.

	Args:
		site_docs_dir (str): The mkdocs docs_dir to scan for topic folders.
		dry_run (bool): When True, plan only; perform no mutation.
		verbose (bool): When True, print a per-topic action summary.

	Returns:
		dict: Combined risk-grouped action plan across all topics, with keys
			delete_downloads, strip_includes, drop_cache_keys,
			quarantine_sources, and unmanaged.
	"""
	# Build the tracked-set once and inject it into every reconcile_topic call
	tracked_set = git_paths.tracked_paths_set()
	# Match topic_page.render_all's topic-folder glob shape exactly
	all_topic_folders = sorted(glob.glob(os.path.join(site_docs_dir, "*/topic??/")))
	if verbose:
		print(f"orphan_prune: reconciling {len(all_topic_folders)} topic folders")
	combined = {
		"delete_downloads": [],
		"strip_includes": [],
		"drop_cache_keys": [],
		"quarantine_sources": [],
		"unmanaged": [],
	}
	# Reconcile each topic and fold its plan into the combined plan
	for topic_folder in all_topic_folders:
		# Live cores are derived from the topic's surviving bbq files
		live_cores, _ = compute_live_state(topic_folder)
		plan = reconcile_topic(topic_folder, live_cores, tracked_set, dry_run)
		for key in combined:
			combined[key].extend(plan[key])
		if verbose:
			summary = (
				f"  {topic_folder}: "
				f"delete={len(plan['delete_downloads'])} "
				f"strip={len(plan['strip_includes'])} "
				f"drop={len(plan['drop_cache_keys'])} "
				f"quarantine={len(plan['quarantine_sources'])} "
				f"unmanaged={len(plan['unmanaged'])}"
			)
			print(summary)
	return combined


#============================================
def _delete_path(path: str, tracked_set: set) -> None:
	"""Delete a generated download orphan, git rm if tracked.

	Args:
		path (str): The file to delete.
		tracked_set (set): Absolute paths git currently tracks.
	"""
	# A tracked file is removed via git so the deletion is staged
	if os.path.realpath(path) in tracked_set:
		git_paths.git_rm(path)
	else:
		os.remove(path)


#============================================
def _quarantine_path(src_path: str, dest_path: str, tracked_set: set) -> None:
	"""Move a topic-level master into quarantine, git mv if tracked.

	Creates the flat orphaned/ parent directory first.

	Args:
		src_path (str): The source master to quarantine.
		dest_path (str): The quarantine destination path.
		tracked_set (set): Absolute paths git currently tracks.
	"""
	# Ensure the quarantine parent directory exists before the move
	dest_parent = os.path.dirname(dest_path)
	if not os.path.isdir(dest_parent):
		os.makedirs(dest_parent)
	# A tracked master is moved via git so history is preserved and staged
	if os.path.realpath(src_path) in tracked_set:
		git_paths.git_mv(src_path, dest_path)
	else:
		os.rename(src_path, dest_path)

"""Build a task-owned snapshot of the public collection and its activity."""

import json
from pathlib import Path
import urllib.parse

import bioproblems_site.bbq_config as bbq_config
import bioproblems_site.bbq_outputs as bbq_outputs
import bioproblems_site.bbq_workflow as bbq_workflow
import bioproblems_site.file_write as file_write
import bioproblems_site.homepage_render as homepage_render
import bioproblems_site.metadata as metadata
import bioproblems_site.mkdocs_nav as mkdocs_nav
import bioproblems_site.problem_set_display as problem_set_display
import bioproblems_site.question_index as question_index
import bioproblems_site.source_history as source_history
import bioproblems_site.topic_page as topic_page


#============================================
def inventory(repo: Path, subjects: dict) -> tuple[dict, dict, dict]:
	"""Resolve current CSV ownership and reuse each authored source's Git query."""
	settings = bbq_config.load_bbq_config(str(repo / "bbq_settings.yml"))
	aliases = metadata.build_topic_alias_map(subjects)
	owners = {}
	match_lengths = {}
	histories = {}
	seen_sources = set()
	for task_file in sorted((repo / "task_files").glob("*.csv")):
		for task in bbq_config.load_tasks_csv(str(task_file), settings, aliases):
			source = source_history.authored_source(task)
			if source not in seen_sources:
				seen_sources.add(source)
				history = source_history.source_history(source)
				if history is not None:
					histories[source] = history
			prefixes, _suffixes = bbq_outputs.build_output_patterns(task)
			for output in bbq_workflow.expected_output_paths(task):
				path = output.resolve()
				length = max((len(prefix) for prefix in prefixes
					if output.name.startswith(prefix)), default=0)
				if path not in owners or length > match_lengths[path]:
					owners[path] = {source}
					match_lengths[path] = length
				elif length == match_lengths[path]:
					owners[path].add(source)
	return owners, histories, settings


#============================================
def summarize(entries: list, site_docs: Path, owners: dict, histories: dict,
		admissions: dict, provenance: dict) -> dict:
	"""Count each owned placement once, independently of its export formats."""
	subjects = {}
	rows = []
	unowned = []
	ambiguous = []
	seen = set()
	for entry in entries:
		path = entry.source_path.resolve()
		if path in seen:
			continue
		seen.add(path)
		key = path.relative_to(site_docs.resolve()).as_posix()
		if path not in owners:
			unowned.append(key)
			continue
		subject_key, topic_key = key.split("/")[:2]
		subject = subjects.setdefault(subject_key, {
			"key": subject_key, "title": entry.subject_title, "icon": "",
			"sets": 0, "topics": set(), "url": f"{subject_key}/",
		})
		subject["sets"] += 1
		subject["topics"].add(topic_key)
		name, _types = problem_set_display.split_title(entry.title)
		anchor = topic_page.extract_core_name(str(path)) + "-button-container"
		row = {
			"id": key, "name": name, "subject": entry.subject_title,
			"topic": entry.topic_title,
			"url": entry.page_path.removesuffix("index.md") + "#" + urllib.parse.quote(anchor),
			"family": None, "created": None,
			"added": None, "updated": None,
		}
		candidates = owners[path]
		published = provenance.get(key)
		if (len(candidates) > 1 and published is not None
				and published["output_fingerprint"] == source_history.fingerprint(path)):
			candidates = {source for source in candidates if source in histories
				and histories[source]["id"] == published["source_id"]}
		if len(candidates) == 1:
			source = next(iter(candidates))
			history = histories.get(source)
			if history is not None:
				row["family"] = history["id"]
				row["created"] = history["origin"]["date"]
				admission = admissions.get(history["id"])
				if admission is not None and not admission["baseline"]:
					row["added"] = admission["date"]
				if (published is not None and published["source_id"] == history["id"]
						and published["output_fingerprint"] == source_history.fingerprint(path)):
					row["updated"] = published["source_updated"]
		else:
			ambiguous.append(key)
		rows.append(row)
	for subject in subjects.values():
		subject["topics"] = len(subject["topics"])
	result = {
		"subjects": list(subjects.values()), "sets": rows,
		"totals": {"sets": len(rows),
			"subjects": len(subjects), "topics": sum(s["topics"] for s in subjects.values())},
		"new": recent(rows, "added"), "updated": recent(rows, "updated"),
		"diagnostics": {"unowned": unowned, "ambiguous": ambiguous},
	}
	return result


#============================================
def recent(rows: list[dict], field: str) -> list[dict]:
	"""Return all dated source families, newest first, without inventing history."""
	selected = []
	seen = set()
	eligible = [row for row in rows if row[field] and row["family"]]
	eligible.sort(key=lambda row: (row[field], row["name"]), reverse=True)
	for row in eligible:
		if row["family"] in seen:
			continue
		if field == "updated" and row["updated"] <= row["created"]:
			continue
		seen.add(row["family"])
		selected.append({"name": row["name"], "date": row[field], "url": row["url"],
			"subject": row["subject"], "topic": row["topic"]})
	return selected


#============================================
def write(repo: Path, site_docs: Path, metadata_path: Path, mkdocs_path: Path,
		dry_run: bool = False) -> set[Path]:
	"""Refresh global homepage data even after a subject-scoped generation run."""
	data_path = site_docs / "assets/data/homepage.json"
	fragment_path = site_docs / "assets/generated/homepage.html"
	activity_paths = {key: site_docs / f"{details['route']}.md"
		for key, details in homepage_render.ACTIVITY.items()}
	outputs = {data_path, fragment_path, *activity_paths.values()}
	if dry_run:
		return outputs
	subjects, order = metadata.load_topics_metadata(str(metadata_path), str(mkdocs_path))
	entries = question_index.collect_entries(site_docs, subjects, order)
	owners, histories, settings = inventory(repo, subjects)
	admissions = source_history.task_admissions(repo, settings, histories)
	provenance_path = site_docs / "assets/data/question_provenance.json"
	provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {}
	snapshot = summarize(entries, site_docs, owners, histories, admissions, provenance)
	labels = mkdocs_nav.subject_display_labels(str(mkdocs_path))
	for subject in snapshot["subjects"]:
		subject["icon"] = labels[subject["key"]].removesuffix(subject["title"]).strip()
	for kind, paths in snapshot["diagnostics"].items():
		if paths:
			print(f"WARNING: homepage {kind} banks ({len(paths)}): " + ", ".join(paths))
	file_write.write_text(data_path, json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
	file_write.write_text(fragment_path, homepage_render.render(snapshot))
	for key, path in activity_paths.items():
		file_write.write_text(path, homepage_render.activity_page(key, snapshot[key]))
	return outputs

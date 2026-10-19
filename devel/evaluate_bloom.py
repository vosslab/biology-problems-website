#!/usr/bin/env python3
"""Small live rubric diagnostics; results describe agreement and stability, not accuracy."""

import json
import random
import datetime
from pathlib import Path

import yaml

import bioproblems_site.bloom as bloom
import bioproblems_site.bloom_rubric as rubric
import bioproblems_site.bloom_evidence as evidence
import bioproblems_site.git_paths as git_paths


#============================================
def ambiguity(record: dict) -> float:
	"""Rank by the closest top-two alternatives on either dimension."""
	margins = []
	for probabilities in record["probabilities"].values():
		values = sorted(probabilities.values(), reverse=True)
		margins.append(values[0] - values[1])
	return min(margins)


#============================================
def main() -> None:
	"""Evaluate source-grounded cases and a reproducible random/targeted bank sample."""
	root = Path(git_paths.get_repo_root())
	key = (Path.home() / ".config/jev/jev-api-key.txt").read_text().strip()
	records = bloom.load(root)
	diagnostics = bloom.experiments(root)
	sources = {entry.source_path.name: entry.source_path for entry in evidence.entries(root)}
	mapping = evidence.yaml_sources(root)
	random_names = random.Random(20261019).sample(sorted(sources.keys() & records.keys()),
		min(10, len(sources.keys() & records.keys())))
	targeted = sorted(sources.keys() & diagnostics.keys(),
		key=lambda name: ambiguity(diagnostics[name]))[:10]
	rare = [name for name in sorted(sources.keys() & records.keys())
		if records[name]["cognitive"] in ("Create", "Evaluate")
		or records[name]["knowledge"] == "Metacognitive"][:5]
	baseline = root / "LOCAL_ONLY/bloom_evaluation_v1.json"
	if rubric.VERSION != "1" and baseline.exists():
		# Freeze the first diagnostic sample so revisions compare the same banks.
		previous = json.loads(baseline.read_text(encoding="utf-8"))["stability"]
		random_names = [row["filename"] for row in previous if row["selection"] == "random"
			and row["filename"] in sources and row["filename"] in records]
		targeted = [row["filename"] for row in previous if row["selection"] == "targeted"
			and row["filename"] in sources and row["filename"] in records]
		rare = []
	run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
	archive = root / "LOCAL_ONLY/bloom_runs" / ("evaluation_" + run_id + ".jsonl")
	archive.parent.mkdir(parents=True, exist_ok=True)
	results = {"rubric_version": rubric.VERSION, "references": [], "stability": []}
	cases = yaml.safe_load((root / "docs/bloom_examples.yml").read_text())
	with archive.open("x", encoding="utf-8") as stream:
		for case in cases:
			# Expectations and rationale are withheld from JEV, not fed back as instructions.
			result, payload = bloom.request({"question": case["prompt"]}, key)
			stream.write(json.dumps({"request": payload, "result": result}) + "\n")
			actual = list(bloom.pair(result))
			results["references"].append({"id": case["id"], "expected": case["expected"],
				"actual": actual, "held_out": case.get("held_out", False)})
			print(case["id"], actual, "agreement:", actual == case["expected"], flush=True)
		for name in sorted(set(random_names + targeted + rare)):
			state = evidence.build(sources[name], mapping, sample_count=10)
			state["examples"].reverse()
			state["example_indices"].reverse()
			# YAML content is unchanged; reverse mapping order to probe presentation sensitivity.
			if "authored_yaml" in state:
				state["authored_yaml"] = dict(reversed(list(state["authored_yaml"].items())))
			result, payload = bloom.request(state, key)
			stream.write(json.dumps({"request": payload, "result": result}) + "\n")
			actual = list(bloom.pair(result))
			original = list(bloom.pair(records[name]))
			results["stability"].append({"filename": name, "original": original,
				"actual": actual, "selection": "random" if name in random_names else "targeted"})
			print(name, actual, "stable:", actual == original, flush=True)
	path = root / "LOCAL_ONLY" / f"bloom_evaluation_v{rubric.VERSION}.json"
	path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
	print(path)


if __name__ == "__main__":
	main()

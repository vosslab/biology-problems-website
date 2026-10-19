"""Readable generated questions and exact authored-YAML mappings for Bloom classification."""

# Standard Library
import re
from pathlib import Path

# PIP3 modules
import bs4
import yaml

# local repo modules
import bioproblems_site.bbq_config as bbq_config
import bioproblems_site.metadata as metadata
import bioproblems_site.question_index as question_index


#============================================
def entries(root: Path) -> list[question_index.QuestionSetEntry]:
	"""Use the same visible inventory as the Question Finder."""
	subjects, order = metadata.load_topics_metadata(
		metadata_path=str(root / "topics_metadata.yml"), mkdocs_path=str(root / "mkdocs.yml"),
	)
	return question_index.collect_entries(root / "site_docs", subjects, order)


#============================================
def yaml_sources(root: Path) -> dict[str, Path]:
	"""Match exact output families and authored stems, never overlapping prefixes."""
	settings = bbq_config.load_bbq_config(str(root / "bbq_settings.yml"))
	subjects, _order = metadata.load_topics_metadata(
		metadata_path=str(root / "topics_metadata.yml"), mkdocs_path=str(root / "mkdocs.yml"),
	)
	aliases = metadata.build_topic_alias_map(subjects)
	families = {
		"yaml_match_to_bbq.py": ("MATCH",),
		"yaml_which_one_mc_to_bbq.py": ("WOMC", "MC"),
		"yaml_mc_statements_to_bbq.py": ("TFMS",),
	}
	mapping = {}
	for csv_path in sorted((root / "task_files").glob("*.csv")):
		for task in bbq_config.load_tasks_csv(str(csv_path), settings, aliases):
			# A Python generator's YAML molecule data is not an authored question bank.
			for family in families.get(Path(task["script"]).name, ()):
				source = Path(task["input_path"])
				name = f"bbq-{family}-{source.stem}-questions.txt"
				if name in mapping and mapping[name] != source:
					raise ValueError(f"Conflicting authored YAML sources for {name}")
				mapping[name] = source
	return mapping


#============================================
def readable(text: str) -> str:
	"""Preserve table rows/cells, math text, and image alternatives; discard presentation."""
	soup = bs4.BeautifulSoup(text, "html.parser")
	for node in soup(["script", "style"]):
		node.decompose()
	for node in soup.find_all("img"):
		node.replace_with("[Image: " + node.get("alt", "no text alternative") + "]")
	for node in soup.find_all(["td", "th"]):
		node.append(" | ")
	for node in soup.find_all(["tr", "p", "div", "br", "li"]):
		node.append("\n")
	lines = [re.sub(r"[ \t\r\f\v]+", " ", line).strip() for line in soup.get_text().splitlines()]
	result = "\n".join(line for line in lines if line)
	# Do not strip numeric-looking prefixes: answer/tolerance fields are data.
	return result


#============================================
def clean_yaml(value: object) -> object:
	"""Retain authored alternatives, keys, and prompts while removing color substitutions."""
	if isinstance(value, str):
		return readable(value)
	if isinstance(value, list):
		return [clean_yaml(item) for item in value]
	if isinstance(value, dict):
		return {key: clean_yaml(item) for key, item in value.items() if key != "replacement_rules"}
	return value


#============================================
def build(source: Path, mapping: dict[str, Path], sample_count: int = 5) -> dict:
	"""Supply complete, spread-out questions, or authored YAML with one output example."""
	lines = [line for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
	if not lines:
		raise ValueError(f"Empty bank: {source.name}")
	count = min(sample_count, len(lines))
	indices = sorted({round(i * (len(lines) - 1) / max(1, count - 1)) for i in range(count)})
	examples = [
		[readable(field) for field in lines[index].split("\t")]
		for index in indices
	]
	result = {
		"filename": source.name, "format": lines[0].split("\t")[0],
		"evidence_kind": "generated_readable", "record_count": len(lines),
		"field_order": "BBQ: format, prompt, then response fields including answer keys/statuses",
		"example_indices": indices, "examples": examples,
	}
	if source.name in mapping:
		yaml_path = mapping[source.name]
		result.update({
			"evidence_kind": "authored_yaml", "source_name": yaml_path.name,
			"authored_yaml": clean_yaml(yaml.safe_load(yaml_path.read_text(encoding="utf-8"))),
			"examples": examples[:1], "example_indices": indices[:1],
		})
	elif source.name.startswith(("bbq-MATCH-", "bbq-WOMC-", "bbq-TFMS-")):
		raise ValueError(f"Authored question YAML not mapped: {source.name}")
	return result

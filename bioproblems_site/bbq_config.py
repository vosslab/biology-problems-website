"""Configuration and CSV-to-task loading for BBQ generation."""

import csv
import os
import shlex

import yaml

import bioproblems_site.git_paths
import bioproblems_site.topic_aliases


INPUT_SCRIPT_BASENAMES = {
	"yaml_match_to_bbq.py",
	"yaml_which_one_mc_to_bbq.py",
	"yaml_make_which_one_multiple_choice.py",
	"yaml_mc_statements_to_bbq.py",
	"yaml_make_match_sets.py",
}


def find_settings_yaml(settings_arg: str) -> str:
	"""Find the BBQ settings file in the current repository."""
	if settings_arg and os.path.isabs(settings_arg):
		if os.path.isfile(settings_arg):
			return settings_arg
		return ""
	settings_basename = os.path.basename(settings_arg) if settings_arg else "bbq_settings.yml"
	repo_root = bioproblems_site.git_paths.get_repo_root()
	package_dir = os.path.dirname(os.path.abspath(__file__))
	search_paths = [
		os.path.join(os.getcwd(), settings_basename),
		os.path.join(repo_root, settings_basename),
		os.path.join(package_dir, settings_basename),
	]
	for candidate in search_paths:
		if os.path.isfile(candidate):
			return candidate
	return ""


def load_bbq_config(config_path: str) -> dict[str, object]:
	"""Load a YAML BBQ configuration, returning an empty config when absent."""
	if not config_path or not os.path.isfile(config_path):
		return {}
	with open(config_path, "r") as config_handle:
		config_data = yaml.safe_load(config_handle)
	if not isinstance(config_data, dict):
		return {}
	return config_data


def apply_aliases(text: str, aliases: dict[str, object]) -> str:
	if not text:
		return ""
	result = text
	for key, value in aliases.items():
		if isinstance(value, str):
			result = result.replace(f"{{{key}}}", value)
	return result


def resolve_alias_map(raw_aliases: dict[str, object]) -> dict[str, object]:
	if not isinstance(raw_aliases, dict):
		return {}
	resolved = dict(raw_aliases)
	for _ in range(3):
		for key, value in resolved.items():
			if isinstance(value, str):
				resolved[key] = apply_aliases(value, resolved)
	for key, value in resolved.items():
		if isinstance(value, str):
			resolved[key] = os.path.expanduser(value)
	return resolved


def resolve_script_alias(script_value: str, script_aliases: dict[str, object]) -> object:
	if not script_value:
		return ""
	if script_value.startswith("@"):
		alias_key = script_value[1:]
		return script_aliases.get(alias_key, script_value)
	if script_value in script_aliases:
		return script_aliases[script_value]
	return script_value


def get_env_bp_root() -> str:
	for key in ("bp_root", "BP_ROOT"):
		value = os.environ.get(key, "").strip()
		if value:
			return os.path.expanduser(value)
	return ""


def apply_env_overrides(path_aliases: dict[str, object]) -> dict[str, object]:
	if not isinstance(path_aliases, dict):
		return {}
	updated = dict(path_aliases)
	env_bp_root = get_env_bp_root()
	if env_bp_root:
		updated["bp_root"] = env_bp_root
	return updated


def _pythonpath_has_repo(python_parts: list[str], repo_name: str) -> bool:
	for part in python_parts:
		if not part:
			continue
		normalized = os.path.abspath(os.path.expanduser(part))
		path_parts = [segment for segment in normalized.split(os.sep) if segment]
		if repo_name in path_parts:
			return True
	return False


def check_pythonpath(bbq_config: dict[str, object]) -> tuple[bool, str]:
	pythonpath_value = os.environ.get("PYTHONPATH", "").strip()
	if not pythonpath_value:
		return False, "ERROR: PYTHONPATH is not set. Run: source source_me.sh"
	python_parts = [part.strip() for part in pythonpath_value.split(os.pathsep) if part.strip()]
	missing_repos = []
	for repo_name in ("qti-package-maker",):
		if not _pythonpath_has_repo(python_parts, repo_name):
			missing_repos.append(repo_name)
	if missing_repos:
		missing_text = ", ".join(missing_repos)
		return (
			False,
			"ERROR: PYTHONPATH is missing required repo path(s): "
			f"{missing_text}. Run: source source_me.sh",
		)
	return True, ""


def build_pythonpath(bbq_config: dict[str, object]) -> str:
	paths_config = bbq_config.get("paths", {}) if isinstance(bbq_config, dict) else {}
	path_aliases = apply_env_overrides(resolve_alias_map(paths_config))
	python_parts: list[str] = []

	def add_path(path_value: str) -> None:
		if not path_value:
			return
		normalized = os.path.abspath(os.path.expanduser(path_value))
		if normalized not in python_parts:
			python_parts.append(normalized)

	bp_root = (path_aliases.get("bp_root") or "").strip()
	if bp_root:
		if os.path.basename(bp_root) == "problems":
			bp_root = os.path.dirname(bp_root)
		add_path(bp_root)
	qti_root = (path_aliases.get("qti_package_maker") or "").strip()
	if qti_root:
		add_path(qti_root)
	existing = os.environ.get("PYTHONPATH", "")
	if existing:
		for part in existing.split(os.pathsep):
			add_path(part)
	return os.pathsep.join(python_parts)


def expand_text(text: str, aliases: dict[str, object]) -> str:
	if not text:
		return ""
	return os.path.expanduser(apply_aliases(text, aliases))


def normalize_path(
	path_value: str,
	repo_root: str,
	base_root: str,
	aliases: dict[str, object],
) -> str:
	if not path_value:
		return ""
	path_value = expand_text(path_value, aliases)
	if not os.path.isabs(path_value):
		root = base_root if base_root else repo_root
		path_value = os.path.join(root, path_value)
	return os.path.abspath(path_value)


def add_input_args(args: list[str], input_flag: str, input_path: str) -> list[str]:
	if not input_path:
		return args
	updated = list(args)
	if input_flag:
		if input_flag not in updated:
			updated.extend([input_flag, input_path])
		elif input_path not in updated:
			updated.append(input_path)
	elif input_path not in updated:
		updated.append(input_path)
	return updated


def get_missing_input_message(task: dict[str, object]) -> str:
	input_path = task.get("input_path") or ""
	if not input_path or os.path.isfile(input_path):
		return ""
	return f"Missing input file: {input_path}"


def get_missing_script_message(task: dict[str, object]) -> str:
	script_path = task.get("script") or ""
	if not script_path or os.path.isfile(script_path):
		return ""
	return f"Missing script file: {script_path}"


def load_tasks(
	config_path: str,
	bbq_config: dict[str, object],
	topic_alias_map: dict[str, object],
) -> list[dict[str, object]]:
	return load_tasks_csv(config_path, bbq_config, topic_alias_map)


def load_tasks_csv(
	config_path: str,
	bbq_config: dict[str, object],
	topic_alias_map: dict[str, object],
) -> list[dict[str, object]]:
	tasks: list[dict[str, object]] = []
	repo_root = bioproblems_site.git_paths.get_repo_root()
	paths_config = bbq_config.get("paths", {}) if isinstance(bbq_config, dict) else {}
	path_aliases = apply_env_overrides(resolve_alias_map(paths_config))
	path_aliases["repo_root"] = repo_root
	script_aliases_raw = bbq_config.get("script_aliases", {}) if isinstance(bbq_config, dict) else {}
	script_aliases: dict[str, object] = {}
	if isinstance(script_aliases_raw, dict):
		for alias_key, alias_value in script_aliases_raw.items():
			if isinstance(alias_value, str):
				script_aliases[alias_key] = expand_text(alias_value, path_aliases)
			elif isinstance(alias_value, list):
				expanded_list = [
					expand_text(item, path_aliases)
					for item in alias_value
					if isinstance(item, str)
				]
				if expanded_list:
					script_aliases[alias_key] = expanded_list
	defaults = bbq_config.get("defaults", {}) if isinstance(bbq_config, dict) else {}
	default_input_flag = ""
	if isinstance(defaults, dict):
		default_input_flag = (defaults.get("input_flag") or "").strip()
	if not default_input_flag:
		default_input_flag = "-y"
	pgml_script_map_raw = bbq_config.get("pgml_script_map", {}) if isinstance(bbq_config, dict) else {}
	pgml_script_map: dict[str, dict[str, object]] = {}
	if isinstance(pgml_script_map_raw, dict):
		for bbq_script_name, pgml_entry in pgml_script_map_raw.items():
			if not isinstance(pgml_entry, dict):
				continue
			pgml_script_map[bbq_script_name] = {
				"script": expand_text(pgml_entry.get("script") or "", path_aliases),
				"suffix": pgml_entry.get("suffix", ""),
				"extension": pgml_entry.get("extension", "pgml"),
			}
	base_root = (path_aliases.get("bp_root") or "").strip()
	if not os.path.isfile(config_path):
		raise FileNotFoundError(f"Config file not found: {config_path}")
	with open(config_path, newline="") as file_handle:
		reader = csv.DictReader(file_handle)
		for row in reader:
			program = (row.get("program") or "python3").strip()
			script = (row.get("script") or "").strip()
			flags = (row.get("flags") or "").strip()
			input_value = (row.get("input") or "").strip()
			output = (row.get("output") or "").strip()
			subject = (row.get("subject") or "").strip()
			raw_topic = (row.get("topic") or "").strip()
			output_file = (row.get("output_file") or "").strip()
			if not script and not flags:
				continue
			topic = bioproblems_site.topic_aliases.resolve_topic_key(
				subject,
				raw_topic,
				topic_alias_map,
				source=config_path,
				line_number=reader.line_num,
			)
			script_value = resolve_script_alias(script, script_aliases)
			if isinstance(script_value, list):
				script_values = [item.strip() for item in script_value if isinstance(item, str) and item.strip()]
			elif isinstance(script_value, str) and script_value:
				script_values = [script_value]
			else:
				script_values = []
			if not script_values and script:
				script_values = [script]
			output_dir_parts = [repo_root, "site_docs"]
			if subject:
				output_dir_parts.append(subject)
			if topic:
				output_dir_parts.append(topic)
			output_dir = os.path.join(*output_dir_parts)
			if not output and output_file:
				output = os.path.join(output_dir, output_file)
			output = normalize_path(output, repo_root, "", path_aliases)
			base_args = shlex.split(expand_text(flags, path_aliases)) if flags else []
			for script_entry in script_values:
				script_path = normalize_path(script_entry, repo_root, base_root, path_aliases)
				args = list(base_args)
				input_path = ""
				if input_value:
					input_value_expanded = input_value
					if os.path.basename(input_value_expanded) == input_value_expanded:
						script_basename = os.path.basename(script_path)
						if script_basename in INPUT_SCRIPT_BASENAMES:
							input_value_expanded = os.path.join(
								os.path.dirname(script_path), input_value_expanded
							)
					input_path = normalize_path(
						input_value_expanded, repo_root, base_root, path_aliases
					)
					args = add_input_args(args, default_input_flag, input_path)
				task: dict[str, object] = {
					"program": program or "python3",
					"script": script_path,
					"args": args,
					"output": output,
					"output_dir": output_dir,
					"input_path": input_path,
					# These canonical keys come from the CSV and metadata resolver.
					# Downstream stages must not recover them from output paths.
					"subject": subject,
					"topic": topic,
				}
				script_basename = os.path.basename(script_path)
				if script_basename in pgml_script_map and input_path:
					pgml_entry = pgml_script_map[script_basename]
					pgml_script_path = normalize_path(
						pgml_entry["script"], repo_root, base_root, path_aliases
					)
					task["pgml_info"] = {
						"script": pgml_script_path,
						"suffix": pgml_entry["suffix"],
						"extension": pgml_entry["extension"],
						"input_path": input_path,
						"output_dir": os.path.join(output_dir, "downloads"),
					}
				tasks.append(task)
	return tasks

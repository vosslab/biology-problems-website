"""Read and publish the repository-wide problem-set title cache."""

# Standard Library
from pathlib import Path

# PIP3 modules
import yaml

# local repo modules
import bioproblems_site.file_write as file_write
import bioproblems_site.git_paths as git_paths


TITLE_CACHE_FILENAME = "problem_set_titles.yml"
LAST_EDIT_KEY = "last edit"


#============================================
def path_for_site_docs(site_docs_dir: str | Path) -> Path:
	"""Return the shared title-cache path for a MkDocs docs directory."""
	return Path(site_docs_dir).parent / TITLE_CACHE_FILENAME


#============================================
def path_for_source(source_path: str | Path) -> Path:
	"""Return the shared title-cache path for one BBQ source."""
	for parent in Path(source_path).parents:
		if parent.name == "site_docs":
			return path_for_site_docs(parent)
	return Path(git_paths.get_repo_root()) / TITLE_CACHE_FILENAME


#============================================
def load(cache_path: str | Path) -> dict:
	"""Load the shared title map, returning an empty map when it is absent."""
	path = Path(cache_path)
	if not path.is_file():
		return {}
	payload = yaml.safe_load(path.read_text(encoding="utf-8"))
	if payload is None:
		return {}
	if not isinstance(payload, dict):
		raise ValueError(f"Title cache must contain a YAML mapping: {path}")
	return payload


#============================================
def save(cache_path: str | Path, titles: dict) -> None:
	"""Write the shared title map as readable YAML."""
	text = yaml.safe_dump(titles, sort_keys=True, allow_unicode=False)
	file_write.write_text(cache_path, text)

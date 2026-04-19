"""Orchestrate page generation: metadata load + scan + subject index
rendering + topic page rendering + mkdocs.yml nav-block update. Called
from the generate_pages.py entrypoint.
"""

# Standard Library
import os

# local repo modules
import bioproblems_site.metadata as metadata_module
import bioproblems_site.scanner as scanner_module
import bioproblems_site.subject_index as subject_index_module
import bioproblems_site.topic_page as topic_page_module
import bioproblems_site.mkdocs_nav as mkdocs_nav_module
import bioproblems_site.llm_helpers as llm_helpers


#============================================
DEFAULT_SITE_DOCS = "site_docs"
DEFAULT_METADATA_PATH = "topics_metadata.yml"
DEFAULT_MKDOCS_PATH = "mkdocs.yml"


def color_text(text: str, color: str) -> str:
	"""Return colored text for CLI readability (ANSI)."""
	return f"\033[{color}m{text}\033[0m"


COLOR_CYAN = "96"
COLOR_GREEN = "92"
COLOR_YELLOW = "93"


#============================================
def _write_subject_index(
	site_docs_dir: str,
	subject,
	scans: dict,
	*,
	dry_run: bool,
	verbose: bool,
) -> None:
	"""Render and write one subject index.md.

	Refuses to overwrite a file that lacks the generated marker; all
	live subject index.md files should carry the marker. If this error
	trips, delete the offending file and regenerate from scratch.
	"""
	out_dir = os.path.join(site_docs_dir, subject.key)
	out_path = os.path.join(out_dir, "index.md")
	expected_target = os.path.normpath(out_path)
	text = subject_index_module.render_subject_index(subject, scans)
	if os.path.isfile(expected_target):
		marker_present = subject_index_module.has_generated_marker(expected_target)
		if not marker_present:
			raise RuntimeError(
				f"Refusing to overwrite {expected_target} -- file has no "
				f"generated marker. Delete the file and re-run to "
				f"regenerate from scratch."
			)
	if dry_run:
		if verbose:
			print(color_text(f"[dry-run] would write {expected_target}", COLOR_YELLOW))
		return
	os.makedirs(out_dir, exist_ok=True)
	with open(expected_target, "w") as file_pointer:
		file_pointer.write(text)
	if verbose:
		print(color_text(f"wrote {expected_target}", COLOR_GREEN))


#============================================
def run(
	*,
	subject_filter: "str | None" = None,
	topic_filter: "str | None" = None,
	subject_indexes: bool = True,
	topic_pages: bool = False,
	generate_downloads: bool = False,
	dry_run: bool = False,
	verbose: bool = True,
	model: "str | None" = None,
	use_ollama: bool = False,
	site_docs_dir: str = DEFAULT_SITE_DOCS,
	metadata_path: str = DEFAULT_METADATA_PATH,
	mkdocs_path: str = DEFAULT_MKDOCS_PATH,
) -> None:
	"""Regenerate subject indexes, topic pages, and the mkdocs.yml nav block.

	Three independent axes. `subject_indexes` also updates mkdocs nav.
	`topic_pages` rewrites topic??/index.md files. `generate_downloads`
	is only meaningful when `topic_pages` is True; when False, download
	artifact files are not created (buttons still render for files that
	already exist on disk).
	"""
	subjects, nav_order = metadata_module.load_topics_metadata(
		metadata_path=metadata_path, mkdocs_path=mkdocs_path
	)
	if subject_filter:
		if subject_filter not in subjects:
			raise ValueError(
				f"Unknown subject {subject_filter!r}; expected one of "
				f"{sorted(subjects)}"
			)
		scoped_subjects = [subjects[subject_filter]]
	else:
		scoped_subjects = [subjects[key] for key in nav_order]

	if subject_indexes:
		if verbose:
			print(color_text("== Rendering subject indexes ==", COLOR_CYAN))
		for subject in scoped_subjects:
			topic_keys = tuple(t.key for t in subject.topics)
			scans = scanner_module.scan_subject(
				site_docs_dir, subject.key, topic_keys
			)
			_write_subject_index(
				site_docs_dir,
				subject,
				scans,
				dry_run=dry_run,
				verbose=verbose,
			)

	if topic_pages:
		if verbose:
			print(color_text("== Rendering topic pages ==", COLOR_CYAN))
		if dry_run:
			if verbose:
				print(color_text(
					"[dry-run] would render topic pages",
					COLOR_YELLOW,
				))
		else:
			# Build a single LLMClient up front; reused for every topic page.
			llm_client = llm_helpers.create_llm_client(
				model=model, use_ollama=use_ollama,
			)
			options = topic_page_module.RenderOptions(
				verbose=verbose,
				llm_client=llm_client,
				generate_downloads=generate_downloads,
			)
			topic_page_module.render_all(options)

	# Nav block regen runs whenever subject indexes were rewritten (nav
	# entries depend on the same visibility/count filter as the index).
	if subject_indexes:
		if verbose:
			print(color_text("== Updating mkdocs.yml nav block ==", COLOR_CYAN))
		mkdocs_nav_module.update_from_sources(
			metadata_path=metadata_path,
			mkdocs_path=mkdocs_path,
			site_docs_dir=site_docs_dir,
			dry_run=dry_run,
		)
		if verbose and not dry_run:
			print(color_text(f"updated {mkdocs_path} nav block", COLOR_GREEN))

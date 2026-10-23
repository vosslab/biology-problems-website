"""Publish named HTML entry points for browser-converted BBQ banks."""

# Standard Library
import html
import pathlib
import posixpath

# PIP3 modules
import mkdocs.config.defaults
import mkdocs.structure.files


#============================================
def on_files(
	files: mkdocs.structure.files.Files, config: mkdocs.config.defaults.MkDocsConfig,
) -> mkdocs.structure.files.Files:
	"""Add lightweight viewers to build output without changing source banks."""
	for source in list(files):
		path = pathlib.PurePosixPath(source.src_uri)
		if not (path.name.startswith("bbq-") and path.name.endswith("-questions.txt")):
			continue
		# ASVS 1.2.1: encode the source filename and script path at HTML boundaries.
		bank = html.escape(path.name, quote=True)
		script = html.escape(posixpath.relpath(
			"assets/scripts/package_download.js", str(path.parent),
		), quote=True)
		wrapper = '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
		wrapper += '<meta charset="utf-8">\n'
		wrapper += '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
		wrapper += f'<title>{bank}</title>\n</head>\n'
		wrapper += f'<body data-human-readable-bank="{bank}">\n'
		wrapper += '<p role="status">Loading question bank...</p>\n'
		wrapper += '<button type="button" id="human-readable-retry" hidden>Retry</button>\n'
		wrapper += '<noscript>Enable JavaScript to view these questions.</noscript>\n'
		wrapper += f'<script src="{script}"></script>\n</body>\n</html>\n'
		viewer = mkdocs.structure.files.File.generated(
			config, str(path.with_suffix(".html")), content=wrapper,
		)
		files.append(viewer)
	return files

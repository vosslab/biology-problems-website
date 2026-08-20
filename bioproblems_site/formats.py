"""Neutral download-format registry.

Single source of truth for format keys and the filename patterns used
by the scanner to detect them. Human labels and button HTML live in
bioproblems_site.download_buttons, not here. This module is a pure
registry with no filesystem I/O; scanner.py owns discovery.
"""

#============================================
# Ordered tuple of format keys. Order controls scan and render order.
FORMAT_KEYS: tuple = (
	"bb_text",
	"bb_export",
	"canvas_qti",
	"human_read",
	"webwork_pgml",
)

# Glob patterns used to detect each format inside a topic or its downloads/
# directory. Generated download names put the format prefix before the core,
# so each pattern spells out that prefix instead of trying to infer a suffix.
FORMAT_FILE_GLOBS: dict = {
	# BBQ Text format: canonical source file lives in the topic directory
	# itself (not downloads/) and is the source of truth for
	# question counts.
	"bb_text": "bbq-*-questions.txt",
	# Blackboard pool export ZIP for Ultra's "Import from file" flow.
	"bb_export": "blackboard_export_zip-*.zip",
	# Canvas/ADAPT QTI v1.2 (zipped)
	"canvas_qti": "canvas_qti_v1_2-*.zip",
	# Human-readable HTML derived from the BBQ text
	"human_read": "human_readable-*.html",
	# WeBWorK PGML
	"webwork_pgml": ".pgml",
}

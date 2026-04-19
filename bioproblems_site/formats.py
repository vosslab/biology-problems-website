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
	"bb_qti",
	"canvas_qti",
	"human_read",
	"webwork_pgml",
)

# File suffix patterns used to detect each format inside a topic's
# downloads/ directory. These are glob suffixes appended to the base
# problem-set stem, e.g. "bbq-foo-questions.txt" -> "-questions.txt".
# Kept as simple suffixes so scanner code stays easy to read.
FORMAT_FILE_SUFFIXES: dict = {
	# Blackboard Learn TXT: original BBQ text file lives in the topic
	# directory itself (not downloads/) and is the source of truth for
	# question counts.
	"bb_text": "-questions.txt",
	# Blackboard Ultra QTI v2.1 (zipped)
	"bb_qti": "-bbq21.zip",
	# Canvas/ADAPT QTI v1.2 (zipped)
	"canvas_qti": "-canvas12.zip",
	# Human-readable HTML derived from the BBQ text
	"human_read": "-human.html",
	# WeBWorK PGML
	"webwork_pgml": ".pgml",
}


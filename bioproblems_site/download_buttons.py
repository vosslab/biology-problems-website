"""Provide download labels and browser formats for topic-page rendering.

bioproblems_site.topic_page imports these constants while it renders button rows.
"""

#============================================
FORMAT_LABELS: dict = {
	"selftest": "Selftest HTML",
	"bb_text": "BBQ Text",
	"bb_export": "Blackboard Ultra ZIP",
	"canvas_qti": "Canvas/ADAPT QTI v1.2",
	"human_read": "Human-Readable HTML",
	"webwork_pgml": "WeBWorK PGML",
}

# Browser conversion uses these canonical converter names and filenames.
BROWSER_FORMATS: dict = {
	"bb_export": ("blackboard_export_zip", "zip"),
	"canvas_qti": ("canvas_qti_v1_2", "zip"),
	"human_read": ("human_readable", "html"),
}

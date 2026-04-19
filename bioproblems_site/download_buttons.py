"""Human labels for download formats. Button-row HTML still lives in
bioproblems_site.topic_page (it has deep ties to the topic renderer);
the constants here are imported from there so there is one canonical
copy.
"""

#============================================
FORMAT_LABELS: dict = {
	"selftest": "Selftest HTML",
	"bb_text": "Blackboard Learn TXT",
	"bb_qti": "Blackboard Ultra QTI v2.1",
	"canvas_qti": "Canvas/ADAPT QTI v1.2",
	"human_read": "Human-Readable TXT",
	"webwork_pgml": "WeBWorK PGML",
}

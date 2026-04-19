"""Minimal pytest: generate_downloads=False must not create artifact files.

Pins the one behavior that actually matters for the --topic-pages
(without --generate-downloads) fast-path workflow.
"""

# Standard Library
import os

# local repo modules
import bioproblems_site.topic_page as topic_page


#============================================
def test_generate_downloads_off_creates_no_files(tmp_path):
	# Build a fake topic folder with one bbq-*-questions.txt source
	# file. The bbq file itself is the bb_text "download"; bb_qti would
	# live under downloads/ if created.
	downloads_dir = tmp_path / "downloads"
	downloads_dir.mkdir()
	bbq_file = tmp_path / "bbq-xx-questions.txt"
	bbq_file.write_text("MC\tQ1\n*A\tyes\nB\tno\n")
	before = set(os.listdir(downloads_dir))
	stats = {}
	topic_page.generate_download_button_row(
		str(bbq_file),
		["bb_text", "bb_qti"],
		force_downloads=False,
		verbose=False,
		stats=stats,
		generate_downloads=False,
	)
	after = set(os.listdir(downloads_dir))
	assert before == after

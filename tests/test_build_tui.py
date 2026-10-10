"""Behavior checks for the site-build operation list."""

import asyncio

import pytest
from textual.widgets import DataTable

import bioproblems_site.bbq_tui as bbq_tui
from bioproblems_site.build_contracts import BuildScope


#============================================
def test_topic_and_index_results_are_listed(monkeypatch: pytest.MonkeyPatch) -> None:
	"""The final operations remain visible and report their own result."""
	monkeypatch.setattr(bbq_tui.SiteBuildApp, "on_mount", lambda self: None)

	async def run_check() -> None:
		app = bbq_tui.SiteBuildApp(BuildScope())
		async with app.run_test() as pilot:
			label = "biotechnology/topic01 (biotech_tasks.csv:2)"
			app._handle_event("plan", {"task_rows": 1, "topics": 1, "row_labels": [label]})
			app._handle_event("stage_completed", {
				"phase": "downloads", "row": 1, "label": label,
				"duration": 0.1, "executed": True,
				"download_count": 10, "download_total": 10,
			})
			await pilot.pause()
			table = app.query_one(DataTable)
			assert str(table.get_row_at(1)[3]) == "10 of 10"
			app._handle_event("bbq_counts", {
				"row": 1, "label": label,
				"question_counts": [{"file": "bbq-example-questions.txt", "count": 2, "limit": 3}],
			})
			assert str(table.get_row_at(0)[3]) == "2/3 questions"
			app._handle_event("phase_plan", {"phase": "topic_pages", "total": 1})
			app._handle_event("stage_started", {
				"phase": "topic_pages", "label": "biotechnology/topic01",
			})
			app._handle_event("stage_completed", {
				"phase": "topic_pages", "label": "biotechnology/topic01",
				"duration": 10.0, "executed": True,
			})
			app._handle_event("phase_plan", {"phase": "indexes", "total": 1})
			app._handle_event("stage_started", {
				"phase": "indexes", "label": "Indexes, navigation, manifest",
			})
			app._handle_event("stage_completed", {
				"phase": "indexes", "label": "Indexes, navigation, manifest",
				"duration": 1.0, "executed": True,
			})
			steps = [tuple(map(str, table.get_row_at(index)[1:])) for index in range(table.row_count)]
			assert ("Topic pages", "biotechnology/topic01", "ok") in steps
			assert ("Indexes, navigation, and manifest", "Indexes, navigation, manifest", "ok") in steps

	asyncio.run(run_check())


#============================================
def test_failed_topic_step_stays_visible(monkeypatch: pytest.MonkeyPatch) -> None:
	"""A title-generation failure identifies the failed operation in the list."""
	monkeypatch.setattr(bbq_tui.SiteBuildApp, "on_mount", lambda self: None)

	async def run_check() -> None:
		app = bbq_tui.SiteBuildApp(BuildScope())
		async with app.run_test():
			details = {"phase": "topic_pages", "label": "biotechnology/topic01"}
			app._handle_event("phase_plan", {"phase": "topic_pages", "total": 1})
			app._handle_event("stage_started", details)
			app._handle_event("stage_failed", {**details, "detail": "invalid title"})
			app._finish_build(1, "Build failed: invalid title")

			assert str(app.query_one(DataTable).get_row_at(0)[3]) == "failed"
			assert "Result: failed" in str(app.query_one("#metrics").render())

	asyncio.run(run_check())

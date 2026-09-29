"""Regression checks for estimates that cover the complete build pipeline."""

import pytest

import bioproblems_site.build_progress as build_progress


#============================================
def test_estimate_includes_conversions_and_finalization(monkeypatch: pytest.MonkeyPatch) -> None:
	"""Slow downloads and row overhead must contribute to the finish estimate."""
	timing = build_progress.BuildTiming()
	clock = [0.0]
	monkeypatch.setattr(build_progress.time, "perf_counter", lambda: clock[0])
	timing.observe("plan", {"task_rows": 3, "topics": 2})
	for row in (1, 2):
		timing.observe("row_started", {"row": row})
		for phase, duration in (("bbq", 1.0), ("selftests", 2.0), ("downloads", 120.0)):
			clock[0] += duration
			if phase == "downloads":
				clock[0] += 7.0
			timing.observe("stage_completed", {
				"phase": phase, "row": row, "duration": duration, "executed": True,
			})

	before_finalization = timing.estimate()
	# A full row remains, plus two topic pages and one final indexing operation.
	row_time = clock[0] / 2
	assert before_finalization is not None and before_finalization > row_time
	for phase, total, duration in (("topic_pages", 2, 30.0), ("indexes", 1, 10.0)):
		timing.observe("phase_plan", {"phase": phase, "total": total})
		timing.observe("stage_completed", {
			"phase": phase, "duration": duration, "executed": True,
		})
	remaining = timing.estimate()
	assert remaining is not None and row_time <= remaining < before_finalization


#============================================
def test_skips_do_not_dilute_estimates(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	"""Skips remove remaining work without reducing measured costs or overhead."""
	timing = build_progress.BuildTiming()
	without_cached_row = build_progress.BuildTiming()
	clock = [0.0]
	monkeypatch.setattr(build_progress.time, "perf_counter", lambda: clock[0])
	timing.observe("plan", {"task_rows": 4, "topics": 0})
	without_cached_row.observe("plan", {"task_rows": 3, "topics": 0})
	for row in (1, 2):
		timing.observe("row_started", {"row": row})
		without_cached_row.observe("row_started", {"row": row})
		for phase in ("bbq", "selftests", "downloads"):
			clock[0] += 10.0
			if phase == "downloads":
				clock[0] += 5.0
			details = {
				"phase": phase, "row": row, "duration": 10.0, "executed": True,
			}
			timing.observe("stage_completed", details)
			without_cached_row.observe("stage_completed", details)
	timing.observe("row_started", {"row": 3})
	for phase in ("bbq", "selftests", "downloads"):
		clock[0] += 1.0
		timing.observe("stage_skipped", {"phase": phase, "row": 3})
	after_cached = timing.estimate()
	assert after_cached is not None
	assert after_cached == pytest.approx(without_cached_row.estimate())

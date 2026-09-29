"""Timing-log retention and complete wall-time accounting."""

import json
import threading
from pathlib import Path

import pytest

import bioproblems_site.build_coordinator as build_coordinator
import bioproblems_site.build_progress as build_progress
import bioproblems_site.build_timing_log as build_timing_log
from bioproblems_site.build_contracts import BuildChanges, BuildScope


#============================================
def test_timing_log_retains_runs_and_exposes_time_outside_stages(
	monkeypatch: pytest.MonkeyPatch,
	tmp_path: Path,
) -> None:
	"""Wall time includes setup and gaps; nested exports are not counted twice."""
	clock = [100.0]
	monkeypatch.setattr(build_timing_log.time, "perf_counter", lambda: clock[0])
	monkeypatch.setattr(build_coordinator.git_paths, "get_repo_root", lambda: str(tmp_path))

	def measured_build(scope: BuildScope, progress: build_progress.BuildProgress) -> build_coordinator.BuildReport:
		progress.emit("plan", task_rows=1, topics=0)
		clock[0] += 2.0
		progress.emit("row_started", row=1, label="genetics/topic01 (tasks.csv:2)")
		for phase, duration in (("bbq", 2.0), ("selftests", 3.0), ("downloads", 4.0)):
			if phase == "selftests":
				clock[0] += 4.0
			progress.emit("stage_started", phase=phase, label="genetics/topic01", row=1)
			clock[0] += duration
			if phase == "downloads":
				progress.emit("artifact_completed", format="blackboard_export_zip", duration=duration)
			progress.emit(
				"stage_completed", phase=phase, label="genetics/topic01", row=1,
				duration=duration, executed=True,
			)
		progress.emit("log", message="question content must not enter the timing log")
		progress.emit("stage_started", phase="indexes", label="Final indexes")
		clock[0] += 1.0
		progress.emit("stage_completed", phase="indexes", duration=1.0, executed=True)
		report = build_coordinator.BuildReport(BuildChanges(), elapsed_seconds=16.0)
		return report

	monkeypatch.setattr(build_coordinator, "build_site", measured_build)
	progress = build_progress.BuildProgress(lambda event, details: None, threading.Event())
	for _run in range(2):
		build_coordinator.build_site_with_timing(BuildScope(), progress)
	log_path = tmp_path / "build_timing.jsonl"
	log_text = log_path.read_text()
	records = [json.loads(line) for line in log_text.splitlines()]
	assert len({record["run_id"] for record in records}) == 2
	assert "question content must not enter" not in log_text
	completed = [record for record in records if record["event"] == "build_completed"]
	assert len(completed) == 2
	for record in completed:
		assert record["wall_seconds"] == pytest.approx(16.0)
		assert record["accounted_stage_seconds"] == pytest.approx(10.0)
		assert record["untracked_seconds"] == pytest.approx(6.0)
		assert record["build_started_at"].endswith("+00:00")
	rows = [record for record in records if record["event"] == "row_completed"]
	assert rows[0]["details"]["duration"] == pytest.approx(13.0)
	assert rows[0]["details"]["untracked_seconds"] == pytest.approx(4.0)
	build_coordinator.build_site_with_timing(BuildScope(dry_run=True), progress)
	assert [json.loads(line) for line in log_path.read_text().splitlines()] == records

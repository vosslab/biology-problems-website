"""Persistent measurements for diagnosing build estimates across runs."""

import io
import json
import time
import uuid
import dataclasses
from datetime import datetime, timedelta, timezone

import bioproblems_site.build_progress as build_progress
from bioproblems_site.build_contracts import BuildScope


#============================================
class BuildTimingLog:
	"""Append structured timings without copying question or command output."""

	EVENTS = frozenset({
		"plan", "phase_plan", "row_started", "stage_started", "stage_completed",
		"stage_skipped", "stage_failed", "bbq_counts", "task_started", "task_completed",
		"artifact_started", "artifact_completed", "artifact_skipped", "artifact_failed",
	})

	def __init__(self, stream: io.TextIOBase, scope: BuildScope) -> None:
		self.stream = stream
		self.run_id = uuid.uuid4().hex
		self.started_at = time.perf_counter()
		self.started_timestamp = datetime.now(timezone.utc).isoformat()
		self.accounted_stage_seconds = 0.0
		self.row_accounted_start = 0.0
		self.timing = build_progress.BuildTiming()
		self.active_phase = ""
		self.active_started_at: float | None = None
		self.row_details: dict[str, object] = {}
		selection = dataclasses.asdict(scope)
		if scope.tasks_csv is not None:
			selection["tasks_csv"] = str(scope.tasks_csv)
		self.write("build_started", {"scope": selection, "estimator_version": 2})

	def write(self, event: str, details: dict[str, object]) -> None:
		"""Flush one correlated measurement, including the current finish estimate."""
		wall_seconds = time.perf_counter() - self.started_at
		active_elapsed = 0.0
		if self.active_started_at is not None:
			active_elapsed = time.perf_counter() - self.active_started_at
		remaining = self.timing.estimate(self.active_phase, active_elapsed)
		# ASVS 16.2.1, 16.2.2: correlate runs with UTC timestamps and monotonic durations.
		now = datetime.now(timezone.utc)
		finish_at = None
		if remaining is not None:
			finish_at = (now + timedelta(seconds=remaining)).isoformat()
		untracked_seconds = max(wall_seconds - self.accounted_stage_seconds - active_elapsed, 0.0)
		record = {
			"schema_version": 1, "run_id": self.run_id, "timestamp": now.isoformat(),
			"build_started_at": self.started_timestamp, "wall_seconds": wall_seconds,
			"accounted_stage_seconds": self.accounted_stage_seconds,
			"active_phase": self.active_phase, "active_stage_seconds": active_elapsed,
			"untracked_seconds": untracked_seconds,
			"event": event, "details": details,
			"estimated_remaining_seconds": remaining, "estimated_finish_at": finish_at,
			"completed_operations": sum(self.timing.completed.values()),
			"planned_operations": sum(self.timing.totals.values()),
			"phase_mean_seconds": {
				phase: sum(values) / len(values) for phase, values in self.timing.samples.items()
			},
		}
		# ASVS 16.4.1: JSON escaping keeps embedded newlines inside one log record.
		line = json.dumps(record, ensure_ascii=True, allow_nan=False) + "\n"
		self.stream.write(line)
		self.stream.flush()

	def observe(self, event: str, details: dict[str, object]) -> None:
		"""Record stage, task, and per-format conversion timings and complete row cost."""
		if event not in self.EVENTS:
			return
		rows_before = len(self.timing.row_samples)
		self.timing.observe(event, details)
		if event == "row_started":
			self.row_details = dict(details)
			self.row_accounted_start = self.accounted_stage_seconds
		elif event == "stage_started":
			self.active_phase = str(details["phase"])
			self.active_started_at = time.perf_counter()
		elif event in ("stage_completed", "stage_skipped", "stage_failed"):
			self.accounted_stage_seconds += float(details.get("duration", 0.0))
			if details["phase"] == self.active_phase:
				self.active_phase = ""
				self.active_started_at = None
		# ASVS 16.2.5: exclude free-form failure output and verbose command logs.
		measurements = {key: value for key, value in details.items() if key != "detail"}
		self.write(event, measurements)
		if len(self.timing.row_samples) > rows_before:
			row_duration = self.timing.row_samples[-1]
			row_stage_seconds = self.accounted_stage_seconds - self.row_accounted_start
			self.write("row_completed", {
				**self.row_details, "duration": row_duration,
				"accounted_stage_seconds": row_stage_seconds,
				"untracked_seconds": max(row_duration - row_stage_seconds, 0.0),
			})

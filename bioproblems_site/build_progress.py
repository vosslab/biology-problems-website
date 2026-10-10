"""Optional progress and cooperative cancellation for unified builds."""

from collections.abc import Callable
from dataclasses import dataclass
from threading import Event
import time
from datetime import datetime, timedelta

import bioproblems_site.bbq_runner as bbq_runner


PHASE_LABELS = {
	"bbq": "BBQ generation",
	"downloads": "Downloads",
	"topic_pages": "Topic pages",
	"indexes": "Indexes, navigation, and manifest",
}


#============================================
def estimate_average(values: list[float]) -> float:
	"""Exclude one longest sample so one-time startup does not inflate remaining work."""
	if not values:
		return 0.0
	if len(values) < 3:
		average = sum(values) / len(values)
	else:
		average = (sum(values) - max(values)) / (len(values) - 1)
	return average


#============================================
class BuildTiming:
	"""Estimate each remaining phase from that phase's completed operations."""

	def __init__(self) -> None:
		self.totals: dict[str, int] = {}
		self.completed: dict[str, int] = {}
		self.samples: dict[str, list[float]] = {}
		self.row_samples: list[float] = []
		self.row_started_at: float | None = None
		self.row_stage_seconds = 0.0
		self.row_overhead_samples: list[float] = []

	def observe(self, event: str, details: dict[str, object]) -> None:
		"""Track all planned work, including cached operations and finalization."""
		if event == "plan":
			rows = int(details["task_rows"])
			self.totals.update({
				"bbq": rows, "downloads": rows,
				"topic_pages": int(details["topics"]), "indexes": 1,
			})
		elif event == "phase_plan":
			self.totals[str(details["phase"])] = int(details["total"])
		elif event == "row_started":
			self.row_started_at = time.perf_counter()
			self.row_stage_seconds = 0.0
		elif event in ("stage_completed", "stage_skipped", "stage_failed"):
			phase = str(details["phase"])
			self.completed[phase] = self.completed.get(phase, 0) + 1
			if event == "stage_completed" and details["executed"]:
				duration = float(details["duration"])
				self.samples.setdefault(phase, []).append(duration)
				if self.row_started_at is not None and phase in ("bbq", "downloads"):
					self.row_stage_seconds += duration
			if (
				phase == "downloads" and "row" in details
				and self.row_started_at is not None and not details.get("planned")
			):
				row_duration = time.perf_counter() - self.row_started_at
				self.row_samples.append(row_duration)
				# Keep every row's wall time for logging; cached rows do not train estimates.
				if self.row_stage_seconds > 0:
					self.row_overhead_samples.append(max(row_duration - self.row_stage_seconds, 0.0))
				self.row_started_at = None

	def estimate(
		self, active_phase: str = "", active_elapsed: float = 0.0,
	) -> float | None:
		"""Estimate after three complete rows, or all rows in a smaller build."""
		rows = self.totals.get("bbq", 0)
		if rows and len(self.row_samples) < min(3, rows):
			return None
		if not self.samples:
			return None
		remaining = 0.0
		row_phase_average = sum(
			estimate_average(self.samples[phase])
			for phase in ("bbq", "downloads") if self.samples.get(phase)
		)
		row_overhead = estimate_average(self.row_overhead_samples)
		row_average = row_phase_average + row_overhead
		for phase, total in self.totals.items():
			count = max(total - self.completed.get(phase, 0), 0)
			if count == 0:
				continue
			values = self.samples.get(phase, [])
			if not values:
				# Reserve a complete row's cost for each final operation until its
				# own timing is available; cheap generation alone is not a proxy.
				average = row_average
			else:
				average = estimate_average(values)
			remaining += count * average
			if phase == active_phase:
				remaining -= min(active_elapsed, average)
				# Keep the estimate visible during an overrun and allow another
				# observed operation's worth of time instead of predicting zero.
				if active_elapsed >= average:
					remaining += max(average, row_average)
		# Row wall time includes freshness checks, output counts, and coordinator
		# overhead that the individual operation durations do not always include.
		rows_left = max(self.totals.get("downloads", 0) - self.completed.get("downloads", 0), 0)
		remaining += rows_left * row_overhead
		return remaining


#============================================
class PlainBuildTiming:
	"""Print pipeline estimates after complete rows and final build operations."""

	def __init__(self) -> None:
		self.timing = BuildTiming()

	def observe(self, event: str, details: dict[str, object]) -> None:
		"""Preserve captured command output and report measured remaining work."""
		self.timing.observe(event, details)
		if event == "log":
			print(details["message"])
		if event not in ("stage_completed", "stage_skipped"):
			return
		if details["phase"] not in ("downloads", "topic_pages", "indexes"):
			return
		if sum(self.timing.completed.values()) >= sum(self.timing.totals.values()):
			return
		remaining = self.timing.estimate()
		if remaining is None:
			return
		remaining_text = bbq_runner.format_elapsed_time(remaining)
		finish_time = datetime.now().astimezone() + timedelta(seconds=remaining)
		clock_time = finish_time.strftime("%I:%M:%S %p").lstrip("0")
		print(f"  remaining: ~{remaining_text}; estimated finish: {clock_time}")


#============================================
class BuildCancelledError(Exception):
	"""Raised when a build reaches a boundary after cancellation was requested."""


#============================================
@dataclass(frozen=True)
class BuildProgress:
	"""Report internal build events and check a caller-owned cancellation signal."""

	callback: Callable[[str, dict[str, object]], None]
	cancel_event: Event

	def emit(self, event: str, **details: object) -> None:
		"""Send one progress event to the caller."""
		self.callback(event, details)

	def check_cancelled(self) -> None:
		"""Stop before starting more work after a cooperative cancellation request."""
		if self.cancel_event.is_set():
			raise BuildCancelledError("Build cancelled after the active operation completed.")

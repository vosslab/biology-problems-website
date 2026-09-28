"""Textual dashboard for the complete unified site build."""

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta
import threading
import time
from collections.abc import Callable

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, RichLog, Static

import bioproblems_site.build_coordinator as build_coordinator
import bioproblems_site.build_progress as build_progress
import bioproblems_site.bbq_runner as bbq_runner
from bioproblems_site.build_contracts import BuildScope


#============================================
class _BuildLogStream:
	"""Send captured coordinator output to the Textual event loop by line."""

	def __init__(self, callback: Callable[[str], None]) -> None:
		self.callback = callback
		self.buffer = ""

	def write(self, value: str) -> int:
		self.buffer += value
		while "\n" in self.buffer:
			line, self.buffer = self.buffer.split("\n", 1)
			if line:
				self.callback(line)
		return len(value)

	def flush(self) -> None:
		if self.buffer:
			self.callback(self.buffer)
			self.buffer = ""


#============================================
class CancelBuildScreen(ModalScreen[bool]):
	"""Confirm cooperative cancellation of the running site build."""

	CSS = (
		"Screen { align: center middle; background: $background 70%; }\n"
		"#cancel_dialog { width: 64; height: 11; padding: 1 2; "
		"border: thick $accent; background: $surface; }\n"
		"#cancel_buttons { height: 3; align: center middle; }\n"
		"Button { margin: 0 1; }\n"
	)

	def compose(self) -> ComposeResult:
		with Vertical(id="cancel_dialog"):
			yield Static(
				"Stop the build after its active command or operation finishes?",
			)
			with Horizontal(id="cancel_buttons"):
				yield Button("Continue build", id="continue")
				yield Button("Stop build", id="stop", variant="error")

	def on_button_pressed(self, event: Button.Pressed) -> None:
		self.dismiss(event.button.id == "stop")


#============================================
class SiteBuildApp(App[int]):
	"""Observe one coordinator run and offer cooperative cancellation."""

	BINDINGS = [("q", "request_cancel", "Cancel or close")]
	STATUS_STYLES = {
		"pending": "yellow",
		"running": "cyan",
		"ok": "green",
		"short": "yellow",
		"planned": "cyan",
		"skipped": "dim",
		"failed": "red",
		"cancelled": "yellow",
	}
	ROW_PHASES = ("bbq", "selftests", "downloads")
	PHASE_LABELS = {
		"bbq": "BBQ generation",
		"selftests": "Self-tests",
		"downloads": "Downloads",
		"topic_pages": "Topic pages",
		"indexes": "Indexes, navigation, and manifest",
	}
	CSS = (
		"#root { height: 1fr; }\n"
		"#top_row { height: 38%; min-height: 10; }\n"
		"#metrics_box { width: 38%; height: 1fr; border: solid gray; padding: 0 1; }\n"
		"#metrics_title { height: 1; text-style: bold; }\n"
		"#eta { height: 2; color: $success; text-style: bold; }\n"
		"#metrics { height: 1fr; }\n"
		"#footer_note { height: 1; }\n"
		"#messages { width: 62%; height: 1fr; border: solid gray; }\n"
		"#task_table { height: 1fr; border: solid gray; }\n"
	)

	def __init__(self, scope: BuildScope) -> None:
		super().__init__()
		self.scope = scope
		self.started_at = time.time()
		self.cancel_event = threading.Event()
		self.progress = build_progress.BuildProgress(self._report_event, self.cancel_event)
		self.step_keys: dict[tuple[str, int | str], object] = {}
		self.step_status: dict[tuple[str, int | str], str] = {}
		self.status_column: object | None = None
		self.phase_totals: dict[str, int] = {}
		self.phase_completed: dict[str, int] = {}
		self.phase_samples: dict[str, list[float]] = {}
		self.active_phase = ""
		self.active_label = ""
		self.active_started_at: float | None = None
		self.log_lines: list[str] = []
		self.exit_code = 0
		self.finished = False
		self.cancel_dialog_open = False

	def compose(self) -> ComposeResult:
		with Vertical(id="root"):
			with Horizontal(id="top_row"):
				with Vertical(id="metrics_box"):
					yield Static("Site Build Dashboard", id="metrics_title")
					yield Static("Estimating finish time...", id="eta")
					yield Static("Preparing build", id="metrics")
					yield Static("Press q to stop or close", id="footer_note")
				yield RichLog(id="messages", wrap=True, highlight=False, markup=False)
			table = DataTable(id="task_table", zebra_stripes=True)
			table.cursor_type = "row"
			table.add_column("#")
			table.add_column("Step")
			table.add_column("Item")
			self.status_column = table.add_column("Status")
			yield table

	def on_mount(self) -> None:
		self.set_interval(1, self.update_metrics)
		self.run_worker(self._run_build, thread=True, exclusive=True)

	def _report_event(self, event: str, details: dict[str, object]) -> None:
		"""Transfer an event from the coordinator thread to the UI thread."""
		self.call_from_thread(self._handle_event, event, details)

	def _handle_event(self, event: str, details: dict[str, object]) -> None:
		"""Apply one coordinator progress event to the dashboard."""
		if event == "plan":
			row_total = int(details["task_rows"])
			topic_total = int(details["topics"])
			self.phase_totals.update({
				"bbq": row_total,
				"selftests": row_total,
				"downloads": row_total,
				"topic_pages": topic_total,
			})
			row_labels = details["row_labels"]
			if isinstance(row_labels, list):
				for row_index, label in enumerate(row_labels, start=1):
					self._add_row_steps(row_index, str(label))
			self.append_log(f"Build plan: {row_total} CSV row(s)")
		elif event == "phase_plan":
			phase = str(details["phase"])
			self.phase_totals[phase] = int(details["total"])
			self.phase_completed.setdefault(phase, 0)
			if phase == "indexes":
				label = "Indexes, navigation, manifest"
				self._add_step((phase, label), self.PHASE_LABELS[phase], label)
			self.append_log(
				f"Planned {self.phase_totals[phase]} {self.PHASE_LABELS[phase].lower()} item(s)"
			)
		elif event == "row_started":
			row_index = int(details["row"])
			self._add_row_steps(row_index, str(details["label"]))
			self._update_metrics_text()
		elif event == "stage_started":
			phase = str(details["phase"])
			self.active_phase = phase
			self.active_label = str(details["label"])
			self.active_started_at = time.time()
			self._set_step_stage(details, "running")
			self.append_log(f"START {self.PHASE_LABELS[phase]}: {self.active_label}")
			self._update_metrics_text()
		elif event == "stage_completed":
			phase = str(details["phase"])
			status = "planned" if details.get("planned") else "ok"
			cell_text = None
			if phase == "downloads" and status == "ok":
				cell_text = self._download_count_text(details)
			self._set_step_stage(details, status, cell_text)
			self._complete_phase(phase, details)
			duration = float(details.get("duration", 0.0))
			self.append_log(
				f"{status.upper()} {self.PHASE_LABELS[phase]}: "
				f"{details['label']} ({duration:.1f}s)"
			)
			self._clear_active_phase(phase)
		elif event == "stage_skipped":
			phase = str(details["phase"])
			cell_text = None
			if phase == "downloads":
				cell_text = self._download_count_text(details)
			self._set_step_stage(details, "skipped", cell_text)
			self.phase_completed[phase] = self.phase_completed.get(phase, 0) + 1
			label = str(details["label"])
			detail = str(details.get("detail", "not required"))
			self.append_log(f"SKIP {self.PHASE_LABELS[phase]}: {label} ({detail})")
			self._clear_active_phase(phase)
		elif event == "stage_failed":
			phase = str(details["phase"])
			self._set_step_stage(details, "failed")
			self._complete_phase(phase, details)
			self.append_log(
				f"FAIL {self.PHASE_LABELS[phase]}: {details['label']} "
				f"({details.get('detail', 'unknown error')})"
			)
			self._clear_active_phase(phase)
		elif event == "bbq_counts":
			count_text, short = self._question_count_text(details)
			if count_text is not None:
				row_index = int(details["row"])
				prior_status = self.step_status[("bbq", row_index)]
				status = "short" if short else prior_status
				self._set_step_stage({**details, "phase": "bbq"}, status, count_text)
		elif event == "log":
			self.append_log(str(details["message"]))

	def _add_row_steps(self, row_index: int, label: str) -> None:
		"""List all three operations owned by one CSV task row."""
		for phase in self.ROW_PHASES:
			self._add_step((phase, row_index), self.PHASE_LABELS[phase], label)

	def _add_step(self, key: tuple[str, int | str], name: str, item: str) -> None:
		"""Add one operation to the ordered build list once."""
		if key in self.step_keys:
			return
		self.step_status[key] = "pending"
		self.step_keys[key] = self.query_one(DataTable).add_row(
			str(len(self.step_keys) + 1), name, item, self._styled_status("pending"),
		)

	def _styled_status(self, status: str, cell_text: str | None = None) -> Text:
		"""Return a colored status cell."""
		display_text = cell_text if cell_text is not None else status
		return Text(display_text, style=self.STATUS_STYLES[status])

	def _set_step_stage(
		self,
		details: dict[str, object],
		status: str,
		cell_text: str | None = None,
	) -> None:
		"""Update the listed operation for any build phase."""
		phase = str(details["phase"])
		row_index = details.get("row")
		label = str(details["label"])
		key = (phase, row_index if isinstance(row_index, int) else label)
		self._add_step(key, self.PHASE_LABELS[phase], label)
		self.step_status[key] = status
		self.query_one(DataTable).update_cell(
			self.step_keys[key],
			self.status_column,
			self._styled_status(status, cell_text),
			update_width=True,
		)

	@staticmethod
	def _download_count_text(details: dict[str, object]) -> str | None:
		"""Format the available and applicable download counts for one task row."""
		count = details.get("download_count")
		total = details.get("download_total")
		if not isinstance(count, int) or not isinstance(total, int):
			return None
		return f"{count} of {total}"

	@staticmethod
	def _question_count_text(details: dict[str, object]) -> tuple[str | None, bool]:
		"""Summarize actual BBQ records and flag outputs below their limit."""
		counts = details["question_counts"]
		if not isinstance(counts, list) or not counts:
			return None, False
		actual = sum(int(result["count"]) for result in counts)
		limits = [result["limit"] for result in counts]
		short = any(
			isinstance(limit, int) and int(result["count"]) < limit
			for result, limit in zip(counts, limits)
		)
		count_text = str(actual)
		if all(isinstance(limit, int) for limit in limits):
			count_text += f"/{sum(limits)}"
		count_text += " questions"
		if len(counts) > 1:
			count_text += f" ({len(counts)} BBQs)"
		return count_text, short

	def _complete_phase(self, phase: str, details: dict[str, object]) -> None:
		"""Record completed work and timing samples for one pipeline phase."""
		self.phase_completed[phase] = self.phase_completed.get(phase, 0) + 1
		if details.get("executed"):
			duration = float(details.get("duration", 0.0))
			if duration > 0.0:
				self.phase_samples.setdefault(phase, []).append(duration)

	def _clear_active_phase(self, phase: str) -> None:
		if self.active_phase == phase:
			self.active_phase = ""
			self.active_label = ""
			self.active_started_at = None
		self.update_metrics()

	def append_log(self, message: str) -> None:
		"""Append captured build output or a progress summary to the log."""
		self.log_lines.append(message)
		if len(self.log_lines) > 300:
			self.log_lines = self.log_lines[-300:]
		self.query_one(RichLog).write(Text.from_ansi(message))

	def update_metrics(self) -> None:
		"""Refresh elapsed time, progress counts, and the estimated local finish."""
		elapsed = time.time() - self.started_at
		completed = sum(self.phase_completed.values())
		planned = sum(self.phase_totals.values())
		if self.finished:
			result = "complete" if self.exit_code == 0 else "cancelled" if self.exit_code == 130 else "failed"
			current = f"\nResult: {result}"
		else:
			active = self.PHASE_LABELS.get(self.active_phase, "Preparing")
			current = f"\nCurrent: {active}"
			if self.active_label:
				current += f"\nItem: {self.active_label}"
		metrics = (
			f"Progress: {completed}/{planned or '...'} operations\n"
			f"Elapsed: {bbq_runner.format_elapsed_time(elapsed)}"
			f"{current}"
		)
		self.query_one("#metrics", Static).update(metrics)
		self._update_eta()

	def _update_metrics_text(self) -> None:
		self.update_metrics()

	def _update_eta(self) -> None:
		"""Estimate remaining time from completed phase timings and known work."""
		eta_widget = self.query_one("#eta", Static)
		if self.finished:
			if self.exit_code == 0:
				eta_widget.update("Build complete")
			elif self.exit_code == 130:
				eta_widget.update("Build cancelled")
			else:
				eta_widget.update("Build failed")
			return
		if self.active_phase and self.active_started_at is not None:
			phase_values = self.phase_samples.get(self.active_phase, [])
			active_elapsed = time.time() - self.active_started_at
			if not phase_values or active_elapsed >= sum(phase_values) / len(phase_values):
				elapsed_text = bbq_runner.format_elapsed_time(active_elapsed)
				eta_widget.update(f"Working: {self.PHASE_LABELS[self.active_phase]}\n{elapsed_text} on item")
				return
		samples = [duration for values in self.phase_samples.values() for duration in values]
		if len(samples) < 2:
			eta_widget.update("Estimating finish time...")
			return
		global_average = sum(samples) / len(samples)
		remaining = 0.0
		for phase, total in self.phase_totals.items():
			phase_remaining = max(total - self.phase_completed.get(phase, 0), 0)
			phase_values = self.phase_samples.get(phase, [])
			average = sum(phase_values) / len(phase_values) if phase_values else global_average
			remaining += phase_remaining * average
		if self.active_phase and self.active_started_at is not None:
			values = self.phase_samples.get(self.active_phase, [])
			active_average = sum(values) / len(values)
			active_elapsed = time.time() - self.active_started_at
			remaining = max(remaining - min(active_elapsed, active_average), 0.0)
		if (
			remaining < 1.0
			and sum(self.phase_completed.values()) < sum(self.phase_totals.values())
		):
			eta_widget.update("Finishing remaining work...")
			return
		finish_time = datetime.now().astimezone() + timedelta(seconds=remaining)
		clock_time = finish_time.strftime("%I:%M:%S %p").lstrip("0")
		remaining_text = bbq_runner.format_elapsed_time(remaining)
		eta_widget.update(f"Finish: {clock_time}\n~{remaining_text} left")

	def action_request_cancel(self) -> None:
		"""Ask before stopping, or close the completed dashboard."""
		if self.finished:
			self.exit(result=self.exit_code)
			return
		if self.cancel_dialog_open:
			return
		self.cancel_dialog_open = True
		self.push_screen(CancelBuildScreen(), self._cancel_confirmation_result)

	def _cancel_confirmation_result(self, confirmed: bool | None) -> None:
		self.cancel_dialog_open = False
		if not confirmed:
			return
		self.cancel_event.set()
		self.append_log("Cancellation requested; waiting for the active operation to finish.")
		self.query_one("#metrics", Static).update(
			"Stopping after the active operation finishes..."
		)
		self.query_one("#eta", Static).update("Cancellation requested")

	def _run_build(self) -> None:
		"""Run the coordinator once on a Textual worker thread."""
		log_stream = _BuildLogStream(self._report_log)
		try:
			with redirect_stdout(log_stream), redirect_stderr(log_stream):
				build_coordinator.build_site(self.scope, self.progress)
			log_stream.flush()
		except build_progress.BuildCancelledError:
			log_stream.flush()
			self.call_from_thread(self._finish_build, 130, "Build cancelled.")
		except Exception as error:
			log_stream.flush()
			self.call_from_thread(self._finish_build, 1, f"Build failed: {error}")
		else:
			self.call_from_thread(self._finish_build, 0, "Build completed successfully.")

	def _report_log(self, message: str) -> None:
		"""Forward captured terminal output through the progress event queue."""
		self._report_event("log", {"message": message})

	def _finish_build(self, exit_code: int, message: str) -> None:
		"""Display the final result and leave the dashboard open for review."""
		if exit_code == 0 and self.cancel_event.is_set():
			exit_code = 130
			message = "Build cancelled."
		self.finished = True
		self.exit_code = exit_code
		for key, status in list(self.step_status.items()):
			if status == "running" or (exit_code == 130 and status == "pending"):
				self.step_status[key] = "cancelled" if exit_code == 130 else "failed"
				self.query_one(DataTable).update_cell(
					self.step_keys[key], self.status_column,
					self._styled_status(self.step_status[key]),
					update_width=True,
				)
		self.active_phase = ""
		self.active_label = ""
		self.active_started_at = None
		self.append_log(message)
		self.update_metrics()
		self.query_one("#footer_note", Static).update("Press q to close")


#============================================
def run_app(scope: BuildScope) -> int:
	"""Run the full-build dashboard and return the coordinator result."""
	result = SiteBuildApp(scope).run()
	return result if isinstance(result, int) else 1

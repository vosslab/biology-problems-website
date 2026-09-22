"""Textual dashboard for interactive BBQ task execution."""

import argparse
import os
import time

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, RichLog, Static

from bioproblems_site.bbq_runner import (
	RunContext,
	build_command,
	format_elapsed_time,
	get_slowest_task_timings,
	run_task_capture,
	shorten_text,
)


class BBQTaskApp(App[None]):
	"""Run BBQ tasks while displaying progress in a Textual dashboard."""

	STATUS_STYLES = {
		"pending": "yellow",
		"running": "cyan",
		"ok": "green",
		"failed": "red",
	}

	CSS = (
		"#root { height: 1fr; }\n"
		"#top_row { height: 40%; min-height: 10; }\n"
		"#metrics_box { width: 30%; height: 1fr; border: solid gray; }\n"
		"#metrics_title { height: 1; }\n"
		"#metrics { height: 1fr; }\n"
		"#footer_note { height: 1; }\n"
		"#messages { width: 70%; height: 1fr; border: solid gray; }\n"
		"#task_table { height: 1fr; border: solid gray; }\n"
	)

	def __init__(
		self,
		tasks: list[dict[str, object]],
		args: argparse.Namespace,
		run_context: RunContext,
	) -> None:
		super().__init__()
		self.tasks = tasks
		self.args = args
		self.run_context = run_context
		self.total = len(tasks)
		self.start_time = time.time()
		self.completed = 0
		self.durations: list[float] = []
		self.timing_records: list[dict[str, object]] = []
		self.log_lines: list[str] = []
		self.task_rows: list[object] = []
		self.column_keys: dict[str, object] = {}

	def format_status(self, status: str) -> Text:
		style = self.STATUS_STYLES.get(status, "")
		return Text(status, style=style) if style else Text(status)

	def compose(self) -> ComposeResult:
		with Vertical(id="root"):
			with Horizontal(id="top_row"):
				with Vertical(id="metrics_box"):
					yield Static("BBQ Task Dashboard", id="metrics_title")
					yield Static("Ready", id="metrics")
					yield Static("Press q to quit", id="footer_note")
				yield RichLog(id="messages", wrap=True, highlight=False)
			table = DataTable(id="task_table", zebra_stripes=True)
			table.cursor_type = "row"
			self.task_rows = []
			self.column_keys = {
				"index": table.add_column("#"),
				"script": table.add_column("script"),
				"status": table.add_column("status"),
				"sec": table.add_column("sec"),
				"lines": table.add_column("lines"),
			}
			for index, task in enumerate(self.tasks, start=1):
				script_path = task.get("script", "")
				label = os.path.basename(script_path) if script_path else task_label(
					task, index, task.get("output", ""), build_command(task)
				)
				row_key = table.add_row(
					str(index),
					shorten_text(label, 120),
					self.format_status("pending"),
					"",
					"",
				)
				self.task_rows.append(row_key)
			yield table

	def on_mount(self) -> None:
		self.run_worker(self.run_tasks, exclusive=True)

	def append_log(self, message: str) -> None:
		self.log_lines.append(message)
		if len(self.log_lines) > 200:
			self.log_lines = self.log_lines[-200:]
		self.query_one(RichLog).write(message)

	def update_metrics(self) -> None:
		elapsed = time.time() - self.start_time
		average = sum(self.durations) / self.completed if self.completed else 0.0
		eta = average * (self.total - self.completed)
		metrics = (
			f"Completed: {self.completed}/{self.total}\n"
			f"Elapsed: {elapsed:.1f}s\n"
			f"ETA: {eta:.1f}s"
		)
		self.query_one("#metrics", Static).update(metrics)

	async def run_tasks(self) -> None:
		for index, task in enumerate(self.tasks, start=1):
			script_path = task.get("script", "")
			label = os.path.basename(script_path) if script_path else task_label(
				task, index, task.get("output", ""), build_command(task)
			)
			label = shorten_text(label, 44)
			table = self.query_one(DataTable)
			row_key = self.task_rows[index - 1]
			table.update_cell(row_key, self.column_keys["status"], self.format_status("running"))
			start = time.time()
			ok, stdout, stderr, line_count = await self.run_in_thread(task)
			duration = time.time() - start
			self.durations.append(duration)
			self.timing_records.append({
				"label": label,
				"elapsed_seconds": duration,
				"status": "DONE" if ok else "FAILED",
			})
			self.completed += 1
			status = "ok" if ok else "failed"
			table.update_cell(row_key, self.column_keys["status"], self.format_status(status))
			table.update_cell(row_key, self.column_keys["sec"], f"{duration:.1f}")
			table.update_cell(row_key, self.column_keys["lines"], str(line_count))
			self.append_log(f"{status.upper()} {label} ({duration:.1f}s, {line_count} lines)")
			if stdout:
				self.append_log(stdout.rstrip()[:2000])
			if stderr:
				self.append_log(stderr.rstrip()[:2000])
			self.update_metrics()
		slowest_records = get_slowest_task_timings(self.timing_records)
		for timing_record in slowest_records:
			self.append_log(
				f"{format_elapsed_time(timing_record['elapsed_seconds']):>10}  "
				f"{timing_record['label']} ({timing_record['status']})"
			)
		self.append_log("All tasks completed.")

	async def run_in_thread(self, task: dict[str, object]) -> tuple[object, ...]:
		worker = self.run_worker(
			lambda: run_task_capture(
				task,
				self.run_context.log_path,
				not self.args.dry_run,
				self.run_context.allow_cleanup,
				self.run_context.pythonpath_value,
				self.run_context.error_log_path,
			),
			thread=True,
			exclusive=False,
		)
		return await worker.wait()

	def on_key(self, event: object) -> None:
		if getattr(event, "key", "") == "q":
			self.exit()


def task_label(
	task: dict[str, object],
	index: int,
	output_path: str,
	command: list[str],
) -> str:
	"""Build the same fallback label used by the non-TUI runner."""
	from bioproblems_site.bbq_runner import task_label as runner_task_label

	return runner_task_label(task, index, output_path, command)


def run_app(
	tasks: list[dict[str, object]],
	args: argparse.Namespace,
	run_context: RunContext,
) -> int:
	"""Run the interactive task dashboard."""
	BBQTaskApp(tasks, args, run_context).run()
	return 0

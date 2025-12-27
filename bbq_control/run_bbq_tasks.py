#!/usr/bin/env python3

"""
Batch runner for BBQ-related scripts (CSV only).

Config format (CSV):
chapter,topic,output_file,script,flags
genetics,topic05,bbq-unique_gametes.txt,unique_gametes.py,"-n 5"
"""

import argparse
import csv
import datetime
import os
import random
import shlex
import shutil
import subprocess
import sys
import time

try:
	# PIP3 modules
	from textual.app import App, ComposeResult
	from textual.containers import Horizontal, Vertical
	from textual.widgets import DataTable, Footer, Header, RichLog, Static
	TEXTUAL_AVAILABLE = True
except ImportError:
	TEXTUAL_AVAILABLE = False

# ANSI colors for concise CLI feedback
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"


def color(text: str, code: str) -> str:
	return f"{code}{text}{COLOR_RESET}"


def get_repo_root() -> str:
	return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def normalize_path(path_value: str, repo_root: str) -> str:
	if not path_value:
		return ""
	path_value = os.path.expanduser(path_value)
	if not os.path.isabs(path_value):
		path_value = os.path.join(repo_root, path_value)
	return os.path.abspath(path_value)


def load_tasks(config_path: str) -> list:
	return load_tasks_csv(config_path)


def load_tasks_csv(config_path: str) -> list:
	tasks = []
	repo_root = get_repo_root()
	if not os.path.isfile(config_path):
		raise FileNotFoundError(f"Config file not found: {config_path}")
	with open(config_path, newline="") as fp:
		reader = csv.DictReader(fp)
		for row in reader:
			program = (row.get("program") or "python3").strip()
			script = (row.get("script") or "").strip()
			flags = (row.get("flags") or "").strip()
			output = (row.get("output") or "").strip()
			chapter = (row.get("chapter") or "").strip()
			topic = (row.get("topic") or "").strip()
			output_file = (row.get("output_file") or "").strip()
			if not script and not flags:
				continue
			script = normalize_path(script, repo_root)
			if not output and output_file:
				output_parts = [repo_root, "site_docs"]
				if chapter:
					output_parts.append(chapter)
				if topic:
					output_parts.append(topic)
				output_parts.append(output_file)
				output = os.path.join(*output_parts)
			output = normalize_path(output, repo_root)
			task = {
				"program": program or "python3",
				"script": script,
				"args": shlex.split(flags) if flags else [],
				"output": output,
			}
			tasks.append(task)
	return tasks


def ensure_parent_dir(path: str):
	parent = os.path.dirname(path)
	if parent and not os.path.isdir(parent):
		os.makedirs(parent, exist_ok=True)


def move_output_if_needed(output_path: str, workdir: str = ".") -> bool:
	"""If output_path does not exist, but the basename exists in workdir, move it."""
	if not output_path:
		return True
	if os.path.isfile(output_path):
		return True
	base = os.path.basename(output_path)
	if not base:
		return False
	candidate = os.path.join(workdir, base)
	if os.path.isfile(candidate):
		ensure_parent_dir(output_path)
		shutil.move(candidate, output_path)
		return True
	return False


def output_exists(output_path: str, workdir: str = ".") -> bool:
	if not output_path:
		return True
	if os.path.isfile(output_path):
		return True
	base = os.path.basename(output_path)
	if not base:
		return False
	candidate = os.path.join(workdir, base)
	return os.path.isfile(candidate)


def resolve_output_candidate(output_path: str, workdir: str = ".") -> str:
	if not output_path:
		return ""
	if os.path.isfile(output_path):
		return output_path
	base = os.path.basename(output_path)
	if not base:
		return ""
	candidate = os.path.join(workdir, base)
	if os.path.isfile(candidate):
		return candidate
	return ""


def count_output_lines(output_path: str, workdir: str = ".") -> int:
	candidate = resolve_output_candidate(output_path, workdir)
	if not candidate:
		return 0
	with open(candidate, "r") as file_handle:
		return sum(1 for _ in file_handle)


def log_line(log_path: str, message: str):
	ensure_parent_dir(log_path)
	timestamp = datetime.datetime.now().isoformat()
	with open(log_path, "a") as fp:
		fp.write(f"[{timestamp}] {message}\n")


def build_command(task: dict) -> list:
	# Simplest form: a single command string
	if "cmd" in task:
		cmd_value = task.get("cmd")
		if isinstance(cmd_value, str):
			parts = shlex.split(cmd_value)
		if isinstance(cmd_value, list):
			parts = [str(x) for x in cmd_value]
		else:
			parts = []
		if parts and parts[0].endswith(".py"):
			parts.insert(0, "python3")
		return parts
	program = task.get("program")
	if not program:
		program = "python3"
	script = task.get("script")
	args = task.get("args", [])
	cmd = [str(program)]
	if script:
		cmd.append(str(script))
	cmd.extend(str(a) for a in args)
	return cmd


def task_label(task: dict, index: int, output_path: str, cmd_list: list) -> str:
	if task.get("name"):
		return task.get("name")
	if task.get("script"):
		return os.path.basename(task["script"])
	if output_path:
		return os.path.basename(output_path)
	if "cmd" in task and isinstance(task["cmd"], str):
		return task["cmd"].split()[0]
	if cmd_list:
		return cmd_list[0]
	return f"Task {index}"


def shorten_text(text: str, max_len: int) -> str:
	if len(text) <= max_len:
		return text
	if max_len <= 3:
		return text[:max_len]
	return text[:max_len - 3] + "..."


def run_task_capture(task: dict, log_path: str, move_output: bool) -> tuple:
	output_path = task.get("output", "")
	workdir = "."
	cmd = build_command(task)

	log_line(log_path, f"CMD   {' '.join(cmd)} (cwd={workdir})")
	try:
		proc = subprocess.run(
			cmd,
			cwd=workdir,
			text=True,
			capture_output=True,
			check=False,
		)
	except Exception as exc:
		log_line(log_path, f"LAUNCH ERROR {exc}")
		return False, "", str(exc), 0

	if proc.stdout:
		log_line(log_path, f"STDOUT:\n{proc.stdout.rstrip()}")
	if proc.stderr:
		log_line(log_path, f"STDERR:\n{proc.stderr.rstrip()}")

	if proc.returncode != 0:
		log_line(log_path, f"EXIT -> {proc.returncode}")
		return False, proc.stdout, proc.stderr, 0

	if output_path:
		if move_output:
			moved_ok = move_output_if_needed(output_path, workdir)
			if not moved_ok:
				log_line(log_path, f"ERROR expected output not found: {output_path}")
				return False, proc.stdout, proc.stderr, 0
		else:
			if not output_exists(output_path, workdir):
				log_line(log_path, f"ERROR expected output not found: {output_path}")
				return False, proc.stdout, proc.stderr, 0

	line_count = count_output_lines(output_path, workdir)
	return True, proc.stdout, proc.stderr, line_count


def run_task(task: dict, log_path: str, index: int, total: int, move_output: bool = True):
	output_path = task.get("output", "")
	workdir = "."

	cmd = build_command(task)
	label = task_label(task, index, output_path, cmd)
	summary = f"[{index}/{total}] {label}"
	print(color(summary, COLOR_CYAN))
	log_line(log_path, f"START {summary} -> {output_path or 'N/A'}")
	log_line(log_path, f"CMD   {' '.join(cmd)} (cwd={workdir})")

	try:
		proc = subprocess.run(
			cmd,
			cwd=workdir,
			text=True,
			capture_output=True,
			check=False,
		)
	except Exception as exc:  # subprocess failure before execution
		print(color(f"FAILED to launch {label}: {exc}", COLOR_RED))
		log_line(log_path, f"LAUNCH ERROR {label}: {exc}")
		return False

	if proc.stdout:
		log_line(log_path, f"STDOUT {label}:\n{proc.stdout.rstrip()}")
	if proc.stderr:
		log_line(log_path, f"STDERR {label}:\n{proc.stderr.rstrip()}")

	if proc.returncode != 0:
		print(color(f"FAILED {label} (exit {proc.returncode})", COLOR_RED))
		log_line(log_path, f"EXIT {label} -> {proc.returncode}")
		return False

	# If the task specifies an output path and the script wrote to CWD, move it.
	if output_path:
		if move_output:
			moved_ok = move_output_if_needed(output_path, workdir)
			if moved_ok:
				if os.path.isfile(output_path):
					log_line(log_path, f"MOVED output to {output_path}")
			else:
				print(color(f"FAILED: expected output not found: {output_path}", COLOR_RED))
				log_line(log_path, f"ERROR: expected output not found: {output_path}")
				return False
		else:
			if not output_exists(output_path, workdir):
				print(color(f"FAILED: expected output not found: {output_path}", COLOR_RED))
				log_line(log_path, f"ERROR: expected output not found: {output_path}")
				return False
			log_line(log_path, f"SKIP MOVE {label} -> {output_path}")

	print(color(f"DONE  {label}", COLOR_GREEN))
	log_line(log_path, f"EXIT {label} -> 0")
	return True


if TEXTUAL_AVAILABLE:
	class BBQTaskApp(App):
		def __init__(self, tasks: list, args: argparse.Namespace) -> None:
			super().__init__()
			self.tasks = tasks
			self.args = args
			self.total = len(tasks)
			self.start_time = time.time()
			self.completed = 0
			self.durations = []
			self.log_lines = []
			self.task_rows = []

		CSS = (
			"#root { height: 1fr; }\n"
			"#top_row { height: 8; }\n"
			"#metrics_box { width: 30%; height: 8; border: solid gray; }\n"
			"#metrics_title { height: 1; }\n"
			"#metrics { height: 1fr; }\n"
			"#footer_note { height: 1; }\n"
			"#messages { width: 70%; height: 8; border: solid gray; }\n"
			"#task_table { height: 1fr; border: solid gray; }\n"
		)

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
				table.add_columns("#", "script", "status", "sec", "lines")
				for idx, task in enumerate(self.tasks, start=1):
					script_path = task.get("script", "")
					label = os.path.basename(script_path) if script_path else task_label(
						task, idx, task.get("output", ""), build_command(task)
					)
					label = shorten_text(label, 120)
					table.add_row(
						str(idx),
						label,
						"pending",
						"",
						"",
					)
					self.task_rows.append(idx - 1)
				yield table

		def on_mount(self) -> None:
			self.run_worker(self.run_tasks, exclusive=True)

		def append_log(self, message: str) -> None:
			self.log_lines.append(message)
			if len(self.log_lines) > 200:
				self.log_lines = self.log_lines[-200:]
			log_widget = self.query_one(RichLog)
			log_widget.write(message)

		def update_metrics(self) -> None:
			elapsed = time.time() - self.start_time
			if self.completed > 0:
				avg = sum(self.durations) / self.completed
				eta = avg * (self.total - self.completed)
			else:
				eta = 0.0
			metrics = (
				f"Completed: {self.completed}/{self.total}\n"
				f"Elapsed: {elapsed:.1f}s\n"
				f"ETA: {eta:.1f}s"
			)
			self.query_one("#metrics", Static).update(metrics)

		async def run_tasks(self) -> None:
			for idx, task in enumerate(self.tasks, start=1):
				script_path = task.get("script", "")
				label = os.path.basename(script_path) if script_path else task_label(
					task, idx, task.get("output", ""), build_command(task)
				)
				label = shorten_text(label, 44)
				table = self.query_one(DataTable)
				table.update_cell_at((self.task_rows[idx - 1], 2), "running")
				start = time.time()

				if self.args.print_only:
					cmd_text = " ".join(build_command(task))
					self.append_log(f"PRINT {label}: {cmd_text}")
					table.update_cell_at((self.task_rows[idx - 1], 2), "print-only")
					self.completed += 1
					self.durations.append(0.0)
					self.update_metrics()
					continue

				ok, stdout, stderr, line_count = await self.run_in_thread(task)
				duration = time.time() - start
				self.durations.append(duration)
				self.completed += 1

				status = "ok" if ok else "failed"
				table.update_cell_at((self.task_rows[idx - 1], 2), status)
				table.update_cell_at((self.task_rows[idx - 1], 3), f"{duration:.1f}")
				table.update_cell_at((self.task_rows[idx - 1], 4), str(line_count))
				self.append_log(f"{status.upper()} {label} ({duration:.1f}s, {line_count} lines)")
				if stdout:
					self.append_log(stdout.rstrip()[:2000])
				if stderr:
					self.append_log(stderr.rstrip()[:2000])
				self.update_metrics()

			self.append_log("All tasks completed.")

		async def run_in_thread(self, task: dict) -> tuple:
			worker = self.run_worker(
				lambda: run_task_capture(task, self.args.log, not self.args.dry_run),
				thread=True,
				exclusive=False
			)
			return await worker.wait()

		def on_key(self, event) -> None:
			if event.key == "q":
				self.exit()


def main():
	parser = argparse.ArgumentParser(description="Run BBQ generation tasks from YAML or CSV.")
	parser.add_argument(
		"-c",
		"--config",
		default="bbq_tasks.csv",
		help="Path to tasks YAML or CSV (default: bbq_tasks.csv)",
	)
	parser.add_argument(
		"-l",
		"--log",
		default="logs/bbq_generation.log",
		help="Path to append combined stdout/stderr logs.",
	)
	mode_group = parser.add_mutually_exclusive_group()
	mode_group.add_argument(
		"--dry-run",
		action="store_true",
		help="Run commands but do not move outputs.",
	)
	mode_group.add_argument(
		"--print-only",
		dest="print_only",
		action="store_true",
		help="Print planned commands without executing them.",
	)
	parser.add_argument(
		"--no-tui",
		dest="no_tui",
		action="store_true",
		help="Disable the Textual TUI interface.",
	)
	parser.add_argument(
		"--limit",
		type=int,
		dest="limit",
		default=None,
		help="Maximum number of tasks to run.",
	)
	parser.add_argument(
		"--seed",
		type=int,
		dest="seed",
		default=None,
		help="Random seed for shuffle mode.",
	)
	order_group = parser.add_mutually_exclusive_group()
	order_group.add_argument(
		"--shuffle",
		dest="shuffle",
		action="store_true",
		help="Randomize task order.",
	)
	order_group.add_argument(
		"--sort",
		dest="sort",
		action="store_true",
		help="Sort tasks by output path.",
	)
	args = parser.parse_args()

	tasks = load_tasks(args.config)
	if args.sort:
		tasks.sort(key=lambda item: item.get("output", ""))
	if args.shuffle:
		random_generator = random.Random(args.seed)
		random_generator.shuffle(tasks)
	if args.limit is not None:
		if args.limit <= 0:
			print(color("Limit must be a positive integer.", COLOR_RED))
			return 1
		tasks = tasks[:args.limit]

	total = len(tasks)
	if total == 0:
		print(color("No tasks found in config.", COLOR_YELLOW))
		return 0

	use_tui = TEXTUAL_AVAILABLE and not args.no_tui and sys.stdout.isatty()
	if use_tui:
		app = BBQTaskApp(tasks, args)
		app.run()
		return 0
	if not TEXTUAL_AVAILABLE and not args.no_tui:
		print(color("Textual is not installed; running in plain mode.", COLOR_YELLOW))

	log_line(args.log, f"=== RUN START ({total} tasks) ===")
	failures = 0

	for idx, task in enumerate(tasks, start=1):
		cmd = build_command(task)
		if args.print_only:
			print(color(f"[{idx}/{total}] DRY-RUN {' '.join(cmd)}", COLOR_CYAN))
			continue
		if args.dry_run:
			print(color(f"[{idx}/{total}] DRY-RUN {' '.join(cmd)}", COLOR_CYAN))
			ok = run_task(task, args.log, idx, total, move_output=False)
		else:
			ok = run_task(task, args.log, idx, total)
		if not ok:
			failures += 1

	log_line(args.log, f"=== RUN END (failures={failures}) ===")
	if failures:
		print(color(f"Completed with {failures} failure(s). See {args.log}", COLOR_RED))
		return 1
	print(color("All tasks completed successfully.", COLOR_GREEN))
	return 0


if __name__ == "__main__":
	sys.exit(main())

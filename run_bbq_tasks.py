#!/usr/bin/env python3

"""
Batch runner for BBQ-related scripts (CSV only).

Config format (CSV):
script,flags,output
~/nsh/biology-problems/inheritance-problems/unique_gametes.py,"-n 5 -x 3 --hint",docs/genetics/topic05/bbq-unique_gametes-with_hint-5_genes-questions.txt
	A 'program' column is optional; defaults to "python3".
"""

import argparse
import csv
import datetime
import os
import shlex
import shutil
import subprocess
import sys

# ANSI colors for concise CLI feedback
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"


def color(text: str, code: str) -> str:
	return f"{code}{text}{COLOR_RESET}"


def load_tasks(config_path: str) -> list:
	return load_tasks_csv(config_path)


def load_tasks_csv(config_path: str) -> list:
	tasks = []
	if not os.path.isfile(config_path):
		raise FileNotFoundError(f"Config file not found: {config_path}")
	with open(config_path, newline="") as fp:
		reader = csv.DictReader(fp)
		for row in reader:
			program = (row.get("program") or "python3").strip()
			script = (row.get("script") or "").strip()
			flags = (row.get("flags") or "").strip()
			output = (row.get("output") or "").strip()
			if not script and not flags:
				continue
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
	if output_path:
		return os.path.basename(output_path)
	if task.get("script"):
		return os.path.basename(task["script"])
	if "cmd" in task and isinstance(task["cmd"], str):
		return task["cmd"].split()[0]
	if cmd_list:
		return cmd_list[0]
	return f"Task {index}"


def run_task(task: dict, log_path: str, index: int, total: int):
	output_path = task.get("output", "")
	workdir = "."

	cmd = build_command(task)
	label = task_label(task, index, output_path, cmd)
	summary = f"[{index}/{total}] {label} -> {output_path or 'N/A'}"
	print(color(summary, COLOR_CYAN))
	log_line(log_path, f"START {summary}")
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
		if move_output_if_needed(output_path, workdir):
			if os.path.isfile(output_path):
				log_line(log_path, f"MOVED output to {output_path}")
		else:
			print(color(f"WARNING: expected output not found: {output_path}", COLOR_YELLOW))
			log_line(log_path, f"WARNING: expected output not found: {output_path}")

	print(color(f"DONE  {label}", COLOR_GREEN))
	log_line(log_path, f"EXIT {label} -> 0")
	return True


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
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Print planned commands without executing them.",
	)
	args = parser.parse_args()

	tasks = load_tasks(args.config)
	total = len(tasks)
	if total == 0:
		print(color("No tasks found in config.", COLOR_YELLOW))
		return 0

	log_line(args.log, f"=== RUN START ({total} tasks) ===")
	failures = 0

	for idx, task in enumerate(tasks, start=1):
		cmd = build_command(task)
		if args.dry_run:
			print(color(f"[{idx}/{total}] DRY-RUN {' '.join(cmd)}", COLOR_CYAN))
			continue
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

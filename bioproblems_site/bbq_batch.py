"""Batch orchestration for the repository's BBQ task CSV files."""

import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

from bioproblems_site.bbq_config import find_settings_yaml
from bioproblems_site.git_paths import get_repo_root


TASK_TIMING_LOG_ENV = "BBQ_TASK_TIMING_LOG"


def find_task_files(task_dir: Path) -> list[Path]:
	"""Return regular task CSV files in deterministic filename order."""
	return sorted(path for path in task_dir.glob("*.csv") if path.is_file())


def build_runner_command(
	repo_root: Path,
	settings_path: Path,
	task_file: Path,
	args: object,
) -> list[str]:
	"""Build the single-CSV application command used by the batch runner."""
	max_questions = args.max_questions if args.max_questions is not None else 199
	command = [
		sys.executable,
		str(repo_root / "build_site.py"),
		"--max-questions", str(max_questions),
		"--tasks", str(task_file),
	]
	if args.limit is not None:
		command.extend(["--limit", str(args.limit)])
	if args.dry_run:
		command.append("--dry-run")
	return command


def format_elapsed_time(elapsed_seconds: float) -> str:
	"""Format one task duration for concise terminal output."""
	if elapsed_seconds < 60:
		return f"{elapsed_seconds:.2f}s"
	minutes = int(elapsed_seconds // 60)
	seconds = elapsed_seconds % 60
	return f"{minutes}m {seconds:05.2f}s"


def print_slowest_task_timings(timing_log_path: Path) -> None:
	"""Print the ten slowest tasks recorded across the batch."""
	if not timing_log_path.is_file():
		return
	with timing_log_path.open() as timing_handle:
		timing_records = [
			json.loads(line)
			for line in timing_handle
			if line.strip()
		]
	if not timing_records:
		return
	slowest_records = sorted(
		timing_records,
		key=lambda record: record["elapsed_seconds"],
		reverse=True,
	)[:10]
	print("=" * 54)
	print(f"Slowest {len(slowest_records)} tasks across all task CSV files")
	print("=" * 54)
	for timing_record in slowest_records:
		duration = format_elapsed_time(timing_record["elapsed_seconds"])
		print(
			f"{duration:>10}  {timing_record['task_file']}: "
			f"{timing_record['label']} ({timing_record['status']})"
		)


def run_task_file(
	repo_root: Path,
	source_me_path: Path,
	settings_path: Path,
	task_file: Path,
	timing_log_path: Path,
	args: object,
) -> int:
	"""Run one CSV after loading the repository shell environment."""
	command = build_runner_command(repo_root, settings_path, task_file, args)
	shell_command = (
		f"source {shlex.quote(str(source_me_path))} && "
		f"{TASK_TIMING_LOG_ENV}={shlex.quote(str(timing_log_path))} "
		f"exec {shlex.join(command)}"
	)
	result = subprocess.run(
		["bash", "-c", shell_command],
		cwd=repo_root,
		check=False,
	)
	return result.returncode


def _resolve_paths(args: object) -> tuple[Path, Path, Path, list[Path]]:
	repo_root = Path(get_repo_root())
	task_files = find_task_files(repo_root / "task_files")
	settings_text = find_settings_yaml(args.settings_yaml)
	settings_path = Path(settings_text) if settings_text else repo_root / "bbq_settings.yml"
	return repo_root, repo_root / "source_me.sh", settings_path, task_files


def list_task_files() -> int:
	"""Print the repository-relative task CSV paths."""
	repo_root = Path(get_repo_root())
	task_files = find_task_files(repo_root / "task_files")
	print(f"{len(task_files)} task CSV file(s):")
	for task_file in task_files:
		print(task_file.relative_to(repo_root))
	return 0


def run_all_task_files(args: object) -> int:
	"""Run each task CSV and return one batch-level exit status."""
	args.max_questions = args.max_questions if args.max_questions is not None else 199
	repo_root, source_me_path, settings_path, task_files = _resolve_paths(args)
	if not task_files:
		print(f"No task CSV files found in {repo_root / 'task_files'}")
		return 1
	required_paths = (
		repo_root / "build_site.py",
		repo_root / "topics_metadata.yml",
		settings_path,
		source_me_path,
	)
	missing_paths = [path for path in required_paths if not path.is_file()]
	if missing_paths:
		for path in missing_paths:
			print(f"Required file not found: {path}")
		return 1
	failures: list[Path] = []
	with tempfile.TemporaryDirectory(prefix="bbq-task-timings-") as temp_dir:
		timing_log_path = Path(temp_dir) / "task_timings.jsonl"
		for index, task_file in enumerate(task_files, start=1):
			relative_path = task_file.relative_to(repo_root)
			print("=" * 54)
			print(f"[{index}/{len(task_files)}] {relative_path}")
			print("=" * 54)
			return_code = run_task_file(
				repo_root,
				source_me_path,
				settings_path,
				task_file,
				timing_log_path,
				args,
			)
			if return_code:
				failures.append(relative_path)
		print_slowest_task_timings(timing_log_path)
	if failures:
		print(f"Completed with failures in {len(failures)} task CSV file(s):")
		for task_file in failures:
			print(task_file)
		return 1
	print(f"Completed all {len(task_files)} task CSV files.")
	return 0

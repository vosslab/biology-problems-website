#!/opt/homebrew/opt/python@3.12/bin/python3.12
"""Run every BBQ task CSV from the repository root."""

# Standard Library
import argparse
from pathlib import Path
import shlex
import subprocess


PYTHON312 = Path("/opt/homebrew/opt/python@3.12/bin/python3.12")


#============================================
def get_repo_root() -> Path:
	"""Return the repository root regardless of the caller's directory."""
	output = subprocess.check_output(
		["git", "rev-parse", "--show-toplevel"],
		cwd=Path(__file__).resolve().parent,
		text=True,
	)
	return Path(output.strip())


#============================================
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	"""Parse batch-runner options."""
	parser = argparse.ArgumentParser(
		description="Run every CSV in bbq_control/task_files from the repository root."
	)
	parser.add_argument(
		"--list", action="store_true",
		help="List the discovered task CSV files without running generators.",
	)
	parser.add_argument(
		"-x", "--max-questions", type=int, default=199,
		help="Pass --max-questions to each task runner (default: 199).",
	)
	parser.add_argument(
		"-l", "--limit", type=int,
		help="Limit each CSV run to this many task rows.",
	)
	parser.add_argument(
		"--no-shuffle", action="store_true",
		help="Keep each CSV's source order instead of shuffling its task rows.",
	)
	args = parser.parse_args(argv)
	if args.max_questions <= 0:
		parser.error("--max-questions must be positive")
	if args.limit is not None and args.limit <= 0:
		parser.error("--limit must be positive")
	return args


#============================================
def find_task_files(task_dir: Path) -> list[Path]:
	"""Return regular task CSV files in deterministic filename order."""
	return sorted(path for path in task_dir.glob("*.csv") if path.is_file())


#============================================
def build_runner_command(
	repo_root: Path,
	settings_path: Path,
	task_file: Path,
	args: argparse.Namespace,
) -> list[str]:
	"""Build one root-anchored run_bbq_tasks.py command."""
	command = [
		str(PYTHON312),
		str(repo_root / "run_bbq_tasks.py"),
		"--flat",
		"--max-questions", str(args.max_questions),
		"--settings", str(settings_path),
		"--tasks", str(task_file),
	]
	if not args.no_shuffle:
		command.append("--shuffle")
	if args.limit is not None:
		command.extend(["--limit", str(args.limit)])
	return command


#============================================
def run_task_file(
	repo_root: Path,
	source_me_path: Path,
	settings_path: Path,
	task_file: Path,
	args: argparse.Namespace,
) -> int:
	"""Run one CSV after loading the repository's shell environment."""
	command = build_runner_command(repo_root, settings_path, task_file, args)
	shell_command = (
		f"source {shlex.quote(str(source_me_path))} && exec {shlex.join(command)}"
	)
	result = subprocess.run(
		["bash", "-c", shell_command],
		cwd=repo_root,
		check=False,
	)
	return result.returncode


#============================================
def main(argv: list[str] | None = None) -> int:
	"""Run each configured CSV and return one batch-level exit code."""
	args = parse_args(argv)
	repo_root = get_repo_root()
	control_dir = repo_root / "bbq_control"
	task_dir = control_dir / "task_files"
	task_files = find_task_files(task_dir)
	if not task_files:
		print(f"No task CSV files found in {task_dir}")
		return 1
	if args.list:
		print(f"{len(task_files)} task CSV file(s):")
		for task_file in task_files:
			print(task_file.relative_to(repo_root))
		return 0

	settings_path = control_dir / "bbq_settings.yml"
	source_me_path = repo_root / "source_me.sh"
	required_paths = (
		PYTHON312,
		repo_root / "run_bbq_tasks.py",
		repo_root / "topics_metadata.yml",
		settings_path,
		source_me_path,
	)
	missing_paths = [path for path in required_paths if not path.is_file()]
	if missing_paths:
		for path in missing_paths:
			print(f"Required file not found: {path}")
		return 1

	failures = []
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
			args,
		)
		if return_code != 0:
			failures.append(relative_path)

	if failures:
		print(f"Completed with failures in {len(failures)} task CSV file(s):")
		for task_file in failures:
			print(task_file)
		return 1
	print(f"Completed all {len(task_files)} task CSV files.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

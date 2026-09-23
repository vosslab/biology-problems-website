"""Output detection, movement, cleanup, and logging for BBQ tasks."""

import datetime
import errno
import os
import re
import shutil
import tempfile


def ensure_parent_dir(path: str) -> None:
	parent = os.path.dirname(path)
	if parent and not os.path.isdir(parent):
		os.makedirs(parent, exist_ok=True)


#============================================
class OutputRollback:
	"""Restore configured BBQ outputs when a generator fails validation."""

	def __init__(self, task: dict[str, object]) -> None:
		output_value = task.get("output", "")
		if isinstance(output_value, str) and output_value:
			output_paths = [output_value]
		else:
			output_dir = task.get("output_dir", "")
			prefixes, suffixes = build_output_patterns(task)
			if not isinstance(output_dir, str) or not output_dir:
				output_paths = []
			else:
				output_paths = [
					os.path.join(output_dir, f"{prefix}{suffix}")
					for prefix in prefixes
					for suffix in suffixes
				]
		self.output_paths = sorted({os.path.abspath(path) for path in output_paths})
		self.backups: dict[str, str] = {}
		self.original_signatures: dict[str, tuple[int, int, int]] = {}
		for output_path in self.output_paths:
			if not os.path.isfile(output_path):
				continue
			output_stat = os.stat(output_path)
			parent_directory = os.path.dirname(output_path)
			file_descriptor, backup_path = tempfile.mkstemp(
				prefix=".bbq-rollback-",
				dir=parent_directory,
			)
			os.close(file_descriptor)
			try:
				shutil.copy2(output_path, backup_path)
			except OSError:
				if os.path.isfile(backup_path):
					os.remove(backup_path)
				raise
			self.backups[output_path] = backup_path
			self.original_signatures[output_path] = (
				output_stat.st_mtime_ns,
				output_stat.st_size,
				output_stat.st_ino,
			)

	def finish(self, keep_output: bool) -> None:
		"""Keep a validated output or restore every prior configured artifact."""
		for output_path in self.output_paths:
			backup_path = self.backups.get(output_path, "")
			if keep_output:
				if backup_path:
					os.remove(backup_path)
					self.backups.pop(output_path)
				continue
			if backup_path:
				try:
					output_stat = os.stat(output_path)
				except FileNotFoundError:
					output_stat = None
				if output_stat is not None and (
					output_stat.st_mtime_ns,
					output_stat.st_size,
					output_stat.st_ino,
				) == self.original_signatures[output_path]:
					os.remove(backup_path)
					self.backups.pop(output_path)
					continue
				os.replace(backup_path, output_path)
				self.backups.pop(output_path)
			elif os.path.isfile(output_path):
				os.remove(output_path)


#============================================
def replace_output_with_candidate(candidate_path: str, output_path: str) -> bool:
	"""Replace an output only after its complete candidate is available."""
	if not candidate_path or not output_path:
		return False
	if os.path.abspath(candidate_path) == os.path.abspath(output_path):
		return True
	ensure_parent_dir(output_path)
	try:
		os.replace(candidate_path, output_path)
		return True
	except OSError as error:
		if error.errno != errno.EXDEV:
			raise

	# Keep the destination intact until a cross-volume copy is complete.
	output_directory = os.path.dirname(os.path.abspath(output_path))
	file_descriptor, temporary_path = tempfile.mkstemp(
		prefix=".bbq-output-",
		dir=output_directory,
	)
	os.close(file_descriptor)
	try:
		shutil.copy2(candidate_path, temporary_path)
		os.replace(temporary_path, output_path)
		os.remove(candidate_path)
	finally:
		if os.path.exists(temporary_path):
			os.remove(temporary_path)
	return True


def output_exists(output_path: str, workdir: str = ".") -> bool:
	if not output_path:
		return True
	if os.path.isfile(output_path):
		return True
	base = os.path.basename(output_path)
	return bool(base and os.path.isfile(os.path.join(workdir, base)))


def resolve_output_candidate(output_path: str, workdir: str = ".") -> str:
	if not output_path:
		return ""
	if os.path.isfile(output_path):
		return output_path
	base = os.path.basename(output_path)
	if not base:
		return ""
	candidate = os.path.join(workdir, base)
	return candidate if os.path.isfile(candidate) else ""


def resolve_output_workdir(output_path: str, workdir: str = ".") -> str:
	if not output_path:
		return ""
	base = os.path.basename(output_path)
	if not base:
		return ""
	candidate = os.path.join(workdir, base)
	return candidate if os.path.isfile(candidate) else ""


def resolve_output_workdir_recent(
	output_path: str,
	workdir: str,
	start_time: float,
) -> str:
	candidate = resolve_output_workdir(output_path, workdir)
	if not candidate:
		return ""
	return candidate if os.path.getmtime(candidate) >= (start_time - 2.0) else ""


def build_output_patterns(task: dict[str, object]) -> tuple[list[str], tuple[str, ...]]:
	script_path = task.get("script", "") if isinstance(task, dict) else ""
	script_basename = os.path.splitext(os.path.basename(script_path))[0]
	if not script_basename:
		return [], ("-problems.txt",)
	prefixes = [f"bbq-{script_basename}"]
	input_path = task.get("input_path", "") if isinstance(task, dict) else ""
	input_basename = os.path.splitext(os.path.basename(input_path))[0] if input_path else ""
	if input_basename:
		if script_basename == "yaml_match_to_bbq":
			prefixes.append(f"bbq-MATCH-{input_basename}")
		elif script_basename == "yaml_which_one_mc_to_bbq":
			prefixes.extend((f"bbq-MC-{input_basename}", f"bbq-WOMC-{input_basename}"))
		elif script_basename == "yaml_mc_statements_to_bbq":
			prefixes.append(f"bbq-TFMS-{input_basename}")
	return prefixes, ("-problems.txt", "-questions.txt")


def find_recent_outputs(
	workdir: str,
	start_time: float,
	prefixes: list[str],
	suffixes: tuple[str, ...],
) -> list[str]:
	candidates: list[tuple[float, str]] = []
	if not workdir or not os.path.isdir(workdir) or not prefixes:
		return []
	for entry in os.scandir(workdir):
		if not entry.is_file():
			continue
		if not any(entry.name.startswith(prefix) for prefix in prefixes):
			continue
		if suffixes and not any(entry.name.endswith(suffix) for suffix in suffixes):
			continue
		try:
			mtime = entry.stat().st_mtime
		except OSError:
			continue
		if mtime >= (start_time - 2.0):
			candidates.append((mtime, entry.path))
	candidates.sort(key=lambda item: item[0], reverse=True)
	return [path for _, path in candidates]


def select_closest_output_candidate(candidates: list[str], prefixes: list[str]) -> str:
	if not candidates or not prefixes:
		return ""
	best_path = ""
	best_score = 0.0
	for candidate_path in candidates:
		candidate_name = os.path.basename(candidate_path).lower()
		candidate_tokens = set(re.findall(r"[a-z0-9]+", candidate_name))
		for prefix in prefixes:
			prefix_text = str(prefix).lower()
			score = 1.0 if candidate_name.startswith(prefix_text) else 0.0
			prefix_tokens = set(re.findall(r"[a-z0-9]+", prefix_text))
			if not score and prefix_tokens:
				score = len(candidate_tokens.intersection(prefix_tokens)) / len(prefix_tokens)
			if score > best_score:
				best_score = score
				best_path = candidate_path
	return best_path if best_score >= 0.5 else ""


def resolve_generated_output(
	task: dict[str, object],
	workdir: str,
	start_time: float,
) -> tuple[bool, str, str, str]:
	output_dir = (task.get("output_dir") or "").strip()
	script_path = task.get("script", "")
	if not script_path:
		return False, "", "", "Missing script path for output detection."
	prefixes, suffixes = build_output_patterns(task)
	if not prefixes:
		return False, "", "", "Missing script basename for output detection."
	candidates = find_recent_outputs(workdir, start_time, prefixes, suffixes)
	if not candidates:
		recent_candidates = find_recent_outputs(workdir, start_time, ["bbq-"], suffixes)
		fallback_candidate = select_closest_output_candidate(recent_candidates, prefixes)
		if not fallback_candidate:
			return False, "", "", "Expected output not found in workdir."
		candidates = [fallback_candidate]
	if len(candidates) > 1:
		names = ", ".join(os.path.basename(path) for path in candidates)
		return False, "", "", f"Multiple outputs found in {workdir}: {names}"
	candidate = candidates[0]
	output_path = os.path.join(output_dir, os.path.basename(candidate)) if output_dir else candidate
	return True, output_path, candidate, ""


def move_output_candidate(candidate: str, output_path: str) -> bool:
	if not candidate or not output_path:
		return False
	return replace_output_with_candidate(candidate, output_path)


def count_output_lines(output_path: str, workdir: str = ".") -> int:
	return count_output_lines_path(resolve_output_candidate(output_path, workdir))


def count_output_lines_path(path: str) -> int:
	if not path:
		return 0
	with open(path, "r") as file_handle:
		return sum(1 for _ in file_handle)


def cleanup_dry_run_output(path: str, log_path: str) -> None:
	if not path:
		return
	base = os.path.basename(path)
	if not base.startswith("bbq") or not base.endswith(".txt"):
		return
	if os.path.isfile(path):
		os.remove(path)
		log_line(log_path, f"CLEANUP removed {path}")


def log_line(log_path: str, message: str) -> None:
	ensure_parent_dir(log_path)
	timestamp = datetime.datetime.now().isoformat()
	with open(log_path, "a") as file_handle:
		file_handle.write(f"[{timestamp}] {message}\n")


def log_error(
	log_path: str,
	label: str,
	message: str,
	stdout_text: str = "",
	stderr_text: str = "",
	cmd_list: list[str] | None = None,
) -> None:
	if not log_path:
		return
	ensure_parent_dir(log_path)
	timestamp = datetime.datetime.now().isoformat()
	with open(log_path, "a") as file_handle:
		file_handle.write(f"[{timestamp}] {label}: {message}\n")
		if cmd_list:
			file_handle.write(f"CMD: {' '.join(str(part) for part in cmd_list)}\n")
		if stdout_text:
			file_handle.write("STDOUT:\n")
			file_handle.write(stdout_text.rstrip() + "\n")
		if stderr_text:
			file_handle.write("STDERR:\n")
			file_handle.write(stderr_text.rstrip() + "\n")
		file_handle.write("\n")


def start_run_log(log_path: str) -> None:
	"""Start one fresh run log and remove numbered backups from older runs."""
	if not log_path:
		return
	ensure_parent_dir(log_path)
	log_directory = os.path.dirname(log_path) or "."
	backup_prefix = os.path.basename(log_path) + "."
	try:
		filenames = os.listdir(log_directory)
	except OSError as exc:
		print(f"WARNING: could not inspect old log backups in {log_directory}: {exc}")
		filenames = []
	for filename in filenames:
		if not filename.startswith(backup_prefix):
			continue
		if not re.fullmatch(r"[0-9]+", filename[len(backup_prefix):]):
			continue
		backup_path = os.path.join(log_directory, filename)
		if not os.path.isfile(backup_path):
			continue
		try:
			os.remove(backup_path)
		except OSError as exc:
			print(f"WARNING: could not remove old log backup {backup_path}: {exc}")
	with open(log_path, "w") as file_handle:
		file_handle.write("")

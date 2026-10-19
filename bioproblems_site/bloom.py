"""Backend-only JEV classification with persistent filename identity and explicit refresh."""

# Standard Library
import json
import math
import time
import random
import datetime
import urllib.error
import urllib.request
from pathlib import Path

# PIP3 modules
import yaml

# local repo modules
import bioproblems_site.bloom_rubric as rubric
import bioproblems_site.bloom_evidence as evidence
import bioproblems_site.file_write as file_write


CACHE_NAME = "problem_set_bloom.yml"


#============================================
class ClassificationError(ValueError):
	"""An external classification failed; keep the site's existing metadata."""


#============================================
class _NoRedirect(urllib.request.HTTPRedirectHandler):
	"""Keep the bearer credential at the fixed API endpoint."""

	def redirect_request(self, req: object, fp: object, code: int, msg: str,
			headers: object, newurl: str) -> None:
		return None


#============================================
def pair(record: dict) -> tuple[str, str]:
	"""Reject partial/unknown pairs at the persistence boundary."""
	cognitive = record.get("cognitive")
	knowledge = record.get("knowledge")
	if cognitive not in rubric.COGNITIVE or knowledge not in rubric.KNOWLEDGE:
		raise ClassificationError("Bloom metadata requires one complete valid pair")
	return cognitive, knowledge


#============================================
def load(root: Path) -> dict:
	"""Read editable metadata without reclassifying existing filenames."""
	path = root / CACHE_NAME
	if not path.exists():
		return {}
	payload = yaml.safe_load(path.read_text(encoding="utf-8"))
	if not isinstance(payload, dict):
		raise ClassificationError("Bloom cache must be a filename mapping")
	records = {}
	for name, value in payload.items():
		if not isinstance(name, str) or Path(name).name != name or not isinstance(value, str):
			raise ClassificationError("Invalid Bloom cache entry")
		parts = [part.strip() for part in value.split(",")]
		if len(parts) != 2:
			raise ClassificationError("Bloom values must be Cognitive, Knowledge")
		record = {"cognitive": parts[0], "knowledge": parts[1]}
		pair(record)
		records[name] = record
	return records


#============================================
def save(root: Path, records: dict) -> None:
	"""Persist completed banks incrementally so interrupted runs can resume."""
	compact = {name: ", ".join(pair(record)) for name, record in records.items()}
	text = yaml.safe_dump(compact, sort_keys=True, allow_unicode=False, width=1000)
	file_write.write_text(root / CACHE_NAME, text)


#============================================
def experiments(root: Path) -> dict:
	"""Read optional untracked diagnostics; these never determine displayed labels."""
	path = root / "LOCAL_ONLY/bloom_metadata.json"
	result = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
	return result


#============================================
def request(state: dict, key: str) -> tuple[dict, dict]:
	"""Return sanitized response metadata and the exact credential-free request."""
	payload = {"model": rubric.MODEL, "state": state, "questions": rubric.questions()}
	body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
	# ASVS 12.2.1, 13.3.1: verified HTTPS, no redirects, no key in logs/artifacts.
	req = urllib.request.Request(
		"https://api.typesafe.ai/v1/systemone", data=body,
		headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
	)
	opener = urllib.request.build_opener(_NoRedirect())
	for attempt in range(3):
		time.sleep(random.random() + attempt * 2)
		try:
			response = opener.open(req, timeout=60)  # nosec B310: fixed HTTPS endpoint
		except urllib.error.HTTPError as error:
			if error.code in (429, 500, 502, 503, 504) and attempt < 2:
				error.close()
				continue
			status = error.code
			error.close()
			raise ClassificationError(f"JEV HTTP {status}") from None
		except (urllib.error.URLError, TimeoutError):
			if attempt < 2:
				continue
			raise ClassificationError("JEV connection failed after retries") from None
		with response:
			try:
				result = json.load(response)
			except (ValueError, UnicodeError):
				raise ClassificationError("JEV returned invalid JSON") from None
		return validate_response(result), payload
	raise ClassificationError("JEV request did not complete")


#============================================
def validate_response(result: object) -> dict:
	"""Accept a complete pair and finite distributions, never a partial assignment."""
	if not isinstance(result, dict) or not isinstance(result.get("answers"), dict):
		raise ClassificationError("JEV response has no answers")
	record = {"model": rubric.MODEL, "rubric_version": rubric.VERSION, "probabilities": {}}
	for dimension, criteria in (("cognitive", rubric.COGNITIVE), ("knowledge", rubric.KNOWLEDGE)):
		answer = result["answers"].get(dimension)
		if not isinstance(answer, dict) or answer.get("choice") not in criteria:
			raise ClassificationError("JEV response has an invalid or missing choice")
		probabilities = answer.get("probabilities")
		if not isinstance(probabilities, dict) or set(probabilities) != set(criteria):
			raise ClassificationError("JEV response has incomplete probabilities")
		if any(not isinstance(p, (float, int)) or not math.isfinite(p) or not 0 <= p <= 1
				for p in probabilities.values()):
			raise ClassificationError("JEV response has invalid probabilities")
		if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=0.02):
			raise ClassificationError("JEV probabilities do not sum to one")
		record[dimension] = answer["choice"]
		record["probabilities"][dimension] = probabilities
	return record


#============================================
def classify(root: Path, refresh: set[str] | None = None, dry_run: bool = False,
		sample_count: int = 5) -> set[str]:
	"""Classify missing filenames, or explicitly selected names, in the visible corpus."""
	records = load(root)
	sources = {entry.source_path.name: entry.source_path for entry in evidence.entries(root)}
	names = sorted(name for name in sources if name not in records or (refresh and name in refresh))
	if not names or dry_run:
		return set()
	key_path = Path.home() / ".config/jev/jev-api-key.txt"
	if not key_path.is_file():
		print(f"Bloom: {len(names)} banks pending; configure ~/.config/jev/jev-api-key.txt")
		return set()
	key = key_path.read_text(encoding="utf-8").strip()
	if not key or any(char.isspace() for char in key):
		print("Bloom: API key file is empty or contains whitespace; metadata preserved")
		return set()
	diagnostics = experiments(root)
	mapping = evidence.yaml_sources(root)
	run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
	archive = root / "LOCAL_ONLY/bloom_runs" / (run_id + ".jsonl")
	archive.parent.mkdir(parents=True, exist_ok=True)
	changed = set()
	with archive.open("x", encoding="utf-8") as stream:
		for index, name in enumerate(names, 1):
			try:
				state = evidence.build(sources[name], mapping, sample_count)
			except (OSError, ValueError, yaml.YAMLError) as error:
				print(f"Bloom [{index}/{len(names)}] {name}: evidence unavailable ({type(error).__name__})")
				stream.write(json.dumps({"filename": name, "error": "evidence unavailable"}) + "\n")
				continue
			try:
				record, payload = request(state, key)
			except ClassificationError as error:
				print(f"Bloom [{index}/{len(names)}] {name}: {error}")
				stream.write(json.dumps({"filename": name, "error": str(error)}) + "\n")
				continue
			record.update({"run": run_id, "evidence_kind": state["evidence_kind"]})
			stream.write(json.dumps({"request": payload, "result": record}) + "\n")
			stream.flush()
			records[name] = record
			save(root, records)
			diagnostics[name] = record
			file_write.write_text(root / "LOCAL_ONLY/bloom_metadata.json",
				json.dumps(diagnostics, indent=2) + "\n")
			changed.add(name)
			print(f"Bloom [{index}/{len(names)}] {name}: {record['cognitive']} / {record['knowledge']}")
	return changed

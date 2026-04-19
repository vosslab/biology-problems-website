"""Topic directory scanner.

Derives generation-time facts about each topic:
  - question count (len of bbq-*-questions.txt)
  - set of download formats present

Pure filesystem inspection. No HTML concerns; those live in
bioproblems_site.download_buttons. No metadata concerns; those live in
bioproblems_site.metadata.
"""

# Standard Library
import os
import glob
import dataclasses

# local repo modules
import bioproblems_site.formats as formats

#============================================
@dataclasses.dataclass(frozen=True)
class TopicScan:
	questions: int
	formats: frozenset


#============================================
def _detect_formats(topic_dir: str) -> frozenset:
	"""Return the set of format keys present in a topic directory.

	Discovery is based on formats.FORMAT_FILE_SUFFIXES. A format counts
	as present if at least one file matching its suffix exists in
	topic_dir or topic_dir/downloads.
	"""
	found = set()
	downloads_dir = os.path.join(topic_dir, "downloads")
	search_dirs = [topic_dir]
	if os.path.isdir(downloads_dir):
		search_dirs.append(downloads_dir)
	for key in formats.FORMAT_KEYS:
		suffix = formats.FORMAT_FILE_SUFFIXES[key]
		for directory in search_dirs:
			pattern = os.path.join(directory, f"*{suffix}")
			if glob.glob(pattern):
				found.add(key)
				break
	return frozenset(found)


#============================================
def scan_topic(topic_dir: str) -> TopicScan:
	"""Inspect a topic directory. Returns TopicScan.

	Missing directory returns TopicScan(questions=0, formats=frozenset()).
	"""
	if not os.path.isdir(topic_dir):
		return TopicScan(questions=0, formats=frozenset())
	bbq_files = glob.glob(os.path.join(topic_dir, "bbq-*-questions.txt"))
	question_count = len(bbq_files)
	format_set = _detect_formats(topic_dir)
	return TopicScan(questions=question_count, formats=format_set)


def scan_subject(site_docs_dir: str, subject_key: str, topic_keys: tuple) -> dict:
	"""Scan every topic folder for a subject. Returns {topic_key: TopicScan}.

	topic_keys drives the iteration (comes from YAML metadata); folders
	not in topic_keys are ignored so an orphaned directory does not
	produce a link in the generated index.
	"""
	subject_dir = os.path.join(site_docs_dir, subject_key)
	result = {}
	for key in topic_keys:
		topic_dir = os.path.join(subject_dir, key)
		result[key] = scan_topic(topic_dir)
	return result

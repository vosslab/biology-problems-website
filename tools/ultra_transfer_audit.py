#!/usr/bin/env python3
"""Audit BBQ question corpus for features that Blackboard Ultra's HTML sanitizer degrades.

Scans every site_docs/**/bbq-*.txt file and classifies each question line for:
  - text_color: inline color: value that is NOT black/inherit/currentcolor
  - bg_color: presence of background-color or bgcolor= (any value)
  - color (meaningful): text_color OR bg_color (combined; excludes black-only text color)
  - fixed_width_table: table with fixed pixel width
  - script_render: RDKit/JS canvas rendering dependency
  - monospace: font-family: monospace usage
  - type_drop: question type dropped by QTI import (MAT, ORD)

Reports at three granularities: per question line, per file, per unique generator.
"""

# Standard Library
import os
import re
import csv
import glob
import argparse
import subprocess


#============================================
# Color values considered "black" (no meaningful color -- Ultra stripping is not a loss)
BLACK_COLOR_VALUES = {'black', '#000', '#000000', 'inherit', 'currentcolor'}

# Question types dropped entirely by QTI import into Ultra
DROPPED_TYPES = {'MAT', 'ORD'}


#============================================
def get_repo_root() -> str:
	"""Return the absolute path to the git repo root via git rev-parse."""
	result = subprocess.run(
		['git', 'rev-parse', '--show-toplevel'],
		capture_output=True, text=True, check=True
	)
	repo_root = result.stdout.strip()
	if not repo_root:
		raise RuntimeError("git rev-parse --show-toplevel returned no repo root; run inside the repository or pass --root")
	return repo_root


#============================================
def has_text_color(line: str) -> bool:
	"""Return True if the line has a non-black inline text color: value.

	An inline color: whose value is NOT black/#000/#000000/inherit/currentcolor.
	Does NOT include background-color or bgcolor.
	"""
	line_lower = line.lower()
	# Extract all color: <value> occurrences from inline style attributes
	# Match color: followed by optional whitespace and the value (up to ; or ')
	color_values = re.findall(r'color\s*:\s*([^;\'"\s]+)', line_lower)
	for val in color_values:
		val_stripped = val.strip().rstrip(';').strip()
		if val_stripped not in BLACK_COLOR_VALUES:
			return True
	return False


#============================================
def has_bg_color(line: str) -> bool:
	"""Return True if the line has a background-color or bgcolor= attribute (any value).

	Background color is typically data (Punnett shading, gel cells, zebra rows),
	not decorative convenience color.
	"""
	line_lower = line.lower()
	if 'background-color' in line_lower:
		return True
	if 'bgcolor=' in line_lower:
		return True
	return False


#============================================
def has_meaningful_color(line: str) -> bool:
	"""Return True if the line has a meaningful color that Ultra would strip.

	Equivalent to: has_text_color(line) OR has_bg_color(line).
	Black-only text color does NOT count as meaningful.
	"""
	return has_text_color(line) or has_bg_color(line)


#============================================
def has_any_color_token(line: str) -> bool:
	"""Return True if the line contains any color-related token (broad, includes black).

	Used only to compute the black-only-color count for the corpus NOTE.
	Not reported as a feature row.
	"""
	line_lower = line.lower()
	if 'background-color' in line_lower:
		return True
	if 'bgcolor=' in line_lower:
		return True
	if re.search(r'color\s*:', line_lower):
		return True
	return False


#============================================
def has_fixed_width_table(line: str) -> bool:
	"""Return True if the line has a table element with a fixed pixel width.

	Checks for:
	  - width: <n>px inside a style attribute on table/td/th/col
	  - width=<n> or width="<n>px" attribute on table/td/th/col
	Pure percentage widths do NOT count.
	"""
	line_lower = line.lower()
	# Only bother if there's a table tag at all
	if '<table' not in line_lower and '<td' not in line_lower and '<th' not in line_lower and '<col' not in line_lower:
		return False
	# Check for width: <digits>px in any style attribute
	if re.search(r'width\s*:\s*\d+\s*px', line_lower):
		return True
	# Check for width="<digits>" or width=<digits> attribute (no %)
	# This matches plain numeric width attributes like width="20" or width='20'
	if re.search(r'\bwidth\s*=\s*["\']?\d+["\']?(?!\s*%)', line_lower):
		return True
	return False


#============================================
def has_script_render(line: str) -> bool:
	"""Return True if the line contains RDKit/JS rendering dependencies.

	Checks for rdkit, <canvas, RDKit_minimal, or <script (case-insensitive).
	"""
	line_lower = line.lower()
	if 'rdkit' in line_lower:
		return True
	if '<canvas' in line_lower:
		return True
	if '<script' in line_lower:
		return True
	return False


#============================================
def has_monospace(line: str) -> bool:
	"""Return True if the line uses font-family: monospace (with optional whitespace)."""
	# Allow optional spaces around the colon
	return bool(re.search(r'font-family\s*:\s*monospace', line, re.IGNORECASE))


#============================================
def classify_line(line: str) -> dict:
	"""Classify a single question line for all Ultra-transfer features.

	Args:
		line: A raw question line from a BBQ file.

	Returns:
		Dict with keys: type_token, text_color, bg_color, color, any_color,
		fixed_width_table, script_render, monospace, type_drop.
	"""
	# Field 0 is the question type token
	fields = line.split('\t')
	type_token = fields[0].strip() if fields else ''

	# Split color into text_color (inline) and bg_color (background)
	text_color_flag = has_text_color(line)
	bg_color_flag = has_bg_color(line)
	# Combined meaningful color = text_color OR bg_color
	color = text_color_flag or bg_color_flag
	# Broad any_color (includes black) -- used only for the corpus NOTE
	any_color = has_any_color_token(line)
	fixed_width = has_fixed_width_table(line)
	script_render = has_script_render(line)
	monospace = has_monospace(line)
	type_drop = type_token in DROPPED_TYPES

	result = {
		'type_token': type_token,
		'text_color': text_color_flag,
		'bg_color': bg_color_flag,
		'color': color,
		'any_color': any_color,
		'fixed_width_table': fixed_width,
		'script_render': script_render,
		'monospace': monospace,
		'type_drop': type_drop,
	}
	return result


#============================================
def is_content_preserving(classification: dict) -> bool:
	"""Return True if the question transfers with content intact (no color, no table, no script, no type_drop).

	Monospace is allowed: text survives, only alignment may degrade.
	"""
	return not (
		classification['color']
		or classification['fixed_width_table']
		or classification['script_render']
		or classification['type_drop']
	)


#============================================
def is_fully_faithful(classification: dict) -> bool:
	"""Return True if the question transfers fully faithfully (content_preserving AND not monospace)."""
	return is_content_preserving(classification) and not classification['monospace']


#============================================
def scan_file(filepath: str) -> list:
	"""Read one BBQ file and return a list of per-line classification dicts.

	Skips blank lines. Each returned dict also has 'filepath' and 'generator' keys.
	"""
	generator = os.path.basename(filepath)
	results = []
	with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
		for raw_line in fh:
			line = raw_line.rstrip('\n')
			# Skip blank lines
			if not line.strip():
				continue
			classification = classify_line(line)
			classification['filepath'] = filepath
			classification['generator'] = generator
			results.append(classification)
	return results


#============================================
def collect_bbq_files(repo_root: str) -> list:
	"""Return sorted list of all bbq-*.txt file paths under site_docs/."""
	pattern = os.path.join(repo_root, 'site_docs', '**', 'bbq-*.txt')
	files = sorted(glob.glob(pattern, recursive=True))
	return files


#============================================
def pct(count: int, total: int) -> str:
	"""Format a percentage string; return '  0.0%' if total is zero."""
	if total == 0:
		return '  0.0%'
	value = 100.0 * count / total
	return f'{value:5.1f}%'


#============================================
def print_report(
	all_lines: list,
	file_line_map: dict,
	files: list,
	generator_line_map: dict,
) -> None:
	"""Print the ASCII summary table to stdout.

	Args:
		all_lines: list of per-line classification dicts across all files.
		file_line_map: dict mapping filepath -> list of classification dicts.
		files: sorted list of all scanned file paths.
		generator_line_map: dict mapping generator basename -> list of classification dicts.
	"""
	total_lines = len(all_lines)
	total_files = len(files)
	total_generators = len(generator_line_map)

	print('=' * 72)
	print('ULTRA TRANSFER AUDIT -- BBQ Corpus Analysis')
	print('=' * 72)
	print(f'Total BBQ files scanned  : {total_files:>6}')
	print(f'Total unique generators  : {total_generators:>6}')
	print(f'Total question lines     : {total_lines:>6}')
	print()

	# Feature names and their dict keys for the feature table
	# any_color (broad) is excluded -- it is identical to color (meaningful) when
	# no black-only color lines exist; a computed NOTE replaces it.
	features = [
		('color (meaningful)',    'color'),
		('  text_color',          'text_color'),
		('  bg_color',            'bg_color'),
		('fixed_width_table',     'fixed_width_table'),
		('script_render',         'script_render'),
		('monospace',             'monospace'),
		('type_drop (MAT/ORD)',   'type_drop'),
	]

	# Compute black-only-color count: any_color minus meaningful color
	# Black-only = has any color token but NOT meaningful (i.e. only black/inherit text color)
	black_only_count = sum(1 for c in all_lines if c['any_color'] and not c['color'])

	# Header
	col_w = 24
	print(f'{"Feature":<{col_w}}  {"Lines":>8}  {"Lines%":>7}  {"Files":>7}  {"Files%":>7}  {"Gens":>6}  {"Gens%":>7}')
	print('-' * 72)

	for label, key in features:
		# per-line count
		line_count = sum(1 for c in all_lines if c[key])
		# per-file count (file "has" feature if any line does)
		file_count = sum(
			1 for fp in files
			if any(c[key] for c in file_line_map[fp])
		)
		# per-generator count
		gen_count = sum(
			1 for gen in generator_line_map
			if any(c[key] for c in generator_line_map[gen])
		)
		print(
			f'{label:<{col_w}}  '
			f'{line_count:>8}  {pct(line_count, total_lines):>7}  '
			f'{file_count:>7}  {pct(file_count, total_files):>7}  '
			f'{gen_count:>6}  {pct(gen_count, total_generators):>7}'
		)

	# Note about black-only color count and why any_color (broad) row was removed
	print()
	print(f'NOTE: any_color (broad) row removed -- black-only-color lines in corpus: {black_only_count}.')
	print('      meaningful color excludes black-only text color; when black-only count is 0,')
	print('      broad and meaningful counts are identical (redundant row).')

	# Legend for Gens/Gens% columns: unique-question view
	print()
	print('NOTE: Gens/Gens% = UNIQUE-QUESTION view: each generator is one question template;')
	print('      lines = randomized variations of that template.')

	print()
	print('Transfer Outcomes')
	print('-' * 72)

	# content_preserving and fully_faithful at line, file, and generator granularity
	cp_lines = sum(1 for c in all_lines if is_content_preserving(c))
	ff_lines = sum(1 for c in all_lines if is_fully_faithful(c))

	# per-file: file passes only if ALL its lines pass
	cp_files = sum(
		1 for fp in files
		if all(is_content_preserving(c) for c in file_line_map[fp])
	)
	ff_files = sum(
		1 for fp in files
		if all(is_fully_faithful(c) for c in file_line_map[fp])
	)

	# per-generator: generator "has" outcome if ALL its lines pass (since a generator is
	# considered transferable only if all questions in it transfer)
	cp_gens = sum(
		1 for gen in generator_line_map
		if all(is_content_preserving(c) for c in generator_line_map[gen])
	)
	ff_gens = sum(
		1 for gen in generator_line_map
		if all(is_fully_faithful(c) for c in generator_line_map[gen])
	)

	print(f'{"content_preserving":<{col_w}}  {cp_lines:>8}  {pct(cp_lines, total_lines):>7}  {cp_files:>7}  {pct(cp_files, total_files):>7}  {cp_gens:>6}  {pct(cp_gens, total_generators):>7}')
	print(f'{"fully_faithful":<{col_w}}  {ff_lines:>8}  {pct(ff_lines, total_lines):>7}  {ff_files:>7}  {pct(ff_files, total_files):>7}  {ff_gens:>6}  {pct(ff_gens, total_generators):>7}')
	print('=' * 72)

	# --- Transfer Tiers ---
	# Three mutually exclusive tiers based on per-line features, then aggregated
	# to file and generator by WORST tier any of their lines reaches.
	#
	# Tier 1 - works as-is: none of {text_color, bg_color, fixed_width_table, script_render, type_drop}
	#   (monospace allowed; may degrade alignment but text survives)
	# Tier 2 - text-color-only: has text_color but none of {bg_color, fixed_width_table, script_render, type_drop}
	# Tier 3 - structural/data break: has any of {bg_color, fixed_width_table, script_render, type_drop}
	print()
	print('Transfer Tiers')
	print('-' * 72)
	print('Tier 1 = works as-is (no data-affecting features; monospace allowed).')
	print('Tier 2 = text-color-only (only sanitization-affected feature is inline text color).')
	print('Tier 3 = structural/data break (bg_color, fixed_width_table, script_render, or type_drop).')
	print()

	def line_tier(c: dict) -> int:
		"""Return the tier (1, 2, or 3) for a single classification dict."""
		# Tier 3: any structural/data-affecting feature
		if c['bg_color'] or c['fixed_width_table'] or c['script_render'] or c['type_drop']:
			return 3
		# Tier 2: text color is the only affected feature
		if c['text_color']:
			return 2
		# Tier 1: clean
		return 1

	# --- Line-level tiers ---
	t1_lines = sum(1 for c in all_lines if line_tier(c) == 1)
	t2_lines = sum(1 for c in all_lines if line_tier(c) == 2)
	t3_lines = sum(1 for c in all_lines if line_tier(c) == 3)

	# --- File-level tiers: worst tier any line in the file reaches ---
	def file_worst_tier(fp: str) -> int:
		"""Return worst tier for a file (max across all its lines)."""
		worst = 1
		for c in file_line_map[fp]:
			t = line_tier(c)
			if t > worst:
				worst = t
		return worst

	t1_files = sum(1 for fp in files if file_worst_tier(fp) == 1)
	t2_files = sum(1 for fp in files if file_worst_tier(fp) == 2)
	t3_files = sum(1 for fp in files if file_worst_tier(fp) == 3)

	# --- Generator-level tiers: worst tier any line in the generator reaches ---
	def gen_worst_tier(gen: str) -> int:
		"""Return worst tier for a generator (max across all its lines)."""
		worst = 1
		for c in generator_line_map[gen]:
			t = line_tier(c)
			if t > worst:
				worst = t
		return worst

	t1_gens = sum(1 for gen in generator_line_map if gen_worst_tier(gen) == 1)
	t2_gens = sum(1 for gen in generator_line_map if gen_worst_tier(gen) == 2)
	t3_gens = sum(1 for gen in generator_line_map if gen_worst_tier(gen) == 3)

	# Tier 1+2 subtotals (optimistic ceiling)
	t12_lines = t1_lines + t2_lines
	t12_files = t1_files + t2_files
	t12_gens = t1_gens + t2_gens

	tier_col_w = 28
	print(f'{"Tier":<{tier_col_w}}  {"Lines":>8}  {"Lines%":>7}  {"Files":>7}  {"Files%":>7}  {"Gens":>6}  {"Gens%":>7}')
	print('-' * 72)
	print(
		f'{"Tier 1 - works as-is":<{tier_col_w}}  '
		f'{t1_lines:>8}  {pct(t1_lines, total_lines):>7}  '
		f'{t1_files:>7}  {pct(t1_files, total_files):>7}  '
		f'{t1_gens:>6}  {pct(t1_gens, total_generators):>7}'
	)
	print(
		f'{"Tier 2 - text-color-only":<{tier_col_w}}  '
		f'{t2_lines:>8}  {pct(t2_lines, total_lines):>7}  '
		f'{t2_files:>7}  {pct(t2_files, total_files):>7}  '
		f'{t2_gens:>6}  {pct(t2_gens, total_generators):>7}'
	)
	print(
		f'{"Tier 3 - structural/data break":<{tier_col_w}}  '
		f'{t3_lines:>8}  {pct(t3_lines, total_lines):>7}  '
		f'{t3_files:>7}  {pct(t3_files, total_files):>7}  '
		f'{t3_gens:>6}  {pct(t3_gens, total_generators):>7}'
	)
	print('-' * 72)
	print(
		f'{"Tier 1+2 (optimistic ceiling)":<{tier_col_w}}  '
		f'{t12_lines:>8}  {pct(t12_lines, total_lines):>7}  '
		f'{t12_files:>7}  {pct(t12_files, total_files):>7}  '
		f'{t12_gens:>6}  {pct(t12_gens, total_generators):>7}'
	)
	print()
	print('NOTE: Tier 2 is an optimistic upper bound -- in this corpus some text color is data')
	print('      (e.g. pipette red digits, HLA marker color), so Tier 2 questions are')
	print('      "maybe survivable," not guaranteed.')
	print('      Monospace (font-family: monospace) is allowed in Tier 1; text survives,')
	print('      only column alignment may degrade slightly.')
	print('=' * 72)

	# Breakdown by question type: line counts AND unique-generator counts per type
	print()
	print('Question type distribution (top types by line count)')
	# Count lines per type
	type_line_counts: dict = {}
	for c in all_lines:
		t = c['type_token']
		type_line_counts[t] = type_line_counts.get(t, 0) + 1

	# Count unique generators per type (a generator counted under each type it contains)
	# A generator is "mixed-type" if it has lines of more than one type
	type_gen_counts: dict = {}
	mixed_type_generators: list = []
	for gen, gen_lines in generator_line_map.items():
		# Collect all distinct type tokens in this generator
		types_in_gen = set(c['type_token'] for c in gen_lines)
		if len(types_in_gen) > 1:
			mixed_type_generators.append((gen, sorted(types_in_gen)))
		# Add this generator to each type it contains
		for t in types_in_gen:
			type_gen_counts[t] = type_gen_counts.get(t, 0) + 1

	# Print table header
	type_col_w = 12
	print(f'  {"Type":<{type_col_w}}  {"Gens":>6}  {"Gens%":>7}  {"Lines":>7}  {"Lines%":>7}')
	print('  ' + '-' * 50)
	for t, cnt in sorted(type_line_counts.items(), key=lambda x: -x[1]):
		drop_marker = ' [DROPPED by QTI]' if t in DROPPED_TYPES else ''
		gen_cnt = type_gen_counts.get(t, 0)
		print(
			f'  {t:<{type_col_w}}  {gen_cnt:>6}  {pct(gen_cnt, total_generators):>7}'
			f'  {cnt:>7}  {pct(cnt, total_lines):>7}{drop_marker}'
		)

	# Note about mixed-type generators (if any exist, generator column may sum > total)
	num_mixed = len(mixed_type_generators)
	if num_mixed > 0:
		print(f'  NOTE: {num_mixed} mixed-type generator(s) counted under each type they contain;')
		print('        generator column may sum to slightly more than total unique generators.')
		for gen_name, types in mixed_type_generators:
			print(f'        mixed: {gen_name}  types: {", ".join(types)}')
	else:
		print('  NOTE: No mixed-type generators found; each generator has exactly one type.')

	print('=' * 72)

	# Variations per generator: show the spread of lines-per-generator
	print()
	print('Variations per generator (lines per unique template)')
	print('-' * 50)
	# Compute lines-per-generator list
	variations_counts = sorted(len(lines) for lines in generator_line_map.values())
	vmin = variations_counts[0]
	vmax = variations_counts[-1]
	vmean = round(sum(variations_counts) / len(variations_counts))
	# Median: middle value (or average of two middle values for even count)
	n_gens = len(variations_counts)
	mid = n_gens // 2
	if n_gens % 2 == 1:
		vmedian = variations_counts[mid]
	else:
		vmedian = (variations_counts[mid - 1] + variations_counts[mid]) / 2
	# Find the name(s) of the largest generator(s)
	largest_names = [gen for gen, lines in generator_line_map.items() if len(lines) == vmax]
	largest_label = largest_names[0] if len(largest_names) == 1 else f'{len(largest_names)} generators'
	print(f'  min     : {vmin}')
	print(f'  median  : {vmedian}')
	print(f'  mean    : {vmean}')
	print(f'  max     : {vmax}  ({largest_label})')
	print('=' * 72)


#============================================
def write_csv(
	csv_path: str,
	files: list,
	file_line_map: dict,
) -> None:
	"""Write a per-file CSV with feature line counts.

	Args:
		csv_path: Output file path.
		files: Sorted list of scanned file paths.
		file_line_map: dict mapping filepath -> list of classification dicts.
	"""
	fieldnames = [
		'filepath', 'generator', 'total_lines',
		'text_color', 'bg_color', 'color', 'fixed_width_table', 'script_render', 'monospace', 'type_drop',
	]
	with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
		writer = csv.DictWriter(fh, fieldnames=fieldnames)
		writer.writeheader()
		for fp in files:
			lines = file_line_map[fp]
			row = {
				'filepath': fp,
				'generator': os.path.basename(fp),
				'total_lines': len(lines),
				'text_color': sum(1 for c in lines if c['text_color']),
				'bg_color': sum(1 for c in lines if c['bg_color']),
				'color': sum(1 for c in lines if c['color']),
				'fixed_width_table': sum(1 for c in lines if c['fixed_width_table']),
				'script_render': sum(1 for c in lines if c['script_render']),
				'monospace': sum(1 for c in lines if c['monospace']),
				'type_drop': sum(1 for c in lines if c['type_drop']),
			}
			writer.writerow(row)
	print(f'CSV written: {csv_path}')


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description='Audit BBQ corpus for Blackboard Ultra HTML sanitizer degradation'
	)
	parser.add_argument(
		'-c', '--csv', dest='csv_path',
		default=None,
		help='Write per-file CSV to this path (optional)',
	)
	parser.add_argument(
		'-r', '--root', dest='repo_root',
		default=None,
		help='Override repo root (default: git rev-parse --show-toplevel)',
	)
	args = parser.parse_args()
	return args


#============================================
def main() -> None:
	"""Main entry point: scan all BBQ files and report Ultra transfer risk."""
	args = parse_args()

	# Determine repo root
	if args.repo_root is not None:
		repo_root = args.repo_root
	else:
		repo_root = get_repo_root()

	# Collect all bbq-*.txt files
	files = collect_bbq_files(repo_root)
	print(f'Scanning {len(files)} BBQ files under {repo_root}/site_docs ...')

	# Scan each file
	all_lines: list = []
	file_line_map: dict = {}
	generator_line_map: dict = {}

	for fp in files:
		file_classifications = scan_file(fp)
		file_line_map[fp] = file_classifications
		all_lines.extend(file_classifications)
		# Group by generator (basename) for the unique-generator granularity
		gen = os.path.basename(fp)
		if gen not in generator_line_map:
			generator_line_map[gen] = []
		generator_line_map[gen].extend(file_classifications)

	# Print the report
	print_report(all_lines, file_line_map, files, generator_line_map)

	# Optionally write CSV
	if args.csv_path is not None:
		write_csv(args.csv_path, files, file_line_map)


if __name__ == '__main__':
	main()

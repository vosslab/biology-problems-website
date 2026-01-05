---
title: Deletion mutants
---

<link rel="stylesheet" href="/assets/stylesheets/deletion_mutants_formatting.css">

<script src="/assets/scripts/daily_puzzle_core.js"></script>
<script src="/assets/scripts/daily_puzzle_stats.js"></script>
<script src="/assets/scripts/deletion_mutants_words.js"></script>
<script src="/assets/scripts/deletion_mutants_colors.js"></script>
<script src="/assets/scripts/deletion_mutants_logic.js"></script>
<script src="/assets/scripts/deletion_mutants_game.js"></script>
<script src="/assets/scripts/deletion_mutants_bootstrap.js"></script>

### Deduce the gene order from deletions

<div id="dm-root">
	<div id="stats"></div>
	<div id="problem">
		<div id="problem-summary"></div>
		<div id="hint-area">
			<button id="hint-button" type="button">I need help: show first gene (-1 guess)</button>
			<div id="hint-status"></div>
		</div>
		<div id="deletion-table"></div>
		<div id="deletion-list"></div>
	</div>
	<div id="message"></div>
	<div id="board"></div>
	<div id="keyboard"></div>
	<div id="help-row">
		<button id="help-button" type="button">Deletion mutant solving tips</button>
	</div>
	<div id="toast-container"></div>
	<div id="instructions">
		<details id="instructions-details">
			<summary><strong>How to solve the deletion mutant puzzle</strong></summary>
			<p>Your goal is to determine the linear order of the genes on a chromosome using deletion mutant evidence.</p>
			<ol>
				<li>Use the deletion list to see which genes are uncovered together.</li>
				<li>Use the table to identify which deletions overlap and which are nested.</li>
				<li>Fit the genes into a single consistent order that explains every deletion.</li>
				<li>Enter your gene order using each gene letter exactly once.</li>
			</ol>
		</details>
	</div>
</div>

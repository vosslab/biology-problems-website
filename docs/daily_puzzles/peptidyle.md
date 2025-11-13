---
title: Peptidyle
---

<link rel="stylesheet" href="/assets/stylesheets/peptidyle_formatting.css">

<script src="https://unpkg.com/@rdkit/rdkit/dist/RDKit_minimal.js"></script>
<script src="/assets/scripts/peptidyle_peptides.js"></script>
<script src="/assets/scripts/peptidyle_words.js"></script>
<script src="/assets/scripts/peptidyle_stats.js"></script>
<script src="/assets/scripts/peptidyle_game.js"></script>
<script src="/assets/scripts/peptidyle_bootstrap.js"></script>

### Deduce the pentapeptide sequence

<div id="pw-root">
	<div id="peptide"></div>
	<div id="help-row">
		<button id="help-button" type="button">Peptide solving tips</button>
	</div>
	<div id="message"></div>
	<div id="board"></div>
	<form id="guess-form" autocomplete="off">
		<label for="guess">Guess:</label>
		<input id="guess" maxlength="5">
		<button type="submit">Enter</button>
	</form>
	<div id="keyboard"></div>
	<div id="toast-container"></div>
	<div id="instructions">
		<details id="instructions-details">
			<summary><strong>How to solve the peptide puzzle</strong></summary>
			<p>A pentapeptide is made up of 5 amino acids. The figure above shows one such peptide chain with an unknown sequence. Your task is to find out the sequence of this pentapeptide.</p>
			<p>Here is a step by step guide to help you:</p>
			<ol>
				<li>
					Looking at an amino acid guide can help. Here is a PDF guide:
					<a href="https://drive.google.com/file/d/1Mgum_TmZ71-XIjb38sStEpzzZLqkQb-W/view?usp=sharing">
						bchm_exam-help_sheet.pdf
					</a>.
					You can also search online for an image of
					<em>"amino acid one-letter code chart"</em> to see all 20 amino acids
					with their single letter codes.
				</li>
				<li>
					First, identify the amino terminal end, which is represented as
					<span style="padding: 2px 6px; color: #0000cc; background-color: #66ff66; border-radius: 999px;">
						NH<sub>3</sub><sup>+</sup>
					</span>
					and highlighted in bright green. It is important to differentiate between the
					general nitrogens found in amino acid backbones (denoted as
					<span style="color:#0000cc">NH</span>) and the nitrogen in the side chains of
					amino acids. Among amino acids, only lysine has a side chain with three
					hydrogens, resembling the
					<span style="color:#0000cc">NH<sub>3</sub><sup>+</sup></span>
					of the amino terminal end.
				</li>
				<li>
					The peptide bonds are highlighted in
					<span style="color: #222222; background-color: #00FF00; padding: 2px;">bright green</span>,
					helping you see the different amino acids.
				</li>
				<li>
					Look at the side chains of each amino acid to figure out their single letter
					amino acid code.
				</li>
				<li>
					Once you know the single letter codes for the 5 side chains, list them in the
					amino to carboxyl (N&rarr;C) direction. This is the accepted way to write peptide
					sequences.
				</li>
				<li>
					The correct sequence of letters will be a five letter English word. This word is
					also an answer in the New York Times Wordle&trade; game.
				</li>
			</ol>
		</details>
	</div>
</div>

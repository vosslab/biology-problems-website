---
title: Biomacromolecules
---

<link rel="stylesheet" href="/assets/stylesheets/biomacromolecule_formatting.css">

<script src="https://unpkg.com/@rdkit/rdkit/dist/RDKit_minimal.js"></script>
<script src="/assets/scripts/biomacromolecule_data.js"></script>
<script src="/assets/scripts/daily_puzzle_core.js"></script>
<script src="/assets/scripts/daily_puzzle_stats.js"></script>
<script src="/assets/scripts/daily_puzzle_ui.js"></script>
<script src="/assets/scripts/daily_puzzle_wordle.js"></script>
<script src="/assets/scripts/biomacromolecule_game.js"></script>
<script src="/assets/scripts/biomacromolecule_bootstrap.js"></script>

### Identify the macromolecule category from its chemical structure

<div id="bm-root">
	<div id="stats"></div>
	<div id="hint-area">
		<div id="controls-left">
			<button id="help-button" type="button">How to play</button>
			<button id="hint-button" type="button">Reveal molecule name (free)</button>
		</div>
		<div id="hint-status"></div>
	</div>
	<div id="molecule-display"></div>
	<div id="formula-display"></div>
	<div id="name-display"></div>
	<div id="message"></div>
	<div id="category-section"></div>
	<div id="subcategory-section"></div>
	<div id="dp-next-reset" class="dp-next-reset" aria-live="off"></div>
	<div id="toast-container"></div>
	<div id="instructions">
		<details id="instructions-details">
			<summary><strong>How to play the biomacromolecule puzzle</strong></summary>
			<p>Each day you are shown a different biomacromolecule drawn as a 2D chemical structure.</p>
			<ol>
				<li>
					Study the structure and molecular formula. You can optionally click
					<em>"Reveal molecule name"</em> at no penalty.
				</li>
				<li>
					<strong>Round 1 (scored):</strong> Choose one of the four macromolecule categories:
					Carbohydrate, Lipid, Nucleic Acid, or Protein. A correct answer counts as a win
					and extends your streak; a wrong answer resets the streak.
				</li>
				<li>
					<strong>Round 2 (for fun):</strong> Identify the subcategory from four choices.
					This does not affect your score.
				</li>
			</ol>
			<table class="bm-guide-table">
			<tr><td class="bm-guide-carb">
				<span class="bm-guide-label" style="color:#0a9bf5;">Carbohydrates (monosaccharides)</span>
				<ul>
					<li>Should have about the same number of oxygens as carbons.</li>
					<li>Look for hydroxyl groups (&ndash;OH) attached to the carbon atoms.</li>
					<li>Carbonyl groups (C=O) are often present as well.</li>
					<li>Look for the base unit of CH<sub>2</sub>O.</li>
					<li>Larger carbohydrates will form hexagon or pentagon ring-like structures.</li>
				</ul>
			</td></tr>
			<tr><td class="bm-guide-lipid">
				<span class="bm-guide-label" style="color:#e69100;">Lipids (fatty acids)</span>
				<ul>
					<li>Contain mostly carbon and hydrogen.</li>
					<li>Very few oxygens and often no nitrogens.</li>
					<li>Fats and oils will have carboxyl groups (&ndash;COOH) and ester bonds.</li>
					<li>Look for long chains or ring structures of only carbon and hydrogen.</li>
					<li>Steroids have four interconnected carbon rings.</li>
				</ul>
			</td></tr>
			<tr><td class="bm-guide-protein">
				<span class="bm-guide-label" style="color:#009900;">Proteins (amino acids and dipeptides)</span>
				<ul>
					<li>Always have a nitrogen/amino group (&ndash;NH<sub>2</sub> or &ndash;NH<sub>3</sub><sup>+</sup>).</li>
					<li>Always have a carboxyl group (&ndash;COOH or &ndash;COO<sup>&ndash;</sup>).</li>
					<li>Identify the central C<sub>&alpha;</sub> (alpha-carbon) attached to an amino group and a carboxyl group.</li>
					<li>Larger protein macromolecules will have a characteristic peptide bond (C&ndash;N).</li>
					<li>Try to identify common side chains (R groups).</li>
				</ul>
			</td></tr>
			<tr><td class="bm-guide-nucleic">
				<span class="bm-guide-label" style="color:#e60000;">Nucleic acids (nucleobases)</span>
				<ul>
					<li>Must have a nucleobase, rings containing carbon and nitrogen.</li>
					<li>Larger nucleic acids will have a sugar backbone and phosphate groups.</li>
				</ul>
			</td></tr>
			<tr><td class="bm-guide-phosphate">
				<span class="bm-guide-label" style="color:#7b12a1;">Phosphate groups (&ndash;PO<sub>4</sub><sup>2&ndash;</sup>)</span>
				<ul>
					<li>Found in all of the macromolecule types.</li>
					<li>It is best to ignore them so they don't confuse you.</li>
					<li>The breakdown of carbohydrates involves adding phosphates.</li>
					<li>Membrane lipids have phosphate head groups.</li>
					<li>Many proteins are phosphorylated for regulatory purposes.</li>
					<li>DNA has a phosphate backbone.</li>
				</ul>
			</td></tr>
		</table>
		</details>
	</div>
</div>

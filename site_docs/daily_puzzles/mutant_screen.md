---
title: Mutant screen
---

<link rel="stylesheet" href="/assets/stylesheets/mutant_screen_formatting.css">

<script src="/assets/scripts/daily_puzzle_core.js"></script>
<script src="/assets/scripts/daily_puzzle_stats.js"></script>
<script src="/assets/scripts/daily_puzzle_keyboard.js"></script>
<script src="/assets/scripts/daily_puzzle_input.js"></script>
<script src="/assets/scripts/daily_puzzle_ui.js"></script>
<script src="/assets/scripts/daily_puzzle_wordle.js"></script>
<script src="/assets/scripts/mutant_screen_words.js"></script>
<script src="/assets/scripts/mutant_screen_logic.js"></script>
<script src="/assets/scripts/mutant_screen_game.js"></script>
<script src="/assets/scripts/mutant_screen_bootstrap.js"></script>

### Deduce the pathway order from auxotroph growth

<div id="ms-root">
<div id="stats"></div>
<p class="dp-intro">This puzzle is based on the classic Beadle and Tatum <em>Neurospora</em> mutant auxotroph experiments that led to the "one gene, one enzyme" hypothesis. Each mutant class is blocked at a different step in a metabolic pathway. A blocked mutant can only grow if you supply a downstream intermediate that bypasses the block.</p>
<div id="problem">
<div id="problem-summary"></div>
<div id="hint-area">
<div id="controls-left">
<button id="help-button" type="button">Auxotroph solving tips</button>
<button id="hint-button" type="button">I need help: show first step (-1 guess)</button>
</div>
<div id="hint-status"></div>
</div>
<div id="growth-table"></div>
</div>

<div id="message"></div>
<div id="board"></div>
<div id="keyboard"></div>
<div id="dp-next-reset" class="dp-next-reset" aria-live="off"></div>
<div id="toast-container"></div>

<div id="instructions">
<details id="instructions-details">
<summary><strong>How to solve the auxotroph puzzle</strong></summary>
<p>Your goal is to determine the order of metabolites in a biosynthetic pathway using mutant growth data.</p>
<ol>
<li>Each mutant class has a block at a different step in the pathway.</li>
<li>A mutant grows (+) only when supplemented with an intermediate <em>downstream</em> of its block.</li>
<li>A mutant does not grow (&ndash;) when given an intermediate <em>upstream</em> of its block.</li>
<li>Count the plus signs: the class with only one + is blocked latest (just before the final product); the class with all + is blocked earliest.</li>
<li>Order the metabolites from first to last in the pathway. The correct order spells a five-letter English word.</li>
</ol>
</details>
</div>
</div>

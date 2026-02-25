"use strict";

/* global RDKitModule */

var _bmToaster = null;

function bmShowToast(text, durationMs) {
	if (!window.DailyPuzzleWordle) {
		return;
	}
	if (!_bmToaster) {
		_bmToaster = window.DailyPuzzleWordle.createToaster("toast-container", 1500);
	}
	_bmToaster(text, durationMs);
}

//=================================================
// Format molecular formula with subscript tags
//=================================================
function bmFormatFormula(raw) {
	if (!raw) {
		return "";
	}
	return raw.replace(/(\d+)/g, "<sub>$1</sub>");
}

//=================================================
// Render molecule SVG using RDKit
//=================================================
function bmRenderMolecule(smiles, containerEl) {
	if (!window.RDKitModule) {
		containerEl.textContent = "RDKit not loaded.";
		return false;
	}
	var mol = null;
	try {
		mol = RDKitModule.get_mol(smiles);
	} catch (e) {
		containerEl.textContent = "Could not parse molecule.";
		return false;
	}
	if (!mol) {
		containerEl.textContent = "Could not parse molecule.";
		return false;
	}

	containerEl.innerHTML = "";
	var canvas = document.createElement("canvas");
	canvas.width = 800;
	canvas.height = 450;
	containerEl.appendChild(canvas);

	// match peptidyle: gray background, explicit methyls, thicker bonds
	mol.draw_to_canvas_with_highlights(canvas, JSON.stringify({
		backgroundColour: [0.8, 0.8, 0.8],
		clearBackground: true,
		explicitMethyl: true,
		bondLineWidth: 1.5
	}));
	mol.delete();
	return true;
}

//=================================================
// localStorage state for same-day replay protection
//=================================================
var BM_STATE_KEY = "biomacromolecule_state_v1";

function bmLoadState(dayKey) {
	try {
		var raw = window.localStorage.getItem(BM_STATE_KEY);
		if (!raw) {
			return null;
		}
		var state = JSON.parse(raw);
		if (state.dayKey !== dayKey) {
			return null;
		}
		return state;
	} catch (_) {
		return null;
	}
}

function bmSaveState(state) {
	try {
		window.localStorage.setItem(BM_STATE_KEY, JSON.stringify(state));
	} catch (_) {
		// ignore
	}
}

//=================================================
// Main game setup
//=================================================
function setupBiomacromoleculeGame() {
	var data = window.BiomacromoleculeData;
	if (!data || !data.molecules || data.molecules.length === 0) {
		document.getElementById("message").textContent = "Error: molecule data not loaded.";
		return;
	}

	var dayKey = window.DailyPuzzleCore
		? window.DailyPuzzleCore.getUtcDayKey(new Date())
		: new Date().toISOString().slice(0, 10);

	var rng = window.DailyPuzzleCore
		? window.DailyPuzzleCore.makeSeededRng(dayKey + "|biomacromolecule-v1")
		: function () { return Math.random(); };

	// Pick today's molecule
	var molIndex = Math.floor(rng() * data.molecules.length);
	var molecule = data.molecules[molIndex];

	// Stats
	var statsStore = window.DailyPuzzleStats
		? window.DailyPuzzleStats.createStore("biomacromolecule_stats_v1", 1)
		: null;
	if (statsStore) {
		statsStore.renderStats("stats");
	}

	// DOM elements
	var moleculeDisplay = document.getElementById("molecule-display");
	var formulaDisplay = document.getElementById("formula-display");
	var nameRevealBtn = document.getElementById("hint-button");
	var nameDisplay = document.getElementById("name-display");
	var messageEl = document.getElementById("message");
	var categorySection = document.getElementById("category-section");
	var subcategorySection = document.getElementById("subcategory-section");

	// Render molecule SVG
	bmRenderMolecule(molecule.smiles, moleculeDisplay);

	// Render formula
	if (formulaDisplay) {
		var formulaHtml = bmFormatFormula(molecule.formula);
		if (molecule.weight) {
			formulaHtml += " &nbsp; <span class='bm-weight'>(" + molecule.weight + " g/mol)</span>";
		}
		formulaDisplay.innerHTML = formulaHtml;
	}

	// Game state
	var state = {
		dayKey: dayKey,
		categoryPicked: null,
		categoryCorrect: null,
		subcategoryPicked: null,
		subcategoryCorrect: null,
		nameRevealed: false,
		finished: false
	};

	var savedState = bmLoadState(dayKey);
	if (savedState && savedState.finished) {
		state = savedState;
	}

	var hintStatusEl = document.getElementById("hint-status");

	// Name reveal button (always free, uses shared hint-button slot)
	function revealName() {
		state.nameRevealed = true;
		nameDisplay.textContent = molecule.name;
		nameDisplay.style.display = "block";
		if (nameRevealBtn) {
			nameRevealBtn.disabled = true;
			nameRevealBtn.textContent = "Name revealed";
		}
		if (hintStatusEl) {
			hintStatusEl.textContent = molecule.name;
		}
		bmSaveState(state);
	}

	if (nameRevealBtn) {
		nameRevealBtn.addEventListener("click", revealName);
	}

	// -----------------------------------------------
	// Build category buttons (Round 1 — scored)
	// -----------------------------------------------
	function buildCategoryButtons() {
		var html = "<div class='bm-question'>Which macromolecule category?</div>";
		html += "<div class='bm-choices'>";
		var cats = data.categories;
		for (var i = 0; i < cats.length; i += 1) {
			html += "<button class='bm-choice-btn' data-cat='" + cats[i] + "'>" + cats[i] + "</button>";
		}
		html += "</div>";
		categorySection.innerHTML = html;

		var buttons = categorySection.querySelectorAll(".bm-choice-btn");
		for (var j = 0; j < buttons.length; j += 1) {
			buttons[j].addEventListener("click", onCategoryClick);
		}
	}

	function onCategoryClick(e) {
		if (state.categoryPicked !== null) {
			return;
		}
		var picked = e.target.getAttribute("data-cat");
		var correct = molecule.category;
		state.categoryPicked = picked;
		state.categoryCorrect = (picked === correct);

		// Highlight buttons
		var buttons = categorySection.querySelectorAll(".bm-choice-btn");
		for (var i = 0; i < buttons.length; i += 1) {
			var btn = buttons[i];
			var cat = btn.getAttribute("data-cat");
			btn.disabled = true;
			if (cat === correct) {
				btn.classList.add("bm-correct");
			} else if (cat === picked && !state.categoryCorrect) {
				btn.classList.add("bm-wrong");
			}
		}

		// Update stats
		var win = state.categoryCorrect;
		if (statsStore) {
			statsStore.updateOnGameEnd(win, dayKey, 1);
			statsStore.renderStats("stats");
		}

		if (win) {
			messageEl.textContent = "Correct! It is a " + correct + ".";
			bmShowToast("Correct!");
		} else {
			messageEl.textContent = "Wrong — it is a " + correct + ".";
			bmShowToast("Wrong — it is a " + correct + ".");
		}

		// Reveal name automatically
		if (!state.nameRevealed) {
			revealName();
		}

		// Show subcategory question after brief delay
		window.setTimeout(function () {
			buildSubcategoryButtons();
		}, 400);

		bmSaveState(state);
	}

	// -----------------------------------------------
	// Build subcategory buttons (Round 2 — for fun)
	// -----------------------------------------------
	function buildSubcategoryButtons() {
		var correct = molecule.subcategory;
		var catSubs = data.subcategories[molecule.category] || [];

		// Pick 3 random distractors from same category using seeded RNG
		var distractors = [];
		for (var i = 0; i < catSubs.length; i += 1) {
			if (catSubs[i] !== correct) {
				distractors.push(catSubs[i]);
			}
		}
		// Shuffle distractors with seeded RNG
		if (window.DailyPuzzleCore) {
			window.DailyPuzzleCore.shuffleInPlace(distractors, rng);
		}
		distractors = distractors.slice(0, 3);

		var options = [correct].concat(distractors);
		// Shuffle all options
		if (window.DailyPuzzleCore) {
			window.DailyPuzzleCore.shuffleInPlace(options, rng);
		}

		var html = "<div class='bm-question'>What subcategory? <span class='bm-fun-label'>(just for fun)</span></div>";
		html += "<div class='bm-choices'>";
		for (var j = 0; j < options.length; j += 1) {
			html += "<button class='bm-choice-btn bm-sub-btn' data-sub='" + options[j] + "'>" + options[j] + "</button>";
		}
		html += "</div>";
		subcategorySection.innerHTML = html;
		subcategorySection.style.display = "block";

		var buttons = subcategorySection.querySelectorAll(".bm-sub-btn");
		for (var k = 0; k < buttons.length; k += 1) {
			buttons[k].addEventListener("click", onSubcategoryClick);
		}
	}

	function onSubcategoryClick(e) {
		if (state.subcategoryPicked !== null) {
			return;
		}
		var picked = e.target.getAttribute("data-sub");
		var correct = molecule.subcategory;
		state.subcategoryPicked = picked;
		state.subcategoryCorrect = (picked === correct);

		var buttons = subcategorySection.querySelectorAll(".bm-sub-btn");
		for (var i = 0; i < buttons.length; i += 1) {
			var btn = buttons[i];
			var sub = btn.getAttribute("data-sub");
			btn.disabled = true;
			if (sub === correct) {
				btn.classList.add("bm-correct");
			} else if (sub === picked && !state.subcategoryCorrect) {
				btn.classList.add("bm-wrong");
			}
		}

		state.finished = true;
		bmSaveState(state);

		// Show game-end modal after delay
		window.setTimeout(function () {
			if (statsStore) {
				statsStore.showGameEndModal({
					win: state.categoryCorrect,
					guessNumber: 1,
					maxGuesses: 1,
					gameName: "Biomacromolecules"
				});
			}
		}, 600);
	}

	// -----------------------------------------------
	// Restore saved state (same-day replay)
	// -----------------------------------------------
	if (savedState && savedState.finished) {
		// Reveal name
		if (savedState.nameRevealed) {
			revealName();
		}
		// Rebuild category with results shown
		buildCategoryButtons();
		var catButtons = categorySection.querySelectorAll(".bm-choice-btn");
		for (var ci = 0; ci < catButtons.length; ci += 1) {
			var catBtn = catButtons[ci];
			var catVal = catBtn.getAttribute("data-cat");
			catBtn.disabled = true;
			if (catVal === molecule.category) {
				catBtn.classList.add("bm-correct");
			} else if (catVal === savedState.categoryPicked && !savedState.categoryCorrect) {
				catBtn.classList.add("bm-wrong");
			}
		}
		if (savedState.categoryCorrect) {
			messageEl.textContent = "Correct! It is a " + molecule.category + ".";
		} else {
			messageEl.textContent = "Wrong — it is a " + molecule.category + ".";
		}

		// Rebuild subcategory if answered
		if (savedState.subcategoryPicked !== null) {
			buildSubcategoryButtons();
			var subButtons = subcategorySection.querySelectorAll(".bm-sub-btn");
			for (var si = 0; si < subButtons.length; si += 1) {
				var subBtn = subButtons[si];
				var subVal = subBtn.getAttribute("data-sub");
				subBtn.disabled = true;
				if (subVal === molecule.subcategory) {
					subBtn.classList.add("bm-correct");
				} else if (subVal === savedState.subcategoryPicked && !savedState.subcategoryCorrect) {
					subBtn.classList.add("bm-wrong");
				}
			}
		} else {
			// Category was picked but subcategory wasn't — show subcategory buttons
			buildSubcategoryButtons();
		}
		return;
	}

	// Fresh game: show category buttons
	buildCategoryButtons();
}

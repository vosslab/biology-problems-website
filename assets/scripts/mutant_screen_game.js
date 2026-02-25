"use strict";

/* global DailyPuzzleCore, DailyPuzzleStats, DailyPuzzleKeyboard, DailyPuzzleUI, DailyPuzzleWordle, MutantScreenWords, MutantScreenLogic */

var MUTANT_SCREEN_CONFIG = {
	numMetabolites: 5,
	maxGuesses: 4,
	firstStepHintPenaltyGuesses: 1
};

function mutantScreenSetupGame() {
	var rootEl = document.getElementById("ms-root");
	var messageEl = document.getElementById("message");
	var hintButton = document.getElementById("hint-button");
	var hintStatusEl = document.getElementById("hint-status");
	var tableEl = document.getElementById("growth-table");
	var summaryEl = document.getElementById("problem-summary");
	var boardEl = document.getElementById("board");
	var keyboardEl = document.getElementById("keyboard");

	if (!rootEl || !messageEl || !hintButton || !hintStatusEl || !tableEl || !summaryEl || !boardEl || !keyboardEl) {
		return;
	}

	var dayKey = DailyPuzzleCore.getUtcDayKey(new Date());
	var statsStore = DailyPuzzleStats.createStore("mutant_screen_stats_v1", MUTANT_SCREEN_CONFIG.maxGuesses);
	var _toaster = null;

	var state = {
		dayKey: dayKey,
		answerWord: null,
		pathwayOrder: null,
		growthData: null,
		guesses: [],
		currentGuess: "",
		letterState: {},
		hintUsed: false,
		gameOver: false
	};

	function listToText(items) {
		if (!items.length) {
			return "";
		}
		if (items.length === 1) {
			return items[0];
		}
		if (items.length === 2) {
			return items[0] + " and " + items[1];
		}
		return items.slice(0, items.length - 1).join(", ") + ", and " + items[items.length - 1];
	}

	function initLetterState() {
		var letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
		var i = 0;
		for (i = 0; i < letters.length; i += 1) {
			state.letterState[letters[i]] = "unknown";
		}
	}

	function scoreGuess(guess, answer) {
		return DailyPuzzleWordle.scoreGuess(guess, answer);
	}

	function updateLetterState(guess, result) {
		DailyPuzzleWordle.updateLetterState(guess, result, state.letterState);
	}

	function showToast(text, durationMs) {
		if (!_toaster) {
			_toaster = DailyPuzzleWordle.createToaster("toast-container", 1600);
		}
		_toaster(text, durationMs);
	}

	function getHintPenaltyUsedCount() {
		return DailyPuzzleWordle.getHintPenaltyUsedCount(state.hintUsed, MUTANT_SCREEN_CONFIG.firstStepHintPenaltyGuesses);
	}

	function getDisplayGuesses() {
		if (!state.pathwayOrder) {
			return state.guesses;
		}
		return DailyPuzzleWordle.getDisplayGuesses(
			state.guesses,
			state.hintUsed,
			MUTANT_SCREEN_CONFIG.numMetabolites,
			state.pathwayOrder[0]
		);
	}

	function renderBoard() {
		DailyPuzzleWordle.renderBoard(boardEl, {
			wordLen: MUTANT_SCREEN_CONFIG.numMetabolites,
			maxRows: MUTANT_SCREEN_CONFIG.maxGuesses,
			guesses: getDisplayGuesses(),
			currentGuess: state.currentGuess,
			gameOver: state.gameOver,
			hideWhenEmpty: true
		});
	}

	function renderKeyboard() {
		if (!window.DailyPuzzleKeyboard) {
			return;
		}

		var allowed = {};
		var i = 0;
		for (i = 0; i < state.pathwayOrder.length; i += 1) {
			allowed[state.pathwayOrder[i]] = true;
		}

		window.DailyPuzzleKeyboard.renderKeyboard(state.letterState, {
			containerId: "keyboard",
			isKeyDisabled: function (ch) {
				return !allowed[ch];
			}
		});
	}

	function renderProblem() {
		var metabolitesText = listToText(state.growthData.metabolites);

		summaryEl.innerHTML =
			"<p>Five <em>Neurospora</em> auxotrophic mutant classes are each blocked at a different biosynthetic step. " +
			"The table shows growth (+) or no growth (&ndash;) when supplemented with intermediates: " + metabolitesText + ". " +
			"<strong>Hint</strong>: The correct pathway order spells an English word.</p>";

		tableEl.innerHTML = "";

		var table = document.createElement("table");
		table.className = "ms-table";

		// Header row: empty corner + metabolite columns
		var theadRow = document.createElement("tr");
		var corner = document.createElement("th");
		corner.textContent = "";
		theadRow.appendChild(corner);

		var col = 0;
		for (col = 0; col < state.growthData.metabolites.length; col += 1) {
			var th = document.createElement("th");
			th.textContent = state.growthData.metabolites[col];
			th.className = "ms-metabolite-header";
			theadRow.appendChild(th);
		}
		table.appendChild(theadRow);

		// Data rows: one per class
		var row = 0;
		for (row = 0; row < state.growthData.classes.length; row += 1) {
			var classInfo = state.growthData.classes[row];

			var tr = document.createElement("tr");

			var rowHead = document.createElement("th");
			rowHead.textContent = "Class " + String(classInfo.classNum);
			rowHead.className = "ms-class-label";
			tr.appendChild(rowHead);

			for (col = 0; col < classInfo.growth.length; col += 1) {
				var td = document.createElement("td");
				td.className = "ms-cell";
				if (classInfo.growth[col]) {
					td.textContent = "+";
					td.className += " ms-grows";
				} else {
					td.innerHTML = "&ndash;";
					td.className += " ms-no-grow";
				}
				tr.appendChild(td);
			}

			table.appendChild(tr);
		}

		tableEl.appendChild(table);
	}

	function renderHintArea() {
		var remaining = DailyPuzzleUI.computeRemainingGuesses(
			MUTANT_SCREEN_CONFIG.maxGuesses,
			state.guesses.length,
			getHintPenaltyUsedCount()
		);

		DailyPuzzleUI.renderPenaltyHint({
			buttonEl: hintButton,
			statusEl: hintStatusEl,
			isRevealed: state.hintUsed,
			isGameOver: state.gameOver,
			isEligible: state.guesses.length === 0 && state.currentGuess.length === 0,
			remaining: remaining,
			minRemainingAfterHint: 1,
			revealedText: "Hint revealed: first metabolite in the pathway is " + state.pathwayOrder[0] + " (-1 guess).",
			unavailableText: "Hint unavailable (not enough guesses remaining)."
		});
	}

	function isValidGuess(raw) {
		var guess = raw.toUpperCase().replace(/[^A-Z]/g, "");
		if (guess.length !== MUTANT_SCREEN_CONFIG.numMetabolites) {
			return false;
		}

		var allowed = {};
		var i = 0;
		for (i = 0; i < state.pathwayOrder.length; i += 1) {
			allowed[state.pathwayOrder[i]] = true;
		}

		var used = {};
		for (i = 0; i < guess.length; i += 1) {
			var ch = guess[i];
			if (!allowed[ch]) {
				return false;
			}
			if (used[ch]) {
				return false;
			}
			used[ch] = true;
		}

		return true;
	}

	function onSubmitGuess() {
		if (state.gameOver) {
			return;
		}

		if (!isValidGuess(state.currentGuess)) {
			showToast("Use each metabolite letter exactly once.");
			return;
		}

		var guess = state.currentGuess.toUpperCase().replace(/[^A-Z]/g, "");
		var answer = state.answerWord;

		var result = scoreGuess(guess, answer);
		state.guesses.push({ guess: guess, result: result });
		updateLetterState(guess, result);
		state.currentGuess = "";

		renderBoard();
		renderKeyboard();
		renderHintArea();

		if (guess === answer) {
			state.gameOver = true;
			messageEl.textContent = "Solved! Pathway: " + answer;
			var winGuessCount = state.guesses.length + getHintPenaltyUsedCount();
			statsStore.updateOnGameEnd(true, state.dayKey, winGuessCount);
			statsStore.renderStats("stats");
			window.setTimeout(function () {
				statsStore.showGameEndModal({
					win: true, guessNumber: winGuessCount,
					maxGuesses: MUTANT_SCREEN_CONFIG.maxGuesses, gameName: "Mutant Screen"
				});
			}, 600);
			renderHintArea();
			return;
		}

		if (state.guesses.length + getHintPenaltyUsedCount() >= MUTANT_SCREEN_CONFIG.maxGuesses) {
			state.gameOver = true;
			messageEl.textContent = "Out of guesses. Pathway: " + answer;
			statsStore.updateOnGameEnd(false, state.dayKey);
			statsStore.renderStats("stats");
			window.setTimeout(function () {
				statsStore.showGameEndModal({
					win: false, maxGuesses: MUTANT_SCREEN_CONFIG.maxGuesses, gameName: "Mutant Screen"
				});
			}, 600);
			renderHintArea();
			return;
		}

		messageEl.textContent = "";
	}

	function onHintClick() {
		if (state.gameOver || state.hintUsed) {
			return;
		}

		if (state.guesses.length > 0) {
			showToast("Hint is only available before your first guess.");
			return;
		}

		if (state.currentGuess.length > 0) {
			return;
		}

		var remaining = MUTANT_SCREEN_CONFIG.maxGuesses - state.guesses.length;
		if (remaining <= 1) {
			showToast("Not enough guesses remaining for a hint.");
			return;
		}

		state.hintUsed = true;
		state.currentGuess = state.pathwayOrder[0];
		state.letterState[state.pathwayOrder[0]] = "correct";
		showToast("Hint: the first metabolite is " + state.pathwayOrder[0] + " (-1 guess)");
		renderBoard();
		renderKeyboard();
		renderHintArea();

		if (state.guesses.length + getHintPenaltyUsedCount() >= MUTANT_SCREEN_CONFIG.maxGuesses) {
			state.gameOver = true;
			messageEl.textContent = "Out of guesses. Pathway: " + state.answerWord;
			statsStore.updateOnGameEnd(false, state.dayKey);
			statsStore.renderStats("stats");
			window.setTimeout(function () {
				statsStore.showGameEndModal({
					win: false, maxGuesses: MUTANT_SCREEN_CONFIG.maxGuesses, gameName: "Mutant Screen"
				});
			}, 600);
			renderHintArea();
		}
	}

	function onKeyInput(key) {
		if (state.gameOver) {
			return;
		}

		if (key === "ENTER") {
			onSubmitGuess();
			return;
		}

		if (key === "BACKSPACE") {
			state.currentGuess = state.currentGuess.slice(0, -1);
			renderBoard();
			return;
		}

		if (!/^[A-Z]$/.test(key)) {
			return;
		}

		var ch = key.toUpperCase();
		if (state.currentGuess.length >= MUTANT_SCREEN_CONFIG.numMetabolites) {
			return;
		}

		if (state.currentGuess.indexOf(ch) >= 0) {
			showToast("Each metabolite can be used once.");
			return;
		}

		if (state.pathwayOrder.indexOf(ch) < 0) {
			showToast("That letter is not in today's metabolite set.");
			return;
		}

		state.currentGuess += ch;
		renderBoard();
	}

	function attachEventHandlers() {
		if (window.DailyPuzzleInput) {
			window.DailyPuzzleInput.install({
				isEnabled: function () { return !state.gameOver; },
				onType: function (ch) { onKeyInput(ch); },
				onEnter: function () { onKeyInput("ENTER"); },
				onBackspace: function () { onKeyInput("BACKSPACE"); }
			});
		}

		if (window.DailyPuzzleKeyboard) {
			window.DailyPuzzleKeyboard.attachKeyboardClick(function (key) {
				onKeyInput(key);
			}, { containerId: "keyboard" });
		}

		hintButton.addEventListener("click", function () {
			onHintClick();
		});
	}

	async function init() {
		initLetterState();
		statsStore.renderStats("stats");
		messageEl.textContent = "Loading today's puzzle...";

		var words = await MutantScreenWords.loadCandidateWords(MUTANT_SCREEN_CONFIG.numMetabolites);
		var answerWord = MutantScreenWords.getDailyWord(words, new Date());

		state.answerWord = answerWord;
		state.pathwayOrder = answerWord.split("");

		var tableSeed = MutantScreenWords.getDailySeed("table", answerWord, new Date());
		var growthData = MutantScreenLogic.generateGrowthTable(state.pathwayOrder, tableSeed);
		state.growthData = growthData;

		messageEl.textContent = "";
		renderProblem();
		renderBoard();
		renderKeyboard();
		renderHintArea();
		attachEventHandlers();
	}

	init().catch(function (e) {
		console.error(e);
		messageEl.textContent = "Error: could not load today's puzzle.";
	});
}

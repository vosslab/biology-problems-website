"use strict";

/* global DailyPuzzleCore, DailyPuzzleStats, DailyPuzzleKeyboard, DailyPuzzleUI, DailyPuzzleWordle, DeletionMutantsWords, DailyPuzzleColors, DeletionMutantsLogic */

var DELETION_MUTANTS_CONFIG = {
	numGenes: 5,
	maxGuesses: 4,
	firstGeneHintPenaltyGuesses: 1
};

function deletionMutantsSetupGame() {
	var rootEl = document.getElementById("dm-root");
	var messageEl = document.getElementById("message");
	var hintButton = document.getElementById("hint-button");
	var hintStatusEl = document.getElementById("hint-status");
	var tableEl = document.getElementById("deletion-table");
	var listEl = document.getElementById("deletion-list");
	var summaryEl = document.getElementById("problem-summary");
	var boardEl = document.getElementById("board");
	var keyboardEl = document.getElementById("keyboard");

	if (!rootEl || !messageEl || !hintButton || !hintStatusEl || !tableEl || !listEl || !summaryEl || !boardEl || !keyboardEl) {
		return;
	}

	var dayKey = DailyPuzzleCore.getUtcDayKey(new Date());
	var statsStore = DailyPuzzleStats.createStore("deletion_mutants_stats_v1", DELETION_MUTANTS_CONFIG.maxGuesses);
	var _toaster = null;

	var state = {
		dayKey: dayKey,
		answerWord: null,
		geneOrder: null,
		deletionsList: null,
		deletionColorMap: null,
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
		return DailyPuzzleWordle.getHintPenaltyUsedCount(state.hintUsed, DELETION_MUTANTS_CONFIG.firstGeneHintPenaltyGuesses);
	}

	function getDisplayGuesses() {
		if (!state.geneOrder) {
			return state.guesses;
		}
		return DailyPuzzleWordle.getDisplayGuesses(
			state.guesses,
			state.hintUsed,
			DELETION_MUTANTS_CONFIG.numGenes,
			state.geneOrder[0]
		);
	}

	function renderBoard() {
		DailyPuzzleWordle.renderBoard(boardEl, {
			wordLen: DELETION_MUTANTS_CONFIG.numGenes,
			maxRows: DELETION_MUTANTS_CONFIG.maxGuesses,
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
		for (i = 0; i < state.geneOrder.length; i += 1) {
			allowed[state.geneOrder[i]] = true;
		}

		window.DailyPuzzleKeyboard.renderKeyboard(state.letterState, {
			containerId: "keyboard",
			isKeyDisabled: function (ch) {
				return !allowed[ch];
			}
		});
	}

	function renderProblem() {
		var sortedGenes = state.geneOrder.slice().sort();
		var genesText = listToText(sortedGenes);

		summaryEl.innerHTML =
			"<p>Genes " + genesText + " are closely linked on one chromosome. " +
			"The deletions below uncover recessive alleles of these genes. " +
			"<strong>Hint</strong>: The correct gene order spells an English word.</p>";

		tableEl.innerHTML = "";

		var table = document.createElement("table");
		table.className = "dm-table";

		var theadRow = document.createElement("tr");
		var corner = document.createElement("th");
		corner.textContent = "";
		theadRow.appendChild(corner);

		var col = 0;
		for (col = 0; col < state.geneOrder.length; col += 1) {
			var th = document.createElement("th");
			th.textContent = "Gene " + String(col + 1);
			theadRow.appendChild(th);
		}
		table.appendChild(theadRow);

		var row = 0;
		for (row = 0; row < state.deletionsList.length; row += 1) {
			var deletion = state.deletionsList[row];
			var key = deletion.slice().sort().join("");
			var colorEntry = state.deletionColorMap[key];

			var tr = document.createElement("tr");
			tr.className = "dm-del-scheme";
			if (colorEntry) {
				tr.style.setProperty("--dm-fill-light", colorEntry.light);
				tr.style.setProperty("--dm-fill-dark", colorEntry.dark);
				tr.style.setProperty("--dm-label-light", colorEntry.dark);
				tr.style.setProperty("--dm-label-dark", colorEntry.light);
			}

			var rowHead = document.createElement("th");
			rowHead.textContent = "Del #" + String(row + 1);
			rowHead.className = "dm-del-label";
			tr.appendChild(rowHead);

			for (col = 0; col < state.geneOrder.length; col += 1) {
				var gene = state.geneOrder[col];
				var td = document.createElement("td");
				td.className = "dm-cell";
				var inDel = deletion.indexOf(gene) >= 0;
				if (inDel) {
					td.className = "dm-cell dm-filled";

					var prevGene = col > 0 ? state.geneOrder[col - 1] : null;
					var nextGene = col + 1 < state.geneOrder.length ? state.geneOrder[col + 1] : null;

					var prevIn = prevGene && deletion.indexOf(prevGene) >= 0;
					var nextIn = nextGene && deletion.indexOf(nextGene) >= 0;

					if (!prevIn) {
						td.className += " dm-run-start";
					}
					if (!nextIn) {
						td.className += " dm-run-end";
					}
				}
				tr.appendChild(td);
			}

			table.appendChild(tr);
		}

		tableEl.appendChild(table);

		listEl.innerHTML = "";
		var ul = document.createElement("ul");
		ul.className = "dm-deletion-list";

		for (row = 0; row < state.deletionsList.length; row += 1) {
			var del = state.deletionsList[row];
			var delKey = del.slice().sort().join("");
			var delColorEntry = state.deletionColorMap[delKey];

			var li = document.createElement("li");
			li.className = "dm-del-scheme";
			if (delColorEntry) {
				li.style.setProperty("--dm-fill-light", delColorEntry.light);
				li.style.setProperty("--dm-fill-dark", delColorEntry.dark);
				li.style.setProperty("--dm-label-light", delColorEntry.dark);
				li.style.setProperty("--dm-label-dark", delColorEntry.light);
			}
			var nameSpan = document.createElement("span");
			nameSpan.textContent = "Deletion #" + String(row + 1) + ": ";
			nameSpan.className = "dm-del-name";

			var genesSpan = document.createElement("span");
			genesSpan.textContent = listToText(del.slice().sort());

			li.appendChild(nameSpan);
			li.appendChild(genesSpan);
			ul.appendChild(li);
		}

		listEl.appendChild(ul);
	}

	function renderHintArea() {
		var remaining = DailyPuzzleUI.computeRemainingGuesses(
			DELETION_MUTANTS_CONFIG.maxGuesses,
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
			revealedText: "Hint revealed: first gene is " + state.geneOrder[0] + " (-1 guess).",
			unavailableText: "Hint unavailable (not enough guesses remaining)."
		});
	}

	function isValidGuess(raw) {
		var guess = raw.toUpperCase().replace(/[^A-Z]/g, "");
		if (guess.length !== DELETION_MUTANTS_CONFIG.numGenes) {
			return false;
		}

		var allowed = {};
		var i = 0;
		for (i = 0; i < state.geneOrder.length; i += 1) {
			allowed[state.geneOrder[i]] = true;
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
			showToast("Use each listed gene letter exactly once.");
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
			messageEl.textContent = "Solved! Answer: " + answer;
			var winGuessCount = state.guesses.length + getHintPenaltyUsedCount();
			statsStore.updateOnGameEnd(true, state.dayKey, winGuessCount);
			statsStore.renderStats("stats");
			window.setTimeout(function () {
				statsStore.showGameEndModal({
					win: true, guessNumber: winGuessCount,
					maxGuesses: DELETION_MUTANTS_CONFIG.maxGuesses, gameName: "Deletion Mutants"
				});
			}, 600);
			renderHintArea();
			return;
		}

		if (state.guesses.length + getHintPenaltyUsedCount() >= DELETION_MUTANTS_CONFIG.maxGuesses) {
			state.gameOver = true;
			messageEl.textContent = "Out of guesses. Answer: " + answer;
			statsStore.updateOnGameEnd(false, state.dayKey);
			statsStore.renderStats("stats");
			window.setTimeout(function () {
				statsStore.showGameEndModal({
					win: false, maxGuesses: DELETION_MUTANTS_CONFIG.maxGuesses, gameName: "Deletion Mutants"
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

		var remaining = DELETION_MUTANTS_CONFIG.maxGuesses - state.guesses.length;
		if (remaining <= 1) {
			showToast("Not enough guesses remaining for a hint.");
			return;
		}

		state.hintUsed = true;
		state.currentGuess = state.geneOrder[0];
		state.letterState[state.geneOrder[0]] = "correct";
		showToast("Hint: the first gene is " + state.geneOrder[0] + " (-1 guess)");
		renderBoard();
		renderKeyboard();
		renderHintArea();

		if (state.guesses.length + getHintPenaltyUsedCount() >= DELETION_MUTANTS_CONFIG.maxGuesses) {
			state.gameOver = true;
			messageEl.textContent = "Out of guesses. Answer: " + state.answerWord;
			statsStore.updateOnGameEnd(false, state.dayKey);
			statsStore.renderStats("stats");
			window.setTimeout(function () {
				statsStore.showGameEndModal({
					win: false, maxGuesses: DELETION_MUTANTS_CONFIG.maxGuesses, gameName: "Deletion Mutants"
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
		if (state.currentGuess.length >= DELETION_MUTANTS_CONFIG.numGenes) {
			return;
		}

		if (state.currentGuess.indexOf(ch) >= 0) {
			showToast("Each gene letter can be used once.");
			return;
		}

		if (state.geneOrder.indexOf(ch) < 0) {
			showToast("That letter is not in today's gene set.");
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

		var words = await DeletionMutantsWords.loadCandidateWords(DELETION_MUTANTS_CONFIG.numGenes);
		var answerWord = DeletionMutantsWords.getDailyWord(words, new Date());

		state.answerWord = answerWord;
		state.geneOrder = answerWord.split("");

		var deletionsSeed = DeletionMutantsWords.getDailySeed("deletions", answerWord, new Date());
		var deletionsList = DeletionMutantsLogic.generateDeletions(state.geneOrder, deletionsSeed);

		var rngShuffle = DailyPuzzleCore.makeSeededRng(DeletionMutantsWords.getDailySeed("shuffle", answerWord, new Date()));
		DailyPuzzleCore.shuffleInPlace(deletionsList, rngShuffle);
		state.deletionsList = deletionsList;

		var rngColors = DailyPuzzleCore.makeSeededRng(DeletionMutantsWords.getDailySeed("colors", answerWord, new Date()));
		var colorPairs = DailyPuzzleColors.pickColorPairs(deletionsList.length, rngColors);

		var colorMap = {};
		var i = 0;
		for (i = 0; i < deletionsList.length; i += 1) {
			var key = deletionsList[i].slice().sort().join("");
			colorMap[key] = colorPairs[i];
		}
		state.deletionColorMap = colorMap;

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

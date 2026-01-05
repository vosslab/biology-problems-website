"use strict";

/* global DailyPuzzleCore, DailyPuzzleStats, DeletionMutantsWords, DeletionMutantsColors, DeletionMutantsLogic */

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
	var statsStore = DailyPuzzleStats.createStore("deletion_mutants_stats_v1");

	var state = {
		dayKey: dayKey,
		answerWord: null,
		geneOrder: null,
		deletionsList: null,
		deletionColorMap: null,
		guesses: [],
		currentGuess: "",
		letterState: {},
		hintsUsed: 0,
		firstGeneHintRevealed: false,
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
		var len = answer.length;
		var result = new Array(len).fill("absent");
		var counts = {};
		var i = 0;

		for (i = 0; i < len; i += 1) {
			var a = answer[i];
			var g = guess[i];
			if (g === a) {
				result[i] = "correct";
			} else {
				counts[a] = (counts[a] || 0) + 1;
			}
		}

		for (i = 0; i < len; i += 1) {
			if (result[i] !== "absent") {
				continue;
			}
			var ch = guess[i];
			if (counts[ch] > 0) {
				result[i] = "present";
				counts[ch] -= 1;
			}
		}

		return result;
	}

	function updateLetterState(guess, result) {
		var i = 0;
		for (i = 0; i < guess.length; i += 1) {
			var ch = guess[i];
			var res = result[i];
			var current = state.letterState[ch] || "unknown";

			if (res === "correct") {
				state.letterState[ch] = "correct";
			} else if (res === "present") {
				if (current !== "correct") {
					state.letterState[ch] = "present";
				}
			} else if (res === "absent") {
				if (current === "unknown") {
					state.letterState[ch] = "absent";
				}
			}
		}
	}

	function showToast(text, durationMs) {
		var container = document.getElementById("toast-container");
		if (!container) {
			return;
		}
		var d = durationMs || 1600;

		var el = document.createElement("div");
		el.className = "toast";
		el.textContent = text;
		container.appendChild(el);

		void el.offsetWidth;
		el.classList.add("show");

		window.setTimeout(function () {
			el.classList.remove("show");
			window.setTimeout(function () {
				if (el.parentNode === container) {
					container.removeChild(el);
				}
			}, 200);
		}, d);
	}

	function renderBoard() {
		var rows = DELETION_MUTANTS_CONFIG.maxGuesses;
		var wordLen = DELETION_MUTANTS_CONFIG.numGenes;

		boardEl.innerHTML = "";

		var rowIndex = 0;
		for (rowIndex = 0; rowIndex < rows; rowIndex += 1) {
			var row = document.createElement("div");
			row.className = "row";

			var text = "";
			var result = null;
			var pending = false;

			if (rowIndex < state.guesses.length) {
				text = state.guesses[rowIndex].guess;
				result = state.guesses[rowIndex].result;
			} else if (rowIndex === state.guesses.length && state.currentGuess) {
				text = state.currentGuess;
				pending = true;
			}

			var col = 0;
			for (col = 0; col < wordLen; col += 1) {
				var cell = document.createElement("span");
				var ch = text[col] || "";
				cell.textContent = ch;

				var cls = "cell";
				if (result) {
					cls += " " + result[col];
				} else if (pending && ch) {
					cls += " pending";
				} else {
					cls += " empty";
				}
				cell.className = cls;
				row.appendChild(cell);
			}

			boardEl.appendChild(row);
		}
	}

	function renderKeyboard() {
		keyboardEl.innerHTML = "";

		var allowed = {};
		var i = 0;
		for (i = 0; i < state.geneOrder.length; i += 1) {
			allowed[state.geneOrder[i]] = true;
		}

		var rows = [
			"QWERTYUIOP",
			"ASDFGHJKL",
			"ZXCVBNM"
		];

		function createRow(letters, isBottom) {
			var rowEl = document.createElement("div");
			rowEl.className = "kb-row";

			if (isBottom) {
				var enterKey = document.createElement("button");
				enterKey.type = "button";
				enterKey.className = "kb-key wide";
				enterKey.textContent = "Enter";
				enterKey.dataset.key = "ENTER";
				rowEl.appendChild(enterKey);
			}

			var j = 0;
			for (j = 0; j < letters.length; j += 1) {
				var ch = letters[j];
				var key = document.createElement("button");
				key.type = "button";

				var cls = "kb-key";
				if (!allowed[ch]) {
					cls += " invalid";
					key.disabled = true;
				} else {
					var st = state.letterState[ch];
					if (st === "correct") {
						cls += " correct";
					} else if (st === "present") {
						cls += " present";
					} else if (st === "absent") {
						cls += " absent";
					}
				}

				key.className = cls;
				key.textContent = ch;
				key.dataset.key = ch;
				rowEl.appendChild(key);
			}

			if (isBottom) {
				var backKey = document.createElement("button");
				backKey.type = "button";
				backKey.className = "kb-key wide";
				backKey.textContent = "DEL";
				backKey.dataset.key = "BACKSPACE";
				rowEl.appendChild(backKey);
			}

			return rowEl;
		}

		keyboardEl.appendChild(createRow(rows[0], false));
		keyboardEl.appendChild(createRow(rows[1], false));
		keyboardEl.appendChild(createRow(rows[2], true));
	}

	function renderProblem() {
		var sortedGenes = state.geneOrder.slice().sort();
		var genesText = listToText(sortedGenes);

		var hintText = "<p><strong>Hint</strong>: The correct answer is an English dictionary word.</p>";

		summaryEl.innerHTML =
			"<p>There are " + state.geneOrder.length + " genes, " + genesText + ", closely linked on one chromosome.</p>" +
			"<p>The deletions below uncover recessive alleles of the genes as follows.</p>" +
			hintText;

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
				tr.style.setProperty("--dm-fill-light", colorEntry.extraLight);
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
				if (deletion.indexOf(gene) >= 0) {
					td.className = "dm-cell dm-filled";
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
				li.style.setProperty("--dm-fill-light", delColorEntry.extraLight);
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
		var remaining = DELETION_MUTANTS_CONFIG.maxGuesses - (state.guesses.length + state.hintsUsed);
		var status = "";

		if (state.firstGeneHintRevealed) {
			status = "Hint revealed: first gene is " + state.geneOrder[0] + ".";
			hintButton.disabled = true;
		} else if (state.gameOver) {
			hintButton.disabled = true;
		} else if (remaining <= 1) {
			status = "Hint unavailable (not enough guesses remaining).";
			hintButton.disabled = true;
		} else {
			hintButton.disabled = false;
		}

		hintStatusEl.textContent = status;
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
			statsStore.updateOnGameEnd(true, state.dayKey);
			statsStore.renderStats("stats");
			renderHintArea();
			return;
		}

		if (state.guesses.length + state.hintsUsed >= DELETION_MUTANTS_CONFIG.maxGuesses) {
			state.gameOver = true;
			messageEl.textContent = "Out of guesses. Answer: " + answer;
			statsStore.updateOnGameEnd(false, state.dayKey);
			statsStore.renderStats("stats");
			renderHintArea();
			return;
		}

		messageEl.textContent = "";
	}

	function onHintClick() {
		if (state.gameOver || state.firstGeneHintRevealed) {
			return;
		}

		var remaining = DELETION_MUTANTS_CONFIG.maxGuesses - (state.guesses.length + state.hintsUsed);
		if (remaining <= 1) {
			showToast("Not enough guesses remaining for a hint.");
			return;
		}

		state.firstGeneHintRevealed = true;
		state.hintsUsed += DELETION_MUTANTS_CONFIG.firstGeneHintPenaltyGuesses;
		showToast("Hint: the first gene is " + state.geneOrder[0] + " (-1 guess)");
		renderHintArea();

		if (state.guesses.length + state.hintsUsed >= DELETION_MUTANTS_CONFIG.maxGuesses) {
			state.gameOver = true;
			messageEl.textContent = "Out of guesses. Answer: " + state.answerWord;
			statsStore.updateOnGameEnd(false, state.dayKey);
			statsStore.renderStats("stats");
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
		document.addEventListener("keydown", function (e) {
			if (e.key === "Enter") {
				e.preventDefault();
				onKeyInput("ENTER");
				return;
			}
			if (e.key === "Backspace") {
				e.preventDefault();
				onKeyInput("BACKSPACE");
				return;
			}
			if (/^[a-zA-Z]$/.test(e.key)) {
				onKeyInput(e.key.toUpperCase());
			}
		});

		keyboardEl.addEventListener("click", function (e) {
			var target = e.target;
			if (!target || target.tagName !== "BUTTON") {
				return;
			}
			var key = target.dataset.key;
			if (key) {
				onKeyInput(key);
			}
		});

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
		var colorPairs = DeletionMutantsColors.pickColorPairs(deletionsList.length, rngColors);

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

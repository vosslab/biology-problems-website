"use strict";

(function () {
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

	function updateLetterState(guess, result, letterState) {
		var i = 0;
		for (i = 0; i < guess.length; i += 1) {
			var ch = guess[i];
			var res = result[i];
			var current = letterState[ch] || "unknown";

			if (res === "correct") {
				letterState[ch] = "correct";
			} else if (res === "present") {
				if (current !== "correct") {
					letterState[ch] = "present";
				}
			} else if (res === "absent") {
				if (current === "unknown") {
					letterState[ch] = "absent";
				}
			}
		}
	}

	function createToaster(containerId, defaultDurationMs) {
		var id = containerId || "toast-container";
		var defaultMs = defaultDurationMs || 1600;

		return function showToast(text, durationMs) {
			var container = document.getElementById(id);
			if (!container) {
				return;
			}
			var d = durationMs || defaultMs;

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
		};
	}

	function buildHintPenaltyRow(wordLen, hintChar) {
		var res = new Array(wordLen).fill("empty");
		res[0] = "correct";
		return { guess: hintChar, result: res, type: "penalty" };
	}

	function getHintPenaltyUsedCount(hintUsed, penaltyGuesses) {
		return hintUsed ? (penaltyGuesses || 1) : 0;
	}

	function getDisplayGuesses(guesses, hintUsed, wordLen, hintChar) {
		if (!hintUsed) {
			return guesses;
		}
		return [buildHintPenaltyRow(wordLen, hintChar)].concat(guesses);
	}

	function canUseHintPenalty(opts) {
		var maxGuesses = opts.maxGuesses;
		var guessesUsed = opts.guessesUsed || 0;
		var hintUsed = Boolean(opts.hintUsed);
		var currentGuess = opts.currentGuess || "";
		var gameOver = Boolean(opts.gameOver);
		var penaltyGuesses = opts.penaltyGuesses || 1;
		var minRemainingAfterHint = opts.minRemainingAfterHint;

		if (minRemainingAfterHint === undefined || minRemainingAfterHint === null) {
			minRemainingAfterHint = 1;
		}

		if (hintUsed) {
			return { canUse: false, reason: "revealed" };
		}
		if (gameOver) {
			return { canUse: false, reason: "game_over" };
		}
		if (opts.requireNoGuessesYet !== false && guessesUsed > 0) {
			return { canUse: false, reason: "after_first_guess" };
		}
		if (opts.requireEmptyCurrentGuess !== false && currentGuess.length > 0) {
			return { canUse: false, reason: "current_guess_not_empty" };
		}

		var remainingBefore = maxGuesses - guessesUsed;
		if (remainingBefore - penaltyGuesses < minRemainingAfterHint) {
			return { canUse: false, reason: "not_enough_guesses" };
		}

		return { canUse: true, reason: null };
	}

	function renderBoard(containerEl, opts) {
		var el = containerEl;
		if (typeof containerEl === "string") {
			el = document.getElementById(containerEl);
		}
		if (!el) {
			return;
		}

		var wordLen = opts.wordLen;
		var maxRows = opts.maxRows;
		var guesses = opts.guesses || [];
		var currentGuess = opts.currentGuess || "";
		var gameOver = Boolean(opts.gameOver);
		var hideWhenEmpty = Boolean(opts.hideWhenEmpty);

		var shouldShow = true;
		if (hideWhenEmpty) {
			shouldShow = guesses.length > 0 || currentGuess.length > 0 || gameOver;
		}

		el.style.display = shouldShow ? "" : "none";
		if (!shouldShow) {
			el.innerHTML = "";
			return;
		}

		var rowsToShow = 0;
		if (gameOver && guesses.length > 0) {
			rowsToShow = maxRows;
		} else {
			rowsToShow = guesses.length + (gameOver ? 0 : 1);
			rowsToShow = Math.max(1, Math.min(rowsToShow, maxRows));
		}

		el.innerHTML = "";

		var rowIndex = 0;
		for (rowIndex = 0; rowIndex < rowsToShow; rowIndex += 1) {
			var row = document.createElement("div");
			row.className = "row";

			var text = "";
			var result = null;
			var pending = false;

			if (rowIndex < guesses.length) {
				text = guesses[rowIndex].guess;
				result = guesses[rowIndex].result;
				if (guesses[rowIndex].type === "penalty") {
					row.className += " dp-penalty-row";
				}
			} else if (rowIndex === guesses.length && currentGuess) {
				text = currentGuess;
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

			el.appendChild(row);
		}
	}

	window.DailyPuzzleWordle = {
		scoreGuess: scoreGuess,
		updateLetterState: updateLetterState,
		createToaster: createToaster,
		buildHintPenaltyRow: buildHintPenaltyRow,
		getHintPenaltyUsedCount: getHintPenaltyUsedCount,
		getDisplayGuesses: getDisplayGuesses,
		canUseHintPenalty: canUseHintPenalty,
		renderBoard: renderBoard
	};
}());


"use strict";

// Letters not allowed for amino acid guesses
const INVALID_LETTERS = {
    B: true,
    X: true,
    Z: true,
    J: true,
    O: true,
    U: true,
    P: true  // Proline excluded by design
};

// Simple letter state for keyboard colouring
const LETTER_STATE = {};
const MAX_GUESSES = 3;
const FIRST_LETTER_HINT_PENALTY = 1;
let _peptidyleToaster = null;

(function initLetterState() {
    const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    for (let i = 0; i < letters.length; i += 1) {
        LETTER_STATE[letters[i]] = "unknown";
    }
}());

//=================================================
// Scoring and validation
//=================================================
function scoreGuess(guess, answer) {
    if (!window.DailyPuzzleWordle) {
        return [];
    }
    return window.DailyPuzzleWordle.scoreGuess(guess, answer);
}

// peptide specific validator: any valid amino acid sequence of length 5
function isValidPeptideGuess(guess) {
    if (guess.length !== 5) {
        return false;
    }
    if (!/^[A-Z]{5}$/.test(guess)) {
        return false;
    }
    for (let i = 0; i < guess.length; i += 1) {
        const ch = guess[i];
        if (INVALID_LETTERS[ch]) {
            return false;
        }
        if (!aminoAcidMapping[ch]) {
            return false;
        }
    }
    return true;
}

//=================================================
// Board rendering: show previous guesses + currentGuess + empty rows
//=================================================
function renderBoard(container, guesses, currentGuess, maxRows, gameOver) {
    if (!window.DailyPuzzleWordle) {
        return;
    }
    window.DailyPuzzleWordle.renderBoard(container, {
        wordLen: 5,
        maxRows: maxRows || 3,
        guesses: guesses || [],
        currentGuess: currentGuess || "",
        gameOver: Boolean(gameOver),
        hideWhenEmpty: true
    });
}

//=================================================
// Keyboard state and rendering
//=================================================
function updateLetterState(guess, result, letterState) {
    if (!window.DailyPuzzleWordle) {
        return;
    }
    window.DailyPuzzleWordle.updateLetterState(guess, result, letterState);
}

function renderKeyboard(letterState) {
    if (!window.DailyPuzzleKeyboard) {
        return;
    }
    window.DailyPuzzleKeyboard.renderKeyboard(letterState, {
        containerId: "keyboard",
        isKeyDisabled: function (ch) {
            return Boolean(INVALID_LETTERS[ch]);
        }
    });
}

//=================================================
// Toast messages
//=================================================
function showToast(text, durationMs) {
    if (!window.DailyPuzzleWordle) {
        return;
    }
    if (!_peptidyleToaster) {
        _peptidyleToaster = window.DailyPuzzleWordle.createToaster("toast-container", 1500);
    }
    _peptidyleToaster(text, durationMs);
}

//=================================================
// Game setup and main loop
//=================================================
function setupGame() {
    const dayKey = window.DailyPuzzleCore
        ? window.DailyPuzzleCore.getUtcDayKey(new Date())
        : new Date().toISOString().slice(0, 10);

    let answer = window.PeptidyleWords
        ? window.PeptidyleWords.getDailyWord(new Date())
        : getDailyWord(); // uppercase

    // Optional override from URL: ?seq=ACRID
    if (window.PEPTIDYL_OVERRIDE) {
        answer = window.PEPTIDYL_OVERRIDE.toUpperCase();
    }

    const maxGuesses = MAX_GUESSES;

    renderSequence(answer, "peptide"); // from peptidyl_peptides.js

    const statsStore = window.DailyPuzzleStats
        ? window.DailyPuzzleStats.createStore("peptidyle_stats_v1", maxGuesses)
        : null;
    if (statsStore) {
        statsStore.renderStats("stats");
    }

    const hintButton = document.getElementById("hint-button");
    const hintStatusEl = document.getElementById("hint-status");

    const form = document.getElementById("guess-form");
    const input = document.getElementById("guess");
    const message = document.getElementById("message");
    const board = document.getElementById("board");

    let guesses = [];
    let finished = false;
    let currentGuess = "";
    let hintUsed = false;

    function getDisplayGuesses() {
        if (!window.DailyPuzzleWordle) {
            return guesses;
        }
        return window.DailyPuzzleWordle.getDisplayGuesses(guesses, hintUsed, 5, answer[0]);
    }

    // keep hidden input in sync but it is not shown
    input.value = "";

    renderBoard(board, getDisplayGuesses(), currentGuess, maxGuesses, finished);
    renderKeyboard(LETTER_STATE);

    function renderHintArea() {
        if (!hintButton || !hintStatusEl) {
            return;
        }
        const hintsUsedCount = window.DailyPuzzleWordle
            ? window.DailyPuzzleWordle.getHintPenaltyUsedCount(hintUsed, FIRST_LETTER_HINT_PENALTY)
            : 0;

        const remaining = window.DailyPuzzleUI
            ? window.DailyPuzzleUI.computeRemainingGuesses(maxGuesses, guesses.length, hintsUsedCount)
            : (maxGuesses - (guesses.length + hintsUsedCount));

        const revealedText = "Hint revealed: first letter is " + answer[0] + " (-1 guess).";
        const unavailableText = "Hint unavailable (not enough guesses remaining).";

        if (window.DailyPuzzleUI) {
            window.DailyPuzzleUI.renderPenaltyHint({
                buttonEl: hintButton,
                statusEl: hintStatusEl,
                isRevealed: hintUsed,
                isGameOver: finished,
                isEligible: guesses.length === 0 && currentGuess.length === 0,
                remaining: remaining,
                minRemainingAfterHint: 1,
                revealedText: revealedText,
                unavailableText: unavailableText
            });
            return;
        }

        if (hintUsed) {
            hintButton.disabled = true;
            hintStatusEl.textContent = revealedText;
            return;
        }
        if (finished || guesses.length > 0 || currentGuess.length > 0 || remaining <= 1) {
            hintButton.disabled = true;
            hintStatusEl.textContent = remaining <= 1 ? unavailableText : "";
            return;
        }
        hintButton.disabled = false;
        hintStatusEl.textContent = "";
    }

    function onHintClick() {
        if (finished || hintUsed) {
            return;
        }
        if (guesses.length > 0) {
            showToast("Hint is only available before your first guess.");
            renderHintArea();
            return;
        }
        if (currentGuess.length > 0) {
            return;
        }
        const remaining = maxGuesses - guesses.length;
        if (remaining <= 1) {
            showToast("Not enough guesses remaining for a hint.");
            renderHintArea();
            return;
        }

        hintUsed = true;
        if (currentGuess.length === 0) {
            currentGuess = answer[0];
            input.value = currentGuess;
        }
        LETTER_STATE[answer[0]] = "correct";
        showToast("Hint: first letter is " + answer[0] + " (-1 guess)");
        renderBoard(board, getDisplayGuesses(), currentGuess, maxGuesses, finished);
        renderKeyboard(LETTER_STATE);
        renderHintArea();

        const hintsUsedCount = window.DailyPuzzleWordle
            ? window.DailyPuzzleWordle.getHintPenaltyUsedCount(hintUsed, FIRST_LETTER_HINT_PENALTY)
            : FIRST_LETTER_HINT_PENALTY;

        if (guesses.length + hintsUsedCount >= maxGuesses) {
            message.textContent = "Out of guesses. Answer was " + answer + ".";
            showToast("Answer was " + answer + ".");
            if (statsStore) {
                statsStore.updateOnGameEnd(false, dayKey);
                statsStore.renderStats("stats");
                window.setTimeout(function () {
                    statsStore.showGameEndModal({
                        win: false, maxGuesses: maxGuesses, gameName: "Peptidyle"
                    });
                }, 600);
            }
            finished = true;
        }
    }

    if (hintButton) {
        hintButton.addEventListener("click", function () {
            onHintClick();
        });
    }

    renderHintArea();

    function submitGuess() {
        if (finished) {
            return;
        }
        const guess = currentGuess.toUpperCase();

        if (guess.length !== 5) {
            showToast("Guess must be 5 letters.");
            return;
        }
        if (!isValidPeptideGuess(guess)) {
            showToast("Not a valid peptide sequence.");
            return;
        }

        const result = scoreGuess(guess, answer);
        guesses.push({ guess: guess, result: result });
        currentGuess = "";
        input.value = "";
        renderBoard(board, getDisplayGuesses(), currentGuess, maxGuesses, finished);
        updateLetterState(guess, result, LETTER_STATE);
        renderKeyboard(LETTER_STATE);

        if (result.every(function (x) { return x === "correct"; })) {
            message.textContent = "Correct.";
            showToast("Correct.");
            var winGuessCount = guesses.length + (hintUsed ? FIRST_LETTER_HINT_PENALTY : 0);
            if (statsStore) {
                statsStore.updateOnGameEnd(true, dayKey, winGuessCount);
                statsStore.renderStats("stats");
                window.setTimeout(function () {
                    statsStore.showGameEndModal({
                        win: true, guessNumber: winGuessCount,
                        maxGuesses: maxGuesses, gameName: "Peptidyle"
                    });
                }, 600);
            }
            renderHintArea();
            finished = true;
            return;
        }
        const hintsUsedCount = window.DailyPuzzleWordle
            ? window.DailyPuzzleWordle.getHintPenaltyUsedCount(hintUsed, FIRST_LETTER_HINT_PENALTY)
            : 0;

        if (guesses.length + hintsUsedCount >= maxGuesses) {
            message.textContent = "Out of guesses. Answer was " + answer + ".";
            showToast("Answer was " + answer + ".");
            if (statsStore) {
                statsStore.updateOnGameEnd(false, dayKey);
                statsStore.renderStats("stats");
                window.setTimeout(function () {
                    statsStore.showGameEndModal({
                        win: false, maxGuesses: maxGuesses, gameName: "Peptidyle"
                    });
                }, 600);
            }
            renderHintArea();
            finished = true;
            return;
        }
        message.textContent = "";
        renderHintArea();
    }

    // Hidden form, in case someone actually hits Enter in it
    form.addEventListener("submit", function (evt) {
        evt.preventDefault();
        submitGuess();
    });

    function handleType(ch) {
        if (finished) {
            return;
        }
        if (INVALID_LETTERS[ch]) {
            return;
        }
        if (currentGuess.length >= 5) {
            return;
        }
        currentGuess += ch;
        input.value = currentGuess;
        renderBoard(board, getDisplayGuesses(), currentGuess, maxGuesses, finished);
    }

    function handleBackspace() {
        if (finished) {
            return;
        }
        currentGuess = currentGuess.slice(0, -1);
        input.value = currentGuess;
        renderBoard(board, getDisplayGuesses(), currentGuess, maxGuesses, finished);
    }

    function handleEnter() {
        submitGuess();
    }

    // On screen keyboard
    if (window.DailyPuzzleKeyboard) {
        window.DailyPuzzleKeyboard.attachKeyboardClick(function (k) {
            if (k === "ENTER") {
                handleEnter();
            } else if (k === "BACKSPACE") {
                handleBackspace();
            } else if (/^[A-Z]$/.test(k)) {
                handleType(k);
            }
        }, { containerId: "keyboard" });
    }

    // Physical keyboard
    if (window.DailyPuzzleInput) {
        window.DailyPuzzleInput.install({
            isEnabled: function () { return !finished; },
            onType: handleType,
            onEnter: handleEnter,
            onBackspace: handleBackspace,
            isBlockedTarget: function (el) {
                if (!el) {
                    return false;
                }
                if (el.isContentEditable) {
                    return true;
                }
                var tag = (el.tagName || "").toLowerCase();
                if (tag === "input" || tag === "textarea" || tag === "select") {
                    return el.id !== "guess";
                }
                return false;
            }
        });
    }
}

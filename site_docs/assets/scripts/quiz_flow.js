"use strict";

// Quiz flow: opens the first self-test <details> automatically, then on a
// correct answer collapses it and opens the next one, scrolling down to it.
// Also highlights the chosen answer green (correct) or red (incorrect) using
// the same CSS classes the questions already define, and plays a wrong-answer
// sound on incorrect. Purely additive -- selftest_progress.js is unaffected.
(function () {
	// Wait long enough for the star-pop (950ms) and confetti to feel complete.
	var ADVANCE_DELAY_MS = 1500;
	var WRONG_SOUND_URL = "/assets/sounds/wrong-answer-buzzer.wav";

	//============================================
	function findQuizDetails() {
		// Only target <details> elements that actually contain a selftest question.
		return Array.from(document.querySelectorAll("details")).filter(function (d) {
			return d.querySelector(".qti-selftest");
		});
	}

	//============================================
	function findResultDiv(detailsEl) {
		// Each question has exactly one result div: id="result_<suffix>".
		return detailsEl.querySelector("[id^='result_']");
	}

	//============================================
	// Match the same verdict logic as selftest_progress.js classifyResultElement.
	function isFullyCorrect(text) {
		if (text === "CORRECT") {
			return true;
		}
		var scoreMatch = text.match(/^Total Score: (\d+) out of (\d+)$/);
		if (scoreMatch && scoreMatch[1] === scoreMatch[2]) {
			return true;
		}
		var posMatch = text.match(/^Correct positions: (\d+) of (\d+)$/);
		if (posMatch && posMatch[1] === posMatch[2]) {
			return true;
		}
		var fibMatch = text.match(/^Correct: (\d+) of (\d+)$/);
		if (fibMatch && fibMatch[1] === fibMatch[2]) {
			return true;
		}
		return false;
	}

	//============================================
	function isNoAnswer(text) {
		return text === "" ||
			text === "Please select an answer." ||
			text === "Please enter a value." ||
			text === "Please enter a valid number.";
	}

	//============================================
	function playWrongSound() {
		try {
			var audio = new window.Audio(WRONG_SOUND_URL);
			audio.play();
		} catch (_) {
			// Sound is optional; silently ignore failures.
		}
	}

	//============================================
	function clearAnswerHighlights(questionDiv) {
		// Remove any previously applied feedback classes from answer <li> items.
		var highlighted = questionDiv.querySelectorAll("li.qti-feedback-success, li.qti-feedback-error");
		highlighted.forEach(function (li) {
			li.classList.remove("qti-feedback-success", "qti-feedback-error");
		});
	}

	//============================================
	function highlightSelectedAnswer(questionDiv, isCorrect) {
		// Apply green or red to the <li> containing the checked radio/checkbox.
		// Matching/drag-drop questions have no radio inputs so this is a no-op.
		var checked = questionDiv.querySelectorAll(
			"input[type='radio']:checked, input[type='checkbox']:checked"
		);
		var cssClass = isCorrect ? "qti-feedback-success" : "qti-feedback-error";
		checked.forEach(function (input) {
			var li = input.closest("li");
			if (li) {
				li.classList.add(cssClass);
			}
		});
	}

	//============================================
	function advanceTo(allDetails, currentIndex) {
		var current = allDetails[currentIndex];
		var next = allDetails[currentIndex + 1];

		// Collapse answered question and open the next one simultaneously.
		current.removeAttribute("open");
		if (next) {
			next.setAttribute("open", "");
			next.scrollIntoView({ behavior: "smooth", block: "start" });
		}
		// No next means this was the last question -- nothing more to do.
	}

	//============================================
	function watchResult(resultDiv, allDetails, index) {
		// Derive the question div from the result div id suffix.
		var suffix = resultDiv.id.replace("result_", "");
		var questionDiv = document.getElementById("question_html_" + suffix);

		var observer = new MutationObserver(function () {
			var text = (resultDiv.textContent || "").trim();
			if (isNoAnswer(text)) {
				return;
			}
			var correct = isFullyCorrect(text);

			// Clear previous highlight then apply the new verdict color.
			if (questionDiv) {
				clearAnswerHighlights(questionDiv);
				highlightSelectedAnswer(questionDiv, correct);
			}

			if (correct) {
				// Disconnect before the timeout so a DOM re-render cannot fire twice.
				observer.disconnect();
				window.setTimeout(function () {
					advanceTo(allDetails, index);
				}, ADVANCE_DELAY_MS);
			} else {
				playWrongSound();
			}
		});
		observer.observe(resultDiv, { childList: true, characterData: true, subtree: true });
	}

	//============================================
	function initQuizFlow() {
		var allDetails = findQuizDetails();
		if (allDetails.length === 0) {
			return;
		}

		// Open the first question; make sure all others start closed.
		allDetails.forEach(function (d, i) {
			if (i === 0) {
				d.setAttribute("open", "");
			} else {
				d.removeAttribute("open");
			}
		});

		// Attach a verdict observer to each details element.
		allDetails.forEach(function (d, i) {
			var resultDiv = findResultDiv(d);
			if (!resultDiv) {
				return;
			}
			watchResult(resultDiv, allDetails, i);
		});
	}

	//============================================
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", initQuizFlow);
	} else {
		initQuizFlow();
	}
})();

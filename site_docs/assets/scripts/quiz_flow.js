"use strict";

// Quiz flow: opens the first self-test <details> automatically, then on a
// correct answer collapses it and opens the next one, scrolling down to it.
// Purely additive — selftest_progress.js star/confetti/badge logic is unaffected.
(function () {
	// Wait long enough for the star-pop (950ms) and confetti to feel complete.
	var ADVANCE_DELAY_MS = 1500;

	//============================================
	function findQuizDetails() {
		// Only target <details> elements that actually contain a selftest question.
		return Array.from(document.querySelectorAll("details")).filter(function (d) {
			return d.querySelector(".qti-selftest");
		});
	}

	//============================================
	function findResultDiv(detailsEl) {
		// Each question has exactly one result div: id="result_<crc>_<id>".
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
	function advanceTo(allDetails, currentIndex) {
		var current = allDetails[currentIndex];
		var next = allDetails[currentIndex + 1];

		// Collapse answered question and open the next one simultaneously.
		current.removeAttribute("open");
		if (next) {
			next.setAttribute("open", "");
			next.scrollIntoView({ behavior: "smooth", block: "start" });
		}
		// No next details means this was the last question — nothing more to do.
	}

	//============================================
	function watchForCorrect(resultDiv, allDetails, index) {
		var observer = new MutationObserver(function () {
			var text = (resultDiv.textContent || "").trim();
			if (!isFullyCorrect(text)) {
				return;
			}
			// Fire only once — disconnect before the timeout so a re-render
			// of the result div cannot trigger a second advance.
			observer.disconnect();
			window.setTimeout(function () {
				advanceTo(allDetails, index);
			}, ADVANCE_DELAY_MS);
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

		// Attach a correct-answer observer to each details element.
		allDetails.forEach(function (d, i) {
			var resultDiv = findResultDiv(d);
			if (!resultDiv) {
				return;
			}
			watchForCorrect(resultDiv, allDetails, i);
		});
	}

	//============================================
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", initQuizFlow);
	} else {
		initQuizFlow();
	}
})();

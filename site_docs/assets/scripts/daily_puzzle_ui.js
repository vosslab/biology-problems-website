"use strict";

(function () {
	function prefersReducedMotion() {
		if (!window.matchMedia) {
			return false;
		}
		return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
	}

	function scrollDetailsIntoView(detailsEl) {
		if (!detailsEl || typeof detailsEl.scrollIntoView !== "function") {
			return;
		}
		detailsEl.scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth" });
	}

	function wireHelpButton(helpButtonId, detailsId) {
		var helpButton = document.getElementById(helpButtonId);
		var details = document.getElementById(detailsId);
		if (!helpButton || !details) {
			return;
		}
		helpButton.addEventListener("click", function () {
			details.open = true;
			scrollDetailsIntoView(details);
		});
	}

	function computeRemainingGuesses(maxGuesses, guessesUsed, hintsUsed) {
		return maxGuesses - (guessesUsed + hintsUsed);
	}

	function renderPenaltyHint(opts) {
		var buttonEl = opts.buttonEl;
		var statusEl = opts.statusEl;
		var isRevealed = Boolean(opts.isRevealed);
		var isGameOver = Boolean(opts.isGameOver);
		var isEligible = opts.isEligible;
		var remaining = opts.remaining;
		var minRemainingAfterHint = opts.minRemainingAfterHint;
		var revealedText = opts.revealedText || "";
		var unavailableText = opts.unavailableText || "";
		var ineligibleText = opts.ineligibleText || "";

		if (!buttonEl || !statusEl) {
			return;
		}

		if (isRevealed) {
			buttonEl.disabled = true;
			statusEl.textContent = revealedText;
			return;
		}

		if (isGameOver) {
			buttonEl.disabled = true;
			statusEl.textContent = "";
			return;
		}

		if (isEligible === false) {
			buttonEl.disabled = true;
			statusEl.textContent = ineligibleText;
			return;
		}

		if (remaining <= minRemainingAfterHint) {
			buttonEl.disabled = true;
			statusEl.textContent = unavailableText;
			return;
		}

		buttonEl.disabled = false;
		statusEl.textContent = "";
	}

	function pad2(n) {
		return n < 10 ? "0" + n : String(n);
	}

	function getTimeZoneShort(date) {
		try {
			var parts = new Intl.DateTimeFormat(undefined, { timeZoneName: "short" }).formatToParts(date);
			var i = 0;
			for (i = 0; i < parts.length; i += 1) {
				if (parts[i].type === "timeZoneName") {
					return parts[i].value;
				}
			}
		} catch (_) {
			// Ignore.
		}
		return "";
	}

	function nextUtcMidnightMs(nowMs) {
		var d = new Date(nowMs);
		return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + 1, 0, 0, 0, 0);
	}

	function mountNextResetTimer(elementId) {
		var el = document.getElementById(elementId);
		if (!el) {
			return;
		}

		if (el.dataset.dpTimerMounted === "1") {
			return;
		}
		el.dataset.dpTimerMounted = "1";

		function render() {
			if (!document.body || !document.body.contains(el)) {
				return false;
			}

			var now = Date.now();
			var nextMs = nextUtcMidnightMs(now);
			var diffMs = Math.max(0, nextMs - now);

			var totalMin = Math.ceil(diffMs / 60000);
			var h = Math.floor(totalMin / 60);
			var m = totalMin % 60;

			var resetLocal = new Date(nextMs);
			var resetTime = new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(
				resetLocal
			);
			var tz = getTimeZoneShort(resetLocal);
			var tzSuffix = tz ? " " + tz : "";

			el.textContent =
				"Next puzzle in " + pad2(h) + ":" + pad2(m) +
				" | Resets at " + resetTime + tzSuffix + " your time";

			return true;
		}

		render();

		function scheduleNextTick() {
			if (!document.body || !document.body.contains(el)) {
				return;
			}
			var now = Date.now();
			var msToNextMinute = 60000 - (now % 60000) + 50;
			window.setTimeout(function () {
				if (!render()) {
					return;
				}
				scheduleNextTick();
			}, msToNextMinute);
		}

		scheduleNextTick();
	}

	window.DailyPuzzleUI = {
		prefersReducedMotion: prefersReducedMotion,
		scrollDetailsIntoView: scrollDetailsIntoView,
		wireHelpButton: wireHelpButton,
		computeRemainingGuesses: computeRemainingGuesses,
		renderPenaltyHint: renderPenaltyHint,
		mountNextResetTimer: mountNextResetTimer
	};
}());

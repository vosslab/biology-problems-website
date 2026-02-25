"use strict";

(function () {
	function createDefaultStats() {
		return {
			gamesPlayed: 0,
			wins: 0,
			currentStreak: 0,
			maxStreak: 0,
			lastDayKey: null,
			lastResult: null,
			guessDistribution: []
		};
	}

	function previousDayKey(dayKey) {
		var d = new Date(dayKey + "T00:00:00Z");
		d.setUTCDate(d.getUTCDate() - 1);
		return d.toISOString().slice(0, 10);
	}

	function createStore(statsKey, maxGuesses) {
		maxGuesses = maxGuesses || 6;

		function renderStatsHtml(stats) {
			var played = String(stats.gamesPlayed || 0);
			var winPct = stats.gamesPlayed > 0
				? String(Math.round((stats.wins / stats.gamesPlayed) * 100))
				: "0";
			var streak = String(stats.currentStreak || 0);
			var maxSt = String(stats.maxStreak || 0);
			var streakActive = (stats.currentStreak || 0) > 1;

			return "" +
			"<div class='dp-stats-card'>" +
				"<div class='dp-stat-item'>" +
					"<span class='dp-stat-value'>" + played + "</span>" +
					"<span class='dp-stat-label'>Played</span>" +
				"</div>" +
				"<div class='dp-stat-item'>" +
					"<span class='dp-stat-value'>" + winPct + "</span>" +
					"<span class='dp-stat-label'>Win %</span>" +
				"</div>" +
				"<div class='dp-stat-item" + (streakActive ? " dp-streak-active" : "") + "'>" +
					"<span class='dp-stat-value'>" + streak + "</span>" +
					"<span class='dp-stat-label'>Streak</span>" +
				"</div>" +
				"<div class='dp-stat-item'>" +
					"<span class='dp-stat-value'>" + maxSt + "</span>" +
					"<span class='dp-stat-label'>Max</span>" +
				"</div>" +
			"</div>";
		}

		function load() {
			var raw = window.localStorage.getItem(statsKey);
			var stats;
			if (!raw) {
				stats = createDefaultStats();
			} else {
				try {
					stats = JSON.parse(raw);
				} catch (_) {
					stats = createDefaultStats();
				}
			}
			// Backfill guessDistribution for old data
			if (!stats.guessDistribution) {
				stats.guessDistribution = [];
			}
			// Pad to maxGuesses length
			while (stats.guessDistribution.length < maxGuesses) {
				stats.guessDistribution.push(0);
			}
			return stats;
		}

		function save(stats) {
			window.localStorage.setItem(statsKey, JSON.stringify(stats));
		}

		function updateOnGameEnd(win, dayKey, guessNumber) {
			var stats = load();

			if (stats.lastDayKey === dayKey && stats.lastResult !== null) {
				return stats;
			}

			stats.gamesPlayed += 1;

			if (win) {
				if (stats.lastDayKey === previousDayKey(dayKey) && stats.lastResult === "win") {
					stats.currentStreak += 1;
				} else {
					stats.currentStreak = 1;
				}
				stats.wins += 1;
				stats.lastResult = "win";
				// Record guess distribution
				if (typeof guessNumber === "number" && guessNumber >= 1 && guessNumber <= maxGuesses) {
					stats.guessDistribution[guessNumber - 1] += 1;
				}
			} else {
				stats.currentStreak = 0;
				stats.lastResult = "loss";
			}

			if (stats.currentStreak > stats.maxStreak) {
				stats.maxStreak = stats.currentStreak;
			}

			stats.lastDayKey = dayKey;
			save(stats);
			return stats;
		}

		function renderStats(elementId) {
			var stats = load();
			var el = document.getElementById(elementId);
			if (!el) {
				return;
			}
			el.innerHTML = renderStatsHtml(stats);
		}

		function buildDistributionHtml(stats, highlightIndex) {
			var dist = stats.guessDistribution || [];
			var maxCount = 0;
			var i;
			for (i = 0; i < dist.length; i += 1) {
				if (dist[i] > maxCount) {
					maxCount = dist[i];
				}
			}

			var html = "<div class='dp-guess-dist'>";
			for (i = 0; i < dist.length; i += 1) {
				var count = dist[i] || 0;
				var pct = maxCount > 0 ? Math.max(8, Math.round((count / maxCount) * 100)) : 8;
				var isCurrent = (i === highlightIndex);
				html += "<div class='dp-dist-row'>" +
					"<span class='dp-dist-label'>" + String(i + 1) + "</span>" +
					"<div class='dp-dist-bar-bg'>" +
						"<div class='dp-dist-bar" + (isCurrent ? " dp-dist-current" : "") + "'" +
						" style='width:" + pct + "%'>" +
						"<span class='dp-dist-count'>" + String(count) + "</span>" +
						"</div>" +
					"</div>" +
				"</div>";
			}
			html += "</div>";
			return html;
		}

		function showGameEndModal(opts) {
			opts = opts || {};
			var win = opts.win;
			var guessNumber = opts.guessNumber;
			var modalMaxGuesses = opts.maxGuesses || maxGuesses;
			var gameName = opts.gameName || "Puzzle";

			// Remove any existing modal
			var existing = document.getElementById("dp-modal-overlay");
			if (existing) {
				existing.parentNode.removeChild(existing);
			}

			var stats = load();

			var title = win ? "You got it!" : "Better luck next time";
			var subtitle = win
				? "Solved in " + guessNumber + " of " + modalMaxGuesses + " guesses"
				: "The answer will be revealed above";

			var highlightIndex = (win && typeof guessNumber === "number") ? (guessNumber - 1) : -1;

			var reducedMotion = window.DailyPuzzleUI && window.DailyPuzzleUI.prefersReducedMotion
				? window.DailyPuzzleUI.prefersReducedMotion()
				: false;
			var animClass = reducedMotion ? " dp-no-animate" : "";

			var html = "" +
				"<div class='dp-modal" + animClass + "' role='dialog' aria-modal='true' aria-label='" + gameName + " Results'>" +
					"<button class='dp-modal-close' aria-label='Close'>&times;</button>" +
					"<div class='dp-modal-title'>" + title + "</div>" +
					"<div class='dp-modal-subtitle'>" + subtitle + "</div>" +
					renderStatsHtml(stats) +
					"<div class='dp-modal-section-title'>Guess Distribution</div>" +
					buildDistributionHtml(stats, highlightIndex) +
					"<div class='dp-modal-timer' id='dp-modal-timer'></div>" +
					"<button class='dp-modal-btn-close'>Close</button>" +
				"</div>";

			var overlay = document.createElement("div");
			overlay.id = "dp-modal-overlay";
			overlay.className = "dp-modal-overlay" + animClass;
			overlay.innerHTML = html;
			document.body.appendChild(overlay);

			// Mount timer inside modal
			if (window.DailyPuzzleUI && window.DailyPuzzleUI.mountNextResetTimer) {
				window.DailyPuzzleUI.mountNextResetTimer("dp-modal-timer");
			}

			// Dismiss handlers
			function dismiss() {
				if (overlay.parentNode) {
					overlay.parentNode.removeChild(overlay);
				}
				document.removeEventListener("keydown", onEscape);
			}

			function onEscape(e) {
				if (e.key === "Escape") {
					dismiss();
				}
			}

			overlay.addEventListener("click", function (e) {
				if (e.target === overlay) {
					dismiss();
				}
			});

			var closeBtn = overlay.querySelector(".dp-modal-close");
			if (closeBtn) {
				closeBtn.addEventListener("click", dismiss);
			}

			var closeBtnBottom = overlay.querySelector(".dp-modal-btn-close");
			if (closeBtnBottom) {
				closeBtnBottom.addEventListener("click", dismiss);
			}

			document.addEventListener("keydown", onEscape);
		}

		return {
			load: load,
			save: save,
			updateOnGameEnd: updateOnGameEnd,
			renderStats: renderStats,
			showGameEndModal: showGameEndModal
		};
	}

	window.DailyPuzzleStats = {
		createStore: createStore
	};
}());

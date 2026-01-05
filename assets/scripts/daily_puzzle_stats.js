"use strict";

(function () {
	function createDefaultStats() {
		return {
			gamesPlayed: 0,
			wins: 0,
			currentStreak: 0,
			maxStreak: 0,
			lastDayKey: null,
			lastResult: null
		};
	}

	function previousDayKey(dayKey) {
		var d = new Date(dayKey + "T00:00:00Z");
		d.setUTCDate(d.getUTCDate() - 1);
		return d.toISOString().slice(0, 10);
	}

	function createStore(statsKey) {
		function renderStatsHtml(stats) {
			var games = String(stats.gamesPlayed || 0);
			var wins = String(stats.wins || 0);
			var streak = String(stats.currentStreak || 0);
			var maxStreak = String(stats.maxStreak || 0);

			return "" +
			"<div class='dp-stats'>" +
				"<span class='dp-stat'>Games <span class='dp-val'>" + games + "</span></span>" +
				"<span class='dp-stat'>Wins <span class='dp-val'>" + wins + "</span></span>" +
				"<span class='dp-stat dp-streak'>Streak <span class='dp-val'>" + streak + "</span></span>" +
				"<span class='dp-stat'>Max <span class='dp-val'>" + maxStreak + "</span></span>" +
			"</div>";
		}

		function load() {
			var raw = window.localStorage.getItem(statsKey);
			if (!raw) {
				return createDefaultStats();
			}
			try {
				return JSON.parse(raw);
			} catch (_) {
				return createDefaultStats();
			}
		}

		function save(stats) {
			window.localStorage.setItem(statsKey, JSON.stringify(stats));
		}

		function updateOnGameEnd(win, dayKey) {
			var stats = load();

			if (stats.lastDayKey === dayKey && stats.lastResult !== null) {
				return;
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
			} else {
				stats.currentStreak = 0;
				stats.lastResult = "loss";
			}

			if (stats.currentStreak > stats.maxStreak) {
				stats.maxStreak = stats.currentStreak;
			}

			stats.lastDayKey = dayKey;
			save(stats);
		}

		function renderStats(elementId) {
			var stats = load();
			var el = document.getElementById(elementId);
			if (!el) {
				return;
			}
			el.innerHTML = renderStatsHtml(stats);
		}

		return {
			load: load,
			save: save,
			updateOnGameEnd: updateOnGameEnd,
			renderStats: renderStats
		};
	}

	window.DailyPuzzleStats = {
		createStore: createStore
	};
}());

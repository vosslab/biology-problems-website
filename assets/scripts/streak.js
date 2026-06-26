"use strict";

// Daily streak tracker. Purely additive -- no changes to selftest_progress.js.
// Stores state in localStorage under STORAGE_KEY, separate from selftest progress.
// Shows a badge after the h1 on every page and a panel on the progress dashboard.
// A streak increments once per calendar day on the first fully correct answer.
(function () {
	var STORAGE_KEY = "selftest_streak_v1";

	//============================================
	function pad2(n) {
		return n < 10 ? "0" + n : String(n);
	}

	function getTodayDate() {
		var d = new Date();
		return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate());
	}

	function getYesterdayDate() {
		var d = new Date();
		d.setDate(d.getDate() - 1);
		return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate());
	}

	//============================================
	function createEmptyStreak() {
		return { version: 1, currentStreak: 0, longestStreak: 0, lastCorrectDate: null };
	}

	function loadStreak() {
		try {
			var raw = window.localStorage.getItem(STORAGE_KEY);
			if (!raw) {
				return createEmptyStreak();
			}
			var parsed = JSON.parse(raw);
			if (parsed.version !== 1) {
				return createEmptyStreak();
			}
			return parsed;
		} catch (_) {
			return createEmptyStreak();
		}
	}

	function saveStreak(data) {
		try {
			window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
		} catch (_) {
			// localStorage unavailable; streak will not persist.
		}
	}

	//============================================
	// Record a correct answer. Returns the action taken:
	// "already"  -- already counted a correct answer today, no change.
	// "extended" -- streak incremented (answered yesterday then today).
	// "started"  -- streak reset to 1 (missed days or first ever).
	function recordCorrectAnswer() {
		var today = getTodayDate();
		var yesterday = getYesterdayDate();
		var data = loadStreak();

		if (data.lastCorrectDate === today) {
			return { action: "already", data: data };
		}

		if (data.lastCorrectDate === yesterday) {
			data.currentStreak += 1;
		} else {
			data.currentStreak = 1;
		}

		data.lastCorrectDate = today;
		if (data.currentStreak > data.longestStreak) {
			data.longestStreak = data.currentStreak;
		}
		saveStreak(data);
		return { action: data.currentStreak === 1 ? "started" : "extended", data: data };
	}

	//============================================
	// Same verdict logic as quiz_flow.js and selftest_progress.js.
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
	function showStreakToast(data) {
		var existing = document.getElementById("streak-toast");
		if (existing && existing.parentNode) {
			existing.parentNode.removeChild(existing);
		}
		var toast = document.createElement("div");
		toast.id = "streak-toast";
		// Reuse the existing toast CSS class for consistent style.
		toast.className = "selftest-progress-toast";
		toast.setAttribute("role", "status");
		if (data.currentStreak === 1) {
			toast.innerHTML = "&#x1F525; Streak started! Come back tomorrow to build it up.";
		} else {
			toast.innerHTML = "&#x1F525; " + data.currentStreak + "-day streak! Keep it going.";
		}
		document.body.appendChild(toast);
		window.setTimeout(function () {
			if (toast.parentNode) {
				toast.parentNode.removeChild(toast);
			}
		}, 4000);
	}

	//============================================
	// Build the streak badge HTML string for the given streak data and today's date.
	function buildBadgeHTML(data) {
		var today = getTodayDate();
		var yesterday = getYesterdayDate();
		var answeredToday = data.lastCorrectDate === today;
		var answeredYesterday = data.lastCorrectDate === yesterday;
		var hasActive = data.currentStreak > 0 && (answeredToday || answeredYesterday);

		if (!hasActive) {
			return "";
		}

		var html = "&#x1F525; <strong>" + data.currentStreak + "-day streak</strong>";
		if (data.longestStreak > data.currentStreak) {
			html += " &nbsp;&middot;&nbsp; Best: " + data.longestStreak + " days";
		}
		if (answeredYesterday && !answeredToday) {
			html += " &nbsp;<span class='streak-at-risk'>&#x26A0;&#xFE0F; Answer today to keep it!</span>";
		}
		return html;
	}

	//============================================
	function renderStreakBadge() {
		// On the progress dashboard page the panel already shows streak info -- skip.
		if (document.getElementById("selftest-progress-dashboard")) {
			return;
		}

		var data = loadStreak();
		var html = buildBadgeHTML(data);

		var badge = document.getElementById("streak-badge");

		// No active streak -- remove badge if it exists and return.
		if (!html) {
			if (badge && badge.parentNode) {
				badge.parentNode.removeChild(badge);
			}
			return;
		}

		if (!badge) {
			var h1 = document.querySelector("h1");
			if (!h1) {
				return;
			}
			badge = document.createElement("div");
			badge.id = "streak-badge";
			badge.className = "streak-badge";
			// Insert after the h1, before the selftest progress panel if present.
			h1.insertAdjacentElement("afterend", badge);
		}
		badge.innerHTML = html;
	}

	//============================================
	// Render a streak summary block into the progress dashboard page.
	function renderStreakDashboardPanel() {
		var root = document.getElementById("selftest-progress-dashboard");
		if (!root) {
			return;
		}
		var data = loadStreak();
		var today = getTodayDate();
		var yesterday = getYesterdayDate();
		var answeredToday = data.lastCorrectDate === today;
		var answeredYesterday = data.lastCorrectDate === yesterday;

		var panel = document.getElementById("streak-dashboard-panel");
		if (!panel) {
			panel = document.createElement("section");
			panel.id = "streak-dashboard-panel";
			panel.className = "selftest-progress-panel";
			// Insert before the dashboard root so it appears above the subject list.
			root.insertAdjacentElement("beforebegin", panel);
		}

		var streakLine = "";
		if (data.currentStreak > 0 && (answeredToday || answeredYesterday)) {
			streakLine = "&#x1F525; <strong>" + data.currentStreak + "-day streak</strong>";
			if (answeredYesterday && !answeredToday) {
				streakLine += " &nbsp;<span class='streak-at-risk'>&#x26A0;&#xFE0F; Answer today to keep it!</span>";
			}
		} else {
			streakLine = "No active streak &mdash; answer a question to start one!";
		}

		var longestLine = data.longestStreak > 0
			? "<br>Best streak: <strong>" + data.longestStreak + " days</strong>"
			: "";
		var lastLine = data.lastCorrectDate
			? "<br>Last active: " + data.lastCorrectDate
			: "";

		panel.innerHTML = "<strong>Daily streak</strong><br>" + streakLine + longestLine + lastLine;
	}

	//============================================
	function watchResultDivs() {
		var resultDivs = document.querySelectorAll("[id^='result_']");
		resultDivs.forEach(function (resultDiv) {
			// fired prevents double-counting if the result div mutates twice.
			var fired = false;
			var observer = new MutationObserver(function () {
				if (fired) {
					return;
				}
				var text = (resultDiv.textContent || "").trim();
				if (!isFullyCorrect(text)) {
					return;
				}
				fired = true;
				observer.disconnect();
				var result = recordCorrectAnswer();
				if (result.action === "extended" || result.action === "started") {
					showStreakToast(result.data);
				}
				// Refresh the badge immediately after recording.
				renderStreakBadge();
				renderStreakDashboardPanel();
			});
			observer.observe(resultDiv, { childList: true, characterData: true, subtree: true });
		});
	}

	//============================================
	function init() {
		renderStreakBadge();
		renderStreakDashboardPanel();
		watchResultDivs();
	}

	//============================================
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();

"use strict";

(function () {
	var STORAGE_KEY = "selftest_progress_v1";
	var MANIFEST_URL = "/assets/data/selftest_question_manifest.json";
	var manifestCache = null;
	var initializedPages = {};

	function createEmptyState() {
		return {
			version: 1,
			completed: {}
		};
	}

	function storageStatus() {
		try {
			var key = "__selftest_progress_probe__";
			window.localStorage.setItem(key, "1");
			window.localStorage.removeItem(key);
			return { available: true, message: "" };
		} catch (_) {
			return {
				available: false,
				message: "Progress cannot be saved because browser local storage is unavailable."
			};
		}
	}

	function loadState() {
		var status = storageStatus();
		if (!status.available) {
			return createEmptyState();
		}
		var raw = window.localStorage.getItem(STORAGE_KEY);
		if (!raw) {
			return createEmptyState();
		}
		try {
			var parsed = JSON.parse(raw);
			if (parsed.version !== 1 || !parsed.completed) {
				return createEmptyState();
			}
			return parsed;
		} catch (_) {
			return createEmptyState();
		}
	}

	function saveState(state) {
		var status = storageStatus();
		if (!status.available) {
			return false;
		}
		window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
		return true;
	}

	function isCompleted(questionId) {
		var state = loadState();
		return Boolean(state.completed[questionId]);
	}

	function markCompleted(questionId) {
		var state = loadState();
		if (state.completed[questionId]) {
			return { changed: false, saved: true };
		}
		state.completed[questionId] = {
			firstCorrectAt: new Date().toISOString()
		};
		var saved = saveState(state);
		return { changed: saved, saved: saved };
	}

	function resetAll() {
		var status = storageStatus();
		if (!status.available) {
			return false;
		}
		window.localStorage.removeItem(STORAGE_KEY);
		return true;
	}

	// Map a question's result element to a completion verdict. The literal
	// strings and score formats below must match what the generated question
	// HTML check functions write into result_<crc>; only "full-correct" marks
	// a question complete. Unknown wording stays "unknown" (no completion).
	function classifyResultElement(resultElement) {
		if (!resultElement) {
			return "unknown";
		}
		var text = (resultElement.textContent || "").trim();
		if (text === "") {
			return "no-answer";
		}
		if (text === "CORRECT") {
			return "full-correct";
		}
		if (
			text === "Please select an answer." ||
			text === "Please enter a value." ||
			text === "Please enter a valid number."
		) {
			return "no-answer";
		}
		var scoreMatch = text.match(/^Total Score: (\d+) out of (\d+)$/);
		if (scoreMatch) {
			return scoreMatch[1] === scoreMatch[2] ? "full-correct" : "partial";
		}
		var positionsMatch = text.match(/^Correct positions: (\d+) of (\d+)$/);
		if (positionsMatch) {
			return positionsMatch[1] === positionsMatch[2] ? "full-correct" : "partial";
		}
		var fibMatch = text.match(/^Correct: (\d+) of (\d+)$/);
		if (fibMatch) {
			return fibMatch[1] === fibMatch[2] ? "full-correct" : "partial";
		}
		if (
			text === "incorrect" ||
			text === "Incorrect. Try again." ||
			text === "Too high. Try again." ||
			text === "Too low. Try again."
		) {
			return "incorrect";
		}
		if (
			text.indexOf("Too many answers selected.") === 0 ||
			text.indexOf("Too few answers selected.") === 0 ||
			text.indexOf("You selected the right number of choices, but only ") === 0
		) {
			return "partial";
		}
		return "unknown";
	}

	// Convert a browser pathname to the manifest pagePath form
	// (subject/topicNN/index.md): strip leading slashes, and append index.md
	// for directory ("/x/") or extensionless URLs.
	function normalizePagePath(pathname) {
		var path = pathname || "";
		path = path.replace(/^\/+/, "");
		if (path === "") {
			return "index.md";
		}
		if (path.slice(-1) === "/") {
			return path + "index.md";
		}
		if (path.slice(-3) !== ".md" && path.indexOf(".") === -1) {
			return path + "/index.md";
		}
		return path;
	}

	function getCurrentRows(manifest) {
		var pagePath = normalizePagePath(window.location.pathname);
		return manifest.questions.filter(function (row) {
			return row.pagePath === pagePath;
		});
	}

	function fetchManifest() {
		if (manifestCache) {
			return Promise.resolve(manifestCache);
		}
		return window.fetch(MANIFEST_URL)
			.then(function (response) {
				if (!response.ok) {
					throw new Error("Could not load self-test progress manifest.");
				}
				return response.json();
			})
			.then(function (manifest) {
				manifestCache = manifest;
				return manifest;
			});
	}

	function topicSummary(topicKey, manifest) {
		var state = loadState();
		var rows = manifest.questions.filter(function (row) {
			return row.topicKey === topicKey;
		});
		var completed = rows.filter(function (row) {
			return Boolean(state.completed[row.questionId]);
		}).length;
		return {
			completed: completed,
			total: rows.length,
			isComplete: rows.length > 0 && completed === rows.length
		};
	}

	function findQuestionRow(rows, crc) {
		for (var i = 0; i < rows.length; i += 1) {
			if (rows[i].crc === crc) {
				return rows[i];
			}
		}
		return null;
	}

	function setQuestionStatus(questionId) {
		var badge = document.querySelector("[data-selftest-status='" + questionId + "']");
		if (!badge) {
			return;
		}
		if (isCompleted(questionId)) {
			badge.textContent = "Completed";
			badge.className = "selftest-status selftest-status-complete";
		} else {
			badge.textContent = "Not completed";
			badge.className = "selftest-status";
		}
	}

	// Count completed questions among the rows actually rendered on this page.
	// Scoped to the page (not the whole topicKey) so the denominator matches
	// the number of badges the learner sees.
	function pageSummary(rows) {
		var state = loadState();
		var completed = rows.filter(function (row) {
			return Boolean(state.completed[row.questionId]);
		}).length;
		return { completed: completed, total: rows.length };
	}

	function renderTopicSummary(rows, manifest) {
		if (!rows.length || document.getElementById("selftest-topic-progress")) {
			return;
		}
		var first = rows[0];
		var summary = pageSummary(rows);
		var h1 = document.querySelector("h1");
		if (!h1) {
			return;
		}
		var panel = document.createElement("div");
		panel.id = "selftest-topic-progress";
		panel.className = "selftest-progress-panel";
		panel.setAttribute("data-topic-key", first.topicKey);
		// Announce live so screen readers hear the count change after an answer.
		panel.setAttribute("aria-live", "polite");
		panel.innerHTML = "<strong>Self-test progress:</strong> " +
			"<span data-selftest-topic-count>" + summary.completed + " / " +
			summary.total + " completed</span>";
		h1.insertAdjacentElement("afterend", panel);
	}

	function updateTopicSummary(rows, manifest) {
		if (!rows.length) {
			return;
		}
		var summary = pageSummary(rows);
		var count = document.querySelector("[data-selftest-topic-count]");
		if (count) {
			count.textContent = summary.completed + " / " + summary.total + " completed";
		}
	}

	function renderQuestionBadges(rows) {
		rows.forEach(function (row) {
			var question = document.getElementById("question_html_" + row.crc);
			if (!question || question.querySelector("[data-selftest-status]")) {
				return;
			}
			var badge = document.createElement("div");
			badge.setAttribute("data-selftest-status", row.questionId);
			// role=status so a screen reader announces Completed / Not completed.
			badge.setAttribute("role", "status");
			question.insertAdjacentElement("afterbegin", badge);
			setQuestionStatus(row.questionId);
		});
	}

	function showPopup(message) {
		var status = storageStatus();
		if (!status.available) {
			return;
		}
		var existing = document.getElementById("selftest-progress-toast");
		if (existing && existing.parentNode) {
			existing.parentNode.removeChild(existing);
		}
		var toast = document.createElement("div");
		toast.id = "selftest-progress-toast";
		toast.className = "selftest-progress-toast";
		toast.setAttribute("role", "status");
		toast.textContent = message;
		document.body.appendChild(toast);
		window.setTimeout(function () {
			if (toast.parentNode) {
				toast.parentNode.removeChild(toast);
			}
		}, 3500);
	}

	function renderStorageWarning() {
		var status = storageStatus();
		if (status.available || document.getElementById("selftest-storage-warning")) {
			return;
		}
		var h1 = document.querySelector("h1");
		if (!h1) {
			return;
		}
		var warning = document.createElement("div");
		warning.id = "selftest-storage-warning";
		warning.className = "selftest-storage-warning";
		warning.textContent = status.message;
		h1.insertAdjacentElement("afterend", warning);
	}

	// Each generated question defines a global checkAnswer_<crc>(). Wrap that
	// global so we can inspect the rendered result after the original runs and
	// mark completion on a fully correct answer. The __selfTestProgressWrapped
	// sentinel prevents double-wrapping when MkDocs Material re-navigates.
	function wrapAnswerChecks(rows, manifest) {
		rows.forEach(function (row) {
			var functionName = "checkAnswer_" + row.crc;
			var original = window[functionName];
			if (typeof original !== "function" || original.__selfTestProgressWrapped) {
				return;
			}
			var wrapped = function () {
				var wasComplete = isCompleted(row.questionId);
				var result = original.apply(this, arguments);
				var resultElement = document.getElementById("result_" + row.crc);
				var status = classifyResultElement(resultElement);
				if (status === "full-correct") {
					var markResult = markCompleted(row.questionId);
					setQuestionStatus(row.questionId);
					updateTopicSummary(rows, manifest);
					if (!wasComplete && markResult.changed) {
						showPopup("Question completed");
						var summary = topicSummary(row.topicKey, manifest);
						if (summary.isComplete) {
							showPopup("Topic complete");
						}
					}
				}
				return result;
			};
			wrapped.__selfTestProgressWrapped = true;
			wrapped.__selfTestProgressOriginal = original;
			window[functionName] = wrapped;
		});
	}

	function renderDashboard(manifest) {
		var root = document.getElementById("selftest-progress-dashboard");
		if (!root) {
			return;
		}
		var status = storageStatus();
		var state = loadState();
		var subjects = {};
		manifest.questions.forEach(function (row) {
			if (!subjects[row.subjectKey]) {
				subjects[row.subjectKey] = {
					completed: 0,
					total: 0,
					topics: {}
				};
			}
			var subject = subjects[row.subjectKey];
			if (!subject.topics[row.topicKey]) {
				subject.topics[row.topicKey] = {
					title: row.topicTitle,
					pagePath: row.pagePath,
					completed: 0,
					total: 0
				};
			}
			subject.total += 1;
			subject.topics[row.topicKey].total += 1;
			if (state.completed[row.questionId]) {
				subject.completed += 1;
				subject.topics[row.topicKey].completed += 1;
			}
		});
		var total = manifest.questions.length;
		var completed = Object.keys(state.completed).filter(function (questionId) {
			return manifest.questions.some(function (row) {
				return row.questionId === questionId;
			});
		}).length;
		var html = "<section class='selftest-dashboard-summary' aria-live='polite'>" +
			"<strong>Completed:</strong> " + completed + " / " + total +
			"</section>";
		if (!status.available) {
			html += "<div class='selftest-storage-warning'>" + status.message + "</div>";
		}
		Object.keys(subjects).sort().forEach(function (subjectKey) {
			var subject = subjects[subjectKey];
			html += "<section class='selftest-dashboard-subject'>" +
				"<h2>" + subjectKey.replace(/_/g, " ") + "</h2>" +
				"<p>" + subject.completed + " / " + subject.total + " completed</p>" +
				"<ul>";
			Object.keys(subject.topics).sort().forEach(function (topicKey) {
				var topic = subject.topics[topicKey];
				var completeClass = topic.completed === topic.total ? " class='selftest-topic-complete'" : "";
				var href = "/" + topic.pagePath.replace(/index\.md$/, "");
				html += "<li" + completeClass + "><a href='" + href + "'>" +
					topic.title + "</a>: " + topic.completed + " / " +
					topic.total + " completed</li>";
			});
			html += "</ul></section>";
		});
		html += "<button type='button' class='md-button md-button--secondary' " +
			"id='selftest-reset-progress' " +
			"aria-label='Reset all self-test completion progress in this browser'" +
			(status.available ? "" : " disabled") +
			">Reset self-test progress</button>";
		root.innerHTML = html;
		var resetButton = document.getElementById("selftest-reset-progress");
		if (resetButton) {
			resetButton.addEventListener("click", function () {
				if (window.confirm("Reset all self-test completion progress in this browser?")) {
					resetAll();
					renderDashboard(manifest);
				}
			});
		}
	}

	function initPage() {
		var pagePath = normalizePagePath(window.location.pathname);
		if (initializedPages[pagePath]) {
			return;
		}
		initializedPages[pagePath] = true;
		fetchManifest().then(function (manifest) {
			renderStorageWarning();
			var rows = getCurrentRows(manifest);
			renderTopicSummary(rows, manifest);
			renderQuestionBadges(rows);
			wrapAnswerChecks(rows, manifest);
			renderDashboard(manifest);
		}).catch(function () {
			renderStorageWarning();
		});
	}

	function installLifecycleHooks() {
		if (document.readyState === "loading") {
			document.addEventListener("DOMContentLoaded", initPage);
		} else {
			initPage();
		}
		// MkDocs Material instant navigation swaps page content without a full
		// reload; document$ fires on each virtual page load so we re-init.
		if (window.document$ && typeof window.document$.subscribe === "function") {
			window.document$.subscribe(function () {
				initPage();
			});
		}
	}

	window.SelfTestProgress = {
		loadState: loadState,
		markCompleted: markCompleted,
		isCompleted: isCompleted,
		topicSummary: topicSummary,
		resetAll: resetAll,
		storageStatus: storageStatus,
		classifyResultElement: classifyResultElement,
		normalizePagePath: normalizePagePath,
		initPage: initPage,
		_installLifecycleHooks: installLifecycleHooks,
		_test: {
			wrapAnswerChecks: wrapAnswerChecks,
			getCurrentRows: getCurrentRows
		}
	};

	// CommonJS export for the Node-based .mjs tests; harmless in the browser.
	if (typeof module !== "undefined" && module.exports) {
		module.exports = window.SelfTestProgress;
	}

	installLifecycleHooks();
}());

"use strict";

(function () {
	var STORAGE_KEY = "selftest_progress_v2";
	var siteBase = new URL("../", document.currentScript.src);
	var MANIFEST_URL = new URL("data/selftest_question_manifest.json", siteBase).href;
	var pageBase = new URL("../", siteBase).pathname;
	var manifestCache = null;

	function createEmptyState() {
		return {
			version: 2,
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
			if (parsed.version !== 2 || !parsed.completed) {
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


	// Convert a browser pathname to the manifest pagePath form
	// (subject/topicNN/index.md): strip leading slashes, and append index.md
	// for directory ("/x/") or extensionless URLs.
	function normalizePagePath(pathname) {
		var path = pathname || "";
		if (path.indexOf(pageBase) === 0) { path = path.slice(pageBase.length); }
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
		var rows = manifest.questions.filter(function (row) {
			return row.topicKey === topicKey;
		});
		return pageSummary(rows);
	}

	function setQuestionStatus(questionId) {
		var badge = document.querySelector("[data-selftest-status='" + questionId + "']");
		if (!badge) {
			return;
		}
		if (isCompleted(questionId)) {
			// Set text content first, then append the star span.
			badge.textContent = "Completed";
			badge.className = "selftest-status selftest-status-complete";
			// Add the earned-star icon; aria-label updated inside addStarToBadge.
			addStarToBadge(badge);
		} else {
			badge.textContent = "Not completed";
			badge.className = "selftest-status";
			badge.removeAttribute("aria-label");
		}
	}

	// Count completed questions among the rows actually rendered on this page.
	// Scoped to the page (not the whole topicKey) so the denominator matches
	// the number of badges the learner sees.
	function pageSummary(rows) {
		var state = loadState();
		var ids = Array.from(new Set(rows.map(function (row) { return row.questionId; })));
		var completed = ids.filter(function (id) { return Boolean(state.completed[id]); }).length;
		return { completed: completed, total: ids.length,
			isComplete: ids.length > 0 && completed === ids.length };
	}

	function renderTopicSummary(rows) {
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

	function updateTopicSummary(rows) {
		if (!rows.length) {
			return;
		}
		var summary = pageSummary(rows);
		var count = document.querySelector("[data-selftest-topic-count]");
		if (count) {
			count.textContent = summary.completed + " / " + summary.total + " completed";
		}
	}

	function renderQuestionBadge(host) {
		var header = host.querySelector(".selftest-question-header");
		if (!header) { return; }
		var badge = header.querySelector("[data-selftest-status]") || document.createElement("div");
		badge.setAttribute("data-selftest-status", host.dataset.bbq);
		badge.setAttribute("role", "status");
		header.prepend(badge);
		setQuestionStatus(host.dataset.bbq);
	}

	function renderQuestionBadges() {
		document.querySelectorAll(".qti-selftest[data-bbq]").forEach(renderQuestionBadge);
	}

	var CORRECT_SOUND_URL = new URL("sounds/mixkit-correct-positive-notification-957.wav", siteBase).href;

	function playCorrectSound() {
		try {
			var audio = new window.Audio(CORRECT_SOUND_URL);
			audio.volume = 0.2;
			audio.play();
		} catch (_) {
			// Sound playback is optional; silently ignore failures.
		}
	}

	function launchConfetti() {
		// canvas-confetti exposes window.confetti; skip silently if unavailable.
		if (typeof window.confetti !== "function") {
			return;
		}
		window.confetti({
			particleCount: 80,
			spread: 70,
			origin: { y: 0.6 }
		});
	}

	// Show a brief star-burst animation near the answered question element.
	// Respects prefers-reduced-motion via CSS (the animation is gated there);
	// we still create and immediately remove the DOM nodes so the persistent
	// star badge still gets added on the same tick.
	function launchStarPop(questionElement) {
		if (!questionElement) {
			return;
		}
		var rect = questionElement.getBoundingClientRect();
		// Anchor near the top-right of the question card.
		var originX = rect.right - 20;
		var originY = rect.top + window.scrollY + 20;

		var container = document.createElement("div");
		container.className = "selftest-star-pop";
		container.setAttribute("aria-hidden", "true");
		container.style.left = originX + "px";
		container.style.top = originY + "px";

		// Five glyphs scattered in different directions.
		var offsets = [
			{ dx: "-28px", dy: "-32px" },
			{ dx: "28px",  dy: "-28px" },
			{ dx: "-36px", dy: "0px" },
			{ dx: "36px",  dy: "-10px" },
			{ dx: "0px",   dy: "-44px" }
		];
		offsets.forEach(function (offset) {
			var glyph = document.createElement("span");
			glyph.className = "selftest-star-pop-glyph";
			// Use HTML entity &#9733; (BLACK STAR) so no UTF-8 raw char in source.
			glyph.innerHTML = "&#9733;";
			glyph.style.setProperty("--star-dx", offset.dx);
			glyph.style.setProperty("--star-dy", offset.dy);
			container.appendChild(glyph);
		});

		document.body.appendChild(container);
		// Remove after animation (800ms) plus small buffer.
		window.setTimeout(function () {
			if (container.parentNode) {
				container.parentNode.removeChild(container);
			}
		}, 950);
	}

	// Add a star glyph to a question badge element if not already present.
	// The visual star is aria-hidden; a .selftest-sr-only span carries the
	// screen-reader text so assistive tech reads "earned star" explicitly.
	function addStarToBadge(badge) {
		if (!badge || badge.querySelector(".selftest-star")) {
			return;
		}
		var star = document.createElement("span");
		star.className = "selftest-star";
		star.setAttribute("aria-hidden", "true");
		// Use HTML entity so no raw UTF-8 in source.
		star.innerHTML = "&#9733;";
		badge.appendChild(star);
		// Visually-hidden text so screen readers announce "earned star".
		var srText = document.createElement("span");
		srText.className = "selftest-sr-only";
		srText.textContent = "earned star";
		badge.appendChild(srText);
		// Keep aria-label in sync as a belt-and-suspenders fallback.
		badge.setAttribute("aria-label", "Completed - earned star");
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

	// Record completion immediately; loading the dashboard must not delay grading.
	function onGraded(event) {
		if (event.detail.verdict !== "full-correct") { return; }
		if (document.querySelector('[data-selftest-personalization="off"]')) { return; }
		var crc = event.detail.crc;
		var questionId = event.target.dataset.bbq;
		var wasComplete = isCompleted(questionId);
		var markResult = markCompleted(questionId);
		setQuestionStatus(questionId);
		playCorrectSound();
		launchConfetti();
		launchStarPop(document.getElementById("question_html_" + crc));
		if (!wasComplete && markResult.changed) { showPopup("Question completed"); }
		return initPage().then(function (current) {
			if (!current || wasComplete || !markResult.changed || !event.target.isConnected) { return; }
			if (pageSummary(current.rows).isComplete) {
				showPopup("Topic complete");
			}
		});
	}

	function onReady(event) {
		if (document.querySelector('[data-selftest-personalization="off"]')) { return; }
		renderQuestionBadge(event.target);
		initPage();
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
					rows: [],
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
			subject.rows.push(row);
			subject.topics[row.topicKey].total += 1;
			if (state.completed[row.questionId]) {
				subject.topics[row.topicKey].completed += 1;
			}
		});
		var summary = pageSummary(manifest.questions);
		var total = summary.total;
		var completed = summary.completed;
		var stars = completed;
		var html = "<section class='selftest-dashboard-summary' aria-live='polite'>" +
			"<strong>Completed:</strong> " + completed + " / " + total +
			"<span class='selftest-dashboard-stars' aria-label='Stars earned: " + stars + "'>" +
			" &#9733; " + stars + "</span>" +
			"</section>";
		if (!status.available) {
			html += "<div class='selftest-storage-warning'>" + status.message + "</div>";
		}
		Object.keys(subjects).sort().forEach(function (subjectKey) {
			var subject = subjects[subjectKey];
			var subjectSummary = pageSummary(subject.rows);
			html += "<section class='selftest-dashboard-subject'>" +
				"<h2>" + subjectKey.replace(/_/g, " ") + "</h2>" +
				"<p>" + subjectSummary.completed + " / " + subjectSummary.total + " completed</p>" +
				"<ul>";
			Object.keys(subject.topics).sort().forEach(function (topicKey) {
				var topic = subject.topics[topicKey];
				var completeClass = topic.completed === topic.total ? " class='selftest-topic-complete'" : "";
				var href = pageBase + topic.pagePath.replace(/index\.md$/, "");
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
		// Instructor catalog pages do not need progress state or storage warnings.
		if (document.querySelector('[data-selftest-personalization="off"]')) {
			return;
		}
		return fetchManifest().then(function (manifest) {
			renderStorageWarning();
			var rows = getCurrentRows(manifest);
			renderTopicSummary(rows);
			renderQuestionBadges();
			updateTopicSummary(rows);
			renderDashboard(manifest);
			return { rows: rows, manifest: manifest };
		}).catch(function () {
			renderStorageWarning();
		});
	}

	function installLifecycleHooks() {
		document.addEventListener("selftest:ready", onReady);
		document.addEventListener("selftest:graded", onGraded);
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
		normalizePagePath: normalizePagePath,
		initPage: initPage,
		_installLifecycleHooks: installLifecycleHooks,
		_test: {
			getCurrentRows: getCurrentRows
		}
	};

	// CommonJS export for the Node-based .mjs tests; harmless in the browser.
	if (typeof module !== "undefined" && module.exports) {
		module.exports = window.SelfTestProgress;
	}

	installLifecycleHooks();
}());

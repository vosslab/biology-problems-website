"use strict";

(function () {
	// One lifecycle owns initial questions, replacements, grading and advancement.
	// Completion and streaks subscribe to its DOM events without owning the flow.
	var states = new Map();
	var advancement = null;
	// Resolve the vendored converter relative to this script's asset directory.
	var assetBase = new URL("../", document.currentScript.src);
	var enginePromise;
	var banks = new Map();

	function sameOrigin(url) {
		if (url.origin !== window.location.origin) {
			throw new Error("Question data must come from this site.");
		}
		return url;
	}

	async function bytes(url) {
		var response = await fetch(sameOrigin(url));
		if (!response.ok) { throw new Error("Could not load question data."); }
		return new Uint8Array(await response.arrayBuffer());
	}

	function engine() {
		if (!enginePromise) {
			enginePromise = (async function () {
				var api = await import(new URL("qti_wasm/src/index.js", assetBase).href);
				await api.initialize(await bytes(new URL("qti_wasm/generated/qti_wasm_bg.wasm", assetBase)));
				return api;
			}()).catch(function (error) { enginePromise = null; throw error; });
		}
		return enginePromise;
	}

	async function bankData(url) {
		if (!banks.has(url.href)) {
			var pending = (async function () {
				var source = await bytes(url);
				var doc = new DOMParser().parseFromString(new TextDecoder().decode(source), "text/html");
				var names = Array.from(new Set(Array.from(doc.querySelectorAll("img[src]")).map(function (img) {
					return img.getAttribute("src");
				}).filter(function (src) { return !/^(data:|https?:|\/\/)/i.test(src); })));
				var companions = await Promise.all(names.map(async function (name) {
					return { name: name, bytes: await bytes(new URL(name, url)) };
				}));
				return { kind: "file", name: url.pathname.split("/").pop(), bytes: source, companions: companions };
			}()).catch(function (error) { banks.delete(url.href); throw error; });
			banks.set(url.href, pending);
		}
		return banks.get(url.href);
	}

	async function questionDocument(state) {
		var url = sameOrigin(new URL(state.host.dataset.bbq, window.location.href));
		var loaded = await Promise.all([engine(), bankData(url)]);
		for (var attempt = 0; attempt < 32; attempt += 1) {
			var seed = crypto.getRandomValues(new Uint32Array(1))[0];
			var result = loaded[0].convert({
				inputFormat: "bbq_text_upload", outputFormat: "html_selftest",
				input: loaded[1], shuffleSeed: seed,
			});
			if (result.status !== "success") { throw new Error(result.error.message); }
			if (!result.artifact || result.artifact.kind !== "file") { throw new Error("No self-test was generated."); }
			var doc = new DOMParser().parseFromString(new TextDecoder().decode(result.artifact.primary.bytes), "text/html");
			var item = doc.querySelector("[id^='question_html_']");
			if (!item) { throw new Error("Generated self-test has no question."); }
			if (item.id !== "question_html_" + state.crc) { return doc; }
		}
		throw new Error("Could not find a different version. This bank may have only one question.");
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

	function current(state, version) {
		return state.host.isConnected && states.get(state.host) === state && state.version === version;
	}

	async function mount(state, next, version) {
		state.cleanup();
		state.ready = false;
		var fragment = document.createDocumentFragment();
		next.querySelectorAll("head style").forEach(function (style) {
			fragment.appendChild(style.cloneNode(true));
		});
		Array.from(next.body.childNodes).forEach(function (node) {
			fragment.appendChild(node.cloneNode(true));
		});
		state.body.replaceChildren(fragment);
		// The converter owns markup and grading. Execute its dependencies in order.
		for (var old of state.body.querySelectorAll("script")) {
			if (!current(state, version)) { return; }
			var script = document.createElement("script");
			Array.from(old.attributes).forEach(function (attr) {
				script.setAttribute(attr.name, attr.value);
			});
			script.textContent = old.textContent;
			if (script.hasAttribute("src")) {
				await new Promise(function (resolve, reject) {
					script.onload = resolve;
					script.onerror = function () {
						reject(new Error("Could not load a question script. Try again."));
					};
					old.replaceWith(script);
				});
			} else {
				old.replaceWith(script);
			}
		}
		if (!current(state, version)) { return; }
		var item = state.body.querySelector("[id^='question_html_']");
		var crc = item.id.slice("question_html_".length);
		bindGrading(state, crc, version);
		state.crc = crc;
		state.ready = true;
		state.advanced = false;
		state.host.dispatchEvent(new CustomEvent("selftest:ready", {
			bubbles: true, detail: { crc: crc }
		}));
	}

	function generate(state) {
		if (state.pending) { return state.pending; }
		state.cleanup();
		var version = ++state.version;
		state.button.disabled = true;
		state.body.inert = true;
		state.body.setAttribute("aria-busy", "true");
		state.status.textContent = "Loading question...";
		state.pending = (async function () {
			try {
				var next = await questionDocument(state);
				if (!current(state, version)) { return false; }
				await mount(state, next, version);
				if (!current(state, version)) { return false; }
				state.button.textContent = "New version";
				state.status.textContent = "Question ready.";
				return true;
			} catch (error) {
				if (current(state, version)) {
					// Conversion failure leaves the prior attempt usable; mounting failure
					// leaves the incomplete body inert until Retry mounts a valid question.
					if (state.ready) { bindGrading(state, state.crc, version); }
					state.status.textContent = error.message || "Could not load a question. Try again.";
					state.button.textContent = "Retry";
				}
				return false;
			} finally {
				if (current(state, version)) {
					state.pending = null;
					state.button.disabled = false;
					state.body.inert = !state.ready;
					state.body.setAttribute("aria-busy", "false");
				}
			}
		}());
		return state.pending;
	}

	function bindGrading(state, crc, version) {
		var name = "checkAnswer_" + crc;
		var original = window[name];
		var resultElement = state.body.querySelector("[id^='result_']");
		if (typeof original !== "function" || !resultElement) {
			throw new Error("Could not initialize question grading. Try again.");
		}
		var wrapped = function () {
			if (!current(state, version) || !state.ready) { return; }
			var result = original.apply(this, arguments);
			state.host.dispatchEvent(new CustomEvent("selftest:graded", {
				bubbles: true, detail: { crc: crc, verdict: classifyResultElement(resultElement) }
			}));
			return result;
		};
		window[name] = wrapped;
		state.cleanup = function () {
			if (window[name] === wrapped) { window[name] = original; }
		};
	}

	function cancelAdvance() {
		if (advancement) { window.clearTimeout(advancement.timer); }
		advancement = null;
	}

	function advance(state) {
		cancelAdvance();
		var hosts = Array.from(states.keys());
		var next = states.get(hosts[hosts.indexOf(state.host) + 1]);
		if (!next) { return; }
		var task = { timer: null, elapsed: false, ready: false, version: state.version };
		advancement = task;
		function finish() {
			if (advancement !== task || !current(state, task.version) || !next.host.isConnected) {
				return;
			}
			if (!task.elapsed || !task.ready) { return; }
			advancement = null;
			next.host.focus({ preventScroll: true });
			var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
			next.host.scrollIntoView({ behavior: reduced ? "instant" : "smooth", block: "start" });
		}
		task.timer = window.setTimeout(function () { task.elapsed = true; finish(); }, 500);
		// Generation and the feedback pause run concurrently; never advance into an empty body.
		var ready = next.pending || (next.ready ? Promise.resolve(true) : generate(next));
		ready.then(function (success) { task.ready = success; finish(); });
	}

	function onGraded(event) {
		var state = states.get(event.target);
		if (!state || !state.ready || event.detail.crc !== state.crc) { return; }
		var verdict = event.detail.verdict;
		if (verdict === "no-answer" || verdict === "unknown") { return; }
		var correct = verdict === "full-correct";
		if (correct && !state.advanced) {
			state.advanced = true;
			advance(state);
		}
	}

	function prepare(host) {
		var header = document.createElement("div");
		header.className = "selftest-question-header";
		var button = document.createElement("button");
		button.type = "button";
		button.className = "qti-btn qti-btn-reset selftest-reroll-button";
		button.textContent = "Start question";
		var status = document.createElement("span");
		status.className = "selftest-question-status";
		status.setAttribute("role", "status");
		status.setAttribute("aria-live", "polite");
		header.append(button, status);
		host.prepend(header);
		host.tabIndex = -1;
		var state = {
			host: host, body: host.querySelector(".selftest-reroll-content"),
			button: button, status: status, crc: null, version: 0, ready: false,
			pending: null, advanced: false, cleanup: function () {}
		};
		button.addEventListener("click", function () {
			cancelAdvance();
			generate(state);
		});
		states.set(host, state);
		return state;
	}

	function initPage() {
		var hosts = Array.from(document.querySelectorAll(".qti-selftest[data-bbq]"));
		if (hosts.length === states.size && hosts.every(function (host) { return states.has(host); })) {
			return;
		}
		cancelAdvance();
		states.forEach(function (state) { state.cleanup(); });
		states.clear();
		hosts.forEach(prepare);
		if (hosts.length) { generate(states.get(hosts[0])); }
	}

	window.SelfTestQuestions = { initPage: initPage, classifyResultElement: classifyResultElement };
	if (typeof module !== "undefined" && module.exports) { module.exports = window.SelfTestQuestions; }
	document.addEventListener("selftest:graded", onGraded);
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", initPage);
	} else { initPage(); }
	if (window.document$) { window.document$.subscribe(initPage); }
}());

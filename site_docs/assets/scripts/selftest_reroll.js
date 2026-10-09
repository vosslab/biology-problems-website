"use strict";

(function () {
	// ASVS 3.6.1: the pinned converter is vendored and loaded from this site.
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

	async function reroll(host, button, status) {
		button.disabled = true;
		status.textContent = "Loading a new version...";
		try {
			var url = sameOrigin(new URL(host.dataset.bbq, window.location.href));
			var loaded = await Promise.all([engine(), bankData(url)]);
			var current = host.querySelector("[id^='question_html_']");
			var currentId = current && current.id;
			var next;
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
				if (item && item.id !== currentId) { next = doc; break; }
			}
			if (!next) { throw new Error("Could not find a different version. This bank may have only one question. Try again."); }
			var content = host.querySelector(".selftest-reroll-content");
			var fragment = document.createDocumentFragment();
			next.querySelectorAll("head style").forEach(function (style) { fragment.appendChild(style.cloneNode(true)); });
			Array.from(next.body.childNodes).forEach(function (node) { fragment.appendChild(node.cloneNode(true)); });
			content.replaceChildren(fragment);
			// Authored repository content is trusted, just as in the build-time include.
			// Recreating scripts initializes the converter's grading and interaction controls.
			for (var old of content.querySelectorAll("script")) {
				var script = document.createElement("script");
				Array.from(old.attributes).forEach(function (attr) { script.setAttribute(attr.name, attr.value); });
				script.textContent = old.textContent;
				if (script.hasAttribute("src")) {
					// Inline drawing code depends on libraries loaded earlier in the document.
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
			if (window.SelfTestProgress) { window.SelfTestProgress.initPage(); }
			status.textContent = "New version ready.";
		} catch (error) {
			// ASVS 3.2.2: errors are text, never interpreted as authored markup.
			status.textContent = error.message || "Could not load a new version. Try again.";
		} finally { button.disabled = false; }
	}

	function init() {
		document.querySelectorAll(".qti-selftest[data-bbq]").forEach(function (host) {
			if (host.querySelector(".selftest-reroll-button")) { return; }
			var content = document.createElement("div");
			content.className = "selftest-reroll-content";
			while (host.firstChild) { content.appendChild(host.firstChild); }
			host.appendChild(content);
			var button = document.createElement("button");
			button.type = "button";
			button.className = "md-button selftest-reroll-button";
			button.textContent = "New version";
			var status = document.createElement("span");
			status.setAttribute("role", "status");
			status.setAttribute("aria-live", "polite");
			host.append(button, status);
			button.addEventListener("click", function () { reroll(host, button, status); });
		});
	}
	if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", init); } else { init(); }
	if (window.document$) { window.document$.subscribe(init); }
}());

"use strict";

(function () {
	var STATE_KEY = "__dailyPuzzleInputStateV1";
	var state = window[STATE_KEY];
	if (!state) {
		state = { listenerInstalled: false, opts: null };
		window[STATE_KEY] = state;
	}

	function defaultBlockedTarget(el) {
		var node = el;
		while (node) {
			if (node.isContentEditable) {
				return true;
			}
			node = node.parentElement;
		}

		if (!el) {
			return false;
		}
		var tag = (el.tagName || "").toLowerCase();
		return tag === "input" || tag === "textarea" || tag === "select";
	}

	function hasOpenDialog() {
		return Boolean(document.querySelector && document.querySelector("dialog[open]"));
	}

	function mergeOptions(target, source) {
		var dst = target || {};
		var src = source || {};
		var k = null;
		for (k in src) {
			if (!Object.prototype.hasOwnProperty.call(src, k)) {
				continue;
			}
			if (src[k] === undefined) {
				continue;
			}
			dst[k] = src[k];
		}
		return dst;
	}

	function install(options) {
		state.opts = mergeOptions(state.opts || {}, options || {});

		if (state.listenerInstalled) {
			return;
		}
		state.listenerInstalled = true;

		window.addEventListener("keydown", function (evt) {
			var opts = state.opts;
			if (!opts) {
				return;
			}
			var isEnabled = opts.isEnabled || function () { return true; };
			if (!isEnabled()) {
				return;
			}

			if (evt.ctrlKey || evt.metaKey || evt.altKey) {
				return;
			}
			if (hasOpenDialog()) {
				return;
			}

			var isBlockedTarget = opts.isBlockedTarget || defaultBlockedTarget;
			if (isBlockedTarget(evt.target)) {
				return;
			}

			var k = evt.key;
			if (k === "Enter") {
				evt.preventDefault();
				if (opts.onEnter) {
					opts.onEnter();
				}
				return;
			}

			if (k === "Backspace") {
				evt.preventDefault();
				if (opts.onBackspace) {
					opts.onBackspace();
				}
				return;
			}

			if (k && k.length === 1) {
				var ch = k.toUpperCase();
				if (ch >= "A" && ch <= "Z") {
					if (evt.repeat) {
						return;
					}
					evt.preventDefault();
					if (opts.onType) {
						opts.onType(ch);
					}
				}
			}
		});
	}

	window.DailyPuzzleInput = window.DailyPuzzleInput || {};
	window.DailyPuzzleInput.install = install;
	window.DailyPuzzleInput._state = state;
}());

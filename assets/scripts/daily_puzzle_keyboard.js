"use strict";

(function () {
	var DEFAULT_ROWS = [
		"QWERTYUIOP",
		"ASDFGHJKL",
		"ZXCVBNM"
	];

	function renderKeyboard(letterState, options) {
		var opts = options || {};
		var containerId = opts.containerId || "keyboard";
		var container = document.getElementById(containerId);
		if (!container) {
			return;
		}

		var rows = opts.rows || DEFAULT_ROWS;
		var isKeyDisabled = opts.isKeyDisabled || function () { return false; };
		var showEnterAndBackspace = opts.showEnterAndBackspace !== false;
		var disableKeys = opts.disableKeys !== false;

		container.innerHTML = "";

		function createKey(label, keyValue, extraClass, disabled) {
			var el = document.createElement("button");
			el.type = "button";
			el.textContent = label;
			el.dataset.key = keyValue;

			var cls = "kb-key";
			if (extraClass) {
				cls += " " + extraClass;
			}
			if (disabled) {
				cls += " disabled";
				if (disableKeys) {
					el.disabled = true;
				}
			}

			if (!disabled && /^[A-Z]$/.test(keyValue) && letterState) {
				var st = letterState[keyValue];
				if (st === "correct") {
					cls += " correct";
				} else if (st === "present") {
					cls += " present";
				} else if (st === "absent") {
					cls += " absent";
				}
			}

			el.className = cls;
			return el;
		}

		function createRow(letters, isBottom) {
			var rowEl = document.createElement("div");
			rowEl.className = "kb-row";

			if (showEnterAndBackspace && isBottom) {
				rowEl.appendChild(createKey("Enter", "ENTER", "wide", false));
			}

			var i = 0;
			for (i = 0; i < letters.length; i += 1) {
				var ch = letters[i];
				var disabled = Boolean(isKeyDisabled(ch));
				rowEl.appendChild(createKey(ch, ch, "", disabled));
			}

			if (showEnterAndBackspace && isBottom) {
				rowEl.appendChild(createKey("DEL", "BACKSPACE", "wide", false));
			}

			return rowEl;
		}

		container.appendChild(createRow(rows[0], false));
		container.appendChild(createRow(rows[1], false));
		container.appendChild(createRow(rows[2], true));
	}

	function attachKeyboardClick(onKey, options) {
		var opts = options || {};
		var containerId = opts.containerId || "keyboard";
		var container = document.getElementById(containerId);
		if (!container) {
			return;
		}

		var isKeyDisabled = opts.isKeyDisabled || function () { return false; };
		var onDisabledKey = opts.onDisabledKey || null;

		container.addEventListener("click", function (evt) {
			var target = evt.target;
			if (!target || target.tagName !== "BUTTON") {
				return;
			}
			var key = target.dataset.key;
			if (!key) {
				return;
			}

			if (/^[A-Z]$/.test(key) && isKeyDisabled(key)) {
				if (onDisabledKey) {
					onDisabledKey(key);
				}
				return;
			}
			onKey(key);
		});
	}

	window.DailyPuzzleKeyboard = {
		renderKeyboard: renderKeyboard,
		attachKeyboardClick: attachKeyboardClick
	};
}());

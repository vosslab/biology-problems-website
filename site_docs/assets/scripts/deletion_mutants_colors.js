"use strict";

(function () {
	var DARK_WHEEL = [
		"b30000", "b34100", "663300", "b37100", "999900", "465927", "4d9900", "008000",
		"008066", "008080", "076cab", "002db3", "004080", "690f8a", "800055", "99004d"
	];

	var LIGHT_WHEEL = [
		"ffcccc", "ffd9cc", "ffe6cc", "ffebcc", "ffffcc", "eaefdc", "d9ffcc", "ccffcc",
		"ccffe6", "ccffff", "ccf2ff", "ccd9ff", "ccccff", "e6ccff", "ffccf2", "ffccff"
	];

	var EXTRA_LIGHT_WHEEL = [
		"ffe6e6", "ffece6", "fff3e6", "fff9e5", "ffffe6", "f5f7ee", "ecffe6", "e6ffe6",
		"e6fff3", "e6ffff", "e6f9ff", "e6ecff", "e6e6ff", "f3e6ff", "ffe6f9", "ffe6ff"
	];

	function minDifference(indices) {
		var sorted = indices.slice().sort(function (a, b) { return a - b; });
		var diffs = [];
		var i = 0;

		for (i = 0; i < sorted.length - 1; i += 1) {
			diffs.push(sorted[i + 1] - sorted[i]);
		}

		if (!diffs.length) {
			return 0;
		}
		return Math.min.apply(null, diffs);
	}

	function getIndicesForColorWheel(numColors, wheelLength, rng) {
		var i = 0;

		if (numColors > wheelLength) {
			var wrap = [];
			for (i = 0; i < numColors; i += 1) {
				wrap.push(i % wheelLength);
			}
			return wrap;
		}

		if (numColors > Math.floor(wheelLength / 2) - 1) {
			var all = [];
			for (i = 0; i < wheelLength; i += 1) {
				all.push(i);
			}
			window.DailyPuzzleCore.shuffleInPlace(all, rng);
			return all.slice(0, numColors).sort(function (a, b) { return a - b; });
		}

		var minDistance = Math.floor(wheelLength / (numColors + 1));
		if (minDistance <= 0) {
			throw new Error("minDistance <= 0");
		}

		if (numColors > Math.floor(wheelLength / minDistance)) {
			throw new Error("numColors too large to satisfy minDistance requirement");
		}

		var selected = [];
		var available = [];
		for (i = 0; i < wheelLength; i += 1) {
			available.push(i);
		}

		for (i = 0; i < numColors; i += 1) {
			if (!available.length) {
				throw new Error("Cannot select further colors within minDistance constraints");
			}

			var idx = window.DailyPuzzleCore.randomIntInclusive(rng, 0, available.length - 1);
			var index = available[idx];
			selected.push(index);

			var offset = 0;
			for (offset = -minDistance + 1; offset < minDistance; offset += 1) {
				var removeIndex = (index + offset) % wheelLength;
				if (removeIndex < 0) {
					removeIndex += wheelLength;
				}
				var pos = available.indexOf(removeIndex);
				if (pos >= 0) {
					available.splice(pos, 1);
				}
			}
		}

		selected.sort(function (a, b) { return a - b; });
		if (numColors > 1 && minDifference(selected) < minDistance) {
			throw new Error("minDifference < minDistance");
		}

		return selected;
	}

	function pickColorPairs(numColors, rng) {
		var wheelLength = Math.min(DARK_WHEEL.length, LIGHT_WHEEL.length, EXTRA_LIGHT_WHEEL.length);
		var indices = getIndicesForColorWheel(numColors, wheelLength, rng);
		var colors = [];
		var i = 0;

		for (i = 0; i < indices.length; i += 1) {
			var j = indices[i];
			colors.push({
				dark: "#" + DARK_WHEEL[j],
				light: "#" + LIGHT_WHEEL[j],
				extraLight: "#" + EXTRA_LIGHT_WHEEL[j]
			});
		}

		return colors;
	}

	window.DeletionMutantsColors = {
		pickColorPairs: pickColorPairs
	};
}());


"use strict";

(function () {
	function getUtcDayKey(date) {
		var d = date || new Date();
		return d.toISOString().slice(0, 10);
	}

	function hashString32(str) {
		var h = 1779033703 ^ str.length;
		var i = 0;

		for (i = 0; i < str.length; i += 1) {
			h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
			h = (h << 13) | (h >>> 19);
		}

		h = Math.imul(h ^ (h >>> 16), 2246822507);
		h = Math.imul(h ^ (h >>> 13), 3266489909);
		h ^= h >>> 16;

		return h >>> 0;
	}

	function mulberry32(seed) {
		var a = seed >>> 0;
		return function () {
			var t = a += 0x6D2B79F5;
			t = Math.imul(t ^ (t >>> 15), t | 1);
			t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
			return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
		};
	}

	function makeSeededRng(seedString) {
		return mulberry32(hashString32(seedString));
	}

	function randomIntInclusive(rng, minValue, maxValue) {
		var r = rng();
		return Math.floor(r * (maxValue - minValue + 1)) + minValue;
	}

	function shuffleInPlace(items, rng) {
		var i = 0;
		for (i = items.length - 1; i > 0; i -= 1) {
			var j = randomIntInclusive(rng, 0, i);
			var tmp = items[i];
			items[i] = items[j];
			items[j] = tmp;
		}
		return items;
	}

	window.DailyPuzzleCore = {
		getUtcDayKey: getUtcDayKey,
		hashString32: hashString32,
		makeSeededRng: makeSeededRng,
		randomIntInclusive: randomIntInclusive,
		shuffleInPlace: shuffleInPlace
	};
}());


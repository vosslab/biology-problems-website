"use strict";

(function () {
	var WORD_SOURCE_PATH = "/daily_puzzles/deletetions_source/real_wordles.txt";
	var SECRET_SALT = "deletion-mutants-v1";
	var LOCALSTORAGE_CACHE_PREFIX = "deletion_mutants_words_cache_v1_";

	var _cache = {};

	function hasAllUniqueLetters(word) {
		var seen = {};
		var i = 0;
		for (i = 0; i < word.length; i += 1) {
			var ch = word[i];
			if (seen[ch]) {
				return false;
			}
			seen[ch] = true;
		}
		return true;
	}

	function parseWordListText(text, wordLength) {
		var lines = text.split(/\r?\n/);
		var words = [];
		var i = 0;

		for (i = 0; i < lines.length; i += 1) {
			var line = lines[i].trim();
			if (!line || line[0] === "#") {
				continue;
			}
			if (line.length !== wordLength) {
				continue;
			}
			if (!/^[a-z]+$/.test(line)) {
				continue;
			}

			var w = line.toUpperCase();
			if (!hasAllUniqueLetters(w)) {
				continue;
			}
			words.push(w);
		}

		return words;
	}

	async function loadCandidateWords(wordLength) {
		if (_cache[wordLength]) {
			return _cache[wordLength];
		}

		var cacheKey = LOCALSTORAGE_CACHE_PREFIX + String(wordLength);
		try {
			var cachedRaw = window.localStorage.getItem(cacheKey);
			if (cachedRaw) {
				var cachedWords = JSON.parse(cachedRaw);
				if (Array.isArray(cachedWords) && cachedWords.length) {
					_cache[wordLength] = cachedWords;
					return cachedWords;
				}
			}
		} catch (_) {
			// ignore and re-fetch
		}

		var resp = await fetch(WORD_SOURCE_PATH);
		if (!resp.ok) {
			throw new Error("Could not load word list (" + resp.status + ")");
		}
		var text = await resp.text();
		var words = parseWordListText(text, wordLength);

		if (!words.length) {
			throw new Error("Word list is empty after filtering");
		}

		_cache[wordLength] = words;
		try {
			window.localStorage.setItem(cacheKey, JSON.stringify(words));
		} catch (_) {
			// ignore quota / disabled storage
		}
		return words;
	}

	function getDailyIndex(words, date) {
		var dayKey = window.DailyPuzzleCore.getUtcDayKey(date || new Date());
		var key = dayKey + "|" + SECRET_SALT;
		var h = window.DailyPuzzleCore.hashString32(key);
		return h % words.length;
	}

	function getDailyWord(words, date) {
		return words[getDailyIndex(words, date)];
	}

	function getDailySeed(tag, answerWord, date) {
		var dayKey = window.DailyPuzzleCore.getUtcDayKey(date || new Date());
		return dayKey + "|" + SECRET_SALT + "|" + tag + "|" + answerWord;
	}

	window.DeletionMutantsWords = {
		loadCandidateWords: loadCandidateWords,
		getDailyWord: getDailyWord,
		getDailySeed: getDailySeed
	};
}());

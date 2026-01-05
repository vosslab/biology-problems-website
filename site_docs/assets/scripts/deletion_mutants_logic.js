"use strict";

(function () {
	function makePairKey(a, b) {
		return a + b;
	}

	function addNewPairs(geneOrder, startIndex, size, splitGenePairs, usedGenePairs) {
		var newPairs = 0;

		if (startIndex > 0) {
			var beforePair = makePairKey(geneOrder[startIndex - 1], geneOrder[startIndex]);
			if (!splitGenePairs[beforePair]) {
				splitGenePairs[beforePair] = true;
				newPairs += 1;
			}
		}

		if (startIndex + size < geneOrder.length) {
			var afterPair = makePairKey(
				geneOrder[startIndex + size - 1],
				geneOrder[startIndex + size]
			);
			if (!splitGenePairs[afterPair]) {
				splitGenePairs[afterPair] = true;
				newPairs += 1;
			}
		}

		var deletion = geneOrder.slice(startIndex, startIndex + size);
		var i = 0;
		for (i = 0; i < deletion.length - 1; i += 1) {
			var usedPair = makePairKey(deletion[i], deletion[i + 1]);
			if (!usedGenePairs[usedPair]) {
				usedGenePairs[usedPair] = true;
				newPairs += 1;
			}
		}

		return newPairs;
	}

	function generateDeletionsSub(geneOrder, rng) {
		var numGenes = geneOrder.length;
		var requiredGenePairs = numGenes - 1;

		var minDeletionSize = 2;
		var upperLimit = Math.floor(Math.sqrt(numGenes) * 2) + 1;
		upperLimit = Math.max(5, upperLimit);
		var maxDeletionSize = Math.min(numGenes - 1, upperLimit);

		var splitGenePairs = {};
		var usedGenePairs = {};
		var deletionsList = [];
		var deletionKeySet = {};

		var maxIterations = 5000;
		var iterations = 0;

		while (
			Object.keys(splitGenePairs).length < requiredGenePairs ||
			Object.keys(usedGenePairs).length < requiredGenePairs
		) {
			iterations += 1;
			if (iterations > maxIterations) {
				throw new Error("Deletion generation exceeded maxIterations");
			}

			var deletionSize = 0;
			if (rng() < 0.1) {
				deletionSize = window.DailyPuzzleCore.randomIntInclusive(rng, minDeletionSize, maxDeletionSize);
			} else if (numGenes > 4 && rng() < 0.7) {
				deletionSize = window.DailyPuzzleCore.randomIntInclusive(
					rng,
					minDeletionSize + 2,
					maxDeletionSize
				);
			} else {
				deletionSize = window.DailyPuzzleCore.randomIntInclusive(
					rng,
					minDeletionSize + 1,
					maxDeletionSize
				);
			}

			var deletionStart = window.DailyPuzzleCore.randomIntInclusive(rng, 0, numGenes - deletionSize);

			var newPairs = addNewPairs(
				geneOrder,
				deletionStart,
				deletionSize,
				splitGenePairs,
				usedGenePairs
			);

			var deletion = geneOrder.slice(deletionStart, deletionStart + deletionSize).slice().sort();
			var deletionKey = deletion.join("");

			if (newPairs > 0 && !deletionKeySet[deletionKey]) {
				deletionKeySet[deletionKey] = true;
				deletionsList.push(deletion);
			}
		}

		return deletionsList;
	}

	function generateDeletions(geneOrder, seedString) {
		var best = null;
		var attempt = 0;

		for (attempt = 0; attempt < 3; attempt += 1) {
			var rng = window.DailyPuzzleCore.makeSeededRng(seedString + "|attempt:" + String(attempt));
			var candidate = generateDeletionsSub(geneOrder, rng);
			if (!best || candidate.length < best.length) {
				best = candidate;
			}
		}

		return best;
	}

	window.DeletionMutantsLogic = {
		generateDeletions: generateDeletions
	};
}());


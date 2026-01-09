"use strict";

(function () {
	// Generate the growth table for a metabolic pathway puzzle.
	//
	// The pathway order is the answer word, left to right:
	// e.g., CRANE means C -> R -> A -> N -> E -> product
	//
	// Each mutant class is blocked at a different step.
	// A mutant grows (+) only when supplemented with a downstream intermediate.
	//
	// Class assignment (by number of rescuing supplements):
	// - Class with 1 plus: blocked between position 4 and 5 (only last letter rescues)
	// - Class with 2 plus: blocked between position 3 and 4
	// - Class with 3 plus: blocked between position 2 and 3
	// - Class with 4 plus: blocked between position 1 and 2
	// - Class with 5 plus: blocked before position 1 (all letters rescue)

	function generateGrowthTable(pathwayOrder, seedString) {
		// pathwayOrder is an array like ['C', 'R', 'A', 'N', 'E']
		var numSteps = pathwayOrder.length;

		// Create classes: each class i is blocked before step i
		// classData[i] = { blockBefore: i, rescueCount: numSteps - i }
		// blockBefore=0 means blocked before first step (all rescue)
		// blockBefore=4 means blocked before last step (only last rescues)
		var classData = [];
		var i = 0;
		for (i = 0; i < numSteps; i += 1) {
			classData.push({
				blockIndex: i,
				rescueCount: numSteps - i
			});
		}

		// Shuffle the class order so they appear in random order
		var rngClasses = window.DailyPuzzleCore.makeSeededRng(seedString + "|classes");
		window.DailyPuzzleCore.shuffleInPlace(classData, rngClasses);

		// Shuffle the column (metabolite) order so the answer cannot be read directly
		var rngColumns = window.DailyPuzzleCore.makeSeededRng(seedString + "|columns");
		var shuffledMetabolites = pathwayOrder.slice();
		window.DailyPuzzleCore.shuffleInPlace(shuffledMetabolites, rngColumns);

		var growthMatrix = [];
		var classIndex = 0;
		for (classIndex = 0; classIndex < classData.length; classIndex += 1) {
			var blockIndex = classData[classIndex].blockIndex;
			var row = [];

			// For each metabolite in shuffled column order
			var metaIndex = 0;
			for (metaIndex = 0; metaIndex < shuffledMetabolites.length; metaIndex += 1) {
				var metabolite = shuffledMetabolites[metaIndex];

				// Find position of this metabolite in the pathway
				var pathwayPosition = pathwayOrder.indexOf(metabolite);

				// Mutant grows if metabolite is at or after the block point
				// blockIndex=0 means blocked before pos 0, so all rescue
				// blockIndex=4 means blocked before pos 4, so only pos 4 rescues
				var grows = (pathwayPosition >= blockIndex);
				row.push(grows);
			}

			growthMatrix.push({
				classNum: classIndex + 1,
				blockIndex: blockIndex,
				rescueCount: classData[classIndex].rescueCount,
				growth: row
			});
		}

		return {
			metabolites: shuffledMetabolites,
			pathwayOrder: pathwayOrder,
			classes: growthMatrix
		};
	}

	window.MutantScreenLogic = {
		generateGrowthTable: generateGrowthTable
	};
}());

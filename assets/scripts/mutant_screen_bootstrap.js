"use strict";

/* global mutantScreenSetupGame */

document.addEventListener("DOMContentLoaded", function () {
	var messageEl = document.getElementById("message");
	if (window.DailyPuzzleUI) {
		window.DailyPuzzleUI.wireHelpButton("help-button", "instructions-details");
		window.DailyPuzzleUI.mountNextResetTimer("dp-next-reset");
	}

	if (typeof mutantScreenSetupGame !== "function") {
		if (messageEl) {
			messageEl.textContent = "Error: mutantScreenSetupGame is not defined.";
		}
		return;
	}

	mutantScreenSetupGame();
});

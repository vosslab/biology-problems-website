"use strict";

/* global deletionMutantsSetupGame */

document.addEventListener("DOMContentLoaded", function () {
	var messageEl = document.getElementById("message");
	if (window.DailyPuzzleUI) {
		window.DailyPuzzleUI.wireHelpButton("help-button", "instructions-details");
		window.DailyPuzzleUI.mountNextResetTimer("dp-next-reset");
	}

	if (typeof deletionMutantsSetupGame !== "function") {
		if (messageEl) {
			messageEl.textContent = "Error: deletionMutantsSetupGame is not defined.";
		}
		return;
	}

	deletionMutantsSetupGame();
});

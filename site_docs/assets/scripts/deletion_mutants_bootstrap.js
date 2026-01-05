"use strict";

/* global deletionMutantsSetupGame */

document.addEventListener("DOMContentLoaded", function () {
	var messageEl = document.getElementById("message");
	var helpButton = document.getElementById("help-button");
	var details = document.getElementById("instructions-details");

	if (helpButton && details) {
		helpButton.addEventListener("click", function () {
			details.open = true;
			details.scrollIntoView({ behavior: "smooth" });
		});
	}

	if (typeof deletionMutantsSetupGame !== "function") {
		if (messageEl) {
			messageEl.textContent = "Error: deletionMutantsSetupGame is not defined.";
		}
		return;
	}

	deletionMutantsSetupGame();
});


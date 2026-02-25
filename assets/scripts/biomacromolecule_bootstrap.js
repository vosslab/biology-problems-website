/* global initRDKitModule, RDKitModule, setupBiomacromoleculeGame */

document.addEventListener("DOMContentLoaded", function () {
	var messageEl = document.getElementById("message");

	// Wire help button to instructions
	if (window.DailyPuzzleUI) {
		window.DailyPuzzleUI.wireHelpButton("help-button", "instructions-details");
		window.DailyPuzzleUI.mountNextResetTimer("dp-next-reset");
	}

	if (typeof initRDKitModule !== "function") {
		messageEl.textContent = "Error: initRDKitModule is not available.";
		return;
	}

	initRDKitModule().then(function (instance) {
		window.RDKitModule = instance;
		console.log("RDKit " + RDKitModule.version());
		if (typeof setupBiomacromoleculeGame === "function") {
			setupBiomacromoleculeGame();
		} else {
			messageEl.textContent = "Error: setupBiomacromoleculeGame is not defined.";
		}
	}).catch(function (e) {
		console.error("RDKit init failed", e);
		messageEl.textContent = "Error: RDKit could not be loaded.";
	});
});

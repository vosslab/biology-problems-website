/* global initRDKitModule, RDKitModule, setupGame */

document.addEventListener("DOMContentLoaded", function () {
    var messageEl = document.getElementById("message");

    // Help button scrolls to instructions
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
        if (typeof setupGame === "function") {
            setupGame();
        } else {
            messageEl.textContent = "Error: setupGame is not defined in peptidyle_game.js.";
        }
    }).catch(function (e) {
        console.error("RDKit init failed", e);
        messageEl.textContent = "Error: RDKit could not be loaded.";
    });
});

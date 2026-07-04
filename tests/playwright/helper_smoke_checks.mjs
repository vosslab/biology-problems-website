// helper_smoke_checks.mjs
//
// Content-agnostic structural and interaction checks for the MkDocs-Material
// site smoke test. This is a bare-library helper (no @playwright/test import):
// it operates only on an already-navigated Playwright `page` handed in by the
// entrypoint (smoke.spec.ts), and it signals failure by throwing an Error
// whose message names the route so the caller can attribute pass/fail.
// Readiness uses web-first waits (locator.waitFor / page.waitForFunction); there
// are no fixed waitForTimeout sleeps.
//
// Two exports:
//   checkPageStructure(page, route)     -> asserts the mkdocs-material shell.
//   driveSelfTestIfPresent(page, route) -> question-agnostic self-test driver,
//                                          returns { present, driven }.
//
// Selector contract (source file:line each selector depends on):
//   Stock mkdocs-material shell (theme-owned; documented in the plan
//   Current-state summary at
//   /Users/vosslab/.claude/plans/recursive-finding-hejlsberg.md:82,106):
//     .md-header, article.md-typeset / .md-content, .md-footer,
//     .md-nav--primary, .md-search input.md-search__input.
//   Self-test container and machinery (site fragments + hook scripts):
//     .qti-selftest ....................... site_docs/assets/scripts/quiz_flow.js:17
//                                            site_docs/biochemistry/topic03/downloads/selftest-alpha_amino_acid_identification.html:2
//     [id^='question_html_'] ............... site_docs/assets/scripts/quiz_flow.js:109
//                                            site_docs/assets/scripts/selftest_progress.js:267
//     radio/checkbox answer inputs ......... site_docs/biochemistry/topic03/downloads/selftest-alpha_amino_acid_identification.html:8,12
//                                            site_docs/assets/scripts/quiz_flow.js:80
//     text input (fill-in-the-blank) ....... site_docs/biochemistry/topic03/downloads/selftest-which_amino_acid-FIB.html:6
//     drag-and-drop (matching) ............. site_docs/biochemistry/topic03/downloads/selftest-MATCH-amino_acids_properties.html:15 (.qti-dropzone), :47 (.draggable)
//     Check-answer button ("Check Answer") . site_docs/biochemistry/topic03/downloads/selftest-alpha_amino_acid_identification.html:24
//                                            site_docs/biochemistry/topic03/downloads/selftest-MATCH-amino_acids_properties.html:63
//     [id^='result_'] result target ....... site_docs/assets/scripts/quiz_flow.js:24
//                                            site_docs/biochemistry/topic03/downloads/selftest-alpha_amino_acid_identification.html:25
//     no-answer prompt strings ............. site_docs/assets/scripts/selftest_progress.js:100-104
//                                            site_docs/assets/scripts/quiz_flow.js:50-53
//     verdict result text (e.g. "CORRECT") . site_docs/assets/scripts/selftest_progress.js:97
//                                            site_docs/biochemistry/topic03/downloads/selftest-MATCH-amino_acids_properties.html:147 ("Total Score:")
//     .qti-feedback-success/-error ......... site_docs/assets/scripts/quiz_flow.js:82
//
// Design note (deviation from the plan's literal rule-2 wording): the plan text
// names "radio/checkbox input" as the required answer control, but the real
// generated fragments use three archetypes -- radio/checkbox (multiple choice),
// text input (fill-in-the-blank), and drag-and-drop (matching). topic03's first
// self-test is a matching question with no radio/checkbox. Requiring
// radio/checkbox would falsely FAIL matching and fill-in-the-blank pages and
// defeat the plan's stated question-agnostic goal. To honor that goal, an
// "answer control" here is any of: radio/checkbox input, text/number input, or
// a drag-and-drop element (.draggable / .qti-dropzone). Rule 2 still FAILS when
// none of these exist (genuinely no way to answer).

// Timeout budgets are hardcoded (no config knobs, per the plan). Structure
// waits are short; the self-test reaction gets a longer budget because the
// generated question JS may run after content and images settle.
const STRUCTURE_TIMEOUT_MS = 10000;
const REACTION_TIMEOUT_MS = 15000;

// Result strings the site treats as "no answer given" rather than a real
// verdict. Kept in sync with selftest_progress.js:100-104 and quiz_flow.js:50-53.
const NO_ANSWER_TEXTS = [
	"",
	"Please select an answer.",
	"Please enter a value.",
	"Please enter a valid number.",
];

// ===========================================================================
// Structural shell checks
// ===========================================================================

// Hard invariants: present and visible on every route. mkdocs-material renders
// the content as <article class="... md-typeset">; .md-content is its wrapper.
const HARD_INVARIANTS = [
	{ selector: ".md-header", label: "site header (.md-header)" },
	{ selector: "article.md-typeset, .md-content", label: "main content (article.md-typeset / .md-content)" },
	{ selector: ".md-footer", label: "site footer (.md-footer)" },
];

// Present-in-DOM only: mkdocs-material hides the primary nav and search input by
// viewport at desktop/mobile widths, so query for attachment, not visibility.
const DOM_PRESENCE_INVARIANTS = [
	{ selector: ".md-nav--primary", label: "primary nav (.md-nav--primary)" },
	{ selector: ".md-search input.md-search__input", label: "search input (.md-search input.md-search__input)" },
];

//============================================
// Assert the core mkdocs-material shell renders on this route. Throws an Error
// naming the route and the missing element on any miss.
export async function checkPageStructure(page, route) {
	// Hard invariants must be present and visible.
	for (const invariant of HARD_INVARIANTS) {
		await requireVisible(page, invariant.selector, invariant.label, route);
	}
	// A top-level <h1> (the page title) must be present and visible.
	await requireHeadingVisible(page, route);
	// Nav and search must exist in the DOM but need not be visible.
	for (const invariant of DOM_PRESENCE_INVARIANTS) {
		await requirePresent(page, invariant.selector, invariant.label, route);
	}
}

//============================================
// Wait for a selector to become visible; rethrow as a clear route-named error.
async function requireVisible(page, selector, label, route) {
	const locator = page.locator(selector).first();
	try {
		await locator.waitFor({ state: "visible", timeout: STRUCTURE_TIMEOUT_MS });
	} catch (_) {
		throw new Error(
			`Structural check failed on ${route}: expected ${label} to be present and visible.`
		);
	}
}

//============================================
// Wait for a selector to be attached to the DOM (visibility not required).
async function requirePresent(page, selector, label, route) {
	const locator = page.locator(selector).first();
	try {
		await locator.waitFor({ state: "attached", timeout: STRUCTURE_TIMEOUT_MS });
	} catch (_) {
		throw new Error(
			`Structural check failed on ${route}: expected ${label} to be present in the DOM.`
		);
	}
}

//============================================
// Wait for a top-level <h1> heading to be present and visible.
async function requireHeadingVisible(page, route) {
	const heading = page.getByRole("heading", { level: 1 }).first();
	try {
		await heading.waitFor({ state: "visible", timeout: STRUCTURE_TIMEOUT_MS });
	} catch (_) {
		throw new Error(
			`Structural check failed on ${route}: expected a top-level <h1> heading to be present and visible.`
		);
	}
}

// ===========================================================================
// Question-agnostic self-test driver
// ===========================================================================

//============================================
// Drive the first self-test on the page without inspecting question or answer
// content. Follows the four-rule decision tree:
//   (1) no .qti-selftest         -> pass (return { present: false }).
//   (2) present but broken       -> throw (missing required machinery).
//   (3) drivable and reacts      -> pass (return { present: true, driven: true }).
//   (4) present but no reaction  -> throw (a valid Check click did nothing).
// Returns { present, driven } on pass so the caller can count self-test pages.
export async function driveSelfTestIfPresent(page, route) {
	const selfTests = page.locator(".qti-selftest");
	const selfTestCount = await selfTests.count();
	// Rule 1: nothing to drive on this page.
	if (selfTestCount === 0) {
		return { present: false, driven: false };
	}

	// Scope everything to the first self-test; the entrypoint enforces one
	// per page, so driving the first is sufficient.
	const container = selfTests.first();

	// Rule 2: the basic machinery must exist, or the markup/JS is broken.
	const missing = await findMissingMachinery(container);
	if (missing.length > 0) {
		throw new Error(
			`Self-test check failed on ${route}: self-test container present but ` +
			`missing required machinery: ${missing.join(", ")}.`
		);
	}

	// The fragment lives inside a <details>; expand it so its controls are
	// reachable for a real click.
	await ensureEnclosingDetailsOpen(container);

	// Record the result element and its pre-click text so a change is detectable.
	const resultLocator = container.locator("[id^='result_']").first();
	const resultId = await resultLocator.getAttribute("id");
	const initialResultText = ((await resultLocator.textContent()) || "").trim();

	// Provide the first available answer generically (never reading content),
	// then click Check by its accessible role/name.
	await provideFirstAnswer(container);
	await container.getByRole("button", { name: /check/i }).first().click();

	// Rule 3 / Rule 4: require an observable, verdict-agnostic reaction.
	await waitForSelfTestReaction(page, resultId, initialResultText, route);
	return { present: true, driven: true };
}

//============================================
// Return a list of missing machinery pieces for the self-test container.
// An empty list means all required pieces are present.
async function findMissingMachinery(container) {
	const missing = [];
	// A question block anchors the rendered question HTML.
	const questionCount = await container.locator("[id^='question_html_']").count();
	if (questionCount === 0) {
		missing.push("question block ([id^='question_html_'])");
	}
	// Some answer mechanism must exist (see the header design note for why this
	// accepts radio/checkbox, text/number inputs, or drag-and-drop elements).
	const answerCount = await countAnswerControls(container);
	if (answerCount === 0) {
		missing.push("an answer control (radio/checkbox, text/number input, or drag-and-drop element)");
	}
	// A Check-answer button drives evaluation.
	const buttonCount = await container.getByRole("button", { name: /check/i }).count();
	if (buttonCount === 0) {
		missing.push("a Check-answer button (getByRole button matching /check/i)");
	}
	// A result target receives the verdict text.
	const resultCount = await container.locator("[id^='result_']").count();
	if (resultCount === 0) {
		missing.push("a result target ([id^='result_'])");
	}
	return missing;
}

//============================================
// Count answer controls across all three question archetypes.
async function countAnswerControls(container) {
	// Multiple-choice and multi-answer use radio/checkbox; fill-in-the-blank and
	// numeric use text/number inputs.
	const inputCount = await container.locator(
		"input[type='radio'], input[type='checkbox'], input[type='text'], input[type='number']"
	).count();
	if (inputCount > 0) {
		return inputCount;
	}
	// Matching questions have no form input; they use drag-and-drop elements.
	const dragDropCount = await container.locator(".draggable, .qti-dropzone").count();
	return dragDropCount;
}

//============================================
// Expand the <details> wrapping this self-test, if any, via a real summary
// click. Skips when already open (quiz_flow.js auto-opens the first) or when
// the self-test is not inside a <details>.
async function ensureEnclosingDetailsOpen(container) {
	const details = container.locator("xpath=ancestor::details[1]");
	const detailsCount = await details.count();
	if (detailsCount === 0) {
		return;
	}
	const isOpen = await details.evaluate((node) => node.open);
	if (isOpen) {
		return;
	}
	// Click the summary, the same gesture a user makes to reveal the question.
	await details.locator("summary").first().click();
}

//============================================
// Provide the first available answer, choosing the interaction that matches the
// control type. Never inspects question or answer content.
async function provideFirstAnswer(container) {
	// Prefer a radio/checkbox: a multiple-choice question with no selection only
	// shows the "Please select an answer." no-answer prompt, not a real verdict.
	const choices = container.locator("input[type='radio'], input[type='checkbox']");
	if ((await choices.count()) > 0) {
		await choices.first().check();
		return;
	}
	// Fill-in-the-blank / numeric questions: a benign value produces a verdict.
	const textInputs = container.locator("input[type='text'], input[type='number']");
	if ((await textInputs.count()) > 0) {
		await textInputs.first().fill("1");
		return;
	}
	// Drag-and-drop (matching) questions have no simple input; clicking Check
	// still scores the empty dropzones and produces an observable reaction.
}

//============================================
// Poll for an observable, verdict-agnostic reaction after the Check click:
// the result element gains non-empty verdict text (different from its initial
// text and not a no-answer prompt), or a qti-feedback class appears in the
// self-test container. Throws a route-named error if nothing reacts in time.
async function waitForSelfTestReaction(page, resultId, initialText, route) {
	try {
		await page.waitForFunction(
			(args) => {
				const resultElement = document.querySelector('[id="' + args.id + '"]');
				if (!resultElement) {
					return false;
				}
				const text = (resultElement.textContent || "").trim();
				const isNoAnswer = args.noAnswer.indexOf(text) !== -1;
				const verdictChanged = text.length > 0 && text !== args.initial && !isNoAnswer;
				const selfTest = resultElement.closest(".qti-selftest");
				const feedback = selfTest
					? selfTest.querySelector(".qti-feedback-success, .qti-feedback-error")
					: null;
				return verdictChanged || feedback !== null;
			},
			{ id: resultId, initial: initialText, noAnswer: NO_ANSWER_TEXTS },
			{ timeout: REACTION_TIMEOUT_MS }
		);
	} catch (_) {
		throw new Error(
			`Self-test check failed on ${route}: a self-test is present and was given ` +
			`a valid answer and a Check click, but its result element ` +
			`([id="${resultId}"]) did not react (no verdict text change and no ` +
			`qti-feedback class). A present-but-inoperable self-test is a regression.`
		);
	}
}

// selftest_visual_survey.mjs
//
// Two-mode Playwright survey of all selftest question types on the biology
// problems website dev server (http://127.0.0.1:8000).
//
// Passive visual survey:
//   Opens each representative page, expands the <details> panel, takes
//   screenshots before interaction, and captures console errors.
//   Covers desktop (1280) and mobile (390) in both light and dark themes
//   (Material "slate" via __palette localStorage seed).
//
// Interactive functional survey:
//   Answers questions correctly (or simulates drag-type interactions via JS),
//   screenshots the result state, captures console errors, and checks the
//   expected result string against the engine contract:
//     - Literal "CORRECT"
//     - "Total Score: X out of Y" with X==Y
//     - "Correct positions: X of Y" with X==Y
//     - "Correct: X of Y" with X==Y
//
// Question types covered: MC, WOMC, TFMS, EQUATION, MA, MATCH, FIB, NUM
// (ORDER and MULTI_FIB are not present in this repo's generated HTML set).
//
// Run from repo root:
//   node tests/playwright/selftest_visual_survey.mjs
//
// Output: test-results/selftest_survey/baseline/ (screenshots + report.json)
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = 'http://127.0.0.1:8000';
const OUT = 'test-results/selftest_survey/baseline';
fs.mkdirSync(OUT, { recursive: true });

const DESKTOP_VP = { width: 1280, height: 900 };
const MOBILE_VP  = { width: 390,  height: 844 };

// ===========================================================================
// Representative targets: one per question type plus bonus pages
//
// topicPages: rendered Material site pages (include fragments via {% include %})
// standaloneFiles: direct selftest-*.html fragments (no Material chrome)
// ===========================================================================

// Topic pages - each entry covers a question type embedded in context
const TOPIC_PAGES = [
	// MC: topic01 has selftest-which_macromolecule-MC.html (RDKit canvas)
	{ slug: 'topic_biochem01', url: '/biochemistry/topic01/', qtype: 'MC+RDKit' },
	// WOMC: topic01 has WOMC fragments
	{ slug: 'topic_biochem01_womc', url: '/biochemistry/topic01/', qtype: 'WOMC' },
	// MATCH: topic01 has MATCH-bond_types (drag-and-drop, long-text)
	{ slug: 'topic_biochem01_match', url: '/biochemistry/topic01/', qtype: 'MATCH' },
	// FIB + RDKit: topic03 has polypeptide_fib_sequence-FIB (canvas + text input)
	{ slug: 'topic_biochem03', url: '/biochemistry/topic03/', qtype: 'FIB+RDKit' },
	// TFMS: topic06 has TFMS-gibbs_free_energy_equation
	{ slug: 'topic_biochem06', url: '/biochemistry/topic06/', qtype: 'TFMS' },
	// MA (multiple-answer checkboxes): topic10 has classify_Fischer-MA
	{ slug: 'topic_biochem10', url: '/biochemistry/topic10/', qtype: 'MA' },
	// EQUATION (MC showing MathML): topic02 has Henderson-Hasselbalch-EQUATION
	{ slug: 'topic_biochem02', url: '/biochemistry/topic02/', qtype: 'EQUATION+NUM' },
	// NUM (MC radio, numeric answer choices): genetics/topic10
	{ slug: 'topic_genetics10', url: '/genetics/topic10/', qtype: 'NUM' },
	// Multi-selftest page: genetics/topic11 has many tables and selftest blocks
	{ slug: 'topic_genetics11_multi', url: '/genetics/topic11/', qtype: 'MULTI-FRAGMENT' },
	// Long-text MATCH: biochem topic01 MATCH-macromolecules is a long matching table
	{ slug: 'topic_biochem01_longmatch', url: '/biochemistry/topic01/', qtype: 'MATCH-long' },
];

// Standalone selftest HTML fragments (served as raw file paths)
const STANDALONE_FILES = [
	// MC with RDKit canvas (standalone - no Material chrome, just the fragment)
	{
		slug: 'standalone_mc_rdkit',
		url: '/biochemistry/topic01/downloads/selftest-which_macromolecule-MC.html',
		qtype: 'MC+RDKit',
	},
	// MATCH standalone
	{
		slug: 'standalone_match',
		url: '/biochemistry/topic01/downloads/selftest-MATCH-bond_types.html',
		qtype: 'MATCH',
	},
	// FIB standalone (expect ReferenceError on Check Answer due to template bug)
	{
		slug: 'standalone_fib',
		url: '/biochemistry/topic03/downloads/selftest-polypeptide_fib_sequence-FIB-2aa.html',
		qtype: 'FIB',
	},
	// EQUATION standalone
	{
		slug: 'standalone_equation',
		url: '/biochemistry/topic02/downloads/selftest-Henderson-Hasselbalch-EQUATION.html',
		qtype: 'EQUATION',
	},
	// TFMS standalone
	{
		slug: 'standalone_tfms',
		url: '/biochemistry/topic06/downloads/selftest-TFMS-gibbs_free_energy_equation.html',
		qtype: 'TFMS',
	},
	// MA standalone
	{
		slug: 'standalone_ma',
		url: '/biochemistry/topic10/downloads/selftest-classify_Fischer-MA-with_hint.html',
		qtype: 'MA',
	},
	// NUM standalone
	{
		slug: 'standalone_num',
		url: '/genetics/topic10/downloads/selftest-hardy_weinberg_numeric-NUM-5_choices.html',
		qtype: 'NUM',
	},
	// WOMC standalone
	{
		slug: 'standalone_womc',
		url: '/biochemistry/topic01/downloads/selftest-WOMC-bond_types.html',
		qtype: 'WOMC',
	},
];

// ===========================================================================
// Helper: seed Material dark theme via localStorage before page load
// ===========================================================================
function darkInitScript() {
	return () => {
		localStorage.setItem('__palette', JSON.stringify({
			index: 1,
			color: { scheme: 'slate', primary: 'green', accent: 'lime' },
		}));
	};
}

// ===========================================================================
// Helper: detect question type from the page DOM and extract CRC
// Returns an array of { crc, qtype } for all selftest blocks on the page.
// ===========================================================================
async function detectQuestions(page) {
	return await page.evaluate(() => {
		// All selftest question containers use id="question_html_<crc>"
		const containers = Array.from(document.querySelectorAll('[id^="question_html_"]'));
		return containers.map(el => {
			const crc = el.id.replace('question_html_', '');
			// Detect question type from DOM structure
			const hasDraggable = Boolean(el.querySelector('.draggable'));
			const hasCheckbox = Boolean(el.querySelector('input[type="checkbox"]'));
			const hasRadio = Boolean(el.querySelector('input[type="radio"]'));
			// NUM uses id="num_input_<crc>" with inputmode="decimal"; FIB uses id="fib_input_<crc>"
			const hasNumInput = Boolean(document.getElementById('num_input_' + crc));
			const hasFibInput = Boolean(document.getElementById('fib_input_' + crc));
			const hasCanvas = Boolean(el.querySelector('canvas'));
			let qtype = 'unknown';
			if (hasDraggable) {
				qtype = 'MATCH';
			} else if (hasCheckbox) {
				qtype = 'MA';
			} else if (hasRadio) {
				qtype = 'MC';
			} else if (hasNumInput) {
				qtype = 'NUM';
			} else if (hasFibInput) {
				qtype = 'FIB';
			}
			return { crc, qtype, hasCanvas };
		});
	});
}

// ===========================================================================
// Helper: attempt a correct answer interaction for a single question block.
// Uses in-page JS to set the correct answer state, then calls checkAnswer.
// Returns { resultText, consoleErrors[] }
// ===========================================================================
async function interactCorrect(page, crc, qtype) {
	// Collect console errors during this interaction
	const errors = [];
	const handler = msg => {
		if (msg.type() === 'error') {
			errors.push(msg.text());
		}
	};
	page.on('console', handler);

	let resultText = null;
	try {
		if (qtype === 'MC' || qtype === 'TFMS' || qtype === 'EQUATION' || qtype === 'WOMC') {
			// Radio button: find correct radio and check it, then call checkAnswer
			await page.evaluate((c) => {
				const container = document.getElementById('question_html_' + c);
				if (!container) return;
				// Find the radio with data-correct="true"
				const correct = container.querySelector('input[type="radio"][data-correct="true"]');
				if (correct) correct.checked = true;
				// Call the global checkAnswer function
				const fn = window['checkAnswer_' + c];
				if (fn) fn();
			}, crc);
		} else if (qtype === 'NUM') {
			// NUM: numAnswer_<crc> is declared as a const in a script tag, so it is NOT
			// accessible via window[]. Extract it from the script text using a regex.
			await page.evaluate((c) => {
				// Find the inline script that declares numAnswer_<crc>
				const scripts = Array.from(document.querySelectorAll('script'));
				let numAnswer = null;
				const pattern = new RegExp('const\\s+numAnswer_' + c.replace('_', '_') + '\\s*=\\s*([\\d.e+-]+)');
				for (const s of scripts) {
					const m = s.textContent.match(pattern);
					if (m) {
						numAnswer = parseFloat(m[1]);
						break;
					}
				}
				const inputEl = document.getElementById('num_input_' + c);
				if (inputEl && numAnswer !== null) {
					inputEl.value = String(numAnswer);
				} else if (inputEl) {
					// fallback: no answer found, try 0 (will be wrong but tests the check path)
					inputEl.value = '0';
				}
				const fn = window['checkAnswer_' + c];
				if (fn) fn();
			}, crc);
		} else if (qtype === 'MA') {
			// Checkboxes: check all with data-correct="true", then call checkAnswer
			await page.evaluate((c) => {
				const container = document.getElementById('question_html_' + c);
				if (!container) return;
				const corrects = container.querySelectorAll('input[type="checkbox"][data-correct="true"]');
				corrects.forEach(cb => { cb.checked = true; });
				const fn = window['checkAnswer_' + c];
				if (fn) fn();
			}, crc);
		} else if (qtype === 'MATCH') {
			// Drag-and-drop: simulate by setting dataset.value on each dropzone
			// to match its data-correct attribute, then call checkAnswer
			await page.evaluate((c) => {
				const container = document.getElementById('question_html_' + c);
				if (!container) return;
				const dropzones = container.querySelectorAll('.dropzone');
				dropzones.forEach(zone => {
					// data-correct holds the correct draggable data-value (CRC token)
					const correctVal = zone.dataset.correct;
					zone.dataset.value = correctVal;
					// Mirror the real drop handler: show the draggable's readable innerText,
					// not the raw CRC token, so after-screenshots match real user behavior.
					const draggable = container.querySelector('.draggable[data-value="' + correctVal + '"]');
					const displayText = draggable ? draggable.innerText.trim() : correctVal;
					zone.textContent = displayText;
					zone.style.border = '2px solid var(--qti-dropzone-border-filled, #888888)';
				});
				const fn = window['checkAnswer_' + c];
				if (fn) fn();
			}, crc);
		} else if (qtype === 'FIB') {
			// FIB: attempt to type a value and call checkAnswer.
			// This is expected to throw ReferenceError due to template bug.
			await page.evaluate((c) => {
				const inputEl = document.getElementById('fib_input_' + c);
				if (inputEl) inputEl.value = 'test';
				const fn = window['checkAnswer_' + c];
				if (fn) fn();
			}, crc);
		}

		// Read the result text
		resultText = await page.evaluate((c) => {
			const el = document.getElementById('result_' + c);
			return el ? el.textContent.trim() : null;
		}, crc);
	} catch (e) {
		errors.push('interact-error: ' + String(e).slice(0, 200));
	}

	page.off('console', handler);
	return { resultText, errors };
}

// ===========================================================================
// Helper: classify a result string against the engine contract
// Returns 'CORRECT', 'SCORE_FULL', 'PARTIAL', 'INCORRECT', 'ERROR', or 'EMPTY'
// ===========================================================================
function classifyResult(text) {
	if (!text || text.trim() === '' || text.trim() === ' ') return 'EMPTY';
	const t = text.trim();
	if (t === 'CORRECT') return 'CORRECT';
	// Total Score: X out of Y with X == Y
	const totalMatch = t.match(/Total Score:\s*(\d+)\s*out of\s*(\d+)/i);
	if (totalMatch && totalMatch[1] === totalMatch[2]) return 'SCORE_FULL';
	// Correct positions: X of Y with X == Y
	const posMatch = t.match(/Correct positions:\s*(\d+)\s*of\s*(\d+)/i);
	if (posMatch && posMatch[1] === posMatch[2]) return 'CORRECT';
	// Correct: X of Y with X == Y
	const cntMatch = t.match(/Correct:\s*(\d+)\s*of\s*(\d+)/i);
	if (cntMatch && cntMatch[1] === cntMatch[2]) return 'CORRECT';
	// Partial score
	if (totalMatch) return 'PARTIAL';
	return 'INCORRECT';
}

// ===========================================================================
// Passive visual survey for one target (topic page or standalone)
// ===========================================================================
async function passiveSurvey(browser, target, theme, viewport) {
	const vpName = viewport.width <= 400 ? 'mobile' : 'desktop';
	const slug = `${target.slug}_${theme}_${vpName}`;

	const ctxOpts = { viewport };
	if (theme === 'dark') ctxOpts.colorScheme = 'dark';
	const ctx = await browser.newContext(ctxOpts);

	if (theme === 'dark') {
		await ctx.addInitScript(darkInitScript());
	}

	const page = await ctx.newPage();
	const consoleErrors = [];
	page.on('console', msg => {
		if (msg.type() === 'error') consoleErrors.push(msg.text());
	});

	let status = 0;
	let qtypes = [];
	let detailsCount = 0;
	let detailsExpanded = 0;
	let shotBefore = null;
	let shotAfterExpand = null;
	let err = null;

	try {
		const resp = await page.goto(BASE + target.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
		status = resp ? resp.status() : 0;
		await page.waitForTimeout(800);

		// Screenshot before expanding any details
		shotBefore = path.join(OUT, `${slug}_before.png`);
		await page.screenshot({ path: shotBefore, fullPage: true });

		// Expand all <details> panels to show selftest fragments
		detailsCount = await page.evaluate(() => document.querySelectorAll('article details').length);
		detailsExpanded = await page.evaluate(() => {
			const panels = Array.from(document.querySelectorAll('article details'));
			panels.forEach(d => { d.open = true; });
			return panels.length;
		});
		// Wait for RDKit canvas renders etc
		await page.waitForTimeout(1500);

		// Screenshot after expanding
		shotAfterExpand = path.join(OUT, `${slug}_expanded.png`);
		await page.screenshot({ path: shotAfterExpand, fullPage: true });

		// Detect question types present
		qtypes = await detectQuestions(page);
	} catch (e) {
		err = String(e).slice(0, 200);
	}

	await ctx.close();

	return {
		mode: 'passive',
		slug,
		target: target.slug,
		qtype: target.qtype,
		theme,
		viewport: vpName,
		url: target.url,
		status,
		detailsCount,
		detailsExpanded,
		questionsDetected: qtypes,
		consoleErrors,
		screenshots: [shotBefore, shotAfterExpand].filter(Boolean),
		err,
	};
}

// ===========================================================================
// Interactive functional survey for one target
// Runs in desktop/light only (consistent baseline for functional checks)
// ===========================================================================
async function interactiveSurvey(browser, target) {
	const slug = `${target.slug}_interactive`;

	const ctx = await browser.newContext({ viewport: DESKTOP_VP });
	const page = await ctx.newPage();
	const consoleErrors = [];
	page.on('console', msg => {
		if (msg.type() === 'error') consoleErrors.push(msg.text());
	});
	// Also catch page-level errors (uncaught exceptions)
	const pageErrors = [];
	page.on('pageerror', e => pageErrors.push(String(e)));

	let status = 0;
	let results = [];
	let shotBefore = null;
	let shotAfter = null;
	let err = null;

	try {
		const resp = await page.goto(BASE + target.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
		status = resp ? resp.status() : 0;
		await page.waitForTimeout(800);

		// Expand all <details> panels
		await page.evaluate(() => {
			document.querySelectorAll('article details').forEach(d => { d.open = true; });
		});
		await page.waitForTimeout(1000);

		shotBefore = path.join(OUT, `${slug}_before.png`);
		await page.screenshot({ path: shotBefore, fullPage: true });

		// Detect all question blocks
		const questions = await detectQuestions(page);

		// Interact with each detected question
		for (const q of questions) {
			const { resultText, errors } = await interactCorrect(page, q.crc, q.qtype);
			const classification = classifyResult(resultText);
			results.push({
				crc: q.crc,
				qtype: q.qtype,
				hasCanvas: q.hasCanvas,
				resultText,
				classification,
				interactionErrors: errors,
			});
		}

		await page.waitForTimeout(500);
		shotAfter = path.join(OUT, `${slug}_after.png`);
		await page.screenshot({ path: shotAfter, fullPage: true });
	} catch (e) {
		err = String(e).slice(0, 200);
	}

	await ctx.close();

	// FIB bug: fibAnswers_{crc16_text} is not defined - shows as ReferenceError in pageerror.
	// Check console errors, page errors, and also any FIB question that had pageErrors
	// (a FIB interaction on a page with pageErrors strongly implies the template bug).
	const fibErrors = consoleErrors.filter(e => e.includes('ReferenceError') || e.includes('{crc16_text}') || e.includes('fibAnswers_'));
	const pageErrsFib = pageErrors.filter(e => e.includes('ReferenceError') || e.includes('{crc16_text}') || e.includes('fibAnswers_'));
	const hasFibQuestions = results.some(q => q.qtype === 'FIB');
	// If page has FIB questions and has page-level errors, the errors are likely the FIB template bug
	const fibReferenceErrorCaptured = fibErrors.length > 0 || pageErrsFib.length > 0
		|| (hasFibQuestions && pageErrors.length > 0);

	return {
		mode: 'interactive',
		slug,
		target: target.slug,
		qtype: target.qtype,
		url: target.url,
		status,
		questionsInteracted: results,
		consoleErrors,
		pageErrors,
		fibReferenceErrorCaptured,
		screenshots: [shotBefore, shotAfter].filter(Boolean),
		err,
	};
}

// ===========================================================================
// Main: run all surveys
// ===========================================================================
const browser = await chromium.launch();
const report = [];

console.log('=== Passive visual survey ===');
// All topic pages: desktop+mobile x light+dark
for (const target of TOPIC_PAGES) {
	// Desktop light
	const r1 = await passiveSurvey(browser, target, 'light', DESKTOP_VP);
	report.push(r1);
	console.log(`[passive][desktop][light] ${r1.status} ${r1.url}  qtypes=${r1.questionsDetected.length} errors=${r1.consoleErrors.length} expanded=${r1.detailsExpanded}`);

	// Desktop dark
	const r2 = await passiveSurvey(browser, target, 'dark', DESKTOP_VP);
	report.push(r2);
	console.log(`[passive][desktop][dark]  ${r2.status} ${r2.url}  qtypes=${r2.questionsDetected.length} errors=${r2.consoleErrors.length}`);

	// Mobile light
	const r3 = await passiveSurvey(browser, target, 'light', MOBILE_VP);
	report.push(r3);
	console.log(`[passive][mobile][light]  ${r3.status} ${r3.url}  qtypes=${r3.questionsDetected.length} errors=${r3.consoleErrors.length}`);

	// Mobile dark
	const r4 = await passiveSurvey(browser, target, 'dark', MOBILE_VP);
	report.push(r4);
	console.log(`[passive][mobile][dark]   ${r4.status} ${r4.url}  qtypes=${r4.questionsDetected.length} errors=${r4.consoleErrors.length}`);
}

// Standalone files: desktop+mobile x light (dark is same content, lower priority)
console.log('\n=== Standalone file passive survey ===');
for (const target of STANDALONE_FILES) {
	const r1 = await passiveSurvey(browser, target, 'light', DESKTOP_VP);
	report.push(r1);
	console.log(`[passive][standalone][desktop][light] ${r1.status} ${r1.url}  errors=${r1.consoleErrors.length}`);

	const r2 = await passiveSurvey(browser, target, 'light', MOBILE_VP);
	report.push(r2);
	console.log(`[passive][standalone][mobile][light]  ${r2.status} ${r2.url}  errors=${r2.consoleErrors.length}`);
}

// ===========================================================================
// Interactive surveys: all topic pages + all standalone files, desktop only
// ===========================================================================
console.log('\n=== Interactive functional survey ===');
const INTERACTIVE_TARGETS = [...TOPIC_PAGES, ...STANDALONE_FILES];
for (const target of INTERACTIVE_TARGETS) {
	const r = await interactiveSurvey(browser, target);
	report.push(r);
	const summary = r.questionsInteracted.map(q =>
		`${q.qtype}:${q.classification}${q.interactionErrors.length ? '(ERR)' : ''}`
	).join(', ');
	console.log(`[interactive] ${r.status} ${r.url}  questions=[${summary}] fibErr=${r.fibReferenceErrorCaptured} pageErrors=${r.pageErrors.length}`);
}

await browser.close();

// ===========================================================================
// Write JSON report
// ===========================================================================
const reportPath = path.join(OUT, 'report.json');
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

// Count screenshots
const allShots = report.flatMap(r => r.screenshots || []).filter(Boolean);
const uniqueShots = [...new Set(allShots)];

// Summarize FIB ReferenceErrors
const fibCaptured = report.filter(r => r.fibReferenceErrorCaptured);

console.log('\n=== Summary ===');
console.log(`Total survey records: ${report.length}`);
console.log(`Total screenshots:    ${uniqueShots.length}`);
console.log(`Report path:          ${reportPath}`);
console.log(`FIB ReferenceError captured in ${fibCaptured.length} interactive runs:`);
fibCaptured.forEach(r => console.log(`  - ${r.slug}: ${r.url}`));

// Per-type coverage table
const typeMap = {};
report.filter(r => r.mode === 'interactive').forEach(r => {
	(r.questionsInteracted || []).forEach(q => {
		if (!typeMap[q.qtype]) typeMap[q.qtype] = [];
		typeMap[q.qtype].push({ slug: r.slug, crc: q.crc, result: q.classification });
	});
});
console.log('\n=== Question type coverage (interactive mode) ===');
for (const [qtype, entries] of Object.entries(typeMap)) {
	const results = entries.map(e => e.result);
	const correct = results.filter(r => r === 'CORRECT' || r === 'SCORE_FULL').length;
	console.log(`  ${qtype}: ${entries.length} interactions, ${correct} correct/full`);
}

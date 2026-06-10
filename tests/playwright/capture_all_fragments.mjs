// capture_all_fragments.mjs
//
// Full-coverage Playwright harness: screenshots every standalone selftest
// fragment in site_docs/ for downstream visual review.
//
// For each fragment: 5 screenshots are captured (light + dark):
//   1. desktop 1280 light  - passive (details expanded)
//   2. desktop 1280 light  - after interaction (correct answer + Check)
//   3. mobile 390  light   - passive (details expanded)
//   4. desktop 1280 dark   - passive (Material slate dark via __palette seed)
//   5. desktop 1280 dark   - after interaction (correct answer + Check)
//   For fragments with canvas/structure: also mobile 390 dark passive.
//
// Also collects per-fragment: console errors, page errors, load status,
// and a highBytes flag (any byte > 0x7F in served HTML = possible mojibake).
//
// Dark theme: seeded via __palette localStorage key (Material slate) and
// colorScheme:'dark' browser context option, matching the pattern in
// tests/playwright/selftest_visual_survey.mjs.
//
// Output:
//   test-results/selftest_survey/full/   - all PNG screenshots
//   test-results/selftest_survey/full/index.json  - full index
//
// Run from repo root:
//   node tests/playwright/capture_all_fragments.mjs
//
// Optional env var LIMIT=N caps the number of fragments processed (smoke test):
//   LIMIT=3 node tests/playwright/capture_all_fragments.mjs
//
// Concurrency: 5 pages in parallel (CONCURRENCY constant below).

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const BASE = 'http://127.0.0.1:8000';
// OUT_OVERRIDE env var allows redirecting output for smoke runs:
//   OUT_OVERRIDE=test-results/selftest_survey/_darksmoke LIMIT=3 node ...
const OUT = process.env.OUT_OVERRIDE || 'test-results/selftest_survey/full';
fs.mkdirSync(OUT, { recursive: true });

const DESKTOP_VP = { width: 1280, height: 900 };
const MOBILE_VP  = { width: 390,  height: 844 };
const CONCURRENCY = 5;
const PAGE_TIMEOUT = 30000;

// Optional fragment limit for smoke runs: LIMIT=3 node capture_all_fragments.mjs
// Set to 0 or omit for full run.
const FRAGMENT_LIMIT = parseInt(process.env.LIMIT || '0', 10);

// ===========================================================================
// Dark theme seed: Material slate via __palette localStorage key.
// Matches the pattern used in selftest_visual_survey.mjs.
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
// Step 1: enumerate all selftest fragment paths from git
// ===========================================================================
function enumerateFragments() {
	const raw = execSync("git ls-files 'site_docs/**/selftest-*.html'", { encoding: 'utf8' });
	const lines = raw.trim().split('\n').filter(Boolean);
	// Transform site_docs/... -> /...  (served URL path)
	return lines.map(filePath => {
		const url = filePath.replace(/^site_docs/, '');
		return { filePath, url };
	});
}

// ===========================================================================
// Helper: detect all question blocks on the current page
// Returns array of { crc, qtype, hasCanvas }
// ===========================================================================
async function detectQuestions(page) {
	return await page.evaluate(() => {
		const containers = Array.from(document.querySelectorAll('[id^="question_html_"]'));
		return containers.map(el => {
			const crc = el.id.replace('question_html_', '');
			const hasDraggable = Boolean(el.querySelector('.draggable'));
			const hasCheckbox = Boolean(el.querySelector('input[type="checkbox"]'));
			const hasRadio = Boolean(el.querySelector('input[type="radio"]'));
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
// Helper: interact correctly with a single question block
// Returns { resultText }
// (Same interaction logic as selftest_visual_survey.mjs)
// ===========================================================================
async function interactCorrect(page, crc, qtype) {
	try {
		if (qtype === 'MC' || qtype === 'TFMS' || qtype === 'EQUATION' || qtype === 'WOMC') {
			await page.evaluate((c) => {
				const container = document.getElementById('question_html_' + c);
				if (!container) return;
				const correct = container.querySelector('input[type="radio"][data-correct="true"]');
				if (correct) correct.checked = true;
				const fn = window['checkAnswer_' + c];
				if (fn) fn();
			}, crc);
		} else if (qtype === 'NUM') {
			await page.evaluate((c) => {
				const scripts = Array.from(document.querySelectorAll('script'));
				let numAnswer = null;
				const pattern = new RegExp('const\\s+numAnswer_' + c + '\\s*=\\s*([\\d.e+-]+)');
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
					inputEl.value = '0';
				}
				const fn = window['checkAnswer_' + c];
				if (fn) fn();
			}, crc);
		} else if (qtype === 'MA') {
			await page.evaluate((c) => {
				const container = document.getElementById('question_html_' + c);
				if (!container) return;
				const corrects = container.querySelectorAll('input[type="checkbox"][data-correct="true"]');
				corrects.forEach(cb => { cb.checked = true; });
				const fn = window['checkAnswer_' + c];
				if (fn) fn();
			}, crc);
		} else if (qtype === 'MATCH') {
			await page.evaluate((c) => {
				const container = document.getElementById('question_html_' + c);
				if (!container) return;
				const dropzones = container.querySelectorAll('.dropzone');
				dropzones.forEach(zone => {
					const correctVal = zone.dataset.correct;
					zone.dataset.value = correctVal;
					const draggable = container.querySelector('.draggable[data-value="' + correctVal + '"]');
					const displayText = draggable ? draggable.innerText.trim() : correctVal;
					zone.textContent = displayText;
					zone.style.border = '2px solid var(--qti-dropzone-border-filled, #888888)';
				});
				const fn = window['checkAnswer_' + c];
				if (fn) fn();
			}, crc);
		} else if (qtype === 'FIB') {
			await page.evaluate((c) => {
				const inputEl = document.getElementById('fib_input_' + c);
				if (inputEl) inputEl.value = 'test';
				const fn = window['checkAnswer_' + c];
				if (fn) fn();
			}, crc);
		}
	} catch (e) {
		// interaction errors are captured at caller level
	}
}

// ===========================================================================
// Helper: check raw HTML bytes for any value > 0x7F (highBytes = mojibake risk)
// ===========================================================================
async function checkHighBytes(url) {
	try {
		const resp = await fetch(BASE + url);
		const buf = await resp.arrayBuffer();
		const bytes = new Uint8Array(buf);
		let count = 0;
		for (const b of bytes) {
			if (b > 0x7F) count++;
		}
		return count;
	} catch (e) {
		return -1;
	}
}

// ===========================================================================
// Core: capture one fragment (up to 6 screenshots: light + dark, + metadata)
//
// Light captures (existing, unchanged):
//   __desktop_passive.png        desktop 1280 light passive
//   __desktop_after.png          desktop 1280 light after interaction
//   __mobile_passive.png         mobile  390  light passive
//
// Dark captures (new):
//   __desktop_dark_passive.png   desktop 1280 dark passive
//   __desktop_dark_after.png     desktop 1280 dark after interaction
//   __mobile_dark_passive.png    mobile  390  dark passive (canvas/structure only)
// ===========================================================================
async function captureFragment(browser, fragment) {
	const { filePath, url } = fragment;
	// Sanitize the file path to create a safe filename prefix
	const safeName = filePath.replace(/^site_docs\//, '').replace(/[\/\\]/g, '__').replace(/\.html$/, '');

	const result = {
		filePath,
		url,
		safeName,
		// light and dark screenshot lists, grouped by theme
		screenshots: [],
		screenshotsLight: [],
		screenshotsDark: [],
		consoleErrors: [],
		pageErrors: [],
		loadOk: false,
		httpStatus: 0,
		highBytes: 0,
		qtypes: [],
		hasCanvas: false,
		interactionResultText: null,
	};

	// Check highBytes from raw HTML
	result.highBytes = await checkHighBytes(url);

	// -------------------------------------------------------------------------
	// LIGHT THEME captures
	// -------------------------------------------------------------------------

	// --- Desktop light passive + after ---
	const desktopCtx = await browser.newContext({ viewport: DESKTOP_VP });
	const desktopPage = await desktopCtx.newPage();
	desktopPage.on('console', msg => {
		if (msg.type() === 'error') result.consoleErrors.push(msg.text());
	});
	desktopPage.on('pageerror', e => result.pageErrors.push(String(e)));

	try {
		const resp = await desktopPage.goto(BASE + url, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
		result.httpStatus = resp ? resp.status() : 0;
		result.loadOk = result.httpStatus >= 200 && result.httpStatus < 400;
		await desktopPage.waitForTimeout(800);

		// Expand all <details> panels
		await desktopPage.evaluate(() => {
			document.querySelectorAll('details').forEach(d => { d.open = true; });
		});
		await desktopPage.waitForTimeout(1000);

		const passiveShot = path.join(OUT, `${safeName}__desktop_passive.png`);
		await desktopPage.screenshot({ path: passiveShot, fullPage: true });
		result.screenshots.push(passiveShot);
		result.screenshotsLight.push(passiveShot);

		// Detect question types (run once per fragment on the light page)
		const questions = await detectQuestions(desktopPage);
		result.qtypes = questions.map(q => q.qtype);
		// hasCanvas: any question block contains a <canvas> element
		result.hasCanvas = questions.some(q => q.hasCanvas);

		// --- Desktop light after interaction ---
		for (const q of questions) {
			await interactCorrect(desktopPage, q.crc, q.qtype);
		}
		await desktopPage.waitForTimeout(500);
		// Read result text from first question
		if (questions.length > 0) {
			result.interactionResultText = await desktopPage.evaluate((crc) => {
				const el = document.getElementById('result_' + crc);
				return el ? el.textContent.trim() : null;
			}, questions[0].crc);
		}

		const afterShot = path.join(OUT, `${safeName}__desktop_after.png`);
		await desktopPage.screenshot({ path: afterShot, fullPage: true });
		result.screenshots.push(afterShot);
		result.screenshotsLight.push(afterShot);
	} catch (e) {
		result.loadError = String(e).slice(0, 300);
	} finally {
		await desktopCtx.close();
	}

	// --- Mobile light passive ---
	const mobileCtx = await browser.newContext({ viewport: MOBILE_VP });
	const mobilePage = await mobileCtx.newPage();

	try {
		const resp = await mobilePage.goto(BASE + url, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
		if (!result.loadOk && resp) {
			result.httpStatus = resp.status();
			result.loadOk = result.httpStatus >= 200 && result.httpStatus < 400;
		}
		await mobilePage.waitForTimeout(600);
		await mobilePage.evaluate(() => {
			document.querySelectorAll('details').forEach(d => { d.open = true; });
		});
		await mobilePage.waitForTimeout(800);
		const mobileShot = path.join(OUT, `${safeName}__mobile_passive.png`);
		await mobilePage.screenshot({ path: mobileShot, fullPage: true });
		result.screenshots.push(mobileShot);
		result.screenshotsLight.push(mobileShot);
	} catch (e) {
		// mobile screenshot failure is non-fatal
	} finally {
		await mobileCtx.close();
	}

	// -------------------------------------------------------------------------
	// DARK THEME captures
	// Uses Material slate theme via __palette localStorage seed +
	// colorScheme:'dark' context option, same pattern as selftest_visual_survey.mjs
	// -------------------------------------------------------------------------

	// --- Desktop dark passive + after ---
	const darkDesktopCtx = await browser.newContext({
		viewport: DESKTOP_VP,
		colorScheme: 'dark',
	});
	// Seed the Material slate dark palette before the page loads
	await darkDesktopCtx.addInitScript(darkInitScript());
	const darkDesktopPage = await darkDesktopCtx.newPage();
	darkDesktopPage.on('console', msg => {
		if (msg.type() === 'error') result.consoleErrors.push('[dark] ' + msg.text());
	});
	darkDesktopPage.on('pageerror', e => result.pageErrors.push('[dark] ' + String(e)));

	try {
		const resp = await darkDesktopPage.goto(BASE + url, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
		// Update loadOk/httpStatus only if not already set from light context
		if (!result.loadOk && resp) {
			result.httpStatus = resp.status();
			result.loadOk = result.httpStatus >= 200 && result.httpStatus < 400;
		}
		await darkDesktopPage.waitForTimeout(800);

		// Expand all <details> panels
		await darkDesktopPage.evaluate(() => {
			document.querySelectorAll('details').forEach(d => { d.open = true; });
		});
		await darkDesktopPage.waitForTimeout(1000);

		const darkPassiveShot = path.join(OUT, `${safeName}__desktop_dark_passive.png`);
		await darkDesktopPage.screenshot({ path: darkPassiveShot, fullPage: true });
		result.screenshots.push(darkPassiveShot);
		result.screenshotsDark.push(darkPassiveShot);

		// Re-detect questions in the dark context for interaction
		const darkQuestions = await detectQuestions(darkDesktopPage);

		// --- Desktop dark after interaction ---
		for (const q of darkQuestions) {
			await interactCorrect(darkDesktopPage, q.crc, q.qtype);
		}
		await darkDesktopPage.waitForTimeout(500);

		const darkAfterShot = path.join(OUT, `${safeName}__desktop_dark_after.png`);
		await darkDesktopPage.screenshot({ path: darkAfterShot, fullPage: true });
		result.screenshots.push(darkAfterShot);
		result.screenshotsDark.push(darkAfterShot);
	} catch (e) {
		result.darkLoadError = String(e).slice(0, 300);
	} finally {
		await darkDesktopCtx.close();
	}

	// --- Mobile dark passive (only for fragments with canvas/structure) ---
	if (result.hasCanvas) {
		const darkMobileCtx = await browser.newContext({
			viewport: MOBILE_VP,
			colorScheme: 'dark',
		});
		await darkMobileCtx.addInitScript(darkInitScript());
		const darkMobilePage = await darkMobileCtx.newPage();

		try {
			await darkMobilePage.goto(BASE + url, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
			await darkMobilePage.waitForTimeout(600);
			await darkMobilePage.evaluate(() => {
				document.querySelectorAll('details').forEach(d => { d.open = true; });
			});
			await darkMobilePage.waitForTimeout(800);
			const darkMobileShot = path.join(OUT, `${safeName}__mobile_dark_passive.png`);
			await darkMobilePage.screenshot({ path: darkMobileShot, fullPage: true });
			result.screenshots.push(darkMobileShot);
			result.screenshotsDark.push(darkMobileShot);
		} catch (e) {
			// mobile dark screenshot failure is non-fatal
		} finally {
			await darkMobileCtx.close();
		}
	}

	return result;
}

// ===========================================================================
// Main: enumerate, run with concurrency, write index.json
// ===========================================================================
const allFragments = enumerateFragments();
// Apply optional LIMIT env var for smoke runs (LIMIT=3 caps to first 3 fragments)
const fragments = FRAGMENT_LIMIT > 0 ? allFragments.slice(0, FRAGMENT_LIMIT) : allFragments;
if (FRAGMENT_LIMIT > 0) {
	console.log(`Enumerated ${allFragments.length} selftest fragments; capped to ${fragments.length} (LIMIT=${FRAGMENT_LIMIT})`);
} else {
	console.log(`Enumerated ${fragments.length} selftest fragments`);
}

const browser = await chromium.launch();
const index = [];
let done = 0;
let failures = 0;

// Process in batches of CONCURRENCY
for (let i = 0; i < fragments.length; i += CONCURRENCY) {
	const batch = fragments.slice(i, i + CONCURRENCY);
	const results = await Promise.all(batch.map(f => captureFragment(browser, f)));
	for (const r of results) {
		index.push(r);
		done++;
		if (!r.loadOk) failures++;
		const pct = ((done / fragments.length) * 100).toFixed(0);
		const errFlag = (r.consoleErrors.length + r.pageErrors.length) > 0 ? ' ERRORS' : '';
		const hbFlag = r.highBytes > 0 ? ` HIGHBYTES=${r.highBytes}` : '';
		const failFlag = !r.loadOk ? ` FAIL(${r.httpStatus})` : '';
		console.log(`[${done}/${fragments.length} ${pct}%]${failFlag}${errFlag}${hbFlag} ${r.url}`);
	}
}

await browser.close();

// Write index.json
const indexPath = path.join(OUT, 'index.json');
const totalScreenshots = index.reduce((acc, r) => acc + r.screenshots.length, 0);
const totalLightScreenshots = index.reduce((acc, r) => acc + (r.screenshotsLight || []).length, 0);
const totalDarkScreenshots = index.reduce((acc, r) => acc + (r.screenshotsDark || []).length, 0);
fs.writeFileSync(indexPath, JSON.stringify({
	generatedAt: new Date().toISOString(),
	totalFragments: fragments.length,
	totalCaptured: index.filter(r => r.loadOk).length,
	totalFailures: index.filter(r => !r.loadOk).length,
	totalScreenshots,
	totalLightScreenshots,
	totalDarkScreenshots,
	fragments: index,
}, null, 2));

// === Summary report ===
const loadFailures = index.filter(r => !r.loadOk);
const withErrors = index.filter(r => r.consoleErrors.length > 0 || r.pageErrors.length > 0);
const withHighBytes = index.filter(r => r.highBytes > 0);

console.log('\n=== SUMMARY ===');
console.log(`Enumerated:          ${fragments.length}`);
console.log(`Captured OK:         ${index.filter(r => r.loadOk).length}`);
console.log(`Load failures:       ${loadFailures.length}`);
console.log(`With JS errors:      ${withErrors.length}`);
console.log(`With highBytes:      ${withHighBytes.length}`);
console.log(`Total screenshots:   ${totalScreenshots}`);
console.log(`  Light screenshots: ${totalLightScreenshots}`);
console.log(`  Dark screenshots:  ${totalDarkScreenshots}`);
console.log(`Index: ${indexPath}`);

if (loadFailures.length > 0) {
	console.log('\nLoad failures:');
	loadFailures.forEach(r => console.log(`  HTTP ${r.httpStatus}: ${r.url}`));
}
if (withHighBytes.length > 0) {
	console.log('\nFragments with bytes > 0x7F:');
	withHighBytes.forEach(r => console.log(`  ${r.highBytes} bytes: ${r.url}`));
}

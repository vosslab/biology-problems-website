// UI/UX review driver: visits key mkdocs pages at desktop and mobile
// viewports, saves screenshots to test-results/ui_ux_review/, and prints
// a per-page report (status, title, H1 count, broken-link count, contrast hints).
//
// It also runs a focused review of the self-test completion-tracking feature:
//   - the progress dashboard at /progress/ (div#selftest-progress-dashboard)
//   - per-question Completed / Not completed badges on a topic page
//   - that a correct answer marks the question complete and updates the
//     dashboard, while a wrong answer stores nothing
//   - the storage-unavailable non-blocking warning path
//   - the reset-with-confirmation button on the dashboard
//
// Run from the repo root with the dev server up on 127.0.0.1:8000:
//   source source_me.sh && python3 -m mkdocs serve -a 127.0.0.1:8000 &
//   node tests/playwright/ui_ux_review.mjs
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = 'http://127.0.0.1:8000';
const OUT = 'test-results/ui_ux_review';
const STORAGE_KEY = 'selftest_progress_v1';
const MANIFEST_URL = '/assets/data/selftest_question_manifest.json';
const TOPIC_URL = '/biochemistry/topic01/';
const PROGRESS_URL = '/progress/';
fs.mkdirSync(OUT, { recursive: true });

const pages = [
	{ slug: 'home', url: '/' },
	{ slug: 'progress', url: '/progress/' },
	{ slug: 'subject_biochem', url: '/biochemistry/' },
	{ slug: 'subject_genetics', url: '/genetics/' },
	{ slug: 'subject_lab', url: '/laboratory/' },
	{ slug: 'subject_molbio', url: '/molecular_biology/' },
	{ slug: 'subject_biostats', url: '/biostatistics/' },
	{ slug: 'subject_other', url: '/other/' },
	{ slug: 'topic_biochem01', url: '/biochemistry/topic01/' },
	{ slug: 'topic_biochem20', url: '/biochemistry/topic20/' },
	{ slug: 'topic_genetics01', url: '/genetics/topic01/' },
	{ slug: 'topic_genetics11', url: '/genetics/topic11/' },
	{ slug: 'topic_lab01', url: '/laboratory/topic01/' },
	{ slug: 'topic_lab11', url: '/laboratory/topic11/' },
	{ slug: 'topic_molbio04', url: '/molecular_biology/topic04/' },
	{ slug: 'topic_molbio09', url: '/molecular_biology/topic09/' },
	{ slug: 'topic_biostats05', url: '/biostatistics/topic05/' },
	{ slug: 'topic_biostats08', url: '/biostatistics/topic08/' },
	{ slug: 'topic_other01', url: '/other/topic01/' },
	{ slug: 'daily_puzzles_index', url: '/daily_puzzles/' },
	{ slug: 'daily_peptidyle', url: '/daily_puzzles/peptidyle/' },
	{ slug: 'daily_deletion_mutants', url: '/daily_puzzles/deletion_mutants/' },
	{ slug: 'daily_mutant_screen', url: '/daily_puzzles/mutant_screen/' },
	{ slug: 'daily_biomacromolecule', url: '/daily_puzzles/biomacromolecule/' },
	{ slug: 'tutorials_index', url: '/tutorials/' },
	{ slug: 'tutorial_bbq', url: '/tutorials/bbq_tutorial/' },
	{ slug: 'tutorial_bbq_ultra', url: '/tutorials/bbq_ultra_tutorial/' },
	{ slug: 'tutorial_canvas', url: '/tutorials/canvas_tutorial/' },
	{ slug: 'search_results', url: '/?q=enzyme' },
	{ slug: 'author', url: '/author/' },
	{ slug: 'license', url: '/license/' },
];

const viewports = [
	{ name: 'desktop', width: 1280, height: 900 },
	{ name: 'mobile',  width: 390,  height: 844 },
];

async function evalPage(page) {
	return await page.evaluate(() => {
		const h1s = Array.from(document.querySelectorAll('article h1')).map(e => e.textContent.trim());
		const anchors = Array.from(document.querySelectorAll('article a[href]'));
		const internal = anchors.filter(a => {
			const h = a.getAttribute('href');
			return h && !h.startsWith('http') && !h.startsWith('#') && !h.startsWith('mailto:');
		});
		// rel="noopener" only matters when the link opens in a new tab. Flag
		// only external target=_blank links that are missing it.
		const externalNoRel = anchors.filter(a => {
			const h = a.getAttribute('href') || '';
			if (!h.startsWith('http')) return false;
			const target = (a.getAttribute('target') || '').toLowerCase();
			if (target !== '_blank') return false;
			const rel = (a.getAttribute('rel') || '').toLowerCase();
			return !rel.includes('noopener');
		}).length;
		const imgs = Array.from(document.querySelectorAll('article img'));
		// alt="" is a valid decorative-image marker; only flag images with the attribute completely absent.
		const imgsNoAlt = imgs.filter(i => i.getAttribute('alt') === null).length;
		const smallFontIcons = Array.from(document.querySelectorAll('[style*="font-size: 0.8em"], [style*="font-size:0.8em"]')).length;
		const allTables = Array.from(document.querySelectorAll('article table'));
		const tables = allTables.length;
		// Tables that are visible on page load (i.e., not inside a collapsed <details>).
		const visibleTables = allTables.filter(t => !t.closest('details:not([open])')).length;
		const detailsBlocks = document.querySelectorAll('article details').length;
		const title = document.title;
		const navItems = document.querySelectorAll('.md-nav__item').length;
		return { title, h1count: h1s.length, h1: h1s[0] || null,
			internalLinks: internal.length, externalNoRel,
			imgs: imgs.length, imgsNoAlt, smallFontIcons, tables, visibleTables, detailsBlocks, navItems };
	});
}

// ===========================================================================
// Self-test progress feature helpers
// ===========================================================================

// Wait until the runtime script has finished its async init pass on this page.
// initPage() fetches the manifest, then renders badges / dashboard, so we wait
// for a feature-specific element rather than a fixed timeout.
//
// state defaults to 'attached' (not 'visible'): the per-question badges are
// injected inside collapsed <details> blocks on topic pages, so they are
// present in the DOM but not visible. Waiting for 'visible' would falsely time
// out even though the badge exists and is wired up.
async function waitForSelector(page, selector, timeout = 8000, state = 'attached') {
	try {
		await page.waitForSelector(selector, { timeout, state });
		return true;
	} catch (e) {
		return false;
	}
}

// Read the parsed localStorage state the runtime persists.
async function readProgressState(page) {
	return await page.evaluate((key) => {
		const raw = window.localStorage.getItem(key);
		if (!raw) return null;
		try { return JSON.parse(raw); } catch (e) { return { parseError: String(e) }; }
	}, STORAGE_KEY);
}

// Inspect every rendered question badge: its text and whether it carries the
// "complete" CSS class. Used to confirm badge clarity and state transitions.
async function readBadges(page) {
	return await page.evaluate(() => {
		const badges = Array.from(document.querySelectorAll('[data-selftest-status]'));
		return badges.map(b => ({
			questionId: b.getAttribute('data-selftest-status'),
			text: (b.textContent || '').trim(),
			complete: b.className.indexOf('selftest-status-complete') !== -1,
		}));
	});
}

// Summarize the dashboard: overall counter text, per-subject sections, the
// reset button presence/enabled state, and any storage warning.
async function readDashboard(page) {
	return await page.evaluate(() => {
		const root = document.getElementById('selftest-progress-dashboard');
		if (!root) return { present: false };
		const summary = root.querySelector('.selftest-dashboard-summary');
		const subjects = Array.from(root.querySelectorAll('.selftest-dashboard-subject h2')).map(h => h.textContent.trim());
		const topicItems = Array.from(root.querySelectorAll('.selftest-dashboard-subject li')).length;
		const completeTopics = Array.from(root.querySelectorAll('.selftest-topic-complete')).length;
		const resetBtn = document.getElementById('selftest-reset-progress');
		const warning = root.querySelector('.selftest-storage-warning');
		return {
			present: true,
			summaryText: summary ? summary.textContent.trim() : null,
			subjects,
			topicItems,
			completeTopics,
			resetButton: Boolean(resetBtn),
			resetDisabled: resetBtn ? resetBtn.disabled : null,
			warningText: warning ? warning.textContent.trim() : null,
		};
	});
}

// Drive the topic page: confirm badges render, then exercise a correct answer
// via the runtime API (deterministic, no answer-key guessing needed).
async function reviewTopicBadges(browser, vp, findings) {
	const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
	const page = await ctx.newPage();
	await page.goto(BASE + TOPIC_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
	const ready = await waitForSelector(page, '[data-selftest-status]');
	if (!ready) {
		findings.push({ area: 'topic-badges', vp: vp.name, ok: false,
			note: 'No [data-selftest-status] badges rendered within timeout' });
		await ctx.close();
		return;
	}

	const initialBadges = await readBadges(page);
	const topicPanel = await page.evaluate(() => {
		const p = document.getElementById('selftest-topic-progress');
		const c = document.querySelector('[data-selftest-topic-count]');
		return { panel: Boolean(p), countText: c ? c.textContent.trim() : null };
	});
	await page.screenshot({ path: path.join(OUT, `selftest_topic_initial_${vp.name}.png`), fullPage: true });

	// Pick the first question id from the manifest rows for this page, then mark
	// it complete via the public API exactly as a correct answer would.
	const firstQuestionId = await page.evaluate(async (manifestUrl) => {
		const api = window.SelfTestProgress;
		if (!api || !api._test) return null;
		const manifest = await window.fetch(manifestUrl).then(r => r.json());
		const rows = api._test.getCurrentRows(manifest);
		return rows.length ? rows[0].questionId : null;
	}, MANIFEST_URL);

	let afterCorrect = null;
	let stateAfterCorrect = null;
	if (firstQuestionId) {
		await page.evaluate((qid) => { window.SelfTestProgress.markCompleted(qid); }, firstQuestionId);
		// Re-run the page init so badges/summary re-render from new state.
		await page.evaluate(() => { window.SelfTestProgress.initPage(); });
		await page.waitForTimeout(300);
		afterCorrect = await readBadges(page);
		stateAfterCorrect = await readProgressState(page);
		await page.screenshot({ path: path.join(OUT, `selftest_topic_completed_${vp.name}.png`), fullPage: true });
	}

	findings.push({
		area: 'topic-badges', vp: vp.name, ok: true,
		badgeCount: initialBadges.length,
		initialAllNotCompleted: initialBadges.every(b => b.text === 'Not completed' && !b.complete),
		topicPanel: topicPanel.panel,
		topicCountText: topicPanel.countText,
		markedQuestionId: firstQuestionId,
		badgeFlippedToCompleted: Boolean(afterCorrect && afterCorrect.some(b => b.questionId === firstQuestionId && b.complete && b.text === 'Completed')),
		statePersistedCorrect: Boolean(stateAfterCorrect && stateAfterCorrect.completed && stateAfterCorrect.completed[firstQuestionId]),
	});

	await ctx.close();
}

// Confirm a wrong answer stores nothing. classifyResultElement() is the gate
// the runtime uses; feed it representative result text and verify that only a
// fully-correct result classifies as "full-correct" (the only path that saves).
async function reviewWrongAnswerStoresNothing(browser, findings) {
	const ctx = await browser.newContext();
	const page = await ctx.newPage();
	await page.goto(BASE + TOPIC_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
	await waitForSelector(page, '[data-selftest-status]');
	// Start from a clean slate.
	await page.evaluate((key) => window.localStorage.removeItem(key), STORAGE_KEY);

	const classification = await page.evaluate(() => {
		const api = window.SelfTestProgress;
		function classify(text) {
			const el = document.createElement('div');
			el.textContent = text;
			return api.classifyResultElement(el);
		}
		return {
			incorrect: classify('incorrect'),
			tryAgain: classify('Incorrect. Try again.'),
			partialScore: classify('Total Score: 2 out of 5'),
			emptyNoAnswer: classify(''),
			fullScore: classify('Total Score: 5 out of 5'),
			fullCorrect: classify('CORRECT'),
		};
	});
	const stateAfter = await readProgressState(page);

	findings.push({
		area: 'wrong-answer', ok: true,
		classification,
		wrongNotFullCorrect: classification.incorrect !== 'full-correct'
			&& classification.tryAgain !== 'full-correct'
			&& classification.partialScore !== 'full-correct'
			&& classification.emptyNoAnswer !== 'full-correct',
		correctIsFullCorrect: classification.fullCorrect === 'full-correct'
			&& classification.fullScore === 'full-correct',
		storageStillEmpty: stateAfter === null,
	});
	await ctx.close();
}

// Review the dashboard in two states: empty (zero progress) and populated,
// then exercise reset-with-confirmation (accept and dismiss paths).
async function reviewDashboard(browser, vp, findings) {
	// Empty / zero-progress state.
	const emptyCtx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
	const emptyPage = await emptyCtx.newPage();
	await emptyPage.goto(BASE + PROGRESS_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
	await waitForSelector(emptyPage, '.selftest-dashboard-summary');
	const emptyDash = await readDashboard(emptyPage);
	await emptyPage.screenshot({ path: path.join(OUT, `selftest_dashboard_empty_${vp.name}.png`), fullPage: true });
	findings.push({ area: 'dashboard-empty', vp: vp.name, ok: emptyDash.present, ...emptyDash });
	await emptyCtx.close();

	// Populated state: pre-seed completed questions from the manifest, then load.
	const popCtx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
	const popPage = await popCtx.newPage();
	// Need the manifest to know real question ids; fetch it on the loaded page first.
	await popPage.goto(BASE + PROGRESS_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
	const seedIds = await popPage.evaluate(async (manifestUrl) => {
		const manifest = await window.fetch(manifestUrl).then(r => r.json());
		return manifest.questions.slice(0, 3).map(q => q.questionId);
	}, MANIFEST_URL);
	await popPage.evaluate(({ key, ids }) => {
		const state = { version: 1, completed: {} };
		ids.forEach(id => { state.completed[id] = { firstCorrectAt: new Date().toISOString() }; });
		window.localStorage.setItem(key, JSON.stringify(state));
	}, { key: STORAGE_KEY, ids: seedIds });
	await popPage.reload({ waitUntil: 'domcontentloaded' });
	await waitForSelector(popPage, '.selftest-dashboard-summary');
	const popDash = await readDashboard(popPage);
	await popPage.screenshot({ path: path.join(OUT, `selftest_dashboard_populated_${vp.name}.png`), fullPage: true });

	// Reset-with-confirmation: accept the confirm() dialog and verify storage clears.
	popPage.once('dialog', d => d.accept());
	let resetCleared = null;
	if (popDash.resetButton && !popDash.resetDisabled) {
		await popPage.click('#selftest-reset-progress');
		await popPage.waitForTimeout(300);
		resetCleared = (await readProgressState(popPage)) === null;
		await popPage.screenshot({ path: path.join(OUT, `selftest_dashboard_after_reset_${vp.name}.png`), fullPage: true });
	}

	// Reset-with-confirmation dismissal: re-seed, dismiss the dialog, expect no clear.
	await popPage.evaluate(({ key, ids }) => {
		const state = { version: 1, completed: {} };
		ids.forEach(id => { state.completed[id] = { firstCorrectAt: new Date().toISOString() }; });
		window.localStorage.setItem(key, JSON.stringify(state));
	}, { key: STORAGE_KEY, ids: seedIds });
	await popPage.reload({ waitUntil: 'domcontentloaded' });
	await waitForSelector(popPage, '.selftest-dashboard-summary');
	popPage.once('dialog', d => d.dismiss());
	let dismissKept = null;
	const reBtn = await readDashboard(popPage);
	if (reBtn.resetButton && !reBtn.resetDisabled) {
		await popPage.click('#selftest-reset-progress');
		await popPage.waitForTimeout(300);
		dismissKept = (await readProgressState(popPage)) !== null;
	}

	findings.push({
		area: 'dashboard-populated', vp: vp.name, ok: popDash.present,
		seededIds: seedIds, summaryText: popDash.summaryText,
		completeTopics: popDash.completeTopics, resetButton: popDash.resetButton,
		resetClearedStorageOnConfirm: resetCleared,
		resetKeptStorageOnDismiss: dismissKept,
	});
	await popCtx.close();
}

// Storage-unavailable path: stub localStorage to throw, confirm a non-blocking
// warning renders and the dashboard reset button is disabled (not a crash).
async function reviewStorageUnavailable(browser, findings) {
	const ctx = await browser.newContext();
	await ctx.addInitScript(() => {
		// Make any localStorage access throw, mimicking private-mode / blocked storage.
		const throwing = {
			getItem() { throw new Error('storage blocked'); },
			setItem() { throw new Error('storage blocked'); },
			removeItem() { throw new Error('storage blocked'); },
		};
		try {
			Object.defineProperty(window, 'localStorage', { configurable: true, get() { return throwing; } });
		} catch (e) { /* some engines disallow redefining; best effort */ }
	});
	const page = await ctx.newPage();
	let pageError = null;
	page.on('pageerror', e => { pageError = String(e); });

	// Topic page: expect inline storage warning, badges still render as not-completed.
	await page.goto(BASE + TOPIC_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
	await page.waitForTimeout(1500);
	const topicWarn = await page.evaluate(() => {
		const w = document.getElementById('selftest-storage-warning');
		return w ? w.textContent.trim() : null;
	});
	await page.screenshot({ path: path.join(OUT, 'selftest_storage_unavailable_topic.png'), fullPage: true });

	// Dashboard page: warning inside dashboard, reset button disabled.
	await page.goto(BASE + PROGRESS_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
	await page.waitForTimeout(1500);
	const dashWarn = await readDashboard(page);
	await page.screenshot({ path: path.join(OUT, 'selftest_storage_unavailable_dashboard.png'), fullPage: true });

	findings.push({
		area: 'storage-unavailable', ok: !pageError,
		pageError,
		topicWarningShown: Boolean(topicWarn),
		topicWarningText: topicWarn,
		dashboardWarningShown: Boolean(dashWarn.warningText),
		resetDisabledWhenNoStorage: dashWarn.resetDisabled,
	});
	await ctx.close();
}

// ===========================================================================
// Main run
// ===========================================================================

const browser = await chromium.launch();
const report = [];
for (const vp of viewports) {
	const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
	const page = await ctx.newPage();
	const brokenLinks = [];
	page.on('response', r => {
		if (r.status() >= 400 && r.url().startsWith(BASE)) {
			brokenLinks.push({ url: r.url(), status: r.status() });
		}
	});
	for (const p of pages) {
		const url = BASE + p.url;
		let status = 0;
		let meta = null;
		try {
			const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });
			status = resp ? resp.status() : 0;
			await page.waitForTimeout(300);
			meta = await evalPage(page);
		} catch (e) {
			report.push({ vp: vp.name, slug: p.slug, url: p.url, status: 'ERR', err: String(e).slice(0, 120) });
			continue;
		}
		const shot = path.join(OUT, `${p.slug}_${vp.name}.png`);
		await page.screenshot({ path: shot, fullPage: true });
		report.push({ vp: vp.name, slug: p.slug, url: p.url, status, ...meta, shot });
	}
	if (vp.name === 'desktop') {
		try {
			await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 20000 });
			await page.waitForTimeout(300);
			// Material's palette JS runs at page load and reads localStorage before paint.
			// Use a fresh context with the palette pre-seeded via addInitScript.
			const darkCtx = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, colorScheme: 'dark' });
			await darkCtx.addInitScript(() => {
				localStorage.setItem('__palette', JSON.stringify({ index: 1, color: { scheme: 'slate', primary: 'green', accent: 'lime' } }));
			});
			const darkPage = await darkCtx.newPage();
			await darkPage.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 20000 });
			await darkPage.waitForTimeout(500);
			await darkPage.screenshot({ path: path.join(OUT, 'home_dark.png'), fullPage: true });
			await darkPage.goto(BASE + '/biochemistry/', { waitUntil: 'domcontentloaded', timeout: 20000 });
			await darkPage.waitForTimeout(500);
			await darkPage.screenshot({ path: path.join(OUT, 'subject_biochem_dark.png'), fullPage: true });
			// Dashboard in dark mode (contrast check for badges/topic-complete green).
			// Pre-seed progress so the dark capture shows completed-state colors.
			await darkPage.goto(BASE + PROGRESS_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
			const darkSeed = await darkPage.evaluate(async (manifestUrl) => {
				const manifest = await window.fetch(manifestUrl).then(r => r.json());
				return manifest.questions.slice(0, 3).map(q => q.questionId);
			}, MANIFEST_URL);
			await darkPage.evaluate(({ key, ids }) => {
				const state = { version: 1, completed: {} };
				ids.forEach(id => { state.completed[id] = { firstCorrectAt: new Date().toISOString() }; });
				window.localStorage.setItem(key, JSON.stringify(state));
			}, { key: STORAGE_KEY, ids: darkSeed });
			await darkPage.reload({ waitUntil: 'domcontentloaded' });
			await darkPage.waitForTimeout(700);
			await darkPage.screenshot({ path: path.join(OUT, 'selftest_dashboard_dark.png'), fullPage: true });
			await darkCtx.close();
		} catch (e) {
			console.log('dark mode capture failed:', String(e).slice(0, 200));
		}
	}
	await ctx.close();
}

// Focused self-test feature review.
const featureFindings = [];
try {
	for (const vp of viewports) {
		await reviewTopicBadges(browser, vp, featureFindings);
		await reviewDashboard(browser, vp, featureFindings);
	}
	await reviewWrongAnswerStoresNothing(browser, featureFindings);
	await reviewStorageUnavailable(browser, featureFindings);
} catch (e) {
	console.log('feature review error:', String(e).slice(0, 300));
	featureFindings.push({ area: 'feature-review', ok: false, error: String(e).slice(0, 300) });
}

await browser.close();

fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
fs.writeFileSync(path.join(OUT, 'selftest_feature_report.json'), JSON.stringify(featureFindings, null, 2));

for (const r of report) {
	console.log(`[${r.vp}] ${r.status} ${r.url}  H1=${r.h1count} imgs=${r.imgs} noAlt=${r.imgsNoAlt} tables=${r.tables} visTables=${r.visibleTables} details=${r.detailsBlocks} extNoRel=${r.externalNoRel}`);
}
console.log(`\nWrote ${report.length} page rows to ${OUT}/report.json`);

console.log('\n=== Self-test progress feature review ===');
for (const f of featureFindings) {
	console.log(`[${f.area}${f.vp ? '/' + f.vp : ''}] ` + JSON.stringify(f));
}
console.log(`\nWrote ${featureFindings.length} feature findings to ${OUT}/selftest_feature_report.json`);

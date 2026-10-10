#!/usr/bin/env node

/**
 * Refresh README views and the complete Python-QPM/BPW screenshot corpus.
 * Run ./devel/capture_screenshots.sh. This runner owns its MkDocs server.
 *
 * It never alters the frozen Python HTML.  Python screenshots use a capture-
 * only host wrapper labelled in the image; BPW screenshots use its normal
 * page controller and route only the corresponding saved one-record bank.
 */

import { execFileSync, spawn } from 'node:child_process';
import { once } from 'node:events';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { chromium } from 'playwright';

const REPO_ROOT = fileURLToPath(new URL('../', import.meta.url));
const BPW_URL = 'http://127.0.0.1:8765';
const FIXTURE_DIR = path.join(REPO_ROOT, '..', 'qti-package-maker-rs', 'tests', 'fixtures', 'python_selftest');
const SCREENSHOT_DIR = path.join(REPO_ROOT, 'docs', 'screenshots');
const RECEIPT_PATH = path.join(SCREENSHOT_DIR, 'selftest_capture_receipt.json');
const GIF_SCRIPT = path.resolve(REPO_ROOT, '../../vosslab-skills/skills/documentation/screenshot-docs/scripts/make_gif.sh');
const DESKTOP = { width: 1280, height: 800 };
const MOBILE = { width: 360, height: 800 };
const THEMES = ['light', 'dark'];

const manifest = JSON.parse(fs.readFileSync(path.join(FIXTURE_DIR, 'manifest.json'), 'utf8'));
const pageForBank = (bank) => `/${path.posix.dirname(bank)}/`;
const basenameForBank = (bank) => path.posix.basename(bank);
const now = new Date().toISOString();
const captures = [];

assert(process.argv.length === 2, 'Usage: ./devel/capture_screenshots.sh (refreshes the complete corpus)');
const OUTPUT_DIR = fs.mkdtempSync(path.join(os.tmpdir(), 'bpw-screenshots-'));
fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

function assert(condition, message) {
	if (!condition) throw new Error(message);
}

function capturePath(slug) {
	return path.join(OUTPUT_DIR, `${slug}.webp`);
}

function sha256(file) {
	return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

function imageInfo(file) {
	const image = file.endsWith('.gif') ? `${file}[0]` : file;
	const output = execFileSync('identify', ['-format', '%w %h', image], { encoding: 'utf8' }).trim().split(' ');
	return { width: Number(output[0]), height: Number(output[1]), bytes: fs.statSync(file).size };
}

function gifDurationSeconds(file) {
	const delays = execFileSync('identify', ['-format', '%T ', file], { encoding: 'utf8' })
		.trim().split(/\s+/).map(Number);
	return delays.reduce((total, delay) => total + delay, 0) / 100;
}

function wrapperDocument(caseData, theme, hostMetrics) {
	const fragment = fs.readFileSync(path.join(FIXTURE_DIR, caseData.output), 'utf8');
	return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Frozen Python reference: ${caseData.name}</title>
<style>
@font-face { font-family: "Atkinson Hyperlegible Next"; src: url("${BPW_URL}/assets/fonts/atkinson_hyperlegible_next/AtkinsonHyperlegibleNext-Variable.woff2") format("woff2"); font-weight: 200 800; font-style: normal; font-display: block; }
@font-face { font-family: "Atkinson Hyperlegible Next"; src: url("${BPW_URL}/assets/fonts/atkinson_hyperlegible_next/AtkinsonHyperlegibleNext-VariableItalic.woff2") format("woff2"); font-weight: 200 800; font-style: italic; font-display: block; }
html { color-scheme: ${theme}; }
body { margin: 0; min-height: 100vh; box-sizing: border-box; color: ${hostMetrics.color}; background: ${hostMetrics.background}; font-family: ${hostMetrics.fontFamily}; font-size: ${hostMetrics.fontSize}; line-height: ${hostMetrics.lineHeight}; ${hostMetrics.variables} }
.capture-frame { width: ${hostMetrics.width}px; max-width: 100%; margin: 20px auto; }
.capture-note { margin: 0 0 18px; padding: 9px 13px; border-left: 4px solid ${hostMetrics.accent}; background: ${hostMetrics.noteBackground}; font-size: 14px; }
.capture-note strong { display: block; }
 .reference-stage { width: ${hostMetrics.width}px; max-width: 100%; background: ${hostMetrics.surface}; }
</style></head><body data-md-color-scheme="${theme === 'dark' ? 'slate' : 'default'}"><main class="capture-frame"><article>
<p class="capture-note"><strong>Frozen Python QPM reference - capture-only host wrapper</strong>Original ${caseData.output} is rendered unchanged below. The wrapper supplies only the page background, system font, width, and this provenance label.</p>
<section class="reference-stage">${fragment}</section></article></main></body></html>`;
}

async function waitForQuestion(host) {
	await host.locator('.selftest-question-status').waitFor({ state: 'visible', timeout: 20_000 });
	await host.locator('.selftest-question-status').waitFor({ state: 'attached', timeout: 20_000 });
	await host.locator('[id^="question_html_"]').waitFor({ state: 'visible', timeout: 20_000 });
}

async function verifyRenderedQuestion(page, host, caseData, errors) {
	assert(await page.locator('#qti-selftest-theme').count() === 1,
		`${caseData.name}: self-test stylesheet was not installed exactly once`);
	const controls = host.locator('button, input, select, textarea');
	assert(await controls.count() > 0, `${caseData.name}: no question controls rendered`);
	if (caseData.name.includes('rdkit')) {
		await host.locator('canvas').first().waitFor({ state: 'visible', timeout: 25_000 });
		const painted = () => host.locator('canvas').evaluateAll((canvases) => canvases.length > 0 && canvases.every((canvas) => {
			const context = canvas.getContext('2d');
			if (!context || canvas.width === 0 || canvas.height === 0) return false;
			const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
			for (let index = 3; index < pixels.length; index += 4) if (pixels[index] !== 0) return true;
			return false;
		}));
		const deadline = Date.now() + 25_000;
		while (!(await painted()) && Date.now() < deadline) await page.waitForTimeout(250);
		assert(await painted(), `${caseData.name}: an RDKit canvas was visible but unpainted`);
	}
	assert(errors.length === 0, `${caseData.name}: browser errors: ${errors.join(' | ')}`);
}

async function screenshot(locator, slug, metadata) {
	const file = capturePath(slug);
	const temporary = path.join(OUTPUT_DIR, `${slug}.png`);
	await locator.screenshot({ path: temporary, animations: 'disabled' });
	let info = imageInfo(temporary);
	if (Math.max(info.width, info.height) > 1920) {
		execFileSync('convert', [temporary, '-resize', '1920x1920>', temporary]);
		info = imageInfo(temporary);
	}
	assert(Math.max(info.width, info.height) <= 1920, `${slug}: longer edge exceeds 1920px`);
	execFileSync('cwebp', ['-quiet', '-preset', 'text', '-q', '90', '-m', '6', temporary, '-o', file]);
	info = imageInfo(file);
	fs.unlinkSync(temporary);
	captures.push({ slug, file: path.relative(REPO_ROOT, path.join(SCREENSHOT_DIR, path.basename(file))), ...metadata, ...info, sha256: sha256(file) });
}

async function captureReadme(browser) {
	const viewport = { width: 1440, height: 900 };
	const context = await browser.newContext({ viewport, colorScheme: 'light', reducedMotion: 'reduce' });
	const page = await context.newPage();
	const errors = [];
	page.on('pageerror', (error) => errors.push(error.message));
	page.on('requestfailed', (request) => errors.push(`${request.url()}: ${request.failure()?.errorText}`));
	for (const [route, slug] of [
		['/', 'website_home'],
		['/daily_puzzles/', 'daily_puzzles'],
		['/genetics/topic03/', 'hla_problem_sets'],
	]) {
		await page.goto(`${BPW_URL}${route}`, { waitUntil: 'networkidle' });
		if (slug === 'hla_problem_sets') {
			const host = page.locator('.qti-selftest[data-bbq="bbq-hla_genotype-3_markers-color-questions.txt"]');
			await host.getByRole('button', { name: 'Show practice question', exact: true }).click();
			await host.locator('.qti-selftest-item').waitFor({ state: 'visible' });
			await page.locator('#qti-selftest-theme').waitFor({ state: 'attached' });
			await host.locator('xpath=preceding-sibling::h2[1]').evaluate((element) => window.scrollTo(0, element.offsetTop - 80));
			await page.waitForTimeout(500);
		}
		await page.evaluate(() => document.fonts.ready);
		assert(errors.length === 0, `README capture failed: ${errors.join(' | ')}`);
		await screenshot(page, slug, { backend: 'bpw_readme', route, theme: 'light', viewport });
		console.log(`README ${slug}`);
	}
	await context.close();
}

async function switchSiteTheme(page, theme) {
	const target = theme === 'dark' ? 'slate' : 'default';
	if (await page.locator('body').getAttribute('data-md-color-scheme') !== target) {
		await page.locator(`label[for="__palette_${theme === 'dark' ? 1 : 0}"]`).click();
	}
	await page.locator('body').waitFor({ state: 'visible' });
	assert(await page.locator('body').getAttribute('data-md-color-scheme') === target,
		`could not switch BPW to ${theme}`);
}

async function captureFrozen(browser, caseData, theme, hostMetrics) {
	const context = await browser.newContext({ viewport: DESKTOP, colorScheme: theme });
	const page = await context.newPage();
	const errors = [];
	page.on('pageerror', (error) => errors.push(error.message));
	await page.route('**/__capture/python/**', (route) => route.fulfill({
		contentType: 'text/html', body: wrapperDocument(caseData, theme, hostMetrics),
	}));
	await page.goto(`${BPW_URL}/__capture/python/${caseData.name}?theme=${theme}`, { waitUntil: 'networkidle' });
	const host = page.locator('.reference-stage .qti-selftest');
	await host.waitFor({ state: 'visible' });
	await page.locator('#qti-selftest-theme').waitFor({ state: 'attached' });
	await verifyRenderedQuestion(page, host, caseData, errors);
	await page.evaluate(() => document.fonts.ready);
	assert(await page.evaluate((font) => document.fonts.check(font), `${hostMetrics.fontSize} ${hostMetrics.fontFamily}`),
		`${caseData.name}: capture wrapper did not load the measured BPW font`);
	const frozenMetrics = await host.evaluate((element) => {
		const style = getComputedStyle(element);
		return { width: Math.round(element.getBoundingClientRect().width), fontFamily: style.fontFamily, fontSize: style.fontSize, lineHeight: style.lineHeight };
	});
	assert(frozenMetrics.width === hostMetrics.width,
		`${caseData.name}: frozen width ${frozenMetrics.width}px did not match BPW ${hostMetrics.width}px`);
	assert(frozenMetrics.fontFamily === hostMetrics.fontFamily && frozenMetrics.fontSize === hostMetrics.fontSize && frozenMetrics.lineHeight === hostMetrics.lineHeight,
		`${caseData.name}: frozen typography did not match the measured BPW host`);
	await screenshot(page.locator('main'), `selftest_python_${caseData.name}_${theme}`, {
		backend: 'frozen_python_host_wrapper', case: caseData.name, theme, viewport: DESKTOP,
		input: caseData.input, output: caseData.output, bank: caseData.bank,
		controls: 'rendered frozen Python question controls',
	});
	await context.close();
}

async function captureBpw(browser, caseData, theme) {
	const context = await browser.newContext({ viewport: DESKTOP, colorScheme: theme });
	const page = await context.newPage();
	console.log(`BPW ${caseData.name} ${theme}`);
	const errors = [];
	page.on('pageerror', (error) => errors.push(error.message));
	const exactRecord = fs.readFileSync(path.join(FIXTURE_DIR, caseData.input), 'utf8').trim();
	await page.route(`**/${basenameForBank(caseData.bank)}`, (route) => route.fulfill({
		contentType: 'text/plain; charset=utf-8', body: `${exactRecord}\n`,
	}));
	// MkDocs keeps long-lived local asset requests open in some browser runs.
	// Question readiness below is the durable capture condition; network-idle is
	// neither necessary nor reliable for this locally served application.
	await page.goto(`${BPW_URL}${pageForBank(caseData.bank)}`, { waitUntil: 'domcontentloaded' });
	await switchSiteTheme(page, theme);
	const host = page.locator(`.qti-selftest[data-bbq="${basenameForBank(caseData.bank)}"]`);
	const start = host.getByRole('button', { name: 'Show practice question', exact: true });
	if (await start.isVisible().catch(() => false)) await start.click();
	await waitForQuestion(host);
	await page.locator('#qti-selftest-theme').waitFor({ state: 'attached' });
	await verifyRenderedQuestion(page, host, caseData, errors);
	const hostMetrics = await host.evaluate((element) => {
		const style = getComputedStyle(element);
		const bodyStyle = getComputedStyle(document.body);
		const variableNames = [
			'--md-default-fg-color', '--md-default-bg-color', '--md-primary-fg-color',
			'--md-code-bg-color', '--md-typeset-a-color', '--md-accent-fg-color',
		];
		const variables = variableNames.map((name) => `${name}: ${style.getPropertyValue(name).trim()};`).join(' ');
		const box = element.getBoundingClientRect();
		return {
			width: Math.round(box.width), fontFamily: style.fontFamily, fontSize: style.fontSize,
			lineHeight: style.lineHeight, color: style.color, background: bodyStyle.backgroundColor,
			surface: style.backgroundColor, border: style.getPropertyValue('--qti-border').trim() || style.color,
			accent: style.getPropertyValue('--qti-btn-bg').trim() || style.color,
			noteBackground: style.getPropertyValue('--qti-slot-bg').trim() || style.backgroundColor,
			variables,
		};
	});
	await page.evaluate(() => document.fonts.ready);
	await screenshot(host, `selftest_bpw_${caseData.name}_${theme}`, {
		backend: 'bpw_actual_wasm', case: caseData.name, theme, viewport: DESKTOP,
		input: caseData.input, bank: caseData.bank,
		controls: 'BPW lifecycle header and real Wasm question controls',
	});
	await context.close();
	return hostMetrics;
}

async function chooseOneAndGrade(host) {
	const slots = host.locator('.qti-match-slot');
	const slot = slots.first();
	const correctValue = await slot.getAttribute('data-correct');
	assert(correctValue, 'MATCH first slot did not identify its correct choice');
	const choice = host.locator(`.qti-match-choice[data-value="${correctValue}"]`);
	await choice.click();
	await slot.click();
	await host.getByRole('button', { name: 'Check Answer', exact: true }).click();
	await host.locator('.feedback').first().waitFor({ state: 'visible', timeout: 10_000 });
	await host.locator('.feedback').first().evaluate((element) => {
		if (!element.textContent?.trim()) throw new Error('MATCH feedback was empty after Check Answer');
	});
	const feedback = host.locator('.feedback').first();
	const feedbackText = await feedback.textContent();
	const feedbackClasses = await feedback.getAttribute('class');
	assert(/correct|success|\u2713|\u2705/i.test(`${feedbackText} ${feedbackClasses}`),
		`MATCH correct assignment did not receive positive feedback: ${feedbackText} (${feedbackClasses})`);
}

async function captureFeatureEvidence(browser) {
	const match = manifest.cases.find((entry) => entry.name === 'match');
	const fib = manifest.cases.find((entry) => entry.name === 'fib');
	const matchRdkit = manifest.cases.find((entry) => entry.name === 'match_rdkit');
	assert(match && fib && matchRdkit, 'fixture manifest lacks required feature cases');

	// Full context preserves the actual page's navigation and the new initial
	// empty state, rather than presenting an isolated control as if it were a page.
	{
		const context = await browser.newContext({ viewport: DESKTOP, colorScheme: 'light' });
		const page = await context.newPage();
		await page.goto(`${BPW_URL}${pageForBank(match.bank)}`, { waitUntil: 'domcontentloaded' });
		const hosts = page.locator('.qti-selftest');
		assert(await hosts.count() > 1, 'site context page did not provide a second untouched self-test host');
		const host = hosts.nth(1);
		await host.getByText('Practice question', { exact: true }).waitFor();
		await host.scrollIntoViewIfNeeded();
		await screenshot(page, 'selftest_bpw_site_context_loaded', {
			backend: 'bpw_actual_site_context', case: 'match', theme: 'light', viewport: DESKTOP,
			controls: 'site navigation and an automatically loaded practice question',
		});
		await context.close();
	}

	// A grade result is captured from the real controller and the same saved
	// record. A single assignment deliberately leaves visible partial feedback.
	{
		const context = await browser.newContext({ viewport: DESKTOP, colorScheme: 'light' });
		const page = await context.newPage();
		const exactRecord = fs.readFileSync(path.join(FIXTURE_DIR, match.input), 'utf8').trim();
		await page.route(`**/${basenameForBank(match.bank)}`, (route) => route.fulfill({
			contentType: 'text/plain; charset=utf-8', body: `${exactRecord}\n`,
		}));
		await page.goto(`${BPW_URL}${pageForBank(match.bank)}`, { waitUntil: 'domcontentloaded' });
		const host = page.locator(`.qti-selftest[data-bbq="${basenameForBank(match.bank)}"]`);
		const start = host.getByRole('button', { name: 'Show practice question', exact: true });
		if (await start.isVisible().catch(() => false)) await start.click();
		await waitForQuestion(host);
		await chooseOneAndGrade(host);
		await screenshot(host, 'selftest_bpw_match_feedback_light', {
			backend: 'bpw_actual_wasm', case: 'match', theme: 'light', viewport: DESKTOP,
			input: match.input, bank: match.bank, controls: 'MATCH assignment then Check Answer with feedback',
		});
		await context.close();
	}

	// Mobile captures prove both a horizontally scrolled authored scientific
	// table and a responsive molecular matching layout.  The FIB record is used
	// unchanged and only its own bank response is routed.
	for (const [caseData, slug] of [[fib, 'selftest_bpw_mobile_fib_scrolled_dark'], [matchRdkit, 'selftest_bpw_mobile_match_rdkit_light']]) {
		const theme = caseData.name === 'fib' ? 'dark' : 'light';
		const context = await browser.newContext({ viewport: MOBILE, colorScheme: theme });
		const page = await context.newPage();
		const errors = [];
		page.on('pageerror', (error) => errors.push(error.message));
		const exactRecord = fs.readFileSync(path.join(FIXTURE_DIR, caseData.input), 'utf8').trim();
		await page.route(`**/${basenameForBank(caseData.bank)}`, (route) => route.fulfill({
			contentType: 'text/plain; charset=utf-8', body: `${exactRecord}\n`,
		}));
		await page.goto(`${BPW_URL}${pageForBank(caseData.bank)}`, { waitUntil: 'domcontentloaded' });
		await switchSiteTheme(page, theme);
		const host = page.locator(`.qti-selftest[data-bbq="${basenameForBank(caseData.bank)}"]`);
		const start = host.getByRole('button', { name: 'Show practice question', exact: true });
		if (await start.isVisible().catch(() => false)) await start.click();
		await waitForQuestion(host);
		await verifyRenderedQuestion(page, host, caseData, errors);
		if (caseData.name === 'fib') {
			const table = host.locator('table').last();
			await table.waitFor({ state: 'visible' });
			await table.evaluate((element) => {
				window.scrollTo({ top: Math.max(0, window.scrollY + element.getBoundingClientRect().top - 80), behavior: 'instant' });
			});
			await page.waitForTimeout(300);
			await screenshot(host, 'selftest_bpw_mobile_fib_initial_dark', {
				backend: 'bpw_actual_wasm', case: caseData.name, theme, viewport: MOBILE,
				input: caseData.input, bank: caseData.bank,
				controls: 'mobile FIB at the initial table position',
			});
			await host.evaluate((element) => { element.scrollLeft = element.scrollWidth; });
			assert(await host.evaluate((element) => element.scrollLeft > 0), 'mobile FIB host did not scroll');
			await page.waitForTimeout(300);
			const lastCell = table.locator('td, th').last();
			const cellBox = await lastCell.boundingBox();
			assert(cellBox && cellBox.y >= 0 && cellBox.y + cellBox.height <= MOBILE.height,
				'mobile FIB final table cell was outside the captured viewport');
		}
		await screenshot(caseData.name === 'fib' ? host : page, slug, {
			backend: 'bpw_actual_wasm', case: caseData.name, theme, viewport: MOBILE,
			input: caseData.input, bank: caseData.bank,
			controls: caseData.name === 'fib' ? 'mobile FIB final table cell after horizontal scroll' : 'mobile RDKit MATCH with painted canvases',
		});
		await context.close();
	}
}

async function captureMatchGif(browser) {
	const match = manifest.cases.find((entry) => entry.name === 'match');
	assert(match, 'fixture manifest lacks MATCH case');
	const videoDirectory = fs.mkdtempSync(path.join(OUTPUT_DIR, 'match-video-'));
	const context = await browser.newContext({ viewport: { width: 1000, height: 760 }, colorScheme: 'light', recordVideo: { dir: videoDirectory, size: { width: 1000, height: 760 } } });
	const page = await context.newPage();
	const recordStartedAt = Date.now();
	const exactRecord = fs.readFileSync(path.join(FIXTURE_DIR, match.input), 'utf8').trim();
	await page.route(`**/${basenameForBank(match.bank)}`, (route) => route.fulfill({
		contentType: 'text/plain; charset=utf-8', body: `${exactRecord}\n`,
	}));
	await page.goto(`${BPW_URL}${pageForBank(match.bank)}`, { waitUntil: 'domcontentloaded' });
	const host = page.locator(`.qti-selftest[data-bbq="${basenameForBank(match.bank)}"]`);
	const start = host.getByRole('button', { name: 'Show practice question', exact: true });
	if (await start.isVisible().catch(() => false)) await start.click();
	await waitForQuestion(host);
	await host.evaluate((element) => {
		window.scrollTo({ top: Math.max(0, window.scrollY + element.getBoundingClientRect().top - 90) });
	});
	await page.waitForTimeout(350);
	const readyAtSeconds = (Date.now() - recordStartedAt) / 1000;
	const gifSlot = host.locator('.qti-match-slot').first();
	const gifCorrectValue = await gifSlot.getAttribute('data-correct');
	assert(gifCorrectValue, 'MATCH GIF slot did not identify its correct choice');
	await host.locator(`.qti-match-choice[data-value="${gifCorrectValue}"]`).click();
	await page.waitForTimeout(450);
	await gifSlot.click();
	await page.waitForTimeout(450);
	await host.getByRole('button', { name: 'Check Answer', exact: true }).click();
	await host.locator('.feedback').first().waitFor({ state: 'visible' });
	await host.locator('.feedback').first().evaluate((element) => {
		if (!element.textContent?.trim()) throw new Error('MATCH GIF ended with empty feedback');
	});
	await page.waitForTimeout(1_700);
	const video = page.video();
	await context.close();
	const videoPath = await video.path();
	const trimmedVideo = path.join(OUTPUT_DIR, 'match-assignment-ready.webm');
	execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-ss', readyAtSeconds.toFixed(2), '-i', videoPath, '-t', '4', '-an', '-c:v', 'libvpx-vp9', trimmedVideo]);
	const gifPath = path.join(OUTPUT_DIR, 'selftest_match_assignment_demo.gif');
	execFileSync(GIF_SCRIPT, [trimmedVideo, gifPath, '1000', '12', '4'], { stdio: 'inherit' });
	const info = imageInfo(gifPath);
	assert(info.bytes <= 5 * 1024 * 1024, 'MATCH GIF exceeds 5 MB');
	const durationSeconds = gifDurationSeconds(gifPath);
	assert(durationSeconds <= 5, 'MATCH GIF exceeds the five-second playback limit');
	captures.push({ slug: 'selftest_match_assignment_demo', file: path.relative(REPO_ROOT, path.join(SCREENSHOT_DIR, path.basename(gifPath))), backend: 'bpw_actual_wasm_video', case: 'match', theme: 'light', viewport: { width: 1000, height: 760 }, controls: 'MATCH click assignment, Check Answer, feedback', ...info, sha256: sha256(gifPath), duration_seconds: durationSeconds, fps: 12, loops: 1 });
	fs.rmSync(videoDirectory, { recursive: true, force: true });
	fs.rmSync(trimmedVideo, { force: true });

	const reduced = await browser.newContext({ viewport: DESKTOP, colorScheme: 'light', reducedMotion: 'reduce' });
	const reducedPage = await reduced.newPage();
	await reducedPage.route(`**/${basenameForBank(match.bank)}`, (route) => route.fulfill({
		contentType: 'text/plain; charset=utf-8', body: `${exactRecord}\n`,
	}));
	await reducedPage.goto(`${BPW_URL}${pageForBank(match.bank)}`, { waitUntil: 'domcontentloaded' });
	const reducedHost = reducedPage.locator(`.qti-selftest[data-bbq="${basenameForBank(match.bank)}"]`);
	const reducedStart = reducedHost.getByRole('button', { name: 'Show practice question', exact: true });
	if (await reducedStart.isVisible().catch(() => false)) await reducedStart.click();
	await waitForQuestion(reducedHost);
	await chooseOneAndGrade(reducedHost);
	assert(await reducedHost.locator('.feedback').first().isVisible(), 'reduced-motion MATCH feedback was not visible');
	await reduced.close();
	return { reduced_motion_result: 'MATCH assignment and feedback remained visible with reduced motion.' };
}

// ASVS 1.2.5: pass process arguments directly, without shell interpolation.
const server = spawn('mkdocs', ['serve', '--dev-addr', '127.0.0.1:8765', '--no-livereload'], {
	cwd: REPO_ROOT, stdio: ['ignore', 'pipe', 'pipe'],
});
let startupLog = '';
let serverError;
server.on('error', (error) => { serverError = error; });
server.stdout.on('data', (data) => { startupLog += data; });
server.stderr.on('data', (data) => { startupLog += data; });
let browser;
let reducedMotion;

async function cleanup() {
	try {
		await browser?.close();
	} finally {
		if (server.pid && server.exitCode === null && server.signalCode === null) {
			const stopped = once(server, 'exit');
			server.kill('SIGTERM');
			await stopped;
		}
		fs.rmSync(OUTPUT_DIR, { recursive: true, force: true });
	}
}

for (const [signal, code] of [['SIGINT', 130], ['SIGTERM', 143]]) {
	process.once(signal, async () => {
		await cleanup();
		process.exit(code);
	});
}

try {
	console.log(`Starting MkDocs at ${BPW_URL}`);
	const deadline = Date.now() + 30_000;
	while (!startupLog.includes(`Serving on ${BPW_URL}`)) {
		if (serverError) throw serverError;
		assert(server.exitCode === null && server.signalCode === null, `MkDocs exited before serving:\n${startupLog}`);
		assert(Date.now() < deadline, `MkDocs did not become ready:\n${startupLog}`);
		await new Promise((resolve) => setTimeout(resolve, 100));
	}
	const response = await fetch(BPW_URL);
	assert(response.ok, `MkDocs returned HTTP ${response.status}`);
	browser = await chromium.launch({ headless: true });
	await captureReadme(browser);
	for (const caseData of manifest.cases) {
		for (const theme of THEMES) {
			const hostMetrics = await captureBpw(browser, caseData, theme);
			await captureFrozen(browser, caseData, theme, hostMetrics);
		}
	}
	await captureFeatureEvidence(browser);
	reducedMotion = await captureMatchGif(browser);
	const receipt = {
		captured_at: now,
		browser: 'Playwright Chromium',
		bpw_url: BPW_URL,
		fixture_manifest: path.relative(REPO_ROOT, path.join(FIXTURE_DIR, 'manifest.json')),
		fixture_python_commit: manifest.python_commit,
		case_count: manifest.cases.length,
		webp_count: captures.filter((entry) => entry.file.endsWith('.webp')).length,
		gif_count: captures.filter((entry) => entry.file.endsWith('.gif')).length,
		controls_exercised: ['Show practice question', 'Show another question', 'MATCH choice assignment', 'Check Answer', 'feedback', 'mobile horizontal scrolling'],
		known_source_quirks: ['Frozen Python references retain authored inline colors and their original external RDKit dependency.', 'The capture-only Python wrapper is visible in every frozen-reference image and does not alter the saved fragment.'],
		...reducedMotion,
		captures,
	};
	// Publish only after all captures succeed, preserving the last corpus on capture failure.
	for (const capture of captures) {
		fs.copyFileSync(path.join(OUTPUT_DIR, path.basename(capture.file)), path.join(REPO_ROOT, capture.file));
	}
	fs.writeFileSync(RECEIPT_PATH, `${JSON.stringify(receipt, null, 2)}\n`);
	console.log(`Captured ${receipt.webp_count} WebP images and ${receipt.gif_count} GIF to docs/screenshots/`);
} finally {
	await cleanup();
}

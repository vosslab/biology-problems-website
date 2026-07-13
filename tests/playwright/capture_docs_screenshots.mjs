#!/usr/bin/env node

/**
 * Capture the stable website views embedded in README.md.
 *
 * Run from the repository root:
 *   ./tests/playwright/capture_docs_screenshots.mjs
 *
 * The script starts and stops its own MkDocs development server.
 */

import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { chromium } from 'playwright';

import { REPO_ROOT } from './repo_root.mjs';

const PORT = Number.parseInt(process.env.DOCS_SCREENSHOT_PORT ?? '8765', 10);
const BASE_URL = `http://127.0.0.1:${PORT}`;
const SCREENSHOT_DIR = path.join(REPO_ROOT, 'docs', 'screenshots');
const VIEWPORT = { width: 1440, height: 900 };

fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

const server = spawn(
	'mkdocs',
	['serve', '--dev-addr', `127.0.0.1:${PORT}`, '--no-livereload'],
	{
		cwd: REPO_ROOT,
		stdio: ['ignore', 'inherit', 'inherit'],
	},
);

async function waitForServer() {
	const deadline = Date.now() + 30_000;
	while (Date.now() < deadline) {
		if (server.exitCode !== null) {
			throw new Error(`mkdocs serve exited with code ${server.exitCode}`);
		}
		try {
			const response = await fetch(BASE_URL);
			if (response.ok) {
				return;
			}
		} catch {
			// The server socket is not ready yet; continue polling until the deadline.
		}
		await new Promise((resolve) => setTimeout(resolve, 100));
	}
	throw new Error(`mkdocs serve did not become ready at ${BASE_URL}`);
}

async function capture(page, route, slug, preparePage) {
	await page.goto(`${BASE_URL}${route}`, { waitUntil: 'networkidle' });
	if (preparePage) {
		await preparePage(page);
	}
	const temporaryPath = path.join(os.tmpdir(), `${slug}.png`);
	await page.screenshot({ path: temporaryPath });
	fs.copyFileSync(temporaryPath, path.join(SCREENSHOT_DIR, `${slug}.png`));
	fs.unlinkSync(temporaryPath);
	console.log(`Captured docs/screenshots/${slug}.png`);
}

let browser;

try {
	await waitForServer();
	browser = await chromium.launch();
	const page = await browser.newPage({ viewport: VIEWPORT, colorScheme: 'light' });
	const pageErrors = [];
	page.on('pageerror', (error) => pageErrors.push(error));

	await capture(page, '/', 'website_home');
	await capture(page, '/daily_puzzles/', 'daily_puzzles');
	await capture(page, '/genetics/topic03/', 'hla_problem_sets', async (topicPage) => {
		const heading = topicPage.getByRole('heading', {
			name: /Offspring HLA Genotypes \(2 Markers, Color\)/,
		});
		await heading.evaluate((element) => window.scrollTo(0, element.offsetTop - 90));
	});

	if (pageErrors.length > 0) {
		throw new AggregateError(pageErrors, 'Website pages raised JavaScript errors during capture');
	}
} finally {
	await browser?.close();
	server.kill('SIGTERM');
}

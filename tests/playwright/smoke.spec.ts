// smoke.spec.ts - full-sitemap structural + self-test smoke, one test per route.
//
// This is the runner-model front door for the smoke suite. The
// playwright.config.ts webServer block owns one managed server (mkdocs build,
// then serve site/ over HTTP) shared by every worker, and the runner owns
// pass/fail. No per-file server, no chromium import, no process.exit.
//
// Route set: every route in the built sitemap. At collection time this reads
// <repoRoot>/site/sitemap.xml from disk (building the site once with
// `mkdocs build` if the sitemap is absent) and parses it with parseSitemap from
// ./helper_discover.mjs -- the same parser the HTTP discovery path uses. One
// test is generated per route, so a bare `npx playwright test` is
// self-sufficient for both collection and the run.
//
// The structural shell and self-test drive logic (and the full selector
// contract, cited by source file:line) live in ./helper_smoke_checks.mjs; both
// exported checks throw on failure, which fails the owning test. The font
// contract is custom.css:1-19 plus mkdocs.yml:4-6.

/// <reference types="node" />

import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

import { REPO_ROOT } from "./repo_root.mjs";
import { parseSitemap } from "./helper_discover.mjs";
import { checkPageStructure, driveSelfTestIfPresent } from "./helper_smoke_checks.mjs";

//============================================
// Collection-time route discovery from the built sitemap on disk
//============================================

// Built sitemap path (mkdocs writes it to the default site/ output directory).
const SITEMAP_PATH = path.join(REPO_ROOT, "site", "sitemap.xml");

// Read site/sitemap.xml, building the site once if it is not yet present. The
// webServer block also builds when the suite runs, but collection happens
// before that server starts, so an idempotent build here keeps a bare
// `npx playwright test` self-sufficient for generating the per-route tests.
function readSitemapText(): string {
	if (!fs.existsSync(SITEMAP_PATH)) {
		// Build in the repo root so mkdocs finds mkdocs.yml and writes site/.
		execSync("mkdocs build", { cwd: REPO_ROOT, stdio: "inherit" });
	}
	return fs.readFileSync(SITEMAP_PATH, "utf8");
}

// The complete route set: normalized, deduped, "/"-first (parseSitemap).
const ROUTES = parseSitemap(readSitemapText());

//============================================
// One test per route
//============================================

for (const route of ROUTES) {
	test(`route: ${route}`, async ({ page }) => {
		// Capture console errors and uncaught page errors; a strict run fails the
		// route on either. Subscribe before navigation so nothing is missed.
		const consoleErrors: string[] = [];
		const pageErrors: string[] = [];
		page.on("console", (msg) => {
			if (msg.type() === "error") {
				consoleErrors.push(msg.text());
			}
		});
		page.on("pageerror", (error) => {
			pageErrors.push(error.message);
		});

		// Seed clean pre-boot state: clear any progress/streak left by a prior
		// visit so each route is checked in isolation.
		await page.addInitScript(() => {
			window.localStorage.removeItem("selftest_progress_v1");
			window.localStorage.removeItem("selftest_streak_v1");
		});

		// baseURL is set in playwright.config.ts; wait for the load event.
		await page.goto(route, { waitUntil: "load" });

		// Structural shell, then the question-agnostic self-test driver. Both
		// throw on failure (helper_smoke_checks.mjs), failing this test.
		await checkPageStructure(page, route);
		await driveSelfTestIfPresent(page, route);

		// Strict: no console errors and no uncaught page errors on this route.
		// Failure screenshots come from the config's screenshot: "only-on-failure".
		expect(consoleErrors).toEqual([]);
		expect(pageErrors).toEqual([]);
	});
}

//============================================
// Site-wide self-hosted font contract
//============================================

test("site uses the self-hosted Atkinson text font", async ({ page }) => {
	await page.goto("/", { waitUntil: "load" });
	const fontState = await page.evaluate(async () => {
		const loadedFaces = await Promise.all([
			document.fonts.load('400 16px "Atkinson Hyperlegible Next"'),
			document.fonts.load('italic 400 16px "Atkinson Hyperlegible Next"'),
		]);
		const resourceUrls = performance.getEntriesByType("resource").map((entry) => entry.name);
		const localFontUrls = resourceUrls.filter((url) =>
			url.includes("/assets/fonts/atkinson_hyperlegible_next/"),
		);
		const state = {
			facesLoaded: loadedFaces.every((faces) => faces.length > 0),
			bodyUsesAtkinson: getComputedStyle(document.body).fontFamily.includes(
				"Atkinson Hyperlegible Next",
			),
			fontsAreLocal:
				localFontUrls.length > 0 &&
				localFontUrls.every((url) => new URL(url).origin === window.location.origin),
			googleFontsAbsent: resourceUrls.every(
				(url) => !/fonts\.(googleapis|gstatic)\.com/.test(url),
			),
		};
		return state;
	});
	expect(fontState).toEqual({
		facesLoaded: true,
		bodyUsesAtkinson: true,
		fontsAreLocal: true,
		googleFontsAbsent: true,
	});
});

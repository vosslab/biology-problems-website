// playwright.config.ts - Playwright test-runner config for the browser suite.
//
// Adopts the runner model (@playwright/test + *.spec.ts) as this repo's
// Playwright model for durable app tests, matching the sibling
// virtual-lab-protocol-simulation config. The .mjs files under
// tests/playwright/ stay bare-library helper/survey scripts and are not
// collected by the runner.
//
// How to run:
//   ./run_playwright_tests.sh          (front door: preflight + entry point)
//   npx playwright test                (config's webServer builds + serves on its own)
//
// Server model: the webServer block below owns one managed server for every
// worker. Its command BUILDS the MkDocs site (mkdocs build, output under the
// default site/ directory) then SERVES site/ over HTTP via Python's
// http.server, so a passing test reflects the shipped static build a reader
// receives (PLAYWRIGHT_TEST_STYLE.md load model: build first, then serve the
// build).
//
// Port: honors the repo random-port convention (8000 + rand(0..999), overridable
// via the PORT env var). The port is chosen once here in the config's main
// process and pinned into BOTH the webServer url and use.baseURL, so every
// worker agrees on one URL. A bind collision fails loud (correct signal) rather
// than triggering a free-port scan.

import { defineConfig, devices } from "@playwright/test";

//============================================
// Environment access without depending on Node's process typings
//============================================

// Access globalThis.process.env without pulling in @types/node globals. The
// cast keeps the config typecheckable without a Node-typed tsconfig (mirrors
// the virtual-lab-protocol-simulation config).
function processEnv(): Record<string, string | undefined> | undefined {
  const proc = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process;
  return proc?.env;
}

// Read an env var off process.env when present.
function readEnv(name: string): string | undefined {
  const env = processEnv();
  return env?.[name];
}

// Persist a value into process.env so worker processes (which re-import this
// config) inherit it from the main runner process.
function writeEnv(name: string, value: string): void {
  const env = processEnv();
  if (env !== undefined) {
    env[name] = value;
  }
}

// CI is truthy when the standard CI env var is set to a non-empty value.
function isCi(): boolean {
  const value = readEnv("CI");
  return value !== undefined && value !== "";
}

//============================================
// Port and base URL (pinned once, shared to all workers)
//============================================

// Random per-run port unless PORT overrides it. The config is evaluated once in
// the main runner process and again in every worker process; a bare
// Math.random() would pick a different port per process, so the browser would
// target a port with no server. Persist the chosen port into process.env.PORT
// on first evaluation so workers inherit the same value.
function choosePort(): number {
  const existing = readEnv("PORT");
  if (existing !== undefined && existing !== "") {
    return Number(existing);
  }
  const port = 8000 + Math.floor(Math.random() * 1000);
  writeEnv("PORT", String(port));
  return port;
}

const PORT = choosePort();
// Use 127.0.0.1 (not localhost) and bind the server to it below: localhost can
// resolve to IPv6 ::1 while python's http.server listens on IPv4, so chromium
// would refuse the connection. The repo's library helpers already standardize
// on 127.0.0.1 for the served MkDocs site.
const BASE_URL = `http://127.0.0.1:${PORT}`;
const CI = isCi();

//============================================
// Config
//============================================

export default defineConfig({
  // Browser specs live alongside the Playwright helpers.
  testDir: "tests/playwright",
  // Only *.spec.ts files are runner specs; *.mjs files are library scripts.
  testMatch: "**/*.spec.ts",
  // Fail the CI build if a stray test.only is left in the source.
  forbidOnly: CI,
  // The site has many routes; run specs in parallel across workers to keep the
  // suite fast.
  fullyParallel: true,
  workers: 4,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    // Failure-only screenshots for post-run diagnosis.
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  // Build the MkDocs site (default output site/), then serve site/ over HTTP.
  // One managed server for every worker. reuseExistingServer lets a dev keep a
  // server running across reruns (off under CI). The build step makes a bare
  // `npx playwright test` self-sufficient without a prior manual build.
  webServer: {
    command: `mkdocs build && python3 -m http.server ${PORT} --bind 127.0.0.1 --directory site`,
    url: BASE_URL,
    reuseExistingServer: !CI,
    timeout: 180_000,
  },
});

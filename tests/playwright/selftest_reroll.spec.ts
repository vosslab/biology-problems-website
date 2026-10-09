// Regression: a reroll must give a fresh attempt without sharing another CRC's completion.
// Uses the published bank and real vendored WASM; only random seeds are controlled.
import { test, expect } from "@playwright/test";
import type { Locator, Page } from "@playwright/test";

async function completeMultipleChoice(host: Locator) {
  const radios = host.locator('input[type="radio"]');
  const check = host.getByRole("button", { name: /check answer/i });
  for (let index = 0; index < await radios.count(); index += 1) {
    await radios.nth(index).check();
    await check.click();
    if ((await host.locator('[id^="result_"]').textContent())?.trim() === "CORRECT") {
      await expect(host.locator("[data-selftest-status]")).toContainText("Completed");
      await expect(check).toBeEnabled();
      return;
    }
  }
  throw new Error("The real MC bank had no correctly grading choice.");
}

async function reroll(host: Locator) {
  await host.getByRole("button", { name: "New version", exact: true }).click();
  await expect(host.getByRole("status").filter({ hasText: "New version ready." })).toBeVisible();
  return host.locator('[id^="question_html_"]').getAttribute("id");
}

async function setSeed(page: Page, seed: number) {
  await page.evaluate((value) => {
    Object.defineProperty(window.crypto, "getRandomValues", { configurable: true,
      value: (array: Uint32Array) => { array[0] = value; return array; } });
  }, seed);
}

test("real WASM rerolls retain completion only for the displayed question", async ({ page }) => {
  const errors: string[] = [];
  const wasmRequests: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (request.url().includes("/qti_wasm/")) { wasmRequests.push(request.url()); }
  });
  await page.goto("/genetics/topic01/");
  const host = page.locator('.qti-selftest[data-bbq="bbq-WOMC-genetic_disorders-questions.txt"]');
  await host.locator("xpath=ancestor::details").evaluate((element) => element.setAttribute("open", ""));
  await expect(host.locator("[data-selftest-status]")).toContainText("Not completed");
  expect(wasmRequests).toEqual([]);

  // Remember the successful selection seed so B -> A exercises the real converter again.
  await page.evaluate(() => {
    let seed = 0;
    Object.defineProperty(window.crypto, "getRandomValues", { configurable: true,
      value: (array: Uint32Array) => {
        array[0] = ++seed;
        (window as unknown as { rerollSeed: number }).rerollSeed = seed;
        return array;
      } });
  });
  const a = await reroll(host);
  const seedA = await page.evaluate(() => (window as unknown as { rerollSeed: number }).rerollSeed);
  expect(wasmRequests.some((url) => url.endsWith(".wasm"))).toBe(true);
  await completeMultipleChoice(host);
  const b = await reroll(host);
  expect(b).not.toEqual(a);
  await expect(host.locator("[data-selftest-status]")).toHaveText("Not completed");
  await expect(host.locator('input[type="radio"]:checked')).toHaveCount(0);
  await expect(host.locator('[id^="result_"]')).toHaveText("");

  await host.locator('input[type="radio"][data-correct="false"]').first().check();
  await host.getByRole("button", { name: /check answer/i }).click();
  await expect(host.locator('[id^="result_"]')).toHaveText("incorrect");
  await expect(host.locator("[data-selftest-status]")).not.toContainText("Completed");
  const afterIncorrect = await page.evaluate(() =>
    JSON.parse(localStorage.getItem("selftest_progress_v1") || "null"));
  expect(Object.keys(afterIncorrect.completed)).toContain(a!.slice("question_html_".length));
  expect(Object.keys(afterIncorrect.completed)).not.toContain(b!.slice("question_html_".length));
  await completeMultipleChoice(host);
  const afterB = await page.evaluate(() =>
    JSON.parse(localStorage.getItem("selftest_progress_v1") || "null"));
  expect(Object.keys(afterB.completed).sort()).toEqual([
    a!.slice("question_html_".length), b!.slice("question_html_".length),
  ].sort());

  await setSeed(page, seedA);
  expect(await reroll(host)).toEqual(a);
  await expect(host.locator("[data-selftest-status]")).toContainText("Completed");
  await expect(host.locator('input[type="radio"]:checked')).toHaveCount(0);
  await expect(host.locator('[id^="result_"]')).toHaveText("");
  expect(errors).toEqual([]);
});

// This converter stub isolates script installation from the separate real-WASM acceptance above.
// The fixture follows topic_page.py's data-bbq contract and loads the built reroll script over HTTP.
// The status/button selector contract is selftest_reroll.js's init() control creation.
async function scriptDependencyHost(page: Page) {
  await page.route("**/qti_wasm/src/index.js", async (route) => {
    await route.fulfill({ contentType: "text/javascript", body: `
      let sequence = 0;
      export async function initialize() {}
      export function convert() {
        const html = '<html><body><div id="question_html_script_' + ++sequence + '">' +
          '<canvas aria-label="Question drawing" width="10" height="10"></canvas></div>' +
          '<script src="/assets/scripts/reroll_dependency.js"></script>' +
          '<script>drawQuestion();</script>' +
          '<script>document.querySelector("canvas[aria-label]")' +
          '.dataset.initialized = "yes";</script></body></html>';
        return { status: "success", artifact: { kind: "file",
          primary: { bytes: new TextEncoder().encode(html) } } };
      }
    ` });
  });
  await page.route("**/reroll_script_fixture/", async (route) => {
    await route.fulfill({ contentType: "text/html", body: `
      <div class="qti-selftest" data-bbq="questions.txt">
        <div id="question_html_original">Original question</div>
      </div>
      <script src="/assets/scripts/selftest_reroll.js"></script>
    ` });
  });
  await page.route("**/reroll_script_fixture/questions.txt", async (route) => {
    await route.fulfill({ body: "MC\tFixture question\tChoice\tCorrect" });
  });
  await page.goto("/reroll_script_fixture/");
  return page.locator(".qti-selftest[data-bbq]");
}

const drawingLibrary = `
  function drawQuestion() {
    const canvas = document.querySelector('[aria-label="Question drawing"]');
    canvas.getContext("2d").fillRect(0, 0, 10, 10);
    canvas.dataset.drawn = "yes";
  }
`;

test("reroll waits for an external drawing library before inline scripts and readiness", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  let release!: () => void;
  const delayed = new Promise<void>((resolve) => { release = resolve; });
  await page.route("**/reroll_dependency.js", async (route) => {
    await delayed;
    await route.fulfill({ contentType: "text/javascript", body: drawingLibrary });
  });
  const host = await scriptDependencyHost(page);
  const requested = page.waitForRequest("**/reroll_dependency.js");
  const button = host.getByRole("button", { name: "New version", exact: true });
  const status = host.locator('.selftest-reroll-button + [role="status"]');
  await button.click();
  await requested;
  await expect(status).toHaveText("Loading a new version...");
  await expect(button).toBeDisabled();
  await expect(host.locator("canvas")).not.toHaveAttribute("data-drawn", "yes");
  await expect(host.locator("canvas")).not.toHaveAttribute("data-initialized", "yes");
  release();
  await expect(status).toHaveText("New version ready.");
  await expect(host.locator("canvas")).toHaveAttribute("data-drawn", "yes");
  await expect(host.locator("canvas")).toHaveAttribute("data-initialized", "yes");
  await expect(button).toBeEnabled();
  expect(errors).toEqual([]);
});

test("reroll reports an external script failure, skips dependents, and permits retry", async ({ page }) => {
  let fail = true;
  await page.route("**/reroll_dependency.js", async (route) => {
    if (fail) { await route.abort(); }
    else { await route.fulfill({ contentType: "text/javascript", body: drawingLibrary }); }
  });
  const host = await scriptDependencyHost(page);
  const button = host.getByRole("button", { name: "New version", exact: true });
  const status = host.locator('.selftest-reroll-button + [role="status"]');
  await button.click();
  await expect(status).toHaveText("Could not load a question script. Try again.");
  await expect(button).toBeEnabled();
  await expect(host.locator("canvas")).not.toHaveAttribute("data-drawn", "yes");
  await expect(host.locator("canvas")).not.toHaveAttribute("data-initialized", "yes");
  fail = false;
  await button.click();
  await expect(status).toHaveText("New version ready.");
  await expect(host.locator("canvas")).toHaveAttribute("data-drawn", "yes");
  await expect(host.locator("canvas")).toHaveAttribute("data-initialized", "yes");
  await expect(button).toBeEnabled();
});

// Dynamic self-test contract. Selectors here describe the student-visible
// container contract in selftest_reroll.js: an empty body is populated on
// demand, its header owns the completion badge and version button, and the
// status region reports readiness.
import { expect, test } from "@playwright/test";
import type { Locator, Page } from "@playwright/test";

const QUESTION_ID_PREFIX = "question_html_";

function questionId(host: Locator): Locator {
  return host.locator(`[id^="${QUESTION_ID_PREFIX}"]`).first();
}

async function waitForReady(host: Locator): Promise<void> {
  await expect(host.locator(".selftest-question-status")).toHaveText("Question ready.");
  await expect(questionId(host)).toBeVisible();
}

test("real WASM starts one question and loads another on request", async ({ page }) => {
  const errors: string[] = [];
  const wasmRequests: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (request.url().includes("/qti_wasm/")) {
      wasmRequests.push(request.url());
    }
  });
  await page.goto("/genetics/topic01/");

  const hosts = page.locator(".qti-selftest[data-bbq][data-selftest]");
  await expect(hosts.first()).toBeAttached();
  const first = hosts.first();
  const second = hosts.nth(1);
  await waitForReady(first);
  expect(wasmRequests.some((url) => url.endsWith(".wasm"))).toBe(true);
  await expect(second.locator(`[id^="${QUESTION_ID_PREFIX}"]`)).toHaveCount(0);
  await expect(second.getByRole("button", { name: "Start question", exact: true })).toBeVisible();

  await second.getByRole("button", { name: "Start question", exact: true }).click();
  await waitForReady(second);
  expect(errors).toEqual([]);
});

// These fixtures isolate controller lifecycle from real-WASM conversion. Each
// artifact includes a valid generated checkAnswer_* function so readiness proves
// scripts finished installing, not merely that markup arrived.
async function lifecycleFixture(page: Page): Promise<Locator> {
  await page.route("**/qti_wasm/src/index.js", async (route) => {
    await route.fulfill({ contentType: "text/javascript", body: `
      let version = 0;
      export async function initialize() {}
      export function convert() {
        version += 1;
        const id = 'fixture_' + version;
        const html = '<html><body><div id="question_html_' + id + '">' +
          '<label><input type="radio" name="' + id + '"> answer</label>' +
          '<button type="button" onclick="checkAnswer_' + id + '()">Check Answer</button>' +
          '<div id="result_' + id + '"></div></div>' +
          '<script>function checkAnswer_' + id + '(){document.getElementById("result_' + id + '").textContent="CORRECT";}</script>' +
          '</body></html>';
        return { status: 'success', artifact: { kind: 'file', primary: {
          bytes: new TextEncoder().encode(html) } } };
      }
    ` });
  });
  await page.route("**/selftest_lifecycle_fixture/", async (route) => {
    await route.fulfill({ contentType: "text/html", body: `
      <div class="qti-selftest" data-bbq="one.txt" data-selftest="one.html"><div class="selftest-reroll-content"></div></div>
      <div class="qti-selftest" data-bbq="two.txt" data-selftest="two.html"><div class="selftest-reroll-content"></div></div>
      <div class="qti-selftest" data-bbq="three.txt" data-selftest="three.html"><div class="selftest-reroll-content"></div></div>
      <script src="/assets/scripts/selftest_reroll.js"></script>
    ` });
  });
  for (const name of ["one", "two", "three"]) {
    await page.route(`**/selftest_lifecycle_fixture/${name}.txt`, async (route) => {
      await route.fulfill({ body: "MC\tFixture\tAnswer\tCorrect" });
    });
  }
  await page.goto("/selftest_lifecycle_fixture/");
  return page.locator(".qti-selftest");
}

async function dependencyFixture(page: Page): Promise<Locator> {
  await page.route("**/qti_wasm/src/index.js", async (route) => {
    await route.fulfill({ contentType: "text/javascript", body: `
      export async function initialize() {}
      export function convert() {
        const html = '<html><body><div id="question_html_dependency">' +
          '<canvas aria-label="Question drawing" width="10" height="10"></canvas>' +
          '<label><input type="radio" name="dependency"> answer</label>' +
          '<button type="button" onclick="checkAnswer_dependency()">Check Answer</button>' +
          '<div id="result_dependency"></div></div>' +
          '<script src="/assets/scripts/reroll_dependency.js"></script>' +
          '<script>drawQuestion();function checkAnswer_dependency(){document.getElementById("result_dependency").textContent="CORRECT";}</script>' +
          '</body></html>';
        return { status: 'success', artifact: { kind: 'file', primary: {
          bytes: new TextEncoder().encode(html) } } };
      }
    ` });
  });
  await page.route("**/selftest_dependency_fixture/", async (route) => {
    await route.fulfill({ contentType: "text/html", body: `
      <div class="qti-selftest" data-bbq="dependency.txt" data-selftest="dependency.html"><div class="selftest-reroll-content"></div></div>
      <script src="/assets/scripts/selftest_reroll.js"></script>
    ` });
  });
  await page.route("**/selftest_dependency_fixture/dependency.txt", async (route) => {
    await route.fulfill({ body: "MC\tFixture\tAnswer\tCorrect" });
  });
  await page.goto("/selftest_dependency_fixture/");
  return page.locator(".qti-selftest");
}

const drawingLibrary = `
  function drawQuestion() {
    const canvas = document.querySelector('[aria-label="Question drawing"]');
    canvas.getContext("2d").fillRect(0, 0, 10, 10);
    canvas.dataset.drawn = "yes";
  }
`;

test("question readiness waits for external drawing dependencies, then retries a failed dependency", async ({ page }) => {
  let fail = true;
  await page.route("**/reroll_dependency.js", async (route) => {
    if (fail) {
      await route.abort();
      return;
    }
    await route.fulfill({ contentType: "text/javascript", body: drawingLibrary });
  });
  const host = await dependencyFixture(page);
  await expect(host.locator(".selftest-question-status")).toContainText("Could not load a question script. Try again.");
  await expect(host.getByRole("button", { name: "Retry", exact: true })).toBeEnabled();
  await expect(host.locator("canvas")).not.toHaveAttribute("data-drawn", "yes");

  fail = false;
  await host.getByRole("button", { name: "Retry", exact: true }).click();
  await waitForReady(host);
  await expect(host.locator("canvas")).toHaveAttribute("data-drawn", "yes");
  await host.locator('input[type="radio"]').check();
  await host.getByRole("button", { name: "Check Answer" }).click();
  await expect(host.locator('[id^="result_"]')).toHaveText("CORRECT");
});

test("correct feedback remains while the next question becomes ready, and reroll only replaces its own question", async ({ page }) => {
  const hosts = await lifecycleFixture(page);
  const first = hosts.nth(0);
  const second = hosts.nth(1);
  const third = hosts.nth(2);
  await waitForReady(first);
  await expect(questionId(second)).toHaveCount(0);

  await first.locator('input[type="radio"]').check();
  await first.getByRole("button", { name: "Check Answer" }).click();
  await expect(first.locator('[id^="result_"]')).toHaveText("CORRECT");
  await waitForReady(second);
  await expect(first.locator('[id^="result_"]')).toHaveText("CORRECT");
  await expect(questionId(third)).toHaveCount(0);

  const firstId = await questionId(first).getAttribute("id");
  const secondId = await questionId(second).getAttribute("id");
  await first.getByRole("button", { name: "New version", exact: true }).click();
  await waitForReady(first);
  await expect(questionId(first)).not.toHaveAttribute("id", firstId!);
  await expect(questionId(second)).toHaveAttribute("id", secondId!);
  await expect(first.locator('[id^="result_"]')).toHaveText("");
});

test("advancement waits 500 ms after feedback and a replacement cancels its stale timer", async ({ page }) => {
  await page.clock.install({ time: new Date("2025-01-01T00:00:00Z") });
  const hosts = await lifecycleFixture(page);
  const first = hosts.nth(0);
  const second = hosts.nth(1);
  await waitForReady(first);
  await page.clock.pauseAt(new Date("2025-01-02T00:00:00Z"));

  await first.locator('input[type="radio"]').check();
  await first.getByRole("button", { name: "Check Answer" }).click();
  await expect(first.locator('[id^="result_"]')).toHaveText("CORRECT");
  await waitForReady(second);
  await page.clock.runFor(499);
  await expect(second).not.toBeFocused();
  await page.clock.runFor(1);
  await expect(second).toBeFocused();

  // A manual replacement cancels a previous automatic transition, so an old
  // timer cannot unexpectedly pull a student away from the current question.
  await first.getByRole("button", { name: "New version", exact: true }).click();
  await waitForReady(first);
  await first.locator('input[type="radio"]').check();
  await first.getByRole("button", { name: "Check Answer" }).click();
  await expect(first.locator('[id^="result_"]')).toHaveText("CORRECT");
  await first.getByRole("button", { name: "New version", exact: true }).click();
  await waitForReady(first);
  await first.focus();
  await page.clock.runFor(500);
  await expect(first).toBeFocused();
  await expect(second).not.toBeFocused();
});

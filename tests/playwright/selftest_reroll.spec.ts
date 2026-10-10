// Dynamic self-test contract. Selectors here describe the student-visible
// container contract in selftest_reroll.js: an empty body is populated on
// demand, its header owns the completion badge and practice button, and the
// status region reports readiness. Question IDs belong to QPM html_selftest;
// labels, hint and status belong to selftest_reroll.js prepare()/generate().
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

test("Show another question walks the bank in source order and wraps", async ({ page }) => {
  // A regression here means restoring sequential selection, not changing the expected order.
  await page.route("**/bbq-MATCH-genetic_disorders-questions.txt", async (route) => {
    await route.fulfill({ body: [
      "MC\tFirst bank question\tATP\tCorrect\tADP\tIncorrect",
      "MC\tSecond bank question\tDNA\tCorrect\tRNA\tIncorrect",
      "MC\tThird bank question\tadenine\tCorrect\tcytosine\tIncorrect",
    ].join("\n") });
  });
  await page.goto("/genetics/topic01/");
  const host = page.locator(".qti-selftest[data-bbq]").first();
  await waitForReady(host);
  await expect(host.getByText("First bank question", { exact: true })).toBeVisible();
  for (const prompt of ["Second bank question", "Third bank question", "First bank question"]) {
    await host.getByRole("radio").first().check();
    await host.getByRole("button", { name: "Show another question", exact: true }).click();
    await waitForReady(host);
    await expect(host.getByText(prompt, { exact: true })).toBeVisible();
    await expect(host.locator("input:checked")).toHaveCount(0);
  }
  await host.getByRole("button", { name: "Show another question", exact: true }).click();
  await expect(host.getByText("Second bank question", { exact: true })).toBeVisible();
  await page.reload();
  await waitForReady(host);
  await expect(host.getByText("First bank question", { exact: true })).toBeVisible();
});

test("real WASM installs question styles and loads another question on request", async ({ page }) => {
  const errors: string[] = [];
  const wasmRequests: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (request.url().includes("/qti_wasm/")) {
      wasmRequests.push(request.url());
    }
  });
  await page.goto("/genetics/topic01/");

  const hosts = page.locator(".qti-selftest[data-bbq]");
  await expect(hosts.first()).toBeAttached();
  const first = hosts.first();
  const second = hosts.nth(1);
  await waitForReady(first);
  await expect(page.locator("#qti-selftest-theme")).toHaveCount(1);
  await expect(first.getByRole("button", { name: "Show another question", exact: true }))
    .toHaveCSS("border-top-style", "solid");
  expect(wasmRequests.some((url) => url.endsWith(".wasm"))).toBe(true);

  // A grouped root/theme rule once lost Material's dark background during isolation.
  for (const scheme of ["slate", "default"]) {
    await page.locator(`label[for="__palette_${scheme === "slate" ? 1 : 0}"]`).click();
    await expect(page.locator("body")).toHaveAttribute("data-md-color-scheme", scheme);
    await expect(page.locator("body")).not.toHaveCSS("background-color", "rgba(0, 0, 0, 0)");
    const contrast = await page.locator("body").evaluate((body) => {
      const style = getComputedStyle(body);
      const bg = style.backgroundColor.match(/[\d.]+/g)!.map(Number);
      const fg = style.color.match(/[\d.]+/g)!.map(Number);
      const alpha = fg[3] ?? 1;
      const foreground = fg.slice(0, 3).map((value, index) => value * alpha + bg[index] * (1 - alpha));
      const luminance = (rgb: number[]) => rgb.slice(0, 3).map((value) => value / 255)
        .map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4)
        .reduce((total, value, index) => total + value * [0.2126, 0.7152, 0.0722][index], 0);
      const values = [luminance(foreground), luminance(bg)];
      return (Math.max(...values) + 0.05) / (Math.min(...values) + 0.05);
    });
    expect(contrast).toBeGreaterThanOrEqual(4.5);
  }
  await expect(second.locator(`[id^="${QUESTION_ID_PREFIX}"]`)).toHaveCount(0);
  await expect(second.getByText("Practice question", { exact: true })).toBeVisible();
  await expect(second.getByText("Your question will appear here.", { exact: true })).toBeVisible();
  await expect(second.getByRole("button", { name: "Show practice question", exact: true })).toBeVisible();

  const start = second.getByRole("button", { name: "Show practice question", exact: true });
  await start.focus();
  await page.keyboard.press("Enter");
  await waitForReady(second);
  await expect(second.getByText("Practice question", { exact: true })).toHaveCount(0);
  await expect(second.getByText("Your question will appear here.", { exact: true })).toHaveCount(0);
  await expect(second.getByText("Replaces this question with another from the same set.",
    { exact: true })).toBeVisible();
  await expect(page.locator("#qti-selftest-theme")).toHaveCount(1);
  expect(errors).toEqual([]);
});

test("wide scientific tables scroll locally on mobile without losing answer controls", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  const bank = "bbq-rna_transcribe-FIB-prime-len_9-questions.txt";
  let answer = "";
  // Use the first shipped source record so real WASM renders a reproducible
  // scientific table, without replacing its authored layout or answer key.
  await page.route(`**/${bank}`, async (route) => {
    const response = await route.fetch();
    const record = (await response.text()).trim().split("\n")[0];
    answer = record.split("\t")[2];
    await route.fulfill({ response, body: record });
  });
  await page.goto("/biochemistry/topic11/");
  const host = page.locator(`.qti-selftest[data-bbq="${bank}"]`);
  await host.getByRole("button", { name: "Show practice question", exact: true }).click();
  await waitForReady(host);
  const table = host.getByRole("table");
  const lastCell = table.getByRole("cell").last();
  expect((await table.boundingBox())!.width).toBeGreaterThan((await host.boundingBox())!.width);

  for (const scheme of ["default", "slate"]) {
    if (await page.locator("body").getAttribute("data-md-color-scheme") !== scheme) {
      await page.locator(`label[for="__palette_${scheme === "slate" ? 1 : 0}"]`).click();
    }
    await host.evaluate((element) => { element.scrollLeft = 0; });
    await host.scrollIntoViewIfNeeded();
    await expect(lastCell).not.toBeInViewport({ ratio: 1 });
    // A normal toolbar tab stop must support native keyboard scrolling so the
    // final nucleotide and strand label are reachable without extra controls.
    await host.getByRole("button", { name: "Show another question", exact: true }).focus();
    for (let step = 0; step < 20; step += 1) {
      await page.keyboard.press("ArrowRight");
    }
    await expect(lastCell).toBeInViewport({ ratio: 1 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth))
      .toBeLessThanOrEqual(await page.evaluate(() => document.documentElement.clientWidth));
    expect(await page.evaluate(() => window.scrollX)).toBe(0);
  }

  const reroll = host.getByRole("button", { name: "Show another question", exact: true });
  await page.keyboard.press("Tab");
  await expect(host.getByRole("textbox")).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  await expect(reroll).toBeFocused();
  await expect(reroll).toBeInViewport({ ratio: 1 });
  await host.getByRole("textbox").fill(answer);
  await host.getByRole("button", { name: "Check Answer", exact: true }).click();
  await expect(host.locator('[id^="result_"]')).toContainText("CORRECT");
  // A one-question bank wraps to its only question with fresh answer controls.
  await host.getByRole("button", { name: "Show another question", exact: true }).click();
  await waitForReady(host);
  await expect(host.getByRole("textbox")).toHaveValue("");
  await expect(host.locator('[id^="result_"]')).toBeEmpty();
  await host.getByRole("textbox").fill(answer);
  await host.getByRole("button", { name: "Check Answer", exact: true }).click();
  await expect(host.locator('[id^="result_"]')).toContainText("CORRECT");
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
      <div class="qti-selftest" data-bbq="one.txt"><div class="selftest-reroll-content"></div></div>
      <div class="qti-selftest" data-bbq="two.txt"><div class="selftest-reroll-content"></div></div>
      <div class="qti-selftest" data-bbq="three.txt"><div class="selftest-reroll-content"></div></div>
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
      export function convert(request) {
        if (window.failSelftestConversion) {
          return { status: 'error', error: { message: 'Could not convert question.' } };
        }
        const html = '<html><body><div id="question_html_dependency">' +
          '<p>Practice question ' + (request.shuffleSeed + 1) + '</p>' +
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
      <div class="qti-selftest" data-bbq="dependency.txt"><div class="selftest-reroll-content"></div></div>
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
  await expect(host.getByText("Practice question", { exact: true })).toBeVisible();
  await expect(host.locator("canvas")).not.toHaveAttribute("data-drawn", "yes");

  fail = false;
  await host.getByRole("button", { name: "Retry", exact: true }).click();
  await waitForReady(host);
  await expect(host.getByText("Practice question 1", { exact: true })).toBeVisible();
  await expect(host.locator("canvas")).toHaveAttribute("data-drawn", "yes");
  await host.locator('input[type="radio"]').check();
  await host.getByRole("button", { name: "Check Answer" }).click();
  await expect(host.locator('[id^="result_"]')).toHaveText("CORRECT");

  // A failed conversion retains usable work; Retry must not skip the next question.
  await page.evaluate(() => { Reflect.set(window, "failSelftestConversion", true); });
  await host.getByRole("button", { name: "Show another question", exact: true }).click();
  await expect(host.getByRole("button", { name: "Retry", exact: true })).toBeEnabled();
  await expect(host.locator(".selftest-question-status"))
    .toContainText("Could not convert question.");
  await expect(host.locator("canvas")).toHaveAttribute("data-drawn", "yes");
  await host.getByRole("button", { name: "Check Answer" }).click();
  await expect(host.locator('[id^="result_"]')).toHaveText("CORRECT");
  await page.evaluate(() => { Reflect.set(window, "failSelftestConversion", false); });
  await host.getByRole("button", { name: "Retry", exact: true }).click();
  await waitForReady(host);
  await expect(host.getByText("Practice question 2", { exact: true })).toBeVisible();
});

test("correct feedback remains while the next question becomes ready, and reroll only replaces its own question", async ({ page }) => {
  const hosts = await lifecycleFixture(page);
  const first = hosts.nth(0);
  const second = hosts.nth(1);
  const third = hosts.nth(2);
  await waitForReady(first);
  await expect(questionId(second)).toHaveCount(0);
  await expect(second.getByRole("button", { name: "Show practice question", exact: true }))
    .toBeEnabled();

  let releaseQuestion: () => void = () => {};
  const pendingQuestion = new Promise<void>((resolve) => { releaseQuestion = resolve; });
  await page.route("**/selftest_lifecycle_fixture/two.txt", async (route) => {
    await pendingQuestion;
    await route.fulfill({ body: "MC\tFixture\tAnswer\tCorrect" });
  });

  await first.locator('input[type="radio"]').check();
  await first.getByRole("button", { name: "Check Answer" }).click();
  await expect(first.locator('[id^="result_"]')).toHaveText("CORRECT");
  await expect(second.getByRole("button", { name: "Loading question...", exact: true }))
    .toBeDisabled();
  await expect(second.getByText("Your question will appear here.", { exact: true })).toBeVisible();
  await expect(questionId(second)).toHaveCount(0);
  releaseQuestion();
  await waitForReady(second);
  await expect(second.getByRole("button", { name: "Show another question", exact: true }))
    .toBeEnabled();
  await expect(first.locator('[id^="result_"]')).toHaveText("CORRECT");
  await expect(questionId(third)).toHaveCount(0);

  const firstId = await questionId(first).getAttribute("id");
  const secondId = await questionId(second).getAttribute("id");
  await first.getByRole("button", { name: "Show another question", exact: true }).click();
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
  await first.getByRole("button", { name: "Show another question", exact: true }).click();
  await waitForReady(first);
  await first.locator('input[type="radio"]').check();
  await first.getByRole("button", { name: "Check Answer" }).click();
  await expect(first.locator('[id^="result_"]')).toHaveText("CORRECT");
  await first.getByRole("button", { name: "Show another question", exact: true }).click();
  await waitForReady(first);
  await first.focus();
  await page.clock.runFor(500);
  await expect(first).toBeFocused();
  await expect(second).not.toBeFocused();
});

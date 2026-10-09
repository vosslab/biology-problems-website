// Rendered HTTP checks. Controls: site_docs/question_finder.md:16 and
// site_docs/assets/scripts/question_finder.js:55 (dropdown labels), :101 (counts).
import { test, expect } from "@playwright/test";
import type { Page } from "@playwright/test";

async function openFilter(page: Page, name: string) {
  await page.getByRole("button", { name: "Filter " + name, exact: true }).click();
  return page.getByRole("dialog", { name: "Filter " + name, exact: true });
}

test("Finder filters combine, announce selection, restore, and clear", async ({ page, context }) => {
  const rows = [
    ["Alpha <bank>", "Biology", "Cells", "MC"],
    ["Beta", "Biology", "DNA", "NUM"],
    ["Gamma", "Chemistry", "Cells", "MC"],
    ["Delta", "Chemistry", "DNA", "NUM"],
    ["Epsilon", "Physics", "Cells", "MC"],
    ["Zeta", "Physics", "DNA", "NUM"],
  ].map(([name, subject, topic, type], index) => ({
    id: `${subject}/topic01/bbq-${index}-questions.txt`, name, subject, topic, type,
    type_code: type, type_description: type === "MC" ? "Multiple Choice" : "Numeric",
    url: "../biology/topic01/",
  }));
  await context.route("**/assets/data/question_finder.json", (route) => route.fulfill({ json: rows }));
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/question_finder/");
  await expect(page.getByText("6 matching question sets", { exact: false })).toBeVisible();
  await expect(page.getByRole("link", { name: "Alpha <bank>", exact: true })).toBeVisible();
  await expect(page.locator("#finder-table bank")).toHaveCount(0);

  await page.getByRole("button", { name: "Filter Subject", exact: true }).focus();
  await page.keyboard.press("Enter");
  const subjects = page.getByRole("dialog", { name: "Filter Subject", exact: true });
  await subjects.getByLabel("Search Subject options").fill("bio");
  await subjects.getByRole("button", { name: "Biology", exact: true }).click();
  await expect(subjects.getByRole("button", { name: "Biology", exact: true })).toHaveAttribute("aria-pressed", "true");
  await subjects.getByLabel("Search Subject options").fill("");
  await subjects.getByRole("button", { name: "Chemistry", exact: true }).click();
  await expect(page.getByText("4 matching question sets", { exact: false })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("button", { name: "Filter Subject", exact: true })).toBeFocused();

  const types = await openFilter(page, "Question type");
  await types.getByRole("button", { name: "MC", exact: true }).click();
  await page.keyboard.press("Escape");
  await expect(page.getByText("2 matching question sets", { exact: false })).toBeVisible();
  const topics = await openFilter(page, "Topic");
  await topics.getByRole("button", { name: "Cells", exact: true }).click();
  await page.keyboard.press("Escape");
  await page.reload();
  await expect(page.getByText("2 matching question sets", { exact: false })).toBeVisible();
  await page.getByRole("button", { name: "Remove Subject: Biology filter", exact: true }).click();
  await expect(page.getByText("1 matching question sets", { exact: false })).toBeVisible();
  const restored = await openFilter(page, "Subject");
  await expect(restored.getByRole("button", { name: "Biology", exact: true })).toHaveAttribute("aria-pressed", "false");
  await expect(restored.getByRole("button", { name: "Chemistry", exact: true })).toHaveAttribute("aria-pressed", "true");
  await page.keyboard.press("Escape");

  const freshTab = await context.newPage();
  await freshTab.goto("/question_finder/");
  await expect(freshTab.getByText("6 matching question sets", { exact: false })).toBeVisible();
  await freshTab.close();
  await page.getByRole("button", { name: "Clear all filters" }).click();
  await expect(page.getByText("6 matching question sets", { exact: false })).toBeVisible();
  const names = await openFilter(page, "Name");
  await names.getByLabel("Filter Name", { exact: true }).fill("Alpha");
  await page.keyboard.press("Escape");
  await page.reload();
  await expect(page.getByText("1 matching question sets", { exact: false })).toBeVisible();
  await page.getByRole("button", { name: "Remove Name: Alpha filter", exact: true }).click();
  await page.getByLabel("Search questions", { exact: true }).fill("nothing matches this");
  await expect(page.getByText("No question sets match.", { exact: false })).toBeVisible();
  await page.getByRole("button", { name: "Clear all filters" }).click();
  await expect(page.getByText("6 matching question sets", { exact: false })).toBeVisible();
  expect(errors).toEqual([]);
});

test("Finder loads the shipped catalog and CDN assets, sorts, pages, and links", async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  const requested: string[] = [];
  page.on("request", (request) => {
    if (request.url().startsWith("https://cdn.datatables.net/")) requested.push(request.url());
  });
  await page.goto("/");
  expect(requested).toEqual([]);
  await page.locator("article").getByRole("link", { name: "Find question sets →", exact: true }).click();
  await expect(page.getByLabel("Search questions", { exact: true })).toBeVisible();
  const response = await page.request.get("/assets/data/question_finder.json");
  const rows = await response.json();
  await expect(page.getByText(`${rows.length} matching question sets`, { exact: false })).toBeVisible();
  for (const suffix of ["dataTables.min.js", "dataTables.columnControl.min.js", "dataTables.dataTables.min.css", "columnControl.dataTables.min.css"]) {
    expect(requested.some((url) => url.endsWith(suffix))).toBeTruthy();
  }
  await page.getByRole("columnheader", { name: /^Name/ }).click();
  await expect(page.getByRole("columnheader", { name: /^Name/ })).toHaveAttribute("aria-sort", "ascending");
  await page.getByRole("columnheader", { name: /^Name/ }).click();
  await expect(page.getByRole("columnheader", { name: /^Name/ })).toHaveAttribute("aria-sort", "descending");
  await page.getByRole("link", { name: "Next", exact: true }).click();
  const firstOnPage = await page.locator("#finder-table tbody a").first().innerText();
  await page.reload();
  await expect(page.locator("#finder-table tbody a").first()).toHaveText(firstOnPage);
  await expect(page.getByRole("columnheader", { name: /^Name/ })).toHaveAttribute("aria-sort", "descending");
  await page.getByLabel("Search questions", { exact: true }).fill(rows[0].name);
  const link = page.locator("#finder-table tbody a").first();
  const href = await link.getAttribute("href");
  expect(href).toMatch(/^\.\.\/[a-z0-9_-]+\/[a-z0-9_-]+\/$/);
  await link.click();
  expect(new URL(page.url()).pathname).toBe(href!.slice(2));
  await page.goto("/question_finder/");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => document.body.setAttribute("data-md-color-scheme", "slate"));
  await expect(page.getByLabel("Search questions", { exact: true })).toBeVisible();
  const region = page.getByRole("region", { name: "Question sets table, scroll horizontally on narrow screens" });
  expect(await region.evaluate((node) => node.scrollWidth > node.clientWidth)).toBeTruthy();
  await region.focus();
  await page.keyboard.press("ArrowRight");
  await expect.poll(() => region.evaluate((node) => node.scrollLeft)).toBeGreaterThan(0);
  expect(consoleErrors).toEqual([]);
});

test("Finder recovers from a failed catalog fetch", async ({ page }) => {
  let fail = true;
  await page.route("**/assets/data/question_finder.json", async (route) => {
    if (fail) await route.fulfill({ status: 503, body: "Unavailable" });
    else await route.continue();
  });
  await page.goto("/question_finder/");
  await expect(page.getByRole("status")).toContainText("Question sets could not load");
  await expect(page.locator("article").getByRole("link", { name: "Browse All Questions in the sitemap" })).toBeVisible();
  fail = false;
  await page.getByRole("button", { name: "Retry loading" }).click();
  await expect(page.getByLabel("Search questions", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Retry loading" })).toBeHidden();
});

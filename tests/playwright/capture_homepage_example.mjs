/** Capture the actual table authored in the Medium pedigree self-test.
 * Build and serve the site first, then run:
 * node tests/playwright/capture_homepage_example.mjs http://127.0.0.1:8000
 * Source selector: genetics/topic05/index.md, Medium pedigree heading and details.
 */
import path from "node:path";
import { chromium } from "playwright";
import { REPO_ROOT } from "./repo_root.mjs";

const baseURL = process.argv[2] ?? "http://127.0.0.1:8000";
const browser = await chromium.launch();
try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 900 }, colorScheme: "light", deviceScaleFactor: 2,
  });
  await page.goto(`${baseURL}/genetics/topic05/`, { waitUntil: "networkidle" });
  const example = page.getByRole("heading", {
    name: "Inheritance Patterns from Pedigrees (Medium)", exact: true,
  }).locator("xpath=following-sibling::details[1]");
  await example.locator("summary").click();
  await example.locator("table").first().screenshot({
    path: path.join(REPO_ROOT, "site_docs/assets/images/homepage_pedigree.png"),
  });
} finally {
  await browser.close();
}

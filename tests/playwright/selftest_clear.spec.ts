// Protect clearing and persistent completion through the real QPM lifecycle.
// Host/readiness selectors: selftest_reroll.js prepare(); question controls are
// the public html_selftest output contract, exercised through real WASM.
import { expect, test } from "@playwright/test";

test("Clear Selection clears answers and feedback while retaining completion", async ({ page }) => {
  await page.goto("/biochemistry/topic04/");
  const host = page.locator('.qti-selftest[data-bbq="bbq-alpha_helix_h-bonds-MA-questions.txt"]');
  await host.getByRole("button", { name: "Show practice question", exact: true }).click();
  await expect(host.locator(".selftest-question-status")).toHaveText("Question ready.");
  const badge = host.locator(".selftest-status");
  await expect(badge).toHaveText("Not completed");
  await host.locator('input[data-correct="false"]').first().check();
  await host.getByRole("button", { name: "Check Answer", exact: true }).click();
  await expect(host.locator('[id^="result_"]')).not.toBeEmpty();
  await expect(badge).toHaveText("Not completed");
  await host.getByRole("button", { name: "Clear Selection", exact: true }).click();
  await expect(host.locator("input:checked")).toHaveCount(0);
  await expect(host.locator('[id^="result_"]')).toBeEmpty();
  for (const choice of await host.locator('input[data-correct="true"]').all()) {
    await choice.check();
  }
  await host.getByRole("button", { name: "Check Answer", exact: true }).click();
  await expect(host.locator('[id^="result_"]')).toHaveText("CORRECT");
  await expect(badge).toContainText("Completed");
  await host.getByRole("button", { name: "Clear Selection", exact: true }).click();
  await expect(host.locator("input:checked")).toHaveCount(0);
  await expect(host.locator('[id^="result_"]')).toBeEmpty();
  await expect(badge).toContainText("Completed");
  await host.getByRole("button", { name: "Show another question", exact: true }).click();
  await expect(host.locator(".selftest-question-status")).toHaveText("Question ready.");
  await expect(host.locator('[id^="result_"]')).toBeEmpty();
  await expect(badge).toContainText("Completed");
  await page.reload();
  await expect(host.locator(".selftest-status")).toContainText("Completed");
});

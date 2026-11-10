import { test, expect } from "@playwright/test";

test.describe("Comparison", () => {
  test("shows compare page", async ({ page }) => {
    await page.goto("/compare");
    await expect(page.getByText("Compare Documents")).toBeVisible();
    await expect(page.getByPlaceholder(/Analysis ID/)).toBeVisible();
  });
});

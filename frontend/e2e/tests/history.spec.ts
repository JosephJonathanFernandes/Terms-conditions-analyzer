import { test, expect } from "@playwright/test";

test.describe("History", () => {
  test("shows history page with empty state", async ({ page }) => {
    await page.goto("/history");
    await expect(page.getByText("History")).toBeVisible();
    await expect(page.getByText("No previous analyses yet")).toBeVisible();
  });
});

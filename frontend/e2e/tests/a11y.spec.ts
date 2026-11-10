import { test, expect } from "@playwright/test";

test.describe("Accessibility", () => {
  test("landing page has proper heading structure", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "ClauseClear" })).toBeVisible();
    await expect(page.getByRole("navigation")).toBeVisible();
  });
});

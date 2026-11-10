import { test, expect } from "@playwright/test";

test.describe("Ingestion", () => {
  test("can analyze pasted text and see results", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("ClauseClear")).toBeVisible();

    // Select paste text method
    await page.getByRole("button", { name: /Paste Text/ }).click();

    // Fill text
    await page
      .getByPlaceholder(/Terms & Conditions text here/)
      .fill(
        "We collect your personal data including name and email. We share your data with third parties. Your subscription will renew automatically unless you cancel."
      );

    // Submit
    await page.getByRole("button", { name: /Analyze Text/ }).click();

    // Should redirect to results
    await expect(page).toHaveURL(/\/results\/\d+/);

    // Should see executive summary
    await expect(page.getByText("Executive Summary")).toBeVisible();
  });

  test("SSRF URL is blocked", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: /Website URL/ }).click();
    await page.getByPlaceholder(/example\.com/).fill("http://127.0.0.1/");
    await page.getByRole("button", { name: /Analyze Website/ }).click();

    // Should show error toast
    await expect(page.getByText(/blocked|invalid/i)).toBeVisible();
  });
});

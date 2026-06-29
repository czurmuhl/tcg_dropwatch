import { expect, test } from "@playwright/test"

test("Signals page is accessible", async ({ page }) => {
  await page.goto("/signals")

  await expect(page.getByRole("heading", { name: "Signals" })).toBeVisible()
  await expect(page.getByText("Drop Board")).toBeVisible()
})

test("Watchlist page is accessible", async ({ page }) => {
  await page.goto("/watchlist")

  await expect(page.getByRole("heading", { name: "Watchlist" })).toBeVisible()
  await expect(page.getByText("Alert Rules")).toBeVisible()
})

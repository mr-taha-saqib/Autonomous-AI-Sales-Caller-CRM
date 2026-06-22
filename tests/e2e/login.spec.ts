import { test, expect } from "@playwright/test";

const ADMIN = "admin@algorixe.com";
const PASSWORD = process.env.E2E_PASSWORD || "ChangeMe!123";

test("login redirects to dashboard and shows KPIs", async ({ page }) => {
  await page.goto("/login");
  await page.fill('input[type="email"]', ADMIN);
  await page.fill('input[type="password"]', PASSWORD);
  await page.click('button:has-text("Sign in")');

  await expect(page).toHaveURL("/");
  await expect(page.getByText("Dashboard")).toBeVisible();
  await expect(page.getByText("Total Leads")).toBeVisible();
});

test("can navigate to lead management", async ({ page }) => {
  await page.goto("/login");
  await page.fill('input[type="email"]', ADMIN);
  await page.fill('input[type="password"]', PASSWORD);
  await page.click('button:has-text("Sign in")');
  await page.click('a:has-text("Lead Management")');

  await expect(page).toHaveURL(/\/leads/);
  await expect(page.getByText("Lead Management")).toBeVisible();
});

test("unauthenticated user is redirected to login", async ({ page }) => {
  await page.goto("/leads");
  await expect(page).toHaveURL(/\/login/);
});

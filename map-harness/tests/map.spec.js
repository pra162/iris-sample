const { test, expect } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");

const screenshotsDir = path.join(__dirname, "..", "screenshots");

test.beforeAll(() => {
  fs.mkdirSync(screenshotsDir, { recursive: true });
});

test("captures deterministic before and after first-load behavior", async ({ page }) => {
  await page.goto("/index.html?legacy=1");
  await expect(page.locator("#map")).toHaveAttribute("data-state", "error");
  await expect(page.locator("#map")).toHaveAttribute("data-style-visible", "false");
  await page.screenshot({ path: path.join(screenshotsDir, "before-fix.png"), fullPage: true });

  await page.goto("/index.html");
  await expect(page.locator("#map")).toHaveAttribute("data-state", "ready");
  await expect(page.locator("#map")).toHaveAttribute("data-style-visible", "true");
  await expect(page.locator("#map .fixture.bess")).toHaveCount(2);
  await expect(page.locator("#map .fixture.peatland")).toHaveCount(1);
  await expect(page.getByRole("row", { name: /BESS/ })).toContainText("2026-10-23");
  await expect(page.getByRole("row", { name: /Peatland/ })).toContainText("2026-10-23");
  await expect(page.getByLabel("Map legend")).toBeVisible();
  await expect(page.locator(".attribution")).toContainText("synthetic sample fixtures");
  await page.screenshot({ path: path.join(screenshotsDir, "after-fix.png"), fullPage: true });
});

test("fixture toggles hide and restore their own layers", async ({ page }) => {
  await page.goto("/index.html");
  const bess = page.locator("#map .fixture.bess");
  const peatland = page.locator("#map .fixture.peatland");

  await page.getByRole("checkbox", { name: "BESS" }).uncheck();
  await expect(bess.first()).toBeHidden();
  await expect(peatland).toBeVisible();
  await page.getByRole("checkbox", { name: "BESS" }).check();
  await expect(bess.first()).toBeVisible();

  await page.getByRole("checkbox", { name: "Peatland" }).uncheck();
  await expect(peatland).toBeHidden();
});

test("tile failures recover to fallback and exhausted fallback offers retry", async ({ page }) => {
  await page.goto("/index.html?failTiles=2");
  await expect(page.locator("#map")).toHaveAttribute("data-state", "fallback");
  await expect(page.locator("#map")).toHaveAttribute("data-tile-source", "local-fallback-tiles");
  await expect(page.locator("#map")).toHaveAttribute("data-style-visible", "true");

  await page.goto("/index.html?failTiles=3");
  await expect(page.locator("#map")).toHaveAttribute("data-state", "error");
  await expect(page.locator("#map .map-status-label")).toContainText("Map tiles failed");
  await expect(page.locator("#map")).toHaveAttribute("data-style-visible", "true");
  await page.getByRole("button", { name: "Retry map" }).click();
  await expect(page.locator("#map")).toHaveAttribute("data-state", "ready");
});

test("records three reproducible first-style latency measurements", async ({ page }) => {
  const latencies = [];
  for (let run = 1; run <= 3; run += 1) {
    await page.goto("/index.html?run=" + run);
    await expect(page.locator("#map")).toHaveAttribute("data-style-visible", "true");
    const latency = await page.locator("#map").getAttribute("data-first-style-ms");
    latencies.push(Number(latency));
  }
  const mean = latencies.reduce((sum, latency) => sum + latency, 0) / latencies.length;
  console.log("FIRST-STYLE LATENCY (ms, 3 page-load runs): " + latencies.join(", "));
  console.log("MEAN FIRST-STYLE LATENCY (ms): " + mean.toFixed(2));
  expect(latencies).toHaveLength(3);
  expect(latencies.every(Number.isFinite)).toBe(true);
});

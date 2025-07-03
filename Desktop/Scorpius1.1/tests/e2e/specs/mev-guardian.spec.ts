import { test, expect } from '@playwright/test';

test('wallet scanner demo video', async ({ browser }) => {
  const context = await browser.newContext({
    recordVideo: {
      dir: 'artifacts/videos/',
      size: { width: 1280, height: 720 },
    },
  });

  const page = await context.newPage();
  await page.goto('/');

  await page.fill('input[name="wallet"]', '0x1234567890abcdef...');
  await page.click('button:has-text("Scan Now")');
  await page.waitForResponse(/\/api\/wallet\/check/);
  await expect(page.locator('.result')).toBeVisible();

  // Close context to finish recording
  await context.close();
});

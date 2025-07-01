import { test, expect } from '@playwright/test';
import * as path from 'path';

test.describe('Mempool Monitor Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/mempool/monitor');
  });

  test('mempool heatmap with SSE data', async ({ browser }) => {
    const context = await browser.newContext({
      recordVideo: {
        dir: 'artifacts/videos/',
        size: { width: 1280, height: 720 },
      },
    });
    
    const page = await context.newPage();
    await page.goto('/mempool/monitor');
    
    // Wait for the mempool monitor page to load
    await page.waitForLoadState('networkidle');
    
    // Mock SSE endpoint to inject test data
    await page.route('**/api/mempool/stream', async route => {
      const mockData = `data: ${JSON.stringify({
        timestamp: Date.now(),
        transactions: Array.from({ length: 50 }, (_, i) => ({
          hash: `0x${i.toString(16).padStart(64, '0')}`,
          gasPrice: 250000000000 + Math.random() * 150000000000, // 250-400 gwei
          value: Math.random() * 1000,
          from: `0x${Math.random().toString(16).substr(2, 40)}`,
          to: `0x${Math.random().toString(16).substr(2, 40)}`,
          priority: Math.random() > 0.7 ? 'high' : 'medium'
        }))
      })}\n\n`;
      
      await route.fulfill({
        status: 200,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
        body: mockData,
      });
    });
    
    // Wait for heatmap to load and display transactions
    await page.waitForSelector('.heatmap-container', { timeout: 10000 });
    
    // Count transaction dots on heatmap
    const transactionDots = page.locator('.transaction-dot');
    const dotCount = await transactionDots.count();
    expect(dotCount).toBeGreaterThanOrEqual(50);
    
    // Test tooltip functionality - hover over a high-value transaction
    const highValueDot = page.locator('.transaction-dot.high-priority').first();
    await highValueDot.hover();
    
    // Assert tooltip shows gas price >= 300 gwei
    const tooltip = page.locator('.tooltip');
    await expect(tooltip).toBeVisible();
    
    const gasPriceText = await tooltip.locator('.gas-price').textContent();
    const gasPriceMatch = gasPriceText?.match(/(\d+(\.\d+)?)\s*gwei/i);
    
    if (gasPriceMatch) {
      const gasPrice = parseFloat(gasPriceMatch[1]);
      expect(gasPrice).toBeGreaterThanOrEqual(300);
      console.log(`Verified gas price: ${gasPrice} gwei`);
    }
    
    // Record 3 seconds of heatmap activity
    await page.waitForTimeout(3000);
    
    // Take screenshot of active heatmap
    await page.screenshot({ 
      path: path.join(__dirname, '../artifacts/tests/mempool-heatmap.png'),
      fullPage: true 
    });
    
    // Verify real-time updates by checking timestamp changes
    const initialTimestamp = await page.locator('.last-update').textContent();
    await page.waitForTimeout(2000);
    const updatedTimestamp = await page.locator('.last-update').textContent();
    
    expect(updatedTimestamp).not.toBe(initialTimestamp);
    console.log('Verified real-time updates are working');
    
    // Close context to finish video recording
    await context.close();
  });
  
  test('mempool filter and search functionality', async ({ page }) => {
    // Navigate to mempool monitor
    await page.click('text=Mempool');
    
    // Wait for initial load
    await page.waitForSelector('.heatmap-container');
    
    // Test gas price filter
    await page.fill('input[name="minGasPrice"]', '300');
    await page.click('button:has-text("Apply Filter")');
    
    // Verify filtered results
    const filteredDots = page.locator('.transaction-dot');
    const filteredCount = await filteredDots.count();
    expect(filteredCount).toBeLessThan(50);
    
    // Test address search
    await page.fill('input[name="searchAddress"]', '0x123');
    await page.keyboard.press('Enter');
    
    // Verify search highlighting
    await expect(page.locator('.highlighted-transaction')).toBeVisible();
    
    // Test value range filter
    await page.selectOption('select[name="valueRange"]', 'high');
    await page.click('button:has-text("Apply Filter")');
    
    // Take screenshot of filtered view
    await page.screenshot({ 
      path: path.join(__dirname, '../artifacts/tests/mempool-filtered.png'),
      fullPage: true 
    });
    
    // Clear filters
    await page.click('button:has-text("Clear Filters")');
    
    // Verify all transactions return
    const allTransactions = await page.locator('.transaction-dot').count();
    expect(allTransactions).toBeGreaterThan(40);
  });
});

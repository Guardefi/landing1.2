import { test, expect } from '@playwright/test';
import * as crypto from 'crypto';
import * as fs from 'fs';
import * as path from 'path';

test.describe('Enterprise Reporting Engine Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('enterprise reporting PDF generation', async ({ page }) => {
    // Navigate to reports section
    await page.click('text=Reports');
    
    // Select a scan ID from dropdown
    await page.selectOption('select[name="scanId"]', { label: 'Scan #12345' });
    
    // Click generate PDF button
    const downloadPromise = page.waitForEvent('download');
    await page.click('button:has-text("Generate PDF")');
    
    // Wait for download to start
    const download = await downloadPromise;
    
    // Assert download was initiated
    expect(download.suggestedFilename()).toMatch(/report.*\.pdf$/);
    
    // Save the downloaded file
    const artifactsDir = path.join(__dirname, '../artifacts/tests');
    const downloadPath = path.join(artifactsDir, 'enterprise-report.pdf');
    await download.saveAs(downloadPath);
    
    // Check file exists and has reasonable size
    const stats = fs.statSync(downloadPath);
    expect(stats.size).toBeGreaterThan(1000); // At least 1KB
    
    // Calculate MD5 hash for verification
    const fileBuffer = fs.readFileSync(downloadPath);
    const md5Hash = crypto.createHash('md5').update(fileBuffer).digest('hex');
    
    console.log(`PDF Report Details:
      File Size: ${stats.size} bytes
      MD5 Hash: ${md5Hash}
      Download Path: ${downloadPath}`);
    
    // Take screenshot of reports page
    await page.screenshot({ 
      path: path.join(artifactsDir, 'reporting-engine-success.png'),
      fullPage: true 
    });
    
    // Verify success message appears
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toHaveText(/Report generated successfully/);
  });
  
  test('report generation with filters', async ({ page }) => {
    // Navigate to reports section
    await page.click('text=Reports');
    
    // Apply date filter
    await page.fill('input[name="startDate"]', '2024-01-01');
    await page.fill('input[name="endDate"]', '2024-12-31');
    
    // Select vulnerability severity filter
    await page.selectOption('select[name="severity"]', 'high');
    
    // Select scan type filter
    await page.selectOption('select[name="scanType"]', 'wallet');
    
    // Generate filtered report
    const downloadPromise = page.waitForEvent('download');
    await page.click('button:has-text("Generate Filtered Report")');
    
    const download = await downloadPromise;
    
    // Save filtered report
    const artifactsDir = path.join(__dirname, '../artifacts/tests');
    const filteredReportPath = path.join(artifactsDir, 'filtered-report.pdf');
    await download.saveAs(filteredReportPath);
    
    // Verify filtered report metadata
    const stats = fs.statSync(filteredReportPath);
    expect(stats.size).toBeGreaterThan(500);
    
    console.log(`Filtered Report Size: ${stats.size} bytes`);
    
    // Take screenshot showing applied filters
    await page.screenshot({ 
      path: path.join(artifactsDir, 'reporting-with-filters.png'),
      fullPage: true 
    });
  });
});

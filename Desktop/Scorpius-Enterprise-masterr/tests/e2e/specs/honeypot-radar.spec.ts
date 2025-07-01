import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

interface HoneypotAssessResponse {
  success: boolean;
  request_id: string;
  contract_address: string;
  chain_id: number;
  is_honeypot: boolean;
  confidence: number;
  honeypot_type?: string;
  risk_factors: string[];
  liquidity_check: Record<string, any>;
  simulation_results: Record<string, any>;
  scan_timestamp: number;
  processing_time_ms: number;
  // Additional fields for compatibility
  honeypot?: boolean;
  riskScore?: number;
}

test.describe('Honeypot Radar Testing', () => {
  const HONEYPOT_TOKEN = '0xH0NEY1234567890abcdef1234567890abcdef0dead';
  const ARTIFACTS_DIR = path.join(__dirname, '..', '..', '..', 'artifacts', 'tests');

  test.beforeEach(async ({ page }) => {
    // Navigate to the honeypot page
    await page.goto('/honeypot');
    await page.waitForLoadState('networkidle');
    
    // Ensure the honeypot interface is visible
    await expect(page.getByText(/honeypot|radar|detection/i).first()).toBeVisible();
  });

  test('should detect honeypot token and display warning', async ({ page }) => {
    console.log('🍯 Starting honeypot detection test...');

    // Step 1: Find the token address input field
    const tokenInput = page.locator('input[type="text"]').filter({
      hasText: ''
    }).or(
      page.locator('input[placeholder*="token"]')
    ).or(
      page.locator('input[placeholder*="contract"]')
    ).or(
      page.locator('input[placeholder*="address"]')
    ).or(
      page.locator('input[name*="token"]')
    ).or(
      page.locator('input[id*="token"]')
    ).first();

    await expect(tokenInput).toBeVisible();
    await expect(tokenInput).toBeEnabled();

    // Step 2: Input the honeypot token address
    console.log(`📝 Entering token address: ${HONEYPOT_TOKEN}`);
    await tokenInput.clear();
    await tokenInput.fill(HONEYPOT_TOKEN);
    await expect(tokenInput).toHaveValue(HONEYPOT_TOKEN);

    // Step 3: Find and click "Analyze" button
    const analyzeButton = page.locator('button').filter({
      hasText: /analyze|check|scan|detect/i
    }).first();

    await expect(analyzeButton).toBeVisible();
    await expect(analyzeButton).toBeEnabled();

    // Set up API response listener
    let apiResponse: HoneypotAssessResponse | null = null;

    page.on('response', async (response) => {
      const url = response.url();
      
      if (url.includes('/api/honeypot/assess')) {
        console.log(`🌐 API Response received from: ${url}`);
        console.log(`📊 Status: ${response.status()}`);
        
        if (response.status() === 200) {
          try {
            const responseData = await response.json();
            apiResponse = responseData as HoneypotAssessResponse;
            console.log('✅ API response parsed successfully');
            console.log(`🍯 Is Honeypot: ${apiResponse.is_honeypot}`);
            console.log(`📈 Confidence: ${apiResponse.confidence}`);
          } catch (error) {
            console.error('❌ Failed to parse API response:', error);
          }
        }
      }
    });

    // Step 4: Click analyze button
    console.log('🚀 Starting honeypot analysis...');
    await analyzeButton.click();

    // Step 5: Wait for analysis completion
    await page.waitForTimeout(3000);

    // Step 6: Validate API response structure
    expect(apiResponse).not.toBeNull();
    expect(apiResponse!.success).toBe(true);
    expect(apiResponse!.contract_address.toLowerCase()).toBe(HONEYPOT_TOKEN.toLowerCase());

    // Step 7: Assert JSON contains required fields
    console.log('🔍 Validating honeypot detection results...');
    
    // Check for honeypot detection (either format)
    const isHoneypot = apiResponse!.is_honeypot || apiResponse!.honeypot || false;
    expect(isHoneypot).toBe(true);
    console.log(`✅ Honeypot detected: ${isHoneypot}`);

    // Check risk score > 80 (either field name)
    const riskScore = apiResponse!.confidence * 100 || apiResponse!.riskScore || 0;
    expect(riskScore).toBeGreaterThan(80);
    console.log(`✅ Risk score: ${riskScore} (above 80 threshold)`);

    // Validate response structure
    expect(apiResponse!.risk_factors).toBeDefined();
    expect(Array.isArray(apiResponse!.risk_factors)).toBe(true);
    expect(apiResponse!.liquidity_check).toBeDefined();
    expect(apiResponse!.simulation_results).toBeDefined();

    // Step 8: Verify red warning badge in UI
    console.log('🔍 Looking for warning UI elements...');
    
    // Look for red warning indicators
    const warningElements = [
      page.locator('[class*="red"]').filter({ hasText: /honeypot|warning|danger/i }),
      page.locator('[class*="danger"]').filter({ hasText: /honeypot|likely/i }),
      page.locator('[class*="warning"]').filter({ hasText: /honeypot/i }),
      page.locator('*').filter({ hasText: /likely honeypot/i }),
      page.locator('[style*="red"], [style*="#ff"], [style*="danger"]').filter({ hasText: /honeypot/i })
    ];

    let warningFound = false;
    for (const element of warningElements) {
      try {
        if (await element.count() > 0 && await element.first().isVisible()) {
          console.log('✅ Found red warning badge with "Likely Honeypot" text');
          warningFound = true;
          break;
        }
      } catch (error) {
        // Continue checking other elements
      }
    }

    // Also check page content for warning text
    const pageContent = await page.textContent('body');
    const hasHoneypotWarning = pageContent!.toLowerCase().includes('honeypot') && 
                              (pageContent!.toLowerCase().includes('likely') || 
                               pageContent!.toLowerCase().includes('warning') ||
                               pageContent!.toLowerCase().includes('danger'));

    if (!warningFound && hasHoneypotWarning) {
      console.log('✅ Found honeypot warning text in page content');
      warningFound = true;
    }

    expect(warningFound).toBe(true);

    // Step 9: Store HTML snapshot
    const htmlSnapshotPath = path.join(ARTIFACTS_DIR, 'honeypot_snapshot.html');
    const htmlContent = await page.content();
    fs.writeFileSync(htmlSnapshotPath, htmlContent);
    console.log(`💾 Saved HTML snapshot to: ${htmlSnapshotPath}`);

    // Step 10: Take additional screenshot for verification
    const screenshotPath = path.join(ARTIFACTS_DIR, 'honeypot_ui_result.png');
    await page.screenshot({
      path: screenshotPath,
      fullPage: true,
      animations: 'disabled'
    });
    console.log(`📸 Saved screenshot to: ${screenshotPath}`);

    // Final validation
    console.log('✅ Honeypot detection test completed!');
    console.log(`📊 Summary:`);
    console.log(`   - Token: ${HONEYPOT_TOKEN}`);
    console.log(`   - Is Honeypot: ${isHoneypot}`);
    console.log(`   - Risk Score: ${riskScore}`);
    console.log(`   - Confidence: ${apiResponse!.confidence}`);
    console.log(`   - Risk Factors: ${apiResponse!.risk_factors.length}`);
  });

  test('should handle legitimate token correctly', async ({ page }) => {
    console.log('🧪 Testing legitimate token detection...');

    // Test with a legitimate-looking token (no "honey" pattern)
    const legitimateToken = '0x1234567890abcdef1234567890abcdef12345678';
    
    const tokenInput = page.locator('input[type="text"]').first();
    await tokenInput.fill(legitimateToken);
    
    const analyzeButton = page.locator('button').filter({
      hasText: /analyze|check|scan|detect/i
    }).first();
    
    let apiResponse: HoneypotAssessResponse | null = null;
    page.on('response', async (response) => {
      if (response.url().includes('/api/honeypot/assess')) {
        if (response.status() === 200) {
          try {
            const responseData = await response.json();
            apiResponse = responseData as HoneypotAssessResponse;
          } catch (error) {
            console.error('Failed to parse response:', error);
          }
        }
      }
    });
    
    await analyzeButton.click();
    await page.waitForTimeout(3000);
    
    if (apiResponse) {
      const isHoneypot = apiResponse.is_honeypot || (apiResponse as any).honeypot || false;
      console.log(`✅ Legitimate token result: ${!isHoneypot ? 'Safe' : 'Flagged'}`);
    } else {
      console.log('⚠️ No API response received for legitimate token test');
    }
  });

  test('should handle invalid token address', async ({ page }) => {
    console.log('🧪 Testing invalid token address handling...');

    const invalidToken = '0xinvalid';
    
    const tokenInput = page.locator('input[type="text"]').first();
    await tokenInput.fill(invalidToken);
    
    const analyzeButton = page.locator('button').filter({
      hasText: /analyze|check|scan|detect/i
    }).first();
    
    let errorResponse = false;
    page.on('response', async (response) => {
      if (response.url().includes('/api/honeypot/assess')) {
        if (response.status() >= 400) {
          errorResponse = true;
          console.log(`⚠️ Expected error response: ${response.status()}`);
        }
      }
    });
    
    await analyzeButton.click();
    await page.waitForTimeout(3000);
    
    const pageContent = await page.textContent('body');
    const hasErrorIndicator = pageContent!.toLowerCase().includes('error') || 
                             pageContent!.toLowerCase().includes('invalid') ||
                             errorResponse;
    
    console.log(hasErrorIndicator ? '✅ Error handling works correctly' : '⚠️ No explicit error handling detected');
  });
});

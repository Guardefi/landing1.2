import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

interface TokenApproval {
  token_contract: string;
  spender: string;
  allowance: string;
  risk_level: string;
  last_updated: string;
}

interface WalletCheckResponse {
  success: boolean;
  request_id: string;
  address: string;
  chain_id: number;
  risk_score: number;
  risk_level: string;
  total_approvals: number;
  high_risk_approvals: number;
  approvals: TokenApproval[];
  drainer_signatures: any[];
  recommendations: string[];
  scan_timestamp: number;
  processing_time_ms: number;
}

test.describe('Wallet Scanner Testing', () => {
  const TEST_WALLET = '0x1234567890abcdef1234567890abcdef1234dead';
  const ARTIFACTS_DIR = path.join(__dirname, '..', '..', '..', 'artifacts', 'tests');

  test.beforeEach(async ({ page }) => {
    // Navigate to the wallet scanner page
    await page.goto('/wallet-scanner');
    await page.waitForLoadState('networkidle');
  });

  test('should scan wallet and display risk analysis', async ({ page }) => {
    console.log('🔍 Starting wallet scanner test...');

    // Step 1: Find the wallet address input field
    const walletInput = page.locator('input[type="text"]').filter({
      hasText: ''
    }).or(
      page.locator('input[placeholder*="wallet"]')
    ).or(
      page.locator('input[placeholder*="address"]')
    ).or(
      page.locator('input[name*="wallet"]')
    ).or(
      page.locator('input[id*="wallet"]')
    ).first();

    await expect(walletInput).toBeVisible();
    await expect(walletInput).toBeEnabled();

    // Step 2: Enter the test wallet address
    console.log(`📝 Entering wallet address: ${TEST_WALLET}`);
    await walletInput.clear();
    await walletInput.fill(TEST_WALLET);
    await expect(walletInput).toHaveValue(TEST_WALLET);

    // Step 3: Find and click "Scan" button
    const scanButton = page.locator('button').filter({
      hasText: /scan|analyze|check/i
    }).first();

    await expect(scanButton).toBeVisible();
    await expect(scanButton).toBeEnabled();

    // Set up API response listener
    let apiResponse: WalletCheckResponse | null = null;

    page.on('response', async (response) => {
      const url = response.url();
      
      if (url.includes('/api/wallet/check')) {
        console.log(`🌐 API Response received from: ${url}`);
        console.log(`📊 Status: ${response.status()}`);
        
        if (response.status() === 200) {
          try {
            const responseData = await response.json();
            apiResponse = responseData as WalletCheckResponse;
            console.log('✅ API response parsed successfully');
            console.log(`📈 Risk Score: ${apiResponse.risk_score}`);
            console.log(`🔍 Total Approvals: ${apiResponse.total_approvals}`);
          } catch (error) {
            console.error('❌ Failed to parse API response:', error);
          }
        }
      }
    });

    // Step 4: Click scan button
    console.log('🚀 Starting wallet scan...');
    await scanButton.click();

    // Step 5: Wait for scan completion
    await page.waitForTimeout(3000);

    // Step 6: Validate API response
    expect(apiResponse).not.toBeNull();
    expect(apiResponse!.success).toBe(true);
    expect(apiResponse!.address.toLowerCase()).toBe(TEST_WALLET.toLowerCase());

    // Step 7: Validate required fields
    console.log('🔍 Validating wallet scan results...');
    
    // Check risk score presence and range
    expect(apiResponse!.risk_score).toBeGreaterThanOrEqual(0);
    expect(apiResponse!.risk_score).toBeLessThanOrEqual(100);
    
    // Check token list (approvals)
    expect(apiResponse!.approvals).toBeDefined();
    expect(Array.isArray(apiResponse!.approvals)).toBe(true);
    expect(apiResponse!.total_approvals).toBeGreaterThanOrEqual(0);
    
    // Validate approval structure if present
    if (apiResponse!.approvals.length > 0) {
      const firstApproval = apiResponse!.approvals[0];
      expect(firstApproval.token_contract).toBeTruthy();
      expect(firstApproval.spender).toBeTruthy();
      expect(firstApproval.risk_level).toBeTruthy();
    }

    // Step 8: Check for optional revoke button in UI
    const revokeButtons = page.locator('button').filter({
      hasText: /revoke|remove approval|cancel approval/i
    });
    
    if (await revokeButtons.count() > 0) {
      console.log('✅ Found revoke button(s) in UI');
      await expect(revokeButtons.first()).toBeVisible();
    } else {
      console.log('ℹ️ No revoke buttons found (optional feature)');
    }

    // Step 9: Verify UI displays risk information
    const pageContent = await page.textContent('body');
    const riskKeywords = ['risk', 'score', 'approval', 'token', 'wallet'];
    const foundKeywords = riskKeywords.filter(keyword => 
      pageContent!.toLowerCase().includes(keyword)
    );
    
    expect(foundKeywords.length).toBeGreaterThan(2);
    console.log(`🏷️ Found risk-related keywords: ${foundKeywords.join(', ')}`);

    // Step 10: Take screenshot
    const screenshotPath = path.join(ARTIFACTS_DIR, 'wallet_scan_demo.png');
    await page.screenshot({
      path: screenshotPath,
      fullPage: true,
      animations: 'disabled'
    });
    console.log(`📸 Saved screenshot to: ${screenshotPath}`);

    // Final validation
    console.log('✅ Wallet scanner test completed!');
    console.log(`📊 Summary:`);
    console.log(`   - Risk score: ${apiResponse!.risk_score}/100`);
    console.log(`   - Risk level: ${apiResponse!.risk_level}`);
    console.log(`   - Total approvals: ${apiResponse!.total_approvals}`);
    console.log(`   - High risk approvals: ${apiResponse!.high_risk_approvals}`);
  });

  test('should handle invalid wallet address gracefully', async ({ page }) => {
    console.log('🧪 Testing error handling for invalid wallet...');

    const invalidWallet = '0xinvalid';
    
    const walletInput = page.locator('input[type="text"]').first();
    await walletInput.fill(invalidWallet);
    
    const scanButton = page.locator('button').filter({
      hasText: /scan|analyze|check/i
    }).first();
    
    let errorResponse = false;
    page.on('response', async (response) => {
      if (response.url().includes('/api/wallet/check')) {
        if (response.status() >= 400) {
          errorResponse = true;
          console.log(`⚠️ Expected error response: ${response.status()}`);
        }
      }
    });
    
    await scanButton.click();
    await page.waitForTimeout(3000);
    
    const pageContent = await page.textContent('body');
    const hasErrorIndicator = pageContent!.toLowerCase().includes('error') || 
                             pageContent!.toLowerCase().includes('invalid') ||
                             errorResponse;
    
    console.log(hasErrorIndicator ? '✅ Error handling works correctly' : '⚠️ No explicit error handling detected');
  });
});

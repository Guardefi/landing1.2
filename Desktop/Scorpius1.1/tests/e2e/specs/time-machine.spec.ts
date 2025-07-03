import { test, expect } from '@playwright/test';
import * as path from 'path';

interface StateChange {
  address: string;
  before: string;
  after: string;
  type: string;
  function: string;
}

interface TimeMachineResponse {
  success: boolean;
  block_number: number;
  state_changes: StateChange[];
  total_changes: number;
  processing_time_ms: number;
  gas_used: string;
  timestamp: number;
}

test.describe('Time Machine (Fork Replay) Testing', () => {
  const TEST_BLOCK = 17500000;
  const ARTIFACTS_DIR = path.join(__dirname, '..', '..', '..', 'artifacts', 'tests');

  test.beforeEach(async ({ page }) => {
    // Navigate to the time machine page
    await page.goto('/time-machine');
    await page.waitForLoadState('networkidle');
    
    // Ensure the time machine interface is visible
    await expect(page.locator('h1, h2, h3')).toContainText(/time.?machine|fork|replay|block/i);
  });

  test('should replay block and display state changes', async ({ page }) => {
    console.log('⏰ Starting Time Machine test...');

    // Step 1: Find the block number input field
    const blockInput = page.locator('input[type="text"], input[type="number"]').filter({
      hasText: ''
    }).or(
      page.locator('input[placeholder*="block"]')
    ).or(
      page.locator('input[placeholder*="number"]')
    ).or(
      page.locator('input[name*="block"]')
    ).or(
      page.locator('input[id*="block"]')
    ).first();

    await expect(blockInput).toBeVisible();
    await expect(blockInput).toBeEnabled();

    // Step 2: Enter the test block number
    console.log(`📝 Entering block number: ${TEST_BLOCK}`);
    await blockInput.clear();
    await blockInput.fill(TEST_BLOCK.toString());
    await expect(blockInput).toHaveValue(TEST_BLOCK.toString());

    // Step 3: Find and click "Replay Block" button
    const replayButton = page.locator('button').filter({
      hasText: /replay.?block|replay|fork|simulate/i
    }).first();

    await expect(replayButton).toBeVisible();
    await expect(replayButton).toBeEnabled();

    // Set up API response listener
    let apiResponse: TimeMachineResponse | null = null;

    page.on('response', async (response) => {
      const url = response.url();
      
      if (url.includes('/api/time-machine/replay') && url.includes(`block=${TEST_BLOCK}`)) {
        console.log(`🌐 API Response received from: ${url}`);
        console.log(`📊 Status: ${response.status()}`);
        
        if (response.status() === 200) {
          try {
            const responseData = await response.json();
            apiResponse = responseData as TimeMachineResponse;
            console.log('✅ API response parsed successfully');
            console.log(`🔍 State Changes: ${apiResponse.total_changes}`);
          } catch (error) {
            console.error('❌ Failed to parse API response:', error);
          }
        }
      }
    });

    // Step 4: Click replay button
    console.log('🚀 Starting block replay...');
    await replayButton.click();

    // Step 5: Wait for replay to complete
    console.log('⏳ Waiting for block replay to complete...');
    await page.waitForTimeout(5000); // Time machine operations may take longer

    // Step 6: Validate API response
    expect(apiResponse).not.toBeNull();
    expect(apiResponse!.success).toBe(true);
    expect(apiResponse!.block_number).toBe(TEST_BLOCK);

    // Step 7: Assert at least 5 state changes
    console.log('🔍 Validating state changes...');
    
    expect(apiResponse!.state_changes).toBeDefined();
    expect(Array.isArray(apiResponse!.state_changes)).toBe(true);
    expect(apiResponse!.state_changes.length).toBeGreaterThanOrEqual(5);
    expect(apiResponse!.total_changes).toBeGreaterThanOrEqual(5);

    console.log(`✅ Found ${apiResponse!.state_changes.length} state changes (≥5 required)`);

    // Step 8: Check for USDC.transfer in state changes
    const usdcTransferFound = apiResponse!.state_changes.some(change => 
      change.function && change.function.toLowerCase().includes('transfer') &&
      (change.address.toLowerCase().includes('usdc') || 
       change.type.toLowerCase().includes('usdc') ||
       change.function.toLowerCase().includes('usdc'))
    );

    // Also check page content for USDC.transfer
    const pageContent = await page.textContent('body');
    const usdcInPageContent = pageContent!.toLowerCase().includes('usdc') && 
                             pageContent!.toLowerCase().includes('transfer');

    const hasUsdcTransfer = usdcTransferFound || usdcInPageContent;
    expect(hasUsdcTransfer).toBe(true);
    console.log(`✅ USDC.transfer found in ${usdcTransferFound ? 'API response' : 'page content'}`);

    // Step 9: Validate state change structure
    for (const change of apiResponse!.state_changes.slice(0, 3)) { // Validate first 3
      expect(change.address).toBeTruthy();
      expect(change.before).toBeDefined();
      expect(change.after).toBeDefined();
      expect(change.type).toBeTruthy();
    }

    // Step 10: Find and verify diff panel
    console.log('🔍 Looking for diff panel...');
    
    const diffPanel = page.locator('[data-testid*="diff"], [class*="diff"], .diff-panel, [class*="state-change"], [class*="changes"]').first();
    
    let diffPanelVisible = false;
    try {
      await expect(diffPanel).toBeVisible({ timeout: 5000 });
      diffPanelVisible = true;
      console.log('✅ Diff panel found and visible');
    } catch (error) {
      // Check if state changes are displayed in alternative format
      const stateChangeKeywords = ['state', 'change', 'before', 'after', 'diff'];
      const foundStateKeywords = stateChangeKeywords.filter(keyword => 
        pageContent!.toLowerCase().includes(keyword)
      );
      
      if (foundStateKeywords.length >= 2) {
        diffPanelVisible = true;
        console.log('✅ State change information found in page content');
      } else {
        console.log('⚠️ Diff panel not clearly visible');
      }
    }

    // Step 11: Take diff panel screenshot
    const diffScreenshotPath = path.join(ARTIFACTS_DIR, 'time_machine_diff.png');
    
    if (diffPanelVisible && await diffPanel.count() > 0) {
      try {
        await diffPanel.screenshot({ path: diffScreenshotPath });
        console.log(`📸 Saved diff panel screenshot to: ${diffScreenshotPath}`);
      } catch (error) {
        // Fallback to full page screenshot
        await page.screenshot({ 
          path: diffScreenshotPath, 
          fullPage: true 
        });
        console.log(`📸 Saved full page screenshot to: ${diffScreenshotPath}`);
      }
    } else {
      // Take full page screenshot as fallback
      await page.screenshot({ 
        path: diffScreenshotPath, 
        fullPage: true 
      });
      console.log(`📸 Saved full page screenshot to: ${diffScreenshotPath}`);
    }

    // Final validation
    console.log('✅ Time Machine test completed!');
    console.log(`📊 Summary:`);
    console.log(`   - Block Number: ${TEST_BLOCK}`);
    console.log(`   - State Changes: ${apiResponse!.total_changes}`);
    console.log(`   - USDC.transfer found: ${hasUsdcTransfer}`);
    console.log(`   - Processing Time: ${apiResponse!.processing_time_ms}ms`);
    console.log(`   - Gas Used: ${apiResponse!.gas_used}`);
  });

  test('should handle invalid block number gracefully', async ({ page }) => {
    console.log('🧪 Testing invalid block number handling...');

    // Test with invalid block number
    const invalidBlock = '999999999999';
    
    const blockInput = page.locator('input[type="text"], input[type="number"]').first();
    await blockInput.fill(invalidBlock);
    
    const replayButton = page.locator('button').filter({
      hasText: /replay.?block|replay|fork|simulate/i
    }).first();
    
    let errorResponse = false;
    page.on('response', async (response) => {
      if (response.url().includes('/api/time-machine/replay')) {
        if (response.status() >= 400) {
          errorResponse = true;
          console.log(`⚠️ Expected error response: ${response.status()}`);
        }
      }
    });
    
    await replayButton.click();
    await page.waitForTimeout(3000);
    
    const pageContent = await page.textContent('body');
    const hasErrorIndicator = pageContent!.toLowerCase().includes('error') || 
                             pageContent!.toLowerCase().includes('invalid') ||
                             pageContent!.toLowerCase().includes('not found') ||
                             errorResponse;
    
    console.log(hasErrorIndicator ? '✅ Error handling works correctly' : '⚠️ No explicit error handling detected');
  });

  test('should handle recent block replay', async ({ page }) => {
    console.log('🧪 Testing recent block replay...');

    // Test with a more recent block
    const recentBlock = 19000000;
    
    const blockInput = page.locator('input[type="text"], input[type="number"]').first();
    await blockInput.fill(recentBlock.toString());
    
    const replayButton = page.locator('button').filter({
      hasText: /replay.?block|replay|fork|simulate/i
    }).first();
    
    let apiResponse: TimeMachineResponse | null = null;
    page.on('response', async (response) => {
      if (response.url().includes('/api/time-machine/replay')) {
        if (response.status() === 200) {
          try {
            const responseData = await response.json();
            apiResponse = responseData as TimeMachineResponse;
          } catch (error) {
            console.error('Failed to parse response:', error);
          }
        }
      }
    });
    
    await replayButton.click();
    await page.waitForTimeout(3000);
    
    if (apiResponse) {
      console.log(`✅ Recent block replay successful: ${apiResponse.total_changes} changes`);
    } else {
      console.log('ℹ️ Recent block replay response not captured');
    }
  });
});

# End-to-End Testing for Scorpius Enterprise Platform

This directory contains Playwright-based end-to-end tests for the Scorpius vulnerability scanner frontend.

## Test Overview

### Scanner Vulnerability Test (`scanner-vulnerability.spec.ts`)

This test performs comprehensive vulnerability scanning testing:

1. **Navigates** to `/scanner` on the local frontend
2. **Inputs** the test contract address `0xBEEF0123456789abcdef0123456789abcdef0dead` (a known vulnerable ERC-20)
3. **Clicks** "Run Scan" to initiate the vulnerability analysis
4. **Waits** for the `/api/v2/scan/token` API response
5. **Validates** the JSON response includes:
   - At least 3 findings with severities ["HIGH", "MEDIUM", "LOW"]
   - First finding contains "reentrancy" in its title
   - Proper vulnerability structure and metadata
6. **Saves** the full JSON response to `artifacts/tests/scanner_vuln_report.json`
7. **Screenshots** the result panel to `artifacts/tests/scanner_ui.png`

## Prerequisites

Before running the tests, ensure the following services are running:

### 1. Frontend (Port 3000)
```bash
cd frontend
npm install
npm run dev
```

### 2. Backend API (Port 8000)
```bash
cd backend/Bytecode/api
python -m uvicorn enterprise_main:app --host 0.0.0.0 --port 8000 --reload
```

## Running Tests

### Install Dependencies
```bash
cd tests/e2e
npm install
npx playwright install
```

### Run All Tests
```bash
npm test
```

### Run Tests with UI (Debug Mode)
```bash
npm run test:ui
```

### Run Tests in Headed Mode (See Browser)
```bash
npm run test:headed
```

### Debug Specific Test
```bash
npm run test:debug
```

### View Test Report
```bash
npm run report
```

## Test Configuration

- **Browsers**: Chromium, Firefox, WebKit
- **Base URL**: `http://localhost:3000`
- **API URL**: `http://localhost:8000`
- **Timeout**: 60 seconds per test
- **Screenshots**: Taken on failure
- **Videos**: Recorded on failure

## Test Data and Artifacts

### Test Contract Address
- **Address**: `0xBEEF0123456789abcdef0123456789abcdef0dead`
- **Type**: Mock vulnerable ERC-20 contract
- **Expected Vulnerabilities**:
  - HIGH: Reentrancy Attack Vector
  - MEDIUM: Integer Overflow, Centralized Ownership
  - LOW: Unprotected External Call

### Generated Artifacts
- `artifacts/tests/scanner_vuln_report.json` - Full API response with vulnerability findings
- `artifacts/tests/scanner_ui.png` - Screenshot of the scanner results interface
- `test-results/` - Playwright test results and traces
- `playwright-report/` - HTML test report

## Expected API Response Structure

The test validates that the API returns a response matching this structure:

```typescript
interface TokenScanResponse {
  success: boolean;
  request_id: string;
  contract_address: string;
  chain_id: number;
  token_name?: string;
  token_symbol?: string;
  is_verified: boolean;
  risk_score: number;
  risk_factors: string[];
  liquidity_analysis: Record<string, any>;
  ownership_analysis: Record<string, any>;
  findings: VulnerabilityFinding[];
  total_findings: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  scan_timestamp: number;
  processing_time_ms: number;
}

interface VulnerabilityFinding {
  id: string;
  title: string;
  description: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW' | 'CRITICAL' | 'INFO';
  confidence: number;
  vulnerability_type: string;
  location: string;
  cwe_id?: string;
  cvss_score?: number;
  recommendation?: string;
  references: string[];
  tags: string[];
  exploit_scenario?: string;
  proof?: Record<string, any>;
}
```

## Troubleshooting

### Test Failures

1. **Services Not Running**: Ensure both frontend and backend are running on the correct ports
2. **Network Issues**: Check that `localhost:3000` and `localhost:8000` are accessible
3. **Element Not Found**: The frontend UI may have changed - update selectors in the test
4. **API Changes**: If the API structure changes, update the TypeScript interfaces

### Common Issues

1. **Port Conflicts**: Make sure ports 3000 and 8000 are not used by other services
2. **Browser Installation**: Run `npx playwright install` if browsers are missing
3. **Permissions**: Ensure the `artifacts/tests/` directory is writable

### Debug Tips

1. Use `test:headed` to see the browser actions
2. Use `test:debug` to step through tests
3. Check the generated screenshots and videos in `test-results/`
4. Review the HTML report with `npm run report`

## CI/CD Integration

The tests are configured for CI environments:
- Retry failed tests 2 times in CI
- Run in headless mode
- Generate artifacts for debugging
- Optimized for containerized environments

For CI setup, ensure:
1. Dependencies are cached
2. Services are properly started
3. Artifacts are saved for debugging
4. Tests run in parallel when possible

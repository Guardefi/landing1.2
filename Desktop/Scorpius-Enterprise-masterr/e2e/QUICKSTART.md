# Quick Start Guide for Running Scanner Vulnerability Tests

## 1. Start the Services

### Terminal 1 - Frontend
```bash
cd frontend
npm install
npm run dev
# Frontend should be running on http://localhost:3000
```

### Terminal 2 - Backend  
```bash
cd backend/Bytecode/api
pip install -r config/config/requirements-dev.txt  # if not already done
python -m uvicorn enterprise_main:app --host 0.0.0.0 --port 8000 --reload
# Backend should be running on http://localhost:8000
```

## 2. Run the Tests

### Terminal 3 - Tests
```bash
cd tests/e2e
npm install
npx playwright install
npx playwright test
```

## Expected Test Results

The test will:
1. Navigate to `/scanner`
2. Input contract address: `0xBEEF0123456789abcdef0123456789abcdef0dead`
3. Click "Run Scan"
4. Wait for API response from `/api/v2/scan/token`
5. Validate that the response contains:
   - At least 3 findings
   - Severities: HIGH, MEDIUM, LOW
   - First finding contains "reentrancy"
6. Save artifacts:
   - `artifacts/tests/scanner_vuln_report.json`
   - `artifacts/tests/scanner_ui.png`

## Quick Commands

- `npx playwright test --headed` - See the browser in action
- `npx playwright test --debug` - Step through the test
- `npx playwright test --ui` - Use the visual test runner
- `npx playwright show-report` - View detailed results

## Troubleshooting

- Make sure both services are running on the correct ports
- Check that the contract address triggers the vulnerability response
- Verify that the artifacts directory is writable
- Use headed mode to see what's happening in the browser

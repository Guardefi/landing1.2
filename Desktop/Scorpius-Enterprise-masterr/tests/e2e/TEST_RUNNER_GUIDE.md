# Scorpius Test Runner Guide

## Overview

The `run-tests.ps1` script is a comprehensive test orchestrator that manages three types of tests:
- **Playwright E2E Tests**: Frontend and backend integration testing
- **Cypress Tests**: Additional UI testing (quantum security placeholder)
- **API Tests**: Backend-only static API testing with pytest

## Quick Start

```powershell
# Run all test types
.\run-tests.ps1 all

# Run with browser visible
.\run-tests.ps1 all -Headed

# Run specific test type
.\run-tests.ps1 playwright
.\run-tests.ps1 cypress
.\run-tests.ps1 api

# Skip service health checks
.\run-tests.ps1 all -SkipServiceCheck

# Verbose output with detailed logs
.\run-tests.ps1 all -Verbose
```

## Test Types Explained

### 1. Playwright E2E Tests (`playwright`)

**Location**: `specs/*.spec.ts`

**Tests Include**:
- `wallet-scanner.spec.ts` - Wallet vulnerability scanning flow
- `honeypot-radar.spec.ts` - Token honeypot detection
- `time-machine.spec.ts` - Block replay and state analysis  
- `mev-guardian.spec.ts` - Demo video recording of wallet scan
- `reporting-engine.spec.ts` - PDF report generation and download
- `mempool-monitor.spec.ts` - Real-time mempool visualization

**Artifacts Generated**:
- Screenshots: `artifacts/tests/`
- Videos: `artifacts/videos/`
- Downloads: `artifacts/downloads/`
- HTML snapshots: `artifacts/tests/`

**Example Run**:
```powershell
.\run-tests.ps1 playwright -Headed -Verbose
```

### 2. Cypress Tests (`cypress`)

**Location**: `cypress/e2e/*.cy.ts`

**Tests Include**:
- `quantum-security.cy.ts` - Quantum security placeholder page testing

**Artifacts Generated**:
- Screenshots: `cypress/screenshots/`
- Videos: `cypress/videos/`

**Example Run**:
```powershell
.\run-tests.ps1 cypress
```

### 3. API Tests (`api`)

**Location**: `../api/test_static_api.py`

**Tests Include**:
- Health endpoint validation (`/api/health`)
- Version endpoint validation (`/api/version`)
- Wallet check endpoint testing (`/api/wallet/check`)
- CORS header validation
- Response time testing
- Error handling validation

**Artifacts Generated**:
- Test results: `../api/test-results/`
- Coverage reports (if configured)

**Example Run**:
```powershell
.\run-tests.ps1 api -Verbose
```

## Command Reference

### Test Execution Commands

| Command | Description |
|---------|-------------|
| `all` | Run all test types (Playwright + Cypress + API) |
| `playwright` | Run only Playwright E2E tests |
| `cypress` | Run only Cypress tests |
| `api` | Run only API tests |

### Options

| Option | Description |
|--------|-------------|
| `-Headed` | Run tests with browser visible (Playwright/Cypress) |
| `-Debug` | Run tests in debug mode (Playwright only) |
| `-SkipServiceCheck` | Skip frontend/backend service health checks |
| `-Verbose` | Show detailed output and progress |

### Utility Commands

| Command | Description |
|---------|-------------|
| `install` | Install all dependencies (npm, Playwright browsers, pip packages) |
| `ui` | Open Playwright UI for interactive test development |
| `report` | View test reports (opens Playwright report) |
| `clean` | Remove all test artifacts and generated files |

## Prerequisites

### Services Required
- **Frontend**: http://localhost:3000 (React/Vite dev server)
- **Backend**: http://localhost:8000 (FastAPI with enterprise_main.py)

### Dependencies
- **Node.js**: For Playwright and Cypress
- **Python**: For API tests (pytest)
- **Browsers**: Chromium, Firefox, WebKit (auto-installed by Playwright)

### Starting Services

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

**Backend**:
```bash
cd backend/Bytecode/api
pip install -r config/config/requirements-dev.txt
python -m uvicorn enterprise_main:app --host 0.0.0.0 --port 8000 --reload
```

## Test Execution Flow

When running `all`, the test runner:

1. **Service Health Check**: Validates frontend and backend availability
2. **Directory Setup**: Creates all required artifact directories
3. **Playwright Tests**: Runs all E2E tests sequentially
4. **Cypress Tests**: Runs quantum security placeholder test
5. **API Tests**: Runs backend-only static API validation
6. **Summary Report**: Shows comprehensive results with timing

## Output and Artifacts

### Test Summary Format
```
📊 TEST EXECUTION SUMMARY
=========================
Total Duration: 2.5m 15.3s

Playwright: Passed (1.8m 45.2s)
Cypress: Passed (25.4s)
API: Passed (4.7s)

🎉 ALL TESTS PASSED! (3/3)
```

### Artifact Locations

```
tests/e2e/
├── artifacts/
│   ├── tests/          # Playwright screenshots & HTML
│   ├── videos/         # Demo videos
│   └── downloads/      # Downloaded files (PDFs)
├── cypress/
│   ├── screenshots/    # Cypress screenshots
│   └── videos/         # Cypress recordings
└── ../api/
    └── test-results/   # API test results
```

## Troubleshooting

### Common Issues

**Services Not Running**:
```
❌ Frontend is not running on port 3000
   Please start with: cd frontend && npm run dev
```
- Solution: Start frontend development server

**Missing Dependencies**:
```
❌ Playwright tests failed (Exit code: 1)
```
- Solution: Run `.\run-tests.ps1 install`

**Port Conflicts**:
- Ensure ports 3000 and 8000 are available
- Use `-SkipServiceCheck` to bypass health checks if needed

### Debug Mode

Use debug options for troubleshooting:
```powershell
# Playwright debug mode (step through tests)
.\run-tests.ps1 playwright -Debug

# Headed mode (watch tests execute)
.\run-tests.ps1 all -Headed

# Verbose logging
.\run-tests.ps1 all -Verbose
```

### Manual Test Execution

You can also run tests manually:

```powershell
# Playwright
npx playwright test
npx playwright test --headed
npx playwright test --ui

# Cypress  
npx cypress run
npx cypress open

# API tests
cd ../api
python -m pytest test_static_api.py -v
```

## Best Practices

1. **Run `install` first**: Ensure all dependencies are up to date
2. **Use `clean` regularly**: Remove old artifacts between test sessions
3. **Check services**: Verify frontend/backend are running before testing
4. **Use verbose mode**: For debugging and detailed progress tracking
5. **Review artifacts**: Check screenshots/videos when tests fail
6. **CI/CD Integration**: Use `-SkipServiceCheck` in automated environments

## Integration with CI/CD

For automated testing environments:

```powershell
# CI-friendly command
.\run-tests.ps1 all -SkipServiceCheck -Verbose

# Exit codes:
# 0 = All tests passed
# 1 = Some tests failed
```

The test runner provides proper exit codes for integration with build pipelines.

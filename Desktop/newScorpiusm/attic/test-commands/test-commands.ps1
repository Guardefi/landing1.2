# Core Application Test Commands
# These commands run the main test suites for the application

Write-Host "=== CORE APPLICATION TEST COMMANDS ===" -ForegroundColor Green

# Python Backend Tests
Write-Host "`n1. Python Backend Tests..." -ForegroundColor Yellow

# Run all tests
Write-Host "   - All tests..." -ForegroundColor Cyan
pytest

# Run tests with verbose output
Write-Host "   - Verbose tests..." -ForegroundColor Cyan
pytest -v

# Run tests with coverage
Write-Host "   - Tests with coverage..." -ForegroundColor Cyan
pytest --cov=backend --cov-report=html --cov-report=term

# Run specific test files
Write-Host "`n2. Specific Backend Test Files..." -ForegroundColor Yellow

# Core API endpoint tests
Write-Host "   - Core API endpoints..." -ForegroundColor Cyan
pytest backend/tests/test_comprehensive.py::TestAPIEndpoints -v

# Authentication tests
Write-Host "   - Authentication tests..." -ForegroundColor Cyan
pytest backend/tests/test_api.py -v

# Production readiness tests
Write-Host "   - Production readiness..." -ForegroundColor Cyan
pytest backend/tests/test_production_readiness.py -v

# MEV bot tests
Write-Host "   - MEV bot tests..." -ForegroundColor Cyan
pytest backend/tests/test_mev_bot.py -v

# Database tests
Write-Host "   - Database tests..." -ForegroundColor Cyan
pytest backend/tests/test_database.py -v

# Run specific test classes/methods
Write-Host "`n3. Specific Test Classes/Methods..." -ForegroundColor Yellow

# Specific test class
Write-Host "   - Specific test class..." -ForegroundColor Cyan
Write-Host "     pytest backend/tests/test_comprehensive.py::TestAPIEndpoints::test_health_check -v" -ForegroundColor Gray

# Test with specific markers
Write-Host "   - Tests with markers..." -ForegroundColor Cyan
Write-Host "     pytest -m 'not slow' -v  # Skip slow tests" -ForegroundColor Gray
Write-Host "     pytest -m 'integration' -v  # Only integration tests" -ForegroundColor Gray

# Parallel test execution
Write-Host "`n4. Parallel Test Execution..." -ForegroundColor Yellow
Write-Host "   - Parallel tests (requires pytest-xdist)..." -ForegroundColor Cyan
pytest -n auto  # Use all available CPUs
pytest -n 4     # Use 4 workers

# Test with different output formats
Write-Host "`n5. Different Output Formats..." -ForegroundColor Yellow

# JUnit XML output
Write-Host "   - JUnit XML output..." -ForegroundColor Cyan
pytest --junitxml=test-results.xml

# HTML report
Write-Host "   - HTML test report..." -ForegroundColor Cyan
pytest --html=test-report.html --self-contained-html

# JSON report
Write-Host "   - JSON report..." -ForegroundColor Cyan
pytest --json-report --json-report-file=test-report.json

# Test Discovery and Info
Write-Host "`n6. Test Discovery and Information..." -ForegroundColor Yellow

# List all tests without running
Write-Host "   - List all tests..." -ForegroundColor Cyan
pytest --collect-only

# Show test durations
Write-Host "   - Show slowest tests..." -ForegroundColor Cyan
pytest --durations=10

# Show test coverage gaps
Write-Host "   - Coverage report..." -ForegroundColor Cyan
pytest --cov=backend --cov-report=term-missing

# Frontend Tests (if applicable)
Write-Host "`n7. Frontend Tests..." -ForegroundColor Yellow

# Jest tests (if using Jest)
Write-Host "   - Jest tests..." -ForegroundColor Cyan
npm test

# Vitest tests (if using Vite)
Write-Host "   - Vitest..." -ForegroundColor Cyan
npm run test

# E2E tests with Playwright
Write-Host "   - Playwright E2E..." -ForegroundColor Cyan
npx playwright test

# Integration Tests
Write-Host "`n8. Integration Tests..." -ForegroundColor Yellow

# API integration tests
Write-Host "   - API integration..." -ForegroundColor Cyan
pytest backend/tests/integration/ -v

# Database integration tests
Write-Host "   - Database integration..." -ForegroundColor Cyan
pytest backend/tests/test_database.py::TestDatabaseIntegration -v

# Test Environment Setup
Write-Host "`n9. Test Environment Commands..." -ForegroundColor Yellow

# Setup test database
Write-Host "   - Setup test database..." -ForegroundColor Cyan
Write-Host "     python -m backend.database create_test_db" -ForegroundColor Gray

# Reset test environment
Write-Host "   - Reset test environment..." -ForegroundColor Cyan
Write-Host "     python -m backend.database reset_test_db" -ForegroundColor Gray

# Load test fixtures
Write-Host "   - Load test fixtures..." -ForegroundColor Cyan
Write-Host "     python -m backend.tests.fixtures load_all" -ForegroundColor Gray

# Test Debugging
Write-Host "`n10. Test Debugging..." -ForegroundColor Yellow

# Run with PDB debugger
Write-Host "   - Debug failing tests..." -ForegroundColor Cyan
pytest --pdb

# Run last failed tests only
Write-Host "   - Re-run last failures..." -ForegroundColor Cyan
pytest --lf

# Run failed tests first
Write-Host "   - Failed tests first..." -ForegroundColor Cyan
pytest --ff

# Expected successful output
Write-Host "`n=== EXPECTED SUCCESSFUL OUTPUT ===" -ForegroundColor Green
Write-Host "====================== test session starts ======================
platform win32 -- Python 3.10.11
collected 25 items

backend/tests/test_comprehensive.py::TestAPIEndpoints::test_health_check PASSED [100%]
backend/tests/test_api.py::test_authentication PASSED [100%]

====================== 25 passed in 5.23s ======================

Coverage:
backend/main.py                 95%    100%
backend/routes/auth_fastapi.py  87%     90%
TOTAL                          89%     85%" -ForegroundColor Gray

Write-Host "`n=== TROUBLESHOOTING ===" -ForegroundColor Red
Write-Host "Common test failures:"
Write-Host "1. Import errors: Check PYTHONPATH and module structure"
Write-Host "2. Database connection: Ensure test database is running"
Write-Host "3. Missing dependencies: Run 'pip install -r requirements.txt'"
Write-Host "4. Port conflicts: Check if test server ports are available"
Write-Host "5. Environment variables: Check test environment configuration"

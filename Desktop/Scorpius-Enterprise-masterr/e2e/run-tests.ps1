#!/usr/bin/env pwsh

# Scorpius Comprehensive Test Runner
# Orchestrates Playwright E2E, Cypress, and API tests with detailed reporting

param(
    [string]$TestType = "",
    [switch]$Headed = $false,
    [switch]$Debug = $false,
    [switch]$SkipServiceCheck = $false,
    [switch]$Verbose = $false
)

Write-Host "🚀 Scorpius Comprehensive Test Runner" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Test results tracking
$TestResults = @{
    Playwright = @{ Status = "Not Run"; Duration = 0; Details = "" }
    Cypress = @{ Status = "Not Run"; Duration = 0; Details = "" }
    API = @{ Status = "Not Run"; Duration = 0; Details = "" }
    StartTime = Get-Date
}

# Helper function to format duration
function Format-Duration {
    param([TimeSpan]$duration)
    if ($duration.TotalMinutes -ge 1) {
        return "{0:F1}m {1:F1}s" -f $duration.TotalMinutes, $duration.Seconds
    } else {
        return "{0:F2}s" -f $duration.TotalSeconds
    }
}

# Helper function to run command with timing and error handling
function Invoke-TestCommand {
    param(
        [string]$Command,
        [string]$Arguments,
        [string]$TestName,
        [string]$WorkingDirectory = $PWD
    )
    
    $startTime = Get-Date
    Write-Host "🧪 Running $TestName tests..." -ForegroundColor Blue
    
    try {
        $process = Start-Process -FilePath $Command -ArgumentList $Arguments -WorkingDirectory $WorkingDirectory -Wait -NoNewWindow -PassThru
        $endTime = Get-Date
        $duration = $endTime - $startTime
        
        if ($process.ExitCode -eq 0) {
            Write-Host "✅ $TestName tests passed" -ForegroundColor Green
            return @{ Status = "Passed"; Duration = $duration; Details = "All tests passed successfully" }
        } else {
            Write-Host "❌ $TestName tests failed (Exit code: $($process.ExitCode))" -ForegroundColor Red
            return @{ Status = "Failed"; Duration = $duration; Details = "Exit code: $($process.ExitCode)" }
        }
    } catch {
        $endTime = Get-Date
        $duration = $endTime - $startTime
        Write-Host "❌ $TestName tests failed with exception: $($_.Exception.Message)" -ForegroundColor Red
        return @{ Status = "Error"; Duration = $duration; Details = $_.Exception.Message }
    }
}

# Check if we're in the right directory
if (!(Test-Path "package.json")) {
    Write-Host "❌ Error: Please run this script from the tests/e2e directory" -ForegroundColor Red
    exit 1
}

# Check if services are running (unless skipped)
if (-not $SkipServiceCheck) {
    Write-Host "🔍 Checking required services..." -ForegroundColor Yellow
    
    $servicesOk = $true
    
    try {
        Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 3 -ErrorAction Stop | Out-Null
        Write-Host "✅ Frontend is running on port 3000" -ForegroundColor Green
    } catch {
        Write-Host "❌ Frontend is not running on port 3000" -ForegroundColor Red
        Write-Host "   Please start with: cd frontend && npm run dev" -ForegroundColor Yellow
        $servicesOk = $false
    }
    
    try {
        Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 3 -ErrorAction Stop | Out-Null
        Write-Host "✅ Backend API is running on port 8000" -ForegroundColor Green
    } catch {
        Write-Host "❌ Backend API is not running on port 8000" -ForegroundColor Red
        Write-Host "   Please start with: cd backend/Bytecode/api && python -m uvicorn enterprise_main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Yellow
        $servicesOk = $false
    }
    
    if (-not $servicesOk -and $TestType -in @("all", "playwright", "cypress", "")) {
        Write-Host "⚠️  Some services are not running. E2E tests may fail." -ForegroundColor Yellow
        Write-Host "   Use -SkipServiceCheck to bypass this check" -ForegroundColor Gray
    }
}

# Ensure all artifact directories exist
$artifactDirs = @(
    "artifacts\tests",
    "artifacts\videos", 
    "artifacts\downloads",
    "cypress\screenshots",
    "cypress\videos",
    "..\api\test-results"
)

foreach ($dir in $artifactDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        if ($Verbose) { Write-Host "📁 Created directory: $dir" -ForegroundColor Blue }
    }
}

# Main test execution logic
switch ($TestType.ToLower()) {
    "playwright" {
        Write-Host "🎭 Running Playwright E2E tests only..." -ForegroundColor Magenta
        $playwrightArgs = "test"
        if ($Headed) { $playwrightArgs += " --headed" }
        if ($Debug) { $playwrightArgs += " --debug" }
        
        $TestResults.Playwright = Invoke-TestCommand -Command "npx" -Arguments "playwright $playwrightArgs" -TestName "Playwright"
    }
    
    "cypress" {
        Write-Host "🌲 Running Cypress tests only..." -ForegroundColor Magenta
        $cypressArgs = "run"
        if ($Headed) { $cypressArgs = "open" }
        
        $TestResults.Cypress = Invoke-TestCommand -Command "npx" -Arguments "cypress $cypressArgs" -TestName "Cypress"
    }
    
    "api" {
        Write-Host "🔗 Running API tests only..." -ForegroundColor Magenta
        # Check if Python virtual environment or dependencies are available
        $apiTestDir = "..\api"
        if (Test-Path "$apiTestDir\requirements.txt") {
            # Try to install dependencies if needed
            if ($Verbose) { Write-Host "Installing API test dependencies..." -ForegroundColor Blue }
            Start-Process -FilePath "pip" -ArgumentList "install -r $apiTestDir\requirements.txt" -Wait -NoNewWindow | Out-Null
        }
        
        $TestResults.API = Invoke-TestCommand -Command "python" -Arguments "-m pytest $apiTestDir\test_static_api.py -v --tb=short" -TestName "API"
    }
    
    "all" {
        Write-Host "🎯 Running ALL test types (Playwright + Cypress + API)..." -ForegroundColor Magenta
        Write-Host ""
        
        # Run Playwright tests
        Write-Host "1/3 🎭 Playwright E2E Tests" -ForegroundColor Blue
        $playwrightArgs = "test"
        if ($Headed) { $playwrightArgs += " --headed" }
        $TestResults.Playwright = Invoke-TestCommand -Command "npx" -Arguments "playwright $playwrightArgs" -TestName "Playwright"
        
        Write-Host ""
        
        # Run Cypress tests
        Write-Host "2/3 � Cypress Tests" -ForegroundColor Blue
        $TestResults.Cypress = Invoke-TestCommand -Command "npx" -Arguments "cypress run" -TestName "Cypress"
        
        Write-Host ""
        
        # Run API tests
        Write-Host "3/3 🔗 API Tests" -ForegroundColor Blue
        $apiTestDir = "..\api"
        if (Test-Path "$apiTestDir\requirements.txt") {
            if ($Verbose) { Write-Host "Installing API test dependencies..." -ForegroundColor Blue }
            Start-Process -FilePath "pip" -ArgumentList "install -r $apiTestDir\requirements.txt" -Wait -NoNewWindow | Out-Null
        }
        $TestResults.API = Invoke-TestCommand -Command "python" -Arguments "-m pytest $apiTestDir\test_static_api.py -v --tb=short" -TestName "API"
    }
    
    "install" {
        Write-Host "� Installing all dependencies..." -ForegroundColor Blue
        Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
        npm install
        Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
        npx playwright install
        Write-Host "Installing API test dependencies..." -ForegroundColor Yellow
        $apiTestDir = "..\api"
        if (Test-Path "$apiTestDir\requirements.txt") {
            pip install -r "$apiTestDir\requirements.txt"
        }
        Write-Host "✅ All dependencies installed!" -ForegroundColor Green
        exit 0
    }
    
    "ui" {
        Write-Host "🎨 Opening Playwright UI..." -ForegroundColor Blue
        npx playwright test --ui
        exit 0
    }
    
    "report" {
        Write-Host "📊 Opening test reports..." -ForegroundColor Blue
        if (Test-Path "playwright-report") {
            Write-Host "Opening Playwright report..." -ForegroundColor Yellow
            npx playwright show-report
        }
        if (Test-Path "cypress\reports") {
            Write-Host "Cypress reports available in cypress\reports\" -ForegroundColor Yellow
        }
        exit 0
    }
    
    "clean" {
        Write-Host "🧹 Cleaning test artifacts..." -ForegroundColor Blue
        $cleanDirs = @("artifacts", "test-results", "playwright-report", "cypress\screenshots", "cypress\videos")
        foreach ($dir in $cleanDirs) {
            if (Test-Path $dir) {
                Remove-Item -Path $dir -Recurse -Force
                Write-Host "🗑️  Removed $dir" -ForegroundColor Gray
            }
        }
        Write-Host "✅ Cleanup complete!" -ForegroundColor Green
        exit 0
    }
    
    default {
        Write-Host "📖 Scorpius Test Runner Commands:" -ForegroundColor Green
        Write-Host ""
        Write-Host "Test Execution:" -ForegroundColor White
        Write-Host "  .\run-tests.ps1 all         - Run all test types (Playwright + Cypress + API)" -ForegroundColor White
        Write-Host "  .\run-tests.ps1 playwright  - Run Playwright E2E tests only" -ForegroundColor White  
        Write-Host "  .\run-tests.ps1 cypress     - Run Cypress tests only" -ForegroundColor White
        Write-Host "  .\run-tests.ps1 api         - Run API tests only" -ForegroundColor White
        Write-Host ""
        Write-Host "Options:" -ForegroundColor White
        Write-Host "  -Headed                     - Run tests with browser visible" -ForegroundColor Gray
        Write-Host "  -Debug                      - Run tests in debug mode (Playwright only)" -ForegroundColor Gray
        Write-Host "  -SkipServiceCheck           - Skip frontend/backend service checks" -ForegroundColor Gray
        Write-Host "  -Verbose                    - Show detailed output" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Utilities:" -ForegroundColor White
        Write-Host "  .\run-tests.ps1 install     - Install all dependencies" -ForegroundColor White
        Write-Host "  .\run-tests.ps1 ui          - Open Playwright UI" -ForegroundColor White
        Write-Host "  .\run-tests.ps1 report      - View test reports" -ForegroundColor White
        Write-Host "  .\run-tests.ps1 clean       - Clean test artifacts" -ForegroundColor White
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\run-tests.ps1 all -Verbose" -ForegroundColor Gray
        Write-Host "  .\run-tests.ps1 playwright -Headed" -ForegroundColor Gray
        Write-Host "  .\run-tests.ps1 cypress -SkipServiceCheck" -ForegroundColor Gray
        Write-Host ""
        Write-Host "💡 Prerequisites:" -ForegroundColor Yellow
        Write-Host "   - Frontend running on http://localhost:3000" -ForegroundColor Gray
        Write-Host "   - Backend API running on http://localhost:8000" -ForegroundColor Gray
        Write-Host "   - Python with pytest installed (for API tests)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "📁 Test artifacts saved to:" -ForegroundColor Blue
        Write-Host "   - artifacts/tests/ (Playwright)" -ForegroundColor Gray
        Write-Host "   - cypress/screenshots/ & cypress/videos/ (Cypress)" -ForegroundColor Gray
        Write-Host "   - ../api/test-results/ (API tests)" -ForegroundColor Gray
        exit 0
    }
}

# Generate comprehensive test summary
$totalDuration = (Get-Date) - $TestResults.StartTime
Write-Host ""
Write-Host "📊 TEST EXECUTION SUMMARY" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Total Duration: $(Format-Duration $totalDuration)" -ForegroundColor White
Write-Host ""

$passedCount = 0
$failedCount = 0

foreach ($testType in @("Playwright", "Cypress", "API")) {
    $result = $TestResults[$testType]
    $statusColor = switch ($result.Status) {
        "Passed" { "Green"; $passedCount++ }
        "Failed" { "Red"; $failedCount++ }
        "Error" { "Red"; $failedCount++ }
        default { "Gray" }
    }
    
    if ($result.Status -ne "Not Run") {
        $durationStr = Format-Duration $result.Duration
        Write-Host "$testType`: $($result.Status) ($durationStr)" -ForegroundColor $statusColor
        if ($Verbose -and $result.Details) {
            Write-Host "  └─ $($result.Details)" -ForegroundColor Gray
        }
    } else {
        Write-Host "$testType`: Not Run" -ForegroundColor Gray
    }
}

Write-Host ""
if ($failedCount -eq 0 -and $passedCount -gt 0) {
    Write-Host "🎉 ALL TESTS PASSED! ($passedCount/$($passedCount + $failedCount))" -ForegroundColor Green
    exit 0
} elseif ($failedCount -gt 0) {
    Write-Host "❌ SOME TESTS FAILED ($failedCount failed, $passedCount passed)" -ForegroundColor Red
    exit 1
} else {
    Write-Host "ℹ️  No tests were executed" -ForegroundColor Yellow
    exit 0
}

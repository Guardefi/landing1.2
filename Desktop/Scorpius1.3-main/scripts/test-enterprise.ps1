# Scorpius Enterprise Testing Framework
# Comprehensive testing for all components and integrations

param(
    [Parameter(Position=0)]
    [string]$TestSuite = "all",
    [string[]]$Arguments,
    [switch]$Headless,
    [switch]$GenerateReport,
    [switch]$Parallel
)

# Configuration
$DockerComposeFile = "docker-compose.enterprise.yml"
$ProjectRoot = $PSScriptRoot | Split-Path -Parent
$TestResultsDir = "$ProjectRoot/test-results"
$ReportsDir = "$ProjectRoot/reports"
$LogsDir = "$ProjectRoot/logs"

# Test configuration
$TestConfig = @{
    BaseUrl = "http://localhost:8000"
    FrontendUrl = "http://localhost:3000"
    ApiTimeout = 30
    TestTimeout = 300
    RetryAttempts = 3
}

function Write-Header {
    param([string]$Message)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
}

function Write-TestResult {
    param([string]$TestName, [string]$Status, [string]$Message = "")
    $color = if ($Status -eq "PASS") { "Green" } else { "Red" }
    $icon = if ($Status -eq "PASS") { "✅" } else { "❌" }
    Write-Host "${icon} ${TestName}: ${Status}" -ForegroundColor $color
    if ($Message) { Write-Host "   $Message" -ForegroundColor Gray }
}

function Initialize-TestEnvironment {
    Write-Header "Initializing Test Environment"
    
    # Create test directories
    New-Item -ItemType Directory -Force -Path $TestResultsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
    
    # Start Docker environment if not running
    Write-Host "Checking Docker environment..." -ForegroundColor Yellow
    $status = docker-compose -f $DockerComposeFile ps
    
    if ($status -notlike "*Up*") {
        Write-Host "Starting Docker environment..." -ForegroundColor Yellow
        .\scripts\docker-enterprise.ps1 start
        Start-Sleep -Seconds 30
    }
    
    Write-Host "✅ Test environment initialized" -ForegroundColor Green
}

function Test-BackendInfrastructure {
    Write-Header "Backend Infrastructure Testing"
    
    $results = @()
    
    # Test database connections
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.BaseUrl)/health/db" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 200) {
            Write-TestResult "Database Connection" "PASS"
            $results += @{Test = "Database Connection"; Status = "PASS"}
        } else {
            Write-TestResult "Database Connection" "FAIL" "Status: $($response.StatusCode)"
            $results += @{Test = "Database Connection"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
        }
    } catch {
        Write-TestResult "Database Connection" "FAIL" $_.Exception.Message
        $results += @{Test = "Database Connection"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    # Test Redis connection
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.BaseUrl)/health/redis" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 200) {
            Write-TestResult "Redis Connection" "PASS"
            $results += @{Test = "Redis Connection"; Status = "PASS"}
        } else {
            Write-TestResult "Redis Connection" "FAIL" "Status: $($response.StatusCode)"
            $results += @{Test = "Redis Connection"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
        }
    } catch {
        Write-TestResult "Redis Connection" "FAIL" $_.Exception.Message
        $results += @{Test = "Redis Connection"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    # Test API authentication
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.BaseUrl)/auth/verify" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 401) { # Expected for unauthenticated request
            Write-TestResult "API Authentication" "PASS"
            $results += @{Test = "API Authentication"; Status = "PASS"}
        } else {
            Write-TestResult "API Authentication" "FAIL" "Unexpected status: $($response.StatusCode)"
            $results += @{Test = "API Authentication"; Status = "FAIL"; Message = "Unexpected status: $($response.StatusCode)"}
        }
    } catch {
        Write-TestResult "API Authentication" "FAIL" $_.Exception.Message
        $results += @{Test = "API Authentication"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    return $results
}

function Test-ScannerIntegrations {
    Write-Header "Security Analysis Tools Integration Testing"
    
    $results = @()
    $scanners = @{
        "slither" = @{Url = "http://localhost:8002"; Name = "Slither"}
        "mythril" = @{Url = "http://localhost:8003"; Name = "Mythril"}
        "mythx" = @{Url = "http://localhost:8004"; Name = "MythX"}
        "manticore" = @{Url = "http://localhost:8005"; Name = "Manticore"}
    }
    
    foreach ($scanner in $scanners.GetEnumerator()) {
        $scannerName = $scanner.Value.Name
        $scannerUrl = $scanner.Value.Url
        
        # Test scanner health
        try {
            $response = Invoke-WebRequest -Uri "$scannerUrl/health" -TimeoutSec $TestConfig.ApiTimeout
            if ($response.StatusCode -eq 200) {
                Write-TestResult "$scannerName Health Check" "PASS"
                $results += @{Test = "$scannerName Health Check"; Status = "PASS"}
            } else {
                Write-TestResult "$scannerName Health Check" "FAIL" "Status: $($response.StatusCode)"
                $results += @{Test = "$scannerName Health Check"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
            }
        } catch {
            Write-TestResult "$scannerName Health Check" "FAIL" $_.Exception.Message
            $results += @{Test = "$scannerName Health Check"; Status = "FAIL"; Message = $_.Exception.Message}
        }
        
        # Test scanner API
        try {
            $response = Invoke-WebRequest -Uri "$scannerUrl/api/v1/status" -TimeoutSec $TestConfig.ApiTimeout
            if ($response.StatusCode -eq 200) {
                Write-TestResult "$scannerName API" "PASS"
                $results += @{Test = "$scannerName API"; Status = "PASS"}
            } else {
                Write-TestResult "$scannerName API" "FAIL" "Status: $($response.StatusCode)"
                $results += @{Test = "$scannerName API"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
            }
        } catch {
            Write-TestResult "$scannerName API" "FAIL" $_.Exception.Message
            $results += @{Test = "$scannerName API"; Status = "FAIL"; Message = $_.Exception.Message}
        }
    }
    
    return $results
}

function Test-WebSocketFunctionality {
    Write-Header "WebSocket Functionality Testing"
    
    $results = @()
    
    # Test WebSocket connection
    try {
        $wsUrl = $TestConfig.BaseUrl -replace "http", "ws"
        $ws = New-Object System.Net.WebSockets.ClientWebSocket
        
        $cancellationToken = New-Object System.Threading.CancellationToken
        $connectTask = $ws.ConnectAsync([Uri]"$wsUrl/ws", $cancellationToken)
        $connectTask.Wait($TestConfig.ApiTimeout * 1000)
        
        if ($ws.State -eq "Open") {
            Write-TestResult "WebSocket Connection" "PASS"
            $results += @{Test = "WebSocket Connection"; Status = "PASS"}
            $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "Test complete", $cancellationToken).Wait()
        } else {
            Write-TestResult "WebSocket Connection" "FAIL" "State: $($ws.State)"
            $results += @{Test = "WebSocket Connection"; Status = "FAIL"; Message = "State: $($ws.State)"}
        }
    } catch {
        Write-TestResult "WebSocket Connection" "FAIL" $_.Exception.Message
        $results += @{Test = "WebSocket Connection"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    return $results
}

function Test-FrontendComponents {
    Write-Header "Frontend Components Testing"
    
    $results = @()
    
    # Test frontend accessibility
    try {
        $response = Invoke-WebRequest -Uri $TestConfig.FrontendUrl -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 200) {
            Write-TestResult "Frontend Accessibility" "PASS"
            $results += @{Test = "Frontend Accessibility"; Status = "PASS"}
        } else {
            Write-TestResult "Frontend Accessibility" "FAIL" "Status: $($response.StatusCode)"
            $results += @{Test = "Frontend Accessibility"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
        }
    } catch {
        Write-TestResult "Frontend Accessibility" "FAIL" $_.Exception.Message
        $results += @{Test = "Frontend Accessibility"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    # Test API integration
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.FrontendUrl)/api/health" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 200) {
            Write-TestResult "Frontend API Integration" "PASS"
            $results += @{Test = "Frontend API Integration"; Status = "PASS"}
        } else {
            Write-TestResult "Frontend API Integration" "FAIL" "Status: $($response.StatusCode)"
            $results += @{Test = "Frontend API Integration"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
        }
    } catch {
        Write-TestResult "Frontend API Integration" "FAIL" $_.Exception.Message
        $results += @{Test = "Frontend API Integration"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    return $results
}

function Test-SystemIntegration {
    Write-Header "System Integration Testing"
    
    $results = @()
    
    # Test complete analysis workflow
    try {
        # 1. Create test project
        $projectData = @{
            name = "Test Project"
            description = "Integration test project"
            contract_type = "solidity"
        }
        
        $response = Invoke-WebRequest -Uri "$($TestConfig.BaseUrl)/api/v1/projects" -Method POST -Body ($projectData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 201) {
            Write-TestResult "Project Creation" "PASS"
            $results += @{Test = "Project Creation"; Status = "PASS"}
            
            $project = $response.Content | ConvertFrom-Json
            $projectId = $project.id
            
            # 2. Upload test contract
            $contractContent = "pragma solidity ^0.8.0; contract Test { function test() public {} }"
            $boundary = [System.Guid]::NewGuid().ToString()
            $LF = "`r`n"
            $bodyLines = @(
                "--$boundary",
                "Content-Disposition: form-data; name=`"file`"; filename=`"test.sol`"",
                "Content-Type: text/plain",
                "",
                $contractContent,
                "--$boundary--"
            )
            $body = $bodyLines -join $LF
            
            $response = Invoke-WebRequest -Uri "$($TestConfig.BaseUrl)/api/v1/projects/$projectId/contracts" -Method POST -Body $body -Headers @{"Content-Type" = "multipart/form-data; boundary=$boundary"} -TimeoutSec $TestConfig.ApiTimeout
            if ($response.StatusCode -eq 201) {
                Write-TestResult "Contract Upload" "PASS"
                $results += @{Test = "Contract Upload"; Status = "PASS"}
            } else {
                Write-TestResult "Contract Upload" "FAIL" "Status: $($response.StatusCode)"
                $results += @{Test = "Contract Upload"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
            }
        } else {
            Write-TestResult "Project Creation" "FAIL" "Status: $($response.StatusCode)"
            $results += @{Test = "Project Creation"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
        }
    } catch {
        Write-TestResult "Analysis Workflow" "FAIL" $_.Exception.Message
        $results += @{Test = "Analysis Workflow"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    return $results
}

function Test-Performance {
    Write-Header "Performance Testing"
    
    $results = @()
    
    # Test API response times
    $responseTimes = @()
    for ($i = 1; $i -le 10; $i++) {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            $response = Invoke-WebRequest -Uri "$($TestConfig.BaseUrl)/health" -TimeoutSec $TestConfig.ApiTimeout
            $stopwatch.Stop()
            $responseTimes += $stopwatch.ElapsedMilliseconds
        } catch {
            $stopwatch.Stop()
            $responseTimes += $stopwatch.ElapsedMilliseconds
        }
    }
    
    $avgResponseTime = ($responseTimes | Measure-Object -Average).Average
    if ($avgResponseTime -lt 1000) {
        Write-TestResult "API Response Time" "PASS" "Average: ${avgResponseTime}ms"
        $results += @{Test = "API Response Time"; Status = "PASS"; Message = "Average: ${avgResponseTime}ms"}
    } else {
        Write-TestResult "API Response Time" "FAIL" "Average: ${avgResponseTime}ms (too slow)"
        $results += @{Test = "API Response Time"; Status = "FAIL"; Message = "Average: ${avgResponseTime}ms (too slow)"}
    }
    
    # Test concurrent requests
    $concurrentResults = @()
    $jobs = @()
    
    for ($i = 1; $i -le 5; $i++) {
        $jobs += Start-Job -ScriptBlock {
            param($url, $timeout)
            try {
                $response = Invoke-WebRequest -Uri $url -TimeoutSec $timeout
                return @{Success = $true; StatusCode = $response.StatusCode}
            } catch {
                return @{Success = $false; Error = $_.Exception.Message}
            }
        } -ArgumentList "$($TestConfig.BaseUrl)/health", $TestConfig.ApiTimeout
    }
    
    $jobResults = $jobs | Wait-Job | Receive-Job
    $successCount = ($jobResults | Where-Object { $_.Success }).Count
    
    if ($successCount -eq 5) {
        Write-TestResult "Concurrent Requests" "PASS" "All 5 requests succeeded"
        $results += @{Test = "Concurrent Requests"; Status = "PASS"; Message = "All 5 requests succeeded"}
    } else {
        Write-TestResult "Concurrent Requests" "FAIL" "Only $successCount/5 requests succeeded"
        $results += @{Test = "Concurrent Requests"; Status = "FAIL"; Message = "Only $successCount/5 requests succeeded"}
    }
    
    $jobs | Remove-Job
    
    return $results
}

function Test-Security {
    Write-Header "Security Testing"
    
    $results = @()
    
    # Test authentication bypass attempts
    $endpoints = @("/api/v1/projects", "/api/v1/users", "/api/v1/admin")
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri "$($TestConfig.BaseUrl)$endpoint" -TimeoutSec $TestConfig.ApiTimeout
            if ($response.StatusCode -eq 401) {
                Write-TestResult "Authentication Required: $endpoint" "PASS"
                $results += @{Test = "Authentication Required: $endpoint"; Status = "PASS"}
            } else {
                Write-TestResult "Authentication Required: $endpoint" "FAIL" "Status: $($response.StatusCode)"
                $results += @{Test = "Authentication Required: $endpoint"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
            }
        } catch {
            if ($_.Exception.Response.StatusCode -eq 401) {
                Write-TestResult "Authentication Required: $endpoint" "PASS"
                $results += @{Test = "Authentication Required: $endpoint"; Status = "PASS"}
            } else {
                Write-TestResult "Authentication Required: $endpoint" "FAIL" $_.Exception.Message
                $results += @{Test = "Authentication Required: $endpoint"; Status = "FAIL"; Message = $_.Exception.Message}
            }
        }
    }
    
    # Test CORS headers
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.BaseUrl)/health" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.Headers["Access-Control-Allow-Origin"]) {
            Write-TestResult "CORS Headers" "PASS"
            $results += @{Test = "CORS Headers"; Status = "PASS"}
        } else {
            Write-TestResult "CORS Headers" "FAIL" "Missing CORS headers"
            $results += @{Test = "CORS Headers"; Status = "FAIL"; Message = "Missing CORS headers"}
        }
    } catch {
        Write-TestResult "CORS Headers" "FAIL" $_.Exception.Message
        $results += @{Test = "CORS Headers"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    return $results
}

function Test-ErrorHandling {
    Write-Header "Error Handling Testing"
    
    $results = @()
    
    # Test invalid endpoints
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.BaseUrl)/invalid-endpoint" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 404) {
            Write-TestResult "404 Error Handling" "PASS"
            $results += @{Test = "404 Error Handling"; Status = "PASS"}
        } else {
            Write-TestResult "404 Error Handling" "FAIL" "Status: $($response.StatusCode)"
            $results += @{Test = "404 Error Handling"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-TestResult "404 Error Handling" "PASS"
            $results += @{Test = "404 Error Handling"; Status = "PASS"}
        } else {
            Write-TestResult "404 Error Handling" "FAIL" $_.Exception.Message
            $results += @{Test = "404 Error Handling"; Status = "FAIL"; Message = $_.Exception.Message}
        }
    }
    
    # Test malformed requests
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.BaseUrl)/api/v1/projects" -Method POST -Body "invalid json" -ContentType "application/json" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 400) {
            Write-TestResult "Malformed Request Handling" "PASS"
            $results += @{Test = "Malformed Request Handling"; Status = "PASS"}
        } else {
            Write-TestResult "Malformed Request Handling" "FAIL" "Status: $($response.StatusCode)"
            $results += @{Test = "Malformed Request Handling"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 400) {
            Write-TestResult "Malformed Request Handling" "PASS"
            $results += @{Test = "Malformed Request Handling"; Status = "PASS"}
        } else {
            Write-TestResult "Malformed Request Handling" "FAIL" $_.Exception.Message
            $results += @{Test = "Malformed Request Handling"; Status = "FAIL"; Message = $_.Exception.Message}
        }
    }
    
    return $results
}

function Generate-TestReport {
    param([array]$AllResults)
    
    Write-Header "Generating Test Report"
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $reportFile = "$ReportsDir/test-report-$timestamp.html"
    
    $totalTests = $AllResults.Count
    $passedTests = ($AllResults | Where-Object { $_.Status -eq "PASS" }).Count
    $failedTests = ($AllResults | Where-Object { $_.Status -eq "FAIL" }).Count
    $successRate = [math]::Round(($passedTests / $totalTests) * 100, 2)
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Scorpius Enterprise Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .test-result { margin: 10px 0; padding: 10px; border-radius: 3px; }
        .pass { background-color: #d4edda; border: 1px solid #c3e6cb; }
        .fail { background-color: #f8d7da; border: 1px solid #f5c6cb; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat { text-align: center; padding: 20px; background-color: #e9ecef; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Scorpius Enterprise Test Report</h1>
        <p>Generated: $(Get-Date)</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <h3>Total Tests</h3>
            <p>$totalTests</p>
        </div>
        <div class="stat">
            <h3>Passed</h3>
            <p style="color: green;">$passedTests</p>
        </div>
        <div class="stat">
            <h3>Failed</h3>
            <p style="color: red;">$failedTests</p>
        </div>
        <div class="stat">
            <h3>Success Rate</h3>
            <p>$successRate%</p>
        </div>
    </div>
    
    <h2>Test Results</h2>
"@
    
    foreach ($result in $AllResults) {
        $cssClass = if ($result.Status -eq "PASS") { "pass" } else { "fail" }
        $html += @"
    <div class="test-result $cssClass">
        <strong>$($result.Test)</strong>: $($result.Status)
        $(if ($result.Message) { "<br><em>$($result.Message)</em>" })
    </div>
"@
    }
    
    $html += @"
</body>
</html>
"@
    
    $html | Out-File -FilePath $reportFile -Encoding UTF8
    Write-Host "✅ Test report generated: $reportFile" -ForegroundColor Green
    
    return $reportFile
}

function Show-Help {
    Write-Header "Scorpius Enterprise Testing Framework"
    
    Write-Host "Available test suites:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  all              - Run all test suites" -ForegroundColor White
    Write-Host "  infrastructure   - Test backend infrastructure" -ForegroundColor White
    Write-Host "  scanners         - Test security analysis tools" -ForegroundColor White
    Write-Host "  websockets       - Test WebSocket functionality" -ForegroundColor White
    Write-Host "  frontend         - Test frontend components" -ForegroundColor White
    Write-Host "  integration      - Test system integration" -ForegroundColor White
    Write-Host "  performance      - Test performance and load" -ForegroundColor White
    Write-Host "  security         - Test security measures" -ForegroundColor White
    Write-Host "  errors           - Test error handling" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  --headless       - Run in headless mode" -ForegroundColor White
    Write-Host "  --generate-report - Generate HTML test report" -ForegroundColor White
    Write-Host "  --parallel       - Run tests in parallel" -ForegroundColor White
    Write-Host ""
    Write-Host "Usage: .\scripts\test-enterprise.ps1 <test-suite> [options]" -ForegroundColor Gray
    Write-Host "Example: .\scripts\test-enterprise.ps1 all --generate-report" -ForegroundColor Gray
}

# Main execution
Set-Location $ProjectRoot

switch ($TestSuite.ToLower()) {
    "help" { Show-Help; exit 0 }
    "all" {
        Initialize-TestEnvironment
        $allResults = @()
        $allResults += Test-BackendInfrastructure
        $allResults += Test-ScannerIntegrations
        $allResults += Test-WebSocketFunctionality
        $allResults += Test-FrontendComponents
        $allResults += Test-SystemIntegration
        $allResults += Test-Performance
        $allResults += Test-Security
        $allResults += Test-ErrorHandling
        
        if ($GenerateReport) {
            Generate-TestReport $allResults
        }
    }
    "infrastructure" { Test-BackendInfrastructure }
    "scanners" { Test-ScannerIntegrations }
    "websockets" { Test-WebSocketFunctionality }
    "frontend" { Test-FrontendComponents }
    "integration" { Test-SystemIntegration }
    "performance" { Test-Performance }
    "security" { Test-Security }
    "errors" { Test-ErrorHandling }
    default {
        Write-Host "Unknown test suite: $TestSuite" -ForegroundColor Red
        Write-Host "Run '.\scripts\test-enterprise.ps1 help' for available options" -ForegroundColor Yellow
        exit 1
    }
} 
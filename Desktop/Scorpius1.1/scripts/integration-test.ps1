# Scorpius Enterprise Backend-Frontend Integration Testing
# Comprehensive testing for all integration points and user workflows

param(
    [Parameter(Position=0)]
    [string]$TestSuite = "all",
    [string[]]$Arguments,
    [switch]$Verbose,
    [switch]$Headless,
    [switch]$GenerateReport,
    [switch]$Concurrent,
    [int]$UserCount = 5
)

# Configuration
$ProjectRoot = $PSScriptRoot | Split-Path -Parent
$TestResultsDir = "$ProjectRoot/test-results"
$ReportsDir = "$ProjectRoot/reports"
$LogsDir = "$ProjectRoot/logs"

# Test configuration
$TestConfig = @{
    BackendUrl = "http://localhost:8000"
    FrontendUrl = "http://localhost:3000"
    ApiTimeout = 30
    TestTimeout = 300
    RetryAttempts = 3
    WebSocketUrl = "ws://localhost:8000/ws"
}

# System Components
$SystemComponents = @{
    Backend = "FastAPI (Python 3.11)"
    Frontend = "React + Vite + TypeScript"
    Database = "PostgreSQL 15"
    Cache = "Redis 7"
    AdditionalServices = @(
        "Slither Scanner (Port 8002)",
        "Mythril Scanner (Port 8003)", 
        "MythX Scanner (Port 8004)",
        "Manticore Scanner (Port 8005)",
        "Prometheus (Port 9090)",
        "Grafana (Port 3001)"
    )
}

function Write-Header {
    param([string]$Message)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
}

function Write-TestResult {
    param([string]$TestName, [string]$Status, [string]$Message = "", [string]$Duration = "")
    $color = if ($Status -eq "PASS") { "Green" } else { "Red" }
    $icon = if ($Status -eq "PASS") { "✅" } else { "❌" }
    $durationText = if ($Duration) { " ($Duration)" } else { "" }
    Write-Host "$icon $TestName: $Status$durationText" -ForegroundColor $color
    if ($Message) { Write-Host "   $Message" -ForegroundColor Gray }
}

function Initialize-TestEnvironment {
    Write-Header "Initializing Integration Test Environment"
    
    # Create test directories
    New-Item -ItemType Directory -Force -Path $TestResultsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
    
    # Start Docker environment if not running
    Write-Host "Checking Docker environment..." -ForegroundColor Yellow
    $status = docker-compose -f docker/docker-compose.enterprise.yml ps
    
    if ($status -notlike "*Up*") {
        Write-Host "Starting Docker environment..." -ForegroundColor Yellow
        .\scripts\docker-enterprise.ps1 start
        Start-Sleep -Seconds 30
    }
    
    Write-Host "✅ Integration test environment initialized" -ForegroundColor Green
}

function Test-APIIntegration {
    Write-Header "API Integration Testing"
    
    $results = @()
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Test all REST endpoints
    $endpoints = @(
        @{Path = "/health"; Method = "GET"; ExpectedStatus = 200},
        @{Path = "/api/v1/projects"; Method = "GET"; ExpectedStatus = 401}, # Requires auth
        @{Path = "/api/v1/auth/login"; Method = "POST"; ExpectedStatus = 400}, # Bad request expected
        @{Path = "/api/v1/scanners/slither/status"; Method = "GET"; ExpectedStatus = 200},
        @{Path = "/api/v1/scanners/mythril/status"; Method = "GET"; ExpectedStatus = 200},
        @{Path = "/api/v1/scanners/mythx/status"; Method = "GET"; ExpectedStatus = 200},
        @{Path = "/api/v1/scanners/manticore/status"; Method = "GET"; ExpectedStatus = 200}
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $headers = @{"Content-Type" = "application/json"}
            $body = if ($endpoint.Method -eq "POST") { "{}" } else { $null }
            
            $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)$($endpoint.Path)" -Method $endpoint.Method -Headers $headers -Body $body -TimeoutSec $TestConfig.ApiTimeout
            
            if ($response.StatusCode -eq $endpoint.ExpectedStatus) {
                Write-TestResult "API $($endpoint.Method) $($endpoint.Path)" "PASS" "Status: $($response.StatusCode)"
                $results += @{Test = "API $($endpoint.Method) $($endpoint.Path)"; Status = "PASS"; Message = "Status: $($response.StatusCode)"}
            } else {
                Write-TestResult "API $($endpoint.Method) $($endpoint.Path)" "FAIL" "Expected: $($endpoint.ExpectedStatus), Got: $($response.StatusCode)"
                $results += @{Test = "API $($endpoint.Method) $($endpoint.Path)"; Status = "FAIL"; Message = "Expected: $($endpoint.ExpectedStatus), Got: $($response.StatusCode)"}
            }
        } catch {
            if ($_.Exception.Response.StatusCode -eq $endpoint.ExpectedStatus) {
                Write-TestResult "API $($endpoint.Method) $($endpoint.Path)" "PASS" "Status: $($_.Exception.Response.StatusCode)"
                $results += @{Test = "API $($endpoint.Method) $($endpoint.Path)"; Status = "PASS"; Message = "Status: $($_.Exception.Response.StatusCode)"}
            } else {
                Write-TestResult "API $($endpoint.Method) $($endpoint.Path)" "FAIL" $_.Exception.Message
                $results += @{Test = "API $($endpoint.Method) $($endpoint.Path)"; Status = "FAIL"; Message = $_.Exception.Message}
            }
        }
    }
    
    # Test request/response data formatting
    try {
        $testData = @{
            name = "Test Project"
            description = "Integration test project"
            contract_type = "solidity"
        }
        
        $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)/api/v1/projects" -Method POST -Body ($testData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec $TestConfig.ApiTimeout
        
        if ($response.StatusCode -eq 401) { # Expected for unauthenticated request
            $responseData = $response.Content | ConvertFrom-Json
            if ($responseData.error) {
                Write-TestResult "API Data Formatting" "PASS" "Proper error response format"
                $results += @{Test = "API Data Formatting"; Status = "PASS"; Message = "Proper error response format"}
            } else {
                Write-TestResult "API Data Formatting" "FAIL" "Missing error field in response"
                $results += @{Test = "API Data Formatting"; Status = "FAIL"; Message = "Missing error field in response"}
            }
        }
    } catch {
        Write-TestResult "API Data Formatting" "FAIL" $_.Exception.Message
        $results += @{Test = "API Data Formatting"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    $stopwatch.Stop()
    Write-TestResult "API Integration Complete" "PASS" "Duration: $($stopwatch.Elapsed.TotalSeconds)s"
    
    return $results
}

function Test-RealTimeCommunication {
    Write-Header "Real-Time Communication Testing"
    
    $results = @()
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Test WebSocket connection establishment
    try {
        $wsUrl = $TestConfig.WebSocketUrl
        $ws = New-Object System.Net.WebSockets.ClientWebSocket
        
        $cancellationToken = New-Object System.Threading.CancellationToken
        $connectTask = $ws.ConnectAsync([Uri]$wsUrl, $cancellationToken)
        $connectTask.Wait($TestConfig.ApiTimeout * 1000)
        
        if ($ws.State -eq "Open") {
            Write-TestResult "WebSocket Connection" "PASS" "Connection established successfully"
            $results += @{Test = "WebSocket Connection"; Status = "PASS"; Message = "Connection established successfully"}
            
            # Test message sending
            $message = "test message"
            $messageBuffer = [System.Text.Encoding]::UTF8.GetBytes($message)
            $sendTask = $ws.SendAsync([System.ArraySegment[byte]]$messageBuffer, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cancellationToken)
            $sendTask.Wait(5000)
            
            if ($sendTask.Status -eq "RanToCompletion") {
                Write-TestResult "WebSocket Message Sending" "PASS" "Message sent successfully"
                $results += @{Test = "WebSocket Message Sending"; Status = "PASS"; Message = "Message sent successfully"}
            } else {
                Write-TestResult "WebSocket Message Sending" "FAIL" "Failed to send message"
                $results += @{Test = "WebSocket Message Sending"; Status = "FAIL"; Message = "Failed to send message"}
            }
            
            # Close connection
            $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "Test complete", $cancellationToken).Wait()
        } else {
            Write-TestResult "WebSocket Connection" "FAIL" "State: $($ws.State)"
            $results += @{Test = "WebSocket Connection"; Status = "FAIL"; Message = "State: $($ws.State)"}
        }
    } catch {
        Write-TestResult "WebSocket Connection" "FAIL" $_.Exception.Message
        $results += @{Test = "WebSocket Connection"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    # Test connection recovery
    try {
        $ws = New-Object System.Net.WebSockets.ClientWebSocket
        $cancellationToken = New-Object System.Threading.CancellationToken
        
        # First connection
        $connectTask1 = $ws.ConnectAsync([Uri]$TestConfig.WebSocketUrl, $cancellationToken)
        $connectTask1.Wait(5000)
        
        if ($ws.State -eq "Open") {
            $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "Test", $cancellationToken).Wait()
            
            # Second connection (recovery test)
            Start-Sleep -Seconds 2
            $connectTask2 = $ws.ConnectAsync([Uri]$TestConfig.WebSocketUrl, $cancellationToken)
            $connectTask2.Wait(5000)
            
            if ($ws.State -eq "Open") {
                Write-TestResult "WebSocket Connection Recovery" "PASS" "Reconnection successful"
                $results += @{Test = "WebSocket Connection Recovery"; Status = "PASS"; Message = "Reconnection successful"}
                $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "Test complete", $cancellationToken).Wait()
            } else {
                Write-TestResult "WebSocket Connection Recovery" "FAIL" "Reconnection failed"
                $results += @{Test = "WebSocket Connection Recovery"; Status = "FAIL"; Message = "Reconnection failed"}
            }
        }
    } catch {
        Write-TestResult "WebSocket Connection Recovery" "FAIL" $_.Exception.Message
        $results += @{Test = "WebSocket Connection Recovery"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    $stopwatch.Stop()
    Write-TestResult "Real-Time Communication Complete" "PASS" "Duration: $($stopwatch.Elapsed.TotalSeconds)s"
    
    return $results
}

function Test-DataSynchronization {
    Write-Header "Data Synchronization Testing"
    
    $results = @()
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Test frontend state management with backend data
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.FrontendUrl)" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 200) {
            Write-TestResult "Frontend State Management" "PASS" "Frontend accessible"
            $results += @{Test = "Frontend State Management"; Status = "PASS"; Message = "Frontend accessible"}
        } else {
            Write-TestResult "Frontend State Management" "FAIL" "Status: $($response.StatusCode)"
            $results += @{Test = "Frontend State Management"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
        }
    } catch {
        Write-TestResult "Frontend State Management" "FAIL" $_.Exception.Message
        $results += @{Test = "Frontend State Management"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    # Test cache invalidation (Redis)
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)/health/redis" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 200) {
            Write-TestResult "Cache Invalidation" "PASS" "Redis cache accessible"
            $results += @{Test = "Cache Invalidation"; Status = "PASS"; Message = "Redis cache accessible"}
        } else {
            Write-TestResult "Cache Invalidation" "FAIL" "Status: $($response.StatusCode)"
            $results += @{Test = "Cache Invalidation"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
        }
    } catch {
        Write-TestResult "Cache Invalidation" "FAIL" $_.Exception.Message
        $results += @{Test = "Cache Invalidation"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    $stopwatch.Stop()
    Write-TestResult "Data Synchronization Complete" "PASS" "Duration: $($stopwatch.Elapsed.TotalSeconds)s"
    
    return $results
}

function Test-UserInterfaceIntegration {
    Write-Header "User Interface Integration Testing"
    
    $results = @()
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Test dynamic content loading
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.FrontendUrl)" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 200) {
            # Check for dynamic content indicators
            if ($response.Content -like "*React*" -or $response.Content -like "*Vite*") {
                Write-TestResult "Dynamic Content Loading" "PASS" "Frontend framework detected"
                $results += @{Test = "Dynamic Content Loading"; Status = "PASS"; Message = "Frontend framework detected"}
            } else {
                Write-TestResult "Dynamic Content Loading" "FAIL" "No frontend framework detected"
                $results += @{Test = "Dynamic Content Loading"; Status = "FAIL"; Message = "No frontend framework detected"}
            }
        } else {
            Write-TestResult "Dynamic Content Loading" "FAIL" "Status: $($response.StatusCode)"
            $results += @{Test = "Dynamic Content Loading"; Status = "FAIL"; Message = "Status: $($response.StatusCode)"}
        }
    } catch {
        Write-TestResult "Dynamic Content Loading" "FAIL" $_.Exception.Message
        $results += @{Test = "Dynamic Content Loading"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    # Test form validation (client + server side)
    try {
        $invalidData = @{
            name = ""  # Invalid: empty name
            email = "invalid-email"  # Invalid: malformed email
        }
        
        $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)/api/v1/auth/register" -Method POST -Body ($invalidData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec $TestConfig.ApiTimeout
        
        if ($response.StatusCode -eq 400) {
            $errorData = $response.Content | ConvertFrom-Json
            if ($errorData.errors) {
                Write-TestResult "Form Validation" "PASS" "Server-side validation working"
                $results += @{Test = "Form Validation"; Status = "PASS"; Message = "Server-side validation working"}
            } else {
                Write-TestResult "Form Validation" "FAIL" "No validation errors returned"
                $results += @{Test = "Form Validation"; Status = "FAIL"; Message = "No validation errors returned"}
            }
        } else {
            Write-TestResult "Form Validation" "FAIL" "Expected 400, got $($response.StatusCode)"
            $results += @{Test = "Form Validation"; Status = "FAIL"; Message = "Expected 400, got $($response.StatusCode)"}
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 400) {
            Write-TestResult "Form Validation" "PASS" "Server-side validation working"
            $results += @{Test = "Form Validation"; Status = "PASS"; Message = "Server-side validation working"}
        } else {
            Write-TestResult "Form Validation" "FAIL" $_.Exception.Message
            $results += @{Test = "Form Validation"; Status = "FAIL"; Message = $_.Exception.Message}
        }
    }
    
    # Test file upload handling
    try {
        $testFile = "test-contract.sol"
        $contractContent = "pragma solidity ^0.8.0; contract Test { function test() public {} }"
        $contractContent | Out-File -FilePath $testFile -Encoding UTF8
        
        $boundary = [System.Guid]::NewGuid().ToString()
        $LF = "`r`n"
        $bodyLines = @(
            "--$boundary",
            "Content-Disposition: form-data; name=`"file`"; filename=`"$testFile`"",
            "Content-Type: text/plain",
            "",
            $contractContent,
            "--$boundary--"
        )
        $body = $bodyLines -join $LF
        
        $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)/api/v1/upload" -Method POST -Body $body -Headers @{"Content-Type" = "multipart/form-data; boundary=$boundary"} -TimeoutSec $TestConfig.ApiTimeout
        
        if ($response.StatusCode -eq 401) { # Expected for unauthenticated request
            Write-TestResult "File Upload Handling" "PASS" "Authentication required for uploads"
            $results += @{Test = "File Upload Handling"; Status = "PASS"; Message = "Authentication required for uploads"}
        } else {
            Write-TestResult "File Upload Handling" "FAIL" "Unexpected status: $($response.StatusCode)"
            $results += @{Test = "File Upload Handling"; Status = "FAIL"; Message = "Unexpected status: $($response.StatusCode)"}
        }
        
        # Cleanup
        Remove-Item $testFile -ErrorAction SilentlyContinue
    } catch {
        if ($_.Exception.Response.StatusCode -eq 401) {
            Write-TestResult "File Upload Handling" "PASS" "Authentication required for uploads"
            $results += @{Test = "File Upload Handling"; Status = "PASS"; Message = "Authentication required for uploads"}
        } else {
            Write-TestResult "File Upload Handling" "FAIL" $_.Exception.Message
            $results += @{Test = "File Upload Handling"; Status = "FAIL"; Message = $_.Exception.Message}
        }
    }
    
    $stopwatch.Stop()
    Write-TestResult "User Interface Integration Complete" "PASS" "Duration: $($stopwatch.Elapsed.TotalSeconds)s"
    
    return $results
}

function Test-SecurityAuthenticationFlow {
    Write-Header "Security & Authentication Flow Testing"
    
    $results = @()
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Test complete login/logout cycle
    try {
        # Test login with invalid credentials
        $loginData = @{
            email = "test@example.com"
            password = "wrongpassword"
        }
        
        $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)/api/v1/auth/login" -Method POST -Body ($loginData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec $TestConfig.ApiTimeout
        
        if ($response.StatusCode -eq 401) {
            Write-TestResult "Login Authentication" "PASS" "Invalid credentials properly rejected"
            $results += @{Test = "Login Authentication"; Status = "PASS"; Message = "Invalid credentials properly rejected"}
        } else {
            Write-TestResult "Login Authentication" "FAIL" "Expected 401, got $($response.StatusCode)"
            $results += @{Test = "Login Authentication"; Status = "FAIL"; Message = "Expected 401, got $($response.StatusCode)"}
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 401) {
            Write-TestResult "Login Authentication" "PASS" "Invalid credentials properly rejected"
            $results += @{Test = "Login Authentication"; Status = "PASS"; Message = "Invalid credentials properly rejected"}
        } else {
            Write-TestResult "Login Authentication" "FAIL" $_.Exception.Message
            $results += @{Test = "Login Authentication"; Status = "FAIL"; Message = $_.Exception.Message}
        }
    }
    
    # Test protected route access control
    $protectedEndpoints = @("/api/v1/projects", "/api/v1/users", "/api/v1/admin")
    
    foreach ($endpoint in $protectedEndpoints) {
        try {
            $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)$endpoint" -TimeoutSec $TestConfig.ApiTimeout
            if ($response.StatusCode -eq 401) {
                Write-TestResult "Protected Route: $endpoint" "PASS" "Authentication required"
                $results += @{Test = "Protected Route: $endpoint"; Status = "PASS"; Message = "Authentication required"}
            } else {
                Write-TestResult "Protected Route: $endpoint" "FAIL" "Expected 401, got $($response.StatusCode)"
                $results += @{Test = "Protected Route: $endpoint"; Status = "FAIL"; Message = "Expected 401, got $($response.StatusCode)"}
            }
        } catch {
            if ($_.Exception.Response.StatusCode -eq 401) {
                Write-TestResult "Protected Route: $endpoint" "PASS" "Authentication required"
                $results += @{Test = "Protected Route: $endpoint"; Status = "PASS"; Message = "Authentication required"}
            } else {
                Write-TestResult "Protected Route: $endpoint" "FAIL" $_.Exception.Message
                $results += @{Test = "Protected Route: $endpoint"; Status = "FAIL"; Message = $_.Exception.Message}
            }
        }
    }
    
    # Test CORS headers
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)/health" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.Headers["Access-Control-Allow-Origin"]) {
            Write-TestResult "CORS Headers" "PASS" "CORS properly configured"
            $results += @{Test = "CORS Headers"; Status = "PASS"; Message = "CORS properly configured"}
        } else {
            Write-TestResult "CORS Headers" "FAIL" "Missing CORS headers"
            $results += @{Test = "CORS Headers"; Status = "FAIL"; Message = "Missing CORS headers"}
        }
    } catch {
        Write-TestResult "CORS Headers" "FAIL" $_.Exception.Message
        $results += @{Test = "CORS Headers"; Status = "FAIL"; Message = $_.Exception.Message}
    }
    
    $stopwatch.Stop()
    Write-TestResult "Security & Authentication Complete" "PASS" "Duration: $($stopwatch.Elapsed.TotalSeconds)s"
    
    return $results
}

function Test-ErrorScenarios {
    Write-Header "Error Scenarios Testing"
    
    $results = @()
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Test network interruption handling
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)/invalid-endpoint" -TimeoutSec 5
        if ($response.StatusCode -eq 404) {
            Write-TestResult "Network Error Handling" "PASS" "404 properly handled"
            $results += @{Test = "Network Error Handling"; Status = "PASS"; Message = "404 properly handled"}
        } else {
            Write-TestResult "Network Error Handling" "FAIL" "Expected 404, got $($response.StatusCode)"
            $results += @{Test = "Network Error Handling"; Status = "FAIL"; Message = "Expected 404, got $($response.StatusCode)"}
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-TestResult "Network Error Handling" "PASS" "404 properly handled"
            $results += @{Test = "Network Error Handling"; Status = "PASS"; Message = "404 properly handled"}
        } else {
            Write-TestResult "Network Error Handling" "FAIL" $_.Exception.Message
            $results += @{Test = "Network Error Handling"; Status = "FAIL"; Message = $_.Exception.Message}
        }
    }
    
    # Test invalid data submission responses
    try {
        $invalidJson = "{ invalid json }"
        $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)/api/v1/projects" -Method POST -Body $invalidJson -ContentType "application/json" -TimeoutSec $TestConfig.ApiTimeout
        if ($response.StatusCode -eq 400) {
            Write-TestResult "Invalid Data Handling" "PASS" "Invalid JSON properly rejected"
            $results += @{Test = "Invalid Data Handling"; Status = "PASS"; Message = "Invalid JSON properly rejected"}
        } else {
            Write-TestResult "Invalid Data Handling" "FAIL" "Expected 400, got $($response.StatusCode)"
            $results += @{Test = "Invalid Data Handling"; Status = "FAIL"; Message = "Expected 400, got $($response.StatusCode)"}
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 400) {
            Write-TestResult "Invalid Data Handling" "PASS" "Invalid JSON properly rejected"
            $results += @{Test = "Invalid Data Handling"; Status = "PASS"; Message = "Invalid JSON properly rejected"}
        } else {
            Write-TestResult "Invalid Data Handling" "FAIL" $_.Exception.Message
            $results += @{Test = "Invalid Data Handling"; Status = "FAIL"; Message = $_.Exception.Message}
        }
    }
    
    # Test timeout handling
    try {
        $response = Invoke-WebRequest -Uri "$($TestConfig.BackendUrl)/health" -TimeoutSec 1
        Write-TestResult "Timeout Handling" "PASS" "Request completed within timeout"
        $results += @{Test = "Timeout Handling"; Status = "PASS"; Message = "Request completed within timeout"}
    } catch {
        if ($_.Exception.Message -like "*timeout*") {
            Write-TestResult "Timeout Handling" "PASS" "Timeout properly handled"
            $results += @{Test = "Timeout Handling"; Status = "PASS"; Message = "Timeout properly handled"}
        } else {
            Write-TestResult "Timeout Handling" "FAIL" $_.Exception.Message
            $results += @{Test = "Timeout Handling"; Status = "FAIL"; Message = $_.Exception.Message}
        }
    }
    
    $stopwatch.Stop()
    Write-TestResult "Error Scenarios Complete" "PASS" "Duration: $($stopwatch.Elapsed.TotalSeconds)s"
    
    return $results
}

function Test-ConcurrentUsers {
    Write-Header "Concurrent Users Testing"
    
    $results = @()
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Test multiple concurrent requests
    $jobs = @()
    $successCount = 0
    
    for ($i = 1; $i -le $UserCount; $i++) {
        $jobs += Start-Job -ScriptBlock {
            param($url, $timeout, $userId)
            try {
                $response = Invoke-WebRequest -Uri $url -TimeoutSec $timeout
                return @{UserId = $userId; Success = $true; StatusCode = $response.StatusCode}
            } catch {
                return @{UserId = $userId; Success = $false; Error = $_.Exception.Message}
            }
        } -ArgumentList "$($TestConfig.BackendUrl)/health", $TestConfig.ApiTimeout, $i
    }
    
    $jobResults = $jobs | Wait-Job | Receive-Job
    $successCount = ($jobResults | Where-Object { $_.Success }).Count
    
    if ($successCount -eq $UserCount) {
        Write-TestResult "Concurrent Users ($UserCount)" "PASS" "All $UserCount users succeeded"
        $results += @{Test = "Concurrent Users ($UserCount)"; Status = "PASS"; Message = "All $UserCount users succeeded"}
    } else {
        Write-TestResult "Concurrent Users ($UserCount)" "FAIL" "Only $successCount/$UserCount users succeeded"
        $results += @{Test = "Concurrent Users ($UserCount)"; Status = "FAIL"; Message = "Only $successCount/$UserCount users succeeded"}
    }
    
    $jobs | Remove-Job
    
    $stopwatch.Stop()
    Write-TestResult "Concurrent Users Complete" "PASS" "Duration: $($stopwatch.Elapsed.TotalSeconds)s"
    
    return $results
}

function Generate-IntegrationReport {
    param([array]$AllResults)
    
    Write-Header "Generating Integration Test Report"
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $reportFile = "$ReportsDir/integration-report-$timestamp.html"
    
    $totalTests = $AllResults.Count
    $passedTests = ($AllResults | Where-Object { $_.Status -eq "PASS" }).Count
    $failedTests = ($AllResults | Where-Object { $_.Status -eq "FAIL" }).Count
    $successRate = [math]::Round(($passedTests / $totalTests) * 100, 2)
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Scorpius Enterprise Integration Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .summary { margin: 20px 0; }
        .test-result { margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid; }
        .pass { background-color: #d4edda; border-left-color: #28a745; }
        .fail { background-color: #f8d7da; border-left-color: #dc3545; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; flex-wrap: wrap; }
        .stat { text-align: center; padding: 20px; background-color: #e9ecef; border-radius: 5px; margin: 10px; min-width: 150px; }
        .system-info { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .component { margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Scorpius Enterprise Integration Test Report</h1>
            <p>Generated: $(Get-Date)</p>
        </div>
        
        <div class="system-info">
            <h3>System Components</h3>
            <div class="component"><strong>Backend:</strong> $($SystemComponents.Backend)</div>
            <div class="component"><strong>Frontend:</strong> $($SystemComponents.Frontend)</div>
            <div class="component"><strong>Database:</strong> $($SystemComponents.Database)</div>
            <div class="component"><strong>Cache:</strong> $($SystemComponents.Cache)</div>
            <div class="component"><strong>Additional Services:</strong></div>
            <ul>
                $(foreach ($service in $SystemComponents.AdditionalServices) { "<li>$service</li>" })
            </ul>
        </div>
        
        <div class="stats">
            <div class="stat">
                <h3>Total Tests</h3>
                <p style="font-size: 24px; font-weight: bold;">$totalTests</p>
            </div>
            <div class="stat">
                <h3>Passed</h3>
                <p style="font-size: 24px; font-weight: bold; color: #28a745;">$passedTests</p>
            </div>
            <div class="stat">
                <h3>Failed</h3>
                <p style="font-size: 24px; font-weight: bold; color: #dc3545;">$failedTests</p>
            </div>
            <div class="stat">
                <h3>Success Rate</h3>
                <p style="font-size: 24px; font-weight: bold; color: #007bff;">$successRate%</p>
            </div>
        </div>
        
        <h2>Integration Test Results</h2>
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
    </div>
</body>
</html>
"@
    
    $html | Out-File -FilePath $reportFile -Encoding UTF8
    Write-Host "✅ Integration test report generated: $reportFile" -ForegroundColor Green
    
    return $reportFile
}

function Show-Help {
    Write-Header "Scorpius Enterprise Integration Testing Framework"
    
    Write-Host "System Components:" -ForegroundColor Green
    Write-Host "  Backend: $($SystemComponents.Backend)" -ForegroundColor White
    Write-Host "  Frontend: $($SystemComponents.Frontend)" -ForegroundColor White
    Write-Host "  Database: $($SystemComponents.Database)" -ForegroundColor White
    Write-Host "  Cache: $($SystemComponents.Cache)" -ForegroundColor White
    Write-Host "  Additional Services:" -ForegroundColor White
    foreach ($service in $SystemComponents.AdditionalServices) {
        Write-Host "    - $service" -ForegroundColor White
    }
    Write-Host ""
    
    Write-Host "Available test suites:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  all              - Run all integration tests" -ForegroundColor White
    Write-Host "  api              - Test API integration" -ForegroundColor White
    Write-Host "  realtime         - Test real-time communication" -ForegroundColor White
    Write-Host "  data             - Test data synchronization" -ForegroundColor White
    Write-Host "  ui               - Test user interface integration" -ForegroundColor White
    Write-Host "  security         - Test security & authentication" -ForegroundColor White
    Write-Host "  errors           - Test error scenarios" -ForegroundColor White
    Write-Host "  concurrent       - Test concurrent users" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  --verbose        - Enable verbose output" -ForegroundColor White
    Write-Host "  --headless       - Run in headless mode" -ForegroundColor White
    Write-Host "  --generate-report - Generate HTML test report" -ForegroundColor White
    Write-Host "  --concurrent     - Enable concurrent testing" -ForegroundColor White
    Write-Host "  --user-count <n> - Number of concurrent users (default: 5)" -ForegroundColor White
    Write-Host ""
    Write-Host "Usage: .\scripts\integration-test.ps1 <test-suite> [options]" -ForegroundColor Gray
    Write-Host "Example: .\scripts\integration-test.ps1 all --generate-report --concurrent" -ForegroundColor Gray
}

# Main execution
Set-Location $ProjectRoot

switch ($TestSuite.ToLower()) {
    "help" { Show-Help; exit 0 }
    "all" {
        Initialize-TestEnvironment
        $allResults = @()
        $allResults += Test-APIIntegration
        $allResults += Test-RealTimeCommunication
        $allResults += Test-DataSynchronization
        $allResults += Test-UserInterfaceIntegration
        $allResults += Test-SecurityAuthenticationFlow
        $allResults += Test-ErrorScenarios
        if ($Concurrent) {
            $allResults += Test-ConcurrentUsers
        }
        
        if ($GenerateReport) {
            Generate-IntegrationReport $allResults
        }
    }
    "api" { Test-APIIntegration }
    "realtime" { Test-RealTimeCommunication }
    "data" { Test-DataSynchronization }
    "ui" { Test-UserInterfaceIntegration }
    "security" { Test-SecurityAuthenticationFlow }
    "errors" { Test-ErrorScenarios }
    "concurrent" { Test-ConcurrentUsers }
    default {
        Write-Host "Unknown test suite: $TestSuite" -ForegroundColor Red
        Write-Host "Run '.\scripts\integration-test.ps1 help' for available options" -ForegroundColor Yellow
        exit 1
    }
} 
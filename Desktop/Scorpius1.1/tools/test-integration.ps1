#!/usr/bin/env pwsh
# Dashboard Integration Test Script
# Tests the connection between the Fusion Dashboard and Backend API

Write-Host "🧪 Scorpius Dashboard Integration Tests" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$TestResults = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [object]$Body = $null
    )
    
    try {
        Write-Host "Testing $Name..." -ForegroundColor Yellow -NoNewline
        
        $params = @{
            Uri = $Url
            Method = $Method
            TimeoutSec = 10
            Headers = $Headers
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        Write-Host " ✅ PASS" -ForegroundColor Green
        return @{ Name = $Name; Status = "PASS"; Response = $response }
    }
    catch {
        Write-Host " ❌ FAIL - $($_.Exception.Message)" -ForegroundColor Red
        return @{ Name = $Name; Status = "FAIL"; Error = $_.Exception.Message }
    }
}

function Test-WebSocketConnection {
    param([string]$Url)
    
    try {
        Write-Host "Testing WebSocket connection..." -ForegroundColor Yellow -NoNewline
        
        # Simple WebSocket test using .NET WebSocket
        Add-Type -AssemblyName System.Net.WebSockets
        $ws = New-Object System.Net.WebSockets.ClientWebSocket
        $uri = [System.Uri]::new($Url)
        $token = [System.Threading.CancellationToken]::None
        
        $task = $ws.ConnectAsync($uri, $token)
        $task.Wait(5000)  # 5 second timeout
        
        if ($ws.State -eq [System.Net.WebSockets.WebSocketState]::Open) {
            Write-Host " ✅ PASS" -ForegroundColor Green
            $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "Test complete", $token).Wait(1000)
            return @{ Name = "WebSocket Connection"; Status = "PASS" }
        } else {
            Write-Host " ❌ FAIL - Connection not opened" -ForegroundColor Red
            return @{ Name = "WebSocket Connection"; Status = "FAIL"; Error = "Connection not opened" }
        }
    }
    catch {
        Write-Host " ❌ FAIL - $($_.Exception.Message)" -ForegroundColor Red
        return @{ Name = "WebSocket Connection"; Status = "FAIL"; Error = $_.Exception.Message }
    }
}

# Test Configuration
$ApiBaseUrl = "http://localhost:8000"
$DashboardUrl = "http://localhost:3000"
$WebSocketUrl = "ws://localhost:8000/ws"

Write-Host ""
Write-Host "🔧 Configuration:" -ForegroundColor Cyan
Write-Host "   API Base URL: $ApiBaseUrl" -ForegroundColor White
Write-Host "   Dashboard URL: $DashboardUrl" -ForegroundColor White
Write-Host "   WebSocket URL: $WebSocketUrl" -ForegroundColor White
Write-Host ""

# Health Check Tests
Write-Host "🏥 Health Check Tests" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan

$TestResults += Test-Endpoint -Name "API Gateway Health" -Url "$ApiBaseUrl/healthz"
$TestResults += Test-Endpoint -Name "API Gateway Readiness" -Url "$ApiBaseUrl/readyz"
$TestResults += Test-Endpoint -Name "Dashboard Health" -Url "$DashboardUrl" -Method "GET"

# API Endpoint Tests
Write-Host ""
Write-Host "🔌 API Endpoint Tests" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan

$TestResults += Test-Endpoint -Name "System Status" -Url "$ApiBaseUrl/api/v1/system/status"
$TestResults += Test-Endpoint -Name "System Metrics" -Url "$ApiBaseUrl/api/v1/system/metrics"
$TestResults += Test-Endpoint -Name "Trading Stats" -Url "$ApiBaseUrl/api/v1/trading/stats"
$TestResults += Test-Endpoint -Name "Trading Bots" -Url "$ApiBaseUrl/api/v1/trading/bots"
$TestResults += Test-Endpoint -Name "Bridge Status" -Url "$ApiBaseUrl/api/v1/bridge/status"
$TestResults += Test-Endpoint -Name "Analytics KPI" -Url "$ApiBaseUrl/api/v1/analytics/kpi"
$TestResults += Test-Endpoint -Name "Scanner Results" -Url "$ApiBaseUrl/api/v1/scanner/results"
$TestResults += Test-Endpoint -Name "Computing Cluster" -Url "$ApiBaseUrl/api/v1/computing/cluster"

# Authentication Tests
Write-Host ""
Write-Host "🔐 Authentication Tests" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

$loginBody = @{
    username = "admin"
    password = "admin"
}

$loginResult = Test-Endpoint -Name "User Login" -Url "$ApiBaseUrl/api/v1/auth/login" -Method "POST" -Body $loginBody
$TestResults += $loginResult

if ($loginResult.Status -eq "PASS" -and $loginResult.Response.access_token) {
    $token = $loginResult.Response.access_token
    $authHeaders = @{ "Authorization" = "Bearer $token" }
    
    $TestResults += Test-Endpoint -Name "Token Verification" -Url "$ApiBaseUrl/api/v1/auth/verify" -Headers $authHeaders
    $TestResults += Test-Endpoint -Name "User Logout" -Url "$ApiBaseUrl/api/v1/auth/logout" -Method "POST" -Headers $authHeaders
}

# WebSocket Tests
Write-Host ""
Write-Host "🔗 WebSocket Tests" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan

$TestResults += Test-WebSocketConnection -Url $WebSocketUrl

# CORS Tests
Write-Host ""
Write-Host "🌐 CORS Tests" -ForegroundColor Cyan
Write-Host "==============" -ForegroundColor Cyan

$corsHeaders = @{
    "Origin" = "http://localhost:3000"
    "Access-Control-Request-Method" = "GET"
}

$TestResults += Test-Endpoint -Name "CORS Preflight" -Url "$ApiBaseUrl/api/v1/system/status" -Method "OPTIONS" -Headers $corsHeaders

# Performance Tests
Write-Host ""
Write-Host "⚡ Performance Tests" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
try {
    Invoke-RestMethod -Uri "$ApiBaseUrl/api/v1/system/metrics" -TimeoutSec 5 | Out-Null
    $responseTime = $stopwatch.ElapsedMilliseconds
    
    if ($responseTime -lt 1000) {
        Write-Host "API Response Time: $responseTime ms ✅ PASS" -ForegroundColor Green
        $TestResults += @{ Name = "API Response Time"; Status = "PASS"; ResponseTime = $responseTime }
    } else {
        Write-Host "API Response Time: $responseTime ms ❌ SLOW" -ForegroundColor Yellow
        $TestResults += @{ Name = "API Response Time"; Status = "SLOW"; ResponseTime = $responseTime }
    }
}
catch {
    Write-Host "API Response Time: Timeout ❌ FAIL" -ForegroundColor Red
    $TestResults += @{ Name = "API Response Time"; Status = "FAIL"; Error = "Timeout" }
}
$stopwatch.Stop()

# Test Summary
Write-Host ""
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan

$passed = ($TestResults | Where-Object { $_.Status -eq "PASS" }).Count
$failed = ($TestResults | Where-Object { $_.Status -eq "FAIL" }).Count
$slow = ($TestResults | Where-Object { $_.Status -eq "SLOW" }).Count
$total = $TestResults.Count

Write-Host ""
Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
Write-Host "Slow: $slow" -ForegroundColor Yellow
Write-Host ""

if ($failed -eq 0) {
    Write-Host "🎉 All tests passed! Dashboard integration is working correctly." -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Please check the errors above." -ForegroundColor Yellow
    
    Write-Host ""
    Write-Host "Failed Tests:" -ForegroundColor Red
    $TestResults | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "   - $($_.Name): $($_.Error)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🔧 Troubleshooting Tips:" -ForegroundColor Cyan
Write-Host "   1. Ensure all services are running: docker-compose -f docker-compose.dev.yml ps" -ForegroundColor White
Write-Host "   2. Check service logs: docker-compose -f docker-compose.dev.yml logs api-gateway dashboard" -ForegroundColor White
Write-Host "   3. Verify environment variables are set correctly" -ForegroundColor White
Write-Host "   4. Try restarting services: .\dashboard-start.ps1 -Clean" -ForegroundColor White

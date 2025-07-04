#!/usr/bin/env pwsh

<#
.SYNOPSIS
Scorpius Enterprise Platform Test Script
Tests all services and endpoints to verify the platform is working correctly

.DESCRIPTION
This script will:
1. Check if all services are running
2. Test API Gateway endpoints
3. Test individual microservices
4. Display service URLs and status
5. Run basic functionality tests

.EXAMPLE
./test-scorpius.ps1
Run all tests and display service status
#>

# Color output functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Magenta" = [ConsoleColor]::Magenta
        "Cyan" = [ConsoleColor]::Cyan
        "White" = [ConsoleColor]::White
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

function Write-Success { param([string]$Message) Write-ColorOutput "✅ $Message" "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput "❌ $Message" "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput "⚠️ $Message" "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ️ $Message" "Blue" }
function Write-Test { param([string]$Message) Write-ColorOutput "🧪 $Message" "Cyan" }

function Test-Endpoint {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$TimeoutSec = 10
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec
        if ($response.StatusCode -eq 200) {
            Write-Success "$ServiceName is responding (Status: $($response.StatusCode))"
            return $true
        } else {
            Write-Warning "$ServiceName returned status: $($response.StatusCode)"
            return $false
        }
    } catch {
        Write-Error "$ServiceName is not responding: $($_.Exception.Message)"
        return $false
    }
}

function Test-DockerServices {
    Write-Test "Checking Docker container status..."
    
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-Object -Skip 1
    
    if ($containers) {
        Write-Info "Running containers:"
        $containers | ForEach-Object { Write-Output "  $_" }
    } else {
        Write-Warning "No containers are running"
    }
}

function Test-CoreInfrastructure {
    Write-Test "Testing core infrastructure..."
    
    # Test PostgreSQL
    $postgresWorking = Test-Endpoint -Url "http://localhost:5432" -ServiceName "PostgreSQL" -TimeoutSec 5
    
    # Test Redis (via Redis Commander)
    $redisWorking = Test-Endpoint -Url "http://localhost:8081" -ServiceName "Redis Commander" -TimeoutSec 5
    
    # Test PgAdmin
    $pgAdminWorking = Test-Endpoint -Url "http://localhost:5050" -ServiceName "PgAdmin" -TimeoutSec 5
    
    return @{
        "PostgreSQL" = $postgresWorking
        "Redis" = $redisWorking
        "PgAdmin" = $pgAdminWorking
    }
}

function Test-ApiGateway {
    Write-Test "Testing API Gateway..."
    
    $endpoints = @{
        "Root" = "http://localhost:8000/"
        "Health" = "http://localhost:8000/health"
        "Readiness" = "http://localhost:8000/readiness"
        "Services" = "http://localhost:8000/api/v1/services"
        "Metrics" = "http://localhost:8000/metrics"
    }
    
    $results = @{}
    foreach ($endpoint in $endpoints.GetEnumerator()) {
        $results[$endpoint.Key] = Test-Endpoint -Url $endpoint.Value -ServiceName "API Gateway $($endpoint.Key)" -TimeoutSec 15
    }
    
    return $results
}

function Test-ScannerServices {
    Write-Test "Testing security scanner services..."
    
    $scanners = @{
        "Slither" = "http://localhost:8002"
        "Mythril" = "http://localhost:8003"
        "MythX" = "http://localhost:8004"
        "Manticore" = "http://localhost:8005"
    }
    
    $results = @{}
    foreach ($scanner in $scanners.GetEnumerator()) {
        $results[$scanner.Key] = Test-Endpoint -Url "$($scanner.Value)/health" -ServiceName "$($scanner.Key) Scanner" -TimeoutSec 10
    }
    
    return $results
}

function Test-MonitoringServices {
    Write-Test "Testing monitoring services..."
    
    $monitoring = @{
        "Prometheus" = "http://localhost:9090"
        "Grafana" = "http://localhost:3001"
    }
    
    $results = @{}
    foreach ($service in $monitoring.GetEnumerator()) {
        $results[$service.Key] = Test-Endpoint -Url $service.Value -ServiceName $service.Key -TimeoutSec 10
    }
    
    return $results
}

function Test-Frontend {
    Write-Test "Testing frontend application..."
    
    return @{
        "Frontend" = Test-Endpoint -Url "http://localhost:3000" -ServiceName "Frontend Application" -TimeoutSec 10
    }
}

function Show-ServiceUrls {
    Write-Info "`n🌐 Scorpius Enterprise Platform - Service URLs:"
    Write-Output ""
    Write-ColorOutput "Core Services:" "Magenta"
    Write-Output "  • API Gateway:           http://localhost:8000"
    Write-Output "  • API Documentation:     http://localhost:8000/docs"
    Write-Output "  • Frontend Application:  http://localhost:3000"
    Write-Output ""
    
    Write-ColorOutput "Security Scanners:" "Magenta"
    Write-Output "  • Slither Scanner:       http://localhost:8002"
    Write-Output "  • Mythril Scanner:       http://localhost:8003"
    Write-Output "  • MythX Scanner:         http://localhost:8004"
    Write-Output "  • Manticore Scanner:     http://localhost:8005"
    Write-Output ""
    
    Write-ColorOutput "Monitoring and Analytics:" "Magenta"
    Write-Output "  • Prometheus:            http://localhost:9090"
    Write-Output "  • Grafana:               http://localhost:3001 (admin/admin)"
    Write-Output ""
    
    Write-ColorOutput "Database Administration:" "Magenta"
    Write-Output "  • PgAdmin:               http://localhost:5050 (admin@scorpius.enterprise/admin)"
    Write-Output "  • Redis Commander:       http://localhost:8081"
    Write-Output ""
}

function Show-TestSummary {
    param([hashtable]$AllResults)
    
    Write-Info "`n📊 Test Summary:"
    Write-Output ""
    
    $totalTests = 0
    $passedTests = 0
    
    foreach ($category in $AllResults.GetEnumerator()) {
        Write-ColorOutput "$($category.Key):" "Yellow"
        foreach ($test in $category.Value.GetEnumerator()) {
            $totalTests++
            if ($test.Value) {
                $passedTests++
                Write-Success "  $($test.Key)"
            } else {
                Write-Error "  $($test.Key)"
            }
        }
        Write-Output ""
    }
    
    $successRate = if ($totalTests -gt 0) { [math]::Round(($passedTests / $totalTests) * 100, 1) } else { 0 }
    
    Write-ColorOutput "Overall Results: $passedTests/$totalTests tests passed ($successRate%)" "Magenta"
    
    if ($successRate -eq 100) {
        Write-Success "`n🎉 All services are working perfectly!"
    } elseif ($successRate -ge 80) {
        Write-Warning "`n⚠️  Most services are working, but some issues were detected."
    } else {
        Write-Error "`n❌ Multiple services are not responding. Check the logs for details."
    }
}

# Main execution
function Main {
    Write-ColorOutput "`n🧪 Scorpius Enterprise Platform - Service Tests" "Magenta"
    Write-ColorOutput "=================================================" "Magenta"
    
    # Check Docker services
    Test-DockerServices
    Write-Output ""
    
    # Run all tests
    $allResults = @{}
    
    $allResults["Infrastructure"] = Test-CoreInfrastructure
    $allResults["API Gateway"] = Test-ApiGateway
    $allResults["Security Scanners"] = Test-ScannerServices
    $allResults["Monitoring"] = Test-MonitoringServices
    $allResults["Frontend"] = Test-Frontend
    
    # Show results
    Show-TestSummary -AllResults $allResults
    Show-ServiceUrls
    
    Write-Info "`n📝 Additional Information:"
    Write-Output "  • Use 'docker-compose -f docker/docker-compose.enterprise.yml logs -f' to view logs"
    Write-Output "  • Use 'docker-compose -f docker/docker-compose.enterprise.yml ps' to check container status"
    Write-Output "  • Use 'docker-compose -f docker/docker-compose.enterprise.yml down' to stop all services"
    
    Write-Output ""
}

# Run main function
try {
    Main
} catch {
    Write-Error "Test execution failed: $($_.Exception.Message)"
    exit 1
} 
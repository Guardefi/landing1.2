#!/usr/bin/env pwsh
<#
.SYNOPSIS
    🦂 SCORPIUS ENTERPRISE PLATFORM - WORLD'S MOST ADVANCED BLOCKCHAIN SECURITY SUITE
    
.DESCRIPTION
    Comprehensive startup script for the Scorpius Enterprise Platform featuring:
    - AI-Powered Threat Detection & Response
    - Real-time MEV Protection & Flashbots Integration  
    - Advanced Blockchain Forensics & Money Laundering Detection
    - Quantum Cryptography & Post-Quantum Security
    - Universal Exploit Testing Framework
    - Enterprise Analytics & ML Pipelines
    - Distributed Computing Infrastructure
    - Advanced Monitoring & Compliance
    
.PARAMETER Action
    Action to perform: start, stop, restart, status, clean, logs
    
.PARAMETER Environment
    Environment to deploy: development, staging, production
    
.EXAMPLE
    .\start-enterprise-scorpius.ps1 start
    .\start-enterprise-scorpius.ps1 stop
    .\start-enterprise-scorpius.ps1 status
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "status", "clean", "logs", "update")]
    [string]$Action = "start",
    
    [Parameter()]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development"
)

# ============================================================================
# ENTERPRISE CONFIGURATION
# ============================================================================

$Config = @{
    ProjectName = "scorpius-enterprise"
    DockerComposeFile = "docker/docker-compose.enterprise.yml"
    EnvironmentFile = ".env"
    LogLevel = "INFO"
    HealthCheckTimeout = 300
    Services = @(
        # Core Infrastructure
        "postgres", "redis", "mongodb", "pgadmin", "redis-commander",
        
        # Core Services
        "api-gateway", "frontend", "bridge", "honeypot", "mempool", 
        "quantum", "time-machine", "bytecode", "settings", "reporting",
        
        # Advanced Security Services
        "threat-monitoring", "elite-security", "ai-forensics", "quantum-crypto",
        "mev-protection", "exploit-testing", "blackhat-tracer", "integration-hub",
        
        # Scanner Services
        "scanner-slither", "scanner-mythril", "scanner-mythx", "scanner-manticore",
        "scanner-ai-orchestrator",
        
        # Monitoring & Analytics
        "prometheus", "grafana", "enterprise-analytics", "distributed-computing",
        
        # Development Tools
        "dev-tools", "simulation-service"
    )
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "🦂 $Message" -ForegroundColor Yellow
    Write-Host "============================================================`n" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Test-Docker {
    try {
        $null = docker --version
        return $true
    } catch {
        return $false
    }
}

function Test-DockerCompose {
    try {
        $null = docker-compose --version
        return $true
    } catch {
        return $false
    }
}

function Wait-ForService {
    param(
        [string]$ServiceName,
        [string]$HealthEndpoint,
        [int]$Timeout = 60
    )
    
    $startTime = Get-Date
    $timeoutTime = $startTime.AddSeconds($Timeout)
    
    Write-Info "Waiting for $ServiceName to be ready..."
    
    while ((Get-Date) -lt $timeoutTime) {
        try {
            $response = Invoke-WebRequest -Uri $HealthEndpoint -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "$ServiceName is ready!"
                return $true
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Error "$ServiceName failed to start within $Timeout seconds"
    return $false
}

# ============================================================================
# ENTERPRISE STARTUP SEQUENCE
# ============================================================================

function Start-EnterpriseScorpius {
    Write-Header "SCORPIUS ENTERPRISE PLATFORM STARTUP"
    
    # Pre-flight checks
    Write-Info "Performing pre-flight checks..."
    
    if (-not (Test-Docker)) {
        Write-Error "Docker is not installed or not running"
        exit 1
    }
    
    if (-not (Test-DockerCompose)) {
        Write-Error "Docker Compose is not installed"
        exit 1
    }
    
    # Check if .env file exists
    if (-not (Test-Path $Config.EnvironmentFile)) {
        Write-Warning "Environment file not found, creating default .env"
        New-Item -Path $Config.EnvironmentFile -ItemType File -Force | Out-Null
        @"
# Scorpius Enterprise Environment Configuration
POSTGRES_DB=scorpius_enterprise
POSTGRES_USER=scorpius_admin
POSTGRES_PASSWORD=enterprise_secure_password_2024
REDIS_PASSWORD=enterprise_redis_password_2024
MONGODB_PASSWORD=enterprise_mongo_password_2024
JWT_SECRET=enterprise_jwt_secret_2024_very_long_and_secure
API_KEY=enterprise_api_key_2024
ENVIRONMENT=$Environment
LOG_LEVEL=$($Config.LogLevel)
"@ | Out-File -FilePath $Config.EnvironmentFile -Encoding UTF8
    }
    
    # Create necessary directories
    Write-Info "Creating enterprise directories..."
    $directories = @(
        "logs/enterprise",
        "data/enterprise",
        "artifacts/enterprise",
        "config/enterprise"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -Path $dir -ItemType Directory -Force | Out-Null
        }
    }
    
    # Start core infrastructure first
    Write-Info "Starting core infrastructure services..."
    docker-compose -f $Config.DockerComposeFile up -d postgres redis mongodb pgadmin redis-commander
    
    # Wait for infrastructure
    Start-Sleep -Seconds 10
    
    # Start core services
    Write-Info "Starting core security services..."
    docker-compose -f $Config.DockerComposeFile up -d api-gateway frontend bridge honeypot mempool quantum time-machine bytecode settings reporting
    
    # Start advanced security services
    Write-Info "Starting advanced security services..."
    docker-compose -f $Config.DockerComposeFile up -d threat-monitoring elite-security ai-forensics quantum-crypto mev-protection exploit-testing blackhat-tracer integration-hub
    
    # Start scanner services
    Write-Info "Starting security scanner services..."
    docker-compose -f $Config.DockerComposeFile up -d scanner-slither scanner-mythril scanner-mythx scanner-manticore scanner-ai-orchestrator
    
    # Start monitoring and analytics
    Write-Info "Starting monitoring and analytics services..."
    docker-compose -f $Config.DockerComposeFile up -d prometheus grafana enterprise-analytics distributed-computing
    
    # Start development tools
    Write-Info "Starting development tools..."
    docker-compose -f $Config.DockerComposeFile up -d dev-tools simulation-service
    
    # Wait for all services to be ready
    Write-Info "Waiting for services to initialize..."
    Start-Sleep -Seconds 30
    
    # Health checks
    Write-Info "Performing health checks..."
    $healthChecks = @(
        @{Service="API Gateway"; Endpoint="http://localhost:8000/health"},
        @{Service="Frontend"; Endpoint="http://localhost:3000"},
        @{Service="Threat Monitoring"; Endpoint="http://localhost:8007/health"},
        @{Service="Elite Security"; Endpoint="http://localhost:8008/health"},
        @{Service="AI Forensics"; Endpoint="http://localhost:8009/health"},
        @{Service="Quantum Crypto"; Endpoint="http://localhost:8010/health"},
        @{Service="MEV Protection"; Endpoint="http://localhost:8011/health"},
        @{Service="Integration Hub"; Endpoint="http://localhost:8014/health"}
    )
    
    $healthyServices = 0
    foreach ($check in $healthChecks) {
        if (Wait-ForService -ServiceName $check.Service -HealthEndpoint $check.Endpoint -Timeout 30) {
            $healthyServices++
        }
    }
    
    # Display status
    Show-EnterpriseStatus
    
    if ($healthyServices -eq $healthChecks.Count) {
        Write-Success "All enterprise services started successfully!"
        Show-EnterpriseUrls
    } else {
        Write-Warning "Some services may still be initializing. Check logs for details."
        Show-EnterpriseUrls
    }
}

function Stop-EnterpriseScorpius {
    Write-Header "STOPPING SCORPIUS ENTERPRISE PLATFORM"
    
    Write-Info "Stopping all enterprise services..."
    docker-compose -f $Config.DockerComposeFile down
    
    Write-Success "All enterprise services stopped"
}

function Show-EnterpriseStatus {
    Write-Header "ENTERPRISE PLATFORM STATUS"
    
    $services = docker-compose -f $Config.DockerComposeFile ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    Write-Host $services
    
    # Show resource usage
    Write-Info "Resource Usage:"
    $stats = docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    Write-Host $stats
}

function Show-EnterpriseUrls {
    Write-Header "ENTERPRISE PLATFORM ACCESS URLs"
    
    $urls = @{
        "Main Dashboard" = "http://localhost:3000"
        "API Gateway" = "http://localhost:8000"
        "API Documentation" = "http://localhost:8000/docs"
        "Threat Monitoring" = "http://localhost:8007"
        "Elite Security" = "http://localhost:8008"
        "AI Forensics" = "http://localhost:8009"
        "Quantum Crypto" = "http://localhost:8010"
        "MEV Protection" = "http://localhost:8011"
        "Integration Hub" = "http://localhost:8014"
        "Slither Scanner" = "http://localhost:8002"
        "Mythril Scanner" = "http://localhost:8003"
        "MythX Scanner" = "http://localhost:8004"
        "Manticore Scanner" = "http://localhost:8005"
        "Grafana Monitor" = "http://localhost:3001"
        "Prometheus" = "http://localhost:9090"
        "Database Admin" = "http://localhost:5050"
        "Redis Admin" = "http://localhost:8081"
    }
    
    foreach ($url in $urls.GetEnumerator()) {
        Write-Host "  • $($url.Key):`t$($url.Value)" -ForegroundColor Cyan
    }
    
    Write-Host "`n🔧 Management Commands:" -ForegroundColor Yellow
    Write-Host "  • View logs:          .\start-enterprise-scorpius.ps1 logs" -ForegroundColor Gray
    Write-Host "  • Stop services:      .\start-enterprise-scorpius.ps1 stop" -ForegroundColor Gray
    Write-Host "  • Restart services:   .\start-enterprise-scorpius.ps1 restart" -ForegroundColor Gray
    Write-Host "  • Clean restart:      .\start-enterprise-scorpius.ps1 clean" -ForegroundColor Gray
}

function Show-EnterpriseLogs {
    Write-Header "ENTERPRISE PLATFORM LOGS"
    
    docker-compose -f $Config.DockerComposeFile logs -f --tail=100
}

function Clean-EnterpriseScorpius {
    Write-Header "CLEANING ENTERPRISE PLATFORM"
    
    Write-Warning "This will remove all containers, volumes, and data. Are you sure? (y/N)"
    $response = Read-Host
    
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Info "Stopping and removing all containers..."
        docker-compose -f $Config.DockerComposeFile down -v --remove-orphans
        
        Write-Info "Removing enterprise images..."
        docker images | Where-Object { $_.Repository -like "*scorpius*" } | ForEach-Object { docker rmi $_.ImageID -f }
        
        Write-Info "Cleaning up volumes..."
        docker volume prune -f
        
        Write-Info "Cleaning up networks..."
        docker network prune -f
        
        Write-Success "Enterprise platform cleaned successfully"
    } else {
        Write-Info "Clean operation cancelled"
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Header "SCORPIUS ENTERPRISE PLATFORM - WORLD'S MOST ADVANCED BLOCKCHAIN SECURITY SUITE"

switch ($Action) {
    "start" {
        Start-EnterpriseScorpius
    }
    "stop" {
        Stop-EnterpriseScorpius
    }
    "restart" {
        Stop-EnterpriseScorpius
        Start-Sleep -Seconds 5
        Start-EnterpriseScorpius
    }
    "status" {
        Show-EnterpriseStatus
    }
    "logs" {
        Show-EnterpriseLogs
    }
    "clean" {
        Clean-EnterpriseScorpius
    }
    "update" {
        Write-Info "Updating enterprise platform..."
        git pull origin main
        docker-compose -f $Config.DockerComposeFile pull
        Write-Success "Enterprise platform updated"
    }
    default {
        Write-Error "Invalid action: $Action"
        Write-Host "Usage: .\start-enterprise-scorpius.ps1 [start|stop|restart|status|logs|clean|update]" -ForegroundColor Yellow
    }
}

Write-Header "ENTERPRISE PLATFORM OPERATION COMPLETE" 
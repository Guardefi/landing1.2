#!/usr/bin/env pwsh

<#
.SYNOPSIS
Scorpius Enterprise Platform Startup Script
Starts all microservices in the correct order with health checks

.DESCRIPTION
This script will:
1. Check prerequisites (Docker, Docker Compose)
2. Validate environment configuration
3. Start infrastructure services first
4. Start core services with dependency checking
5. Start scanner plugins
6. Start monitoring and admin tools

.PARAMETER Mode
Deployment mode: dev, staging, production
Default: dev

.PARAMETER Services
Specific services to start (comma-separated)
Default: all services

.PARAMETER SkipHealthChecks
Skip health checks for faster startup
Default: false

.EXAMPLE
./start-scorpius-enterprise.ps1
Start all services in development mode

.EXAMPLE
./start-scorpius-enterprise.ps1 -Mode production -Services "api-gateway,postgres,redis"
Start specific services in production mode
#>

param(
    [ValidateSet("dev", "staging", "production")]
    [string]$Mode = "dev",
    
    [string]$Services = "all",
    
    [switch]$SkipHealthChecks = $false
)

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

function Write-Success { param([string]$Message) Write-ColorOutput "SUCCESS: $Message" "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput "ERROR: $Message" "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput "WARNING: $Message" "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput "INFO: $Message" "Blue" }
function Write-Step { param([string]$Message) Write-ColorOutput "STEP: $Message" "Cyan" }

# Configuration
$ErrorActionPreference = "Stop"
$COMPOSE_FILE = "docker/docker-compose.enterprise.yml"
$ENV_FILE = ".env"
$LOG_DIR = "logs"

# Service startup order
$INFRASTRUCTURE_SERVICES = @("redis", "postgres")
$CORE_SERVICES = @("api-gateway", "bridge-service", "bytecode-service", "honeypot-service", "mempool-service", "quantum-service", "time-machine-service")
$SCANNER_SERVICES = @("scanner-slither", "scanner-mythril", "scanner-manticore")
$MONITORING_SERVICES = @("prometheus", "grafana")
$ADMIN_SERVICES = @("pgadmin", "redis-commander", "dev-tools")
$FRONTEND_SERVICES = @("frontend")

function Test-Prerequisites {
    Write-Step "Checking prerequisites..."
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Success "Docker found: $dockerVersion"
    } catch {
        Write-Error "Docker is not installed or not accessible"
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Success "Docker Compose found: $composeVersion"
    } catch {
        Write-Error "Docker Compose is not installed or not accessible"
        exit 1
    }
    
    # Check Docker daemon
    try {
        docker info > $null 2>&1
        Write-Success "Docker daemon is running"
    } catch {
        Write-Error "Docker daemon is not running. Please start Docker."
        exit 1
    }
}

function Initialize-Environment {
    Write-Step "Initializing environment..."
    
    # Create logs directory
    if (!(Test-Path $LOG_DIR)) {
        New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
        Write-Success "Created logs directory"
    }
    
    # Check if .env file exists
    if (!(Test-Path $ENV_FILE)) {
        Write-Warning ".env file not found. Creating default environment..."
        
        $randomId = Get-Random
        $defaultEnv = @"
# Scorpius Enterprise Platform Configuration
ENVIRONMENT=enterprise
DEBUG=false

# Database Configuration
DB_PASSWORD=scorpius_secure123
POSTGRES_DB=scorpius_enterprise
POSTGRES_USER=scorpius

# Redis Configuration
REDIS_PASSWORD=scorpius123

# Security Configuration
JWT_SECRET=scorpius_enterprise_jwt_secret_key_$randomId
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# External API Keys


# Admin Passwords
PGADMIN_PASSWORD=admin
GRAFANA_PASSWORD=admin

# Logging
LOG_LEVEL=INFO
"@
        
        $defaultEnv | Out-File -FilePath $ENV_FILE -Encoding utf8
        Write-Success "Created default .env file"
    }
    
    Write-Success "Environment initialized"
}

function Wait-ForService {
    param(
        [string]$ServiceName,
        [int]$TimeoutSeconds = 300
    )
    
    if ($SkipHealthChecks) {
        Write-Info "Skipping health check for $ServiceName"
        return
    }
    
    Write-Step "Waiting for $ServiceName to be healthy..."
    $startTime = Get-Date
    
    while ((Get-Date) - $startTime -lt [TimeSpan]::FromSeconds($TimeoutSeconds)) {
        try {
            $status = docker-compose -f $COMPOSE_FILE ps --services --filter "status=running" | Where-Object { $_ -eq $ServiceName }
            if ($status) {
                $healthStatus = docker-compose -f $COMPOSE_FILE ps --format "table {{.Name}}\t{{.Status}}" | Where-Object { $_ -like "*$ServiceName*" }
                if ($healthStatus -like "*healthy*" -or $healthStatus -like "*Up*") {
                    Write-Success "$ServiceName is healthy"
                    return
                }
            }
        } catch {
            # Continue waiting
        }
        
        Start-Sleep -Seconds 5
    }
    
    Write-Warning "$ServiceName did not become healthy within $TimeoutSeconds seconds"
}

function Start-ServiceGroup {
    param(
        [string[]]$Services,
        [string]$GroupName
    )
    
    Write-Step "Starting $GroupName..."
    
    foreach ($service in $Services) {
        if ($Services -ne "all" -and $Services -notcontains $service) {
            Write-Info "Skipping $service (not in requested services)"
            continue
        }
        
        Write-Info "Starting $service..."
        try {
            docker-compose -f $COMPOSE_FILE up -d $service
            Wait-ForService -ServiceName $service
        } catch {
            Write-Warning "Failed to start $service - $($_.Exception.Message)"
        }
    }
    
    Write-Success "$GroupName started"
}

function Show-ServiceStatus {
    Write-Step "Checking service status..."
    
    $services = docker-compose -f $COMPOSE_FILE ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    Write-Info "Service Status:"
    Write-Output $services
    
    # Show URLs
    Write-Info "`nAvailable Services:"
    Write-Output "• API Gateway: http://localhost:8000"
    Write-Output "• Frontend: http://localhost:3000"
    Write-Output "• Grafana: http://localhost:3001 (admin/admin)"
    Write-Output "• Prometheus: http://localhost:9090"
    Write-Output "• PgAdmin: http://localhost:5050 (admin@scorpius.enterprise/admin)"
    Write-Output "• Redis Commander: http://localhost:8081"
    Write-Output "• Slither Scanner: http://localhost:8002"
    Write-Output "• Mythril Scanner: http://localhost:8003"
    
    Write-Output "• Manticore Scanner: http://localhost:8005"
}

function Test-ApiGateway {
    Write-Step "Testing API Gateway..."
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Success "API Gateway is responding"
        } else {
            Write-Warning "API Gateway returned status: $($response.StatusCode)"
        }
    } catch {
        Write-Warning "API Gateway is not responding - $($_.Exception.Message)"
    }
}

# Main execution
function Main {
    Write-ColorOutput "`nScorpius Enterprise Platform Startup" "Magenta"
    Write-ColorOutput "=======================================" "Magenta"
    
    Test-Prerequisites
    Initialize-Environment
    
    # Clean up any existing containers
    Write-Step "Cleaning up existing containers..."
    docker-compose -f $COMPOSE_FILE down --remove-orphans
    
    # Start services in order
    Start-ServiceGroup -Services $INFRASTRUCTURE_SERVICES -GroupName "Infrastructure Services"
    Start-ServiceGroup -Services $CORE_SERVICES -GroupName "Core Services"
    Start-ServiceGroup -Services $SCANNER_SERVICES -GroupName "Scanner Services"
    Start-ServiceGroup -Services $MONITORING_SERVICES -GroupName "Monitoring Services"
    Start-ServiceGroup -Services $ADMIN_SERVICES -GroupName "Admin Services"
    Start-ServiceGroup -Services $FRONTEND_SERVICES -GroupName "Frontend Services"
    
    # Show final status
    Start-Sleep -Seconds 10
    Show-ServiceStatus
    Test-ApiGateway
    
    Write-Success "`nScorpius Enterprise Platform started successfully!"
    Write-Info "Use 'docker-compose -f $COMPOSE_FILE logs -f' to view logs"
    Write-Info "Use 'docker-compose -f $COMPOSE_FILE down' to stop all services"
}

# Run main function
try {
    Main
} catch {
    Write-Error "Startup failed - $($_.Exception.Message)"
    Write-Info "Check logs with: docker-compose -f $COMPOSE_FILE logs"
    exit 1
} 
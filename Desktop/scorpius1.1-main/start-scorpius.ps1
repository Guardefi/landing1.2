#!/usr/bin/env powershell
# Scorpius Enterprise Platform - Simple Startup Script
# This script starts the complete Scorpius Enterprise platform with all services

param(
    [string]$Action = "start",
    [switch]$Clean = $false,
    [switch]$Dev = $false
)

# Colors for output
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green
$Blue = [System.ConsoleColor]::Blue
$Yellow = [System.ConsoleColor]::Yellow
$Cyan = [System.ConsoleColor]::Cyan

function Write-ColorOutput {
    param([string]$Message, [System.ConsoleColor]$Color = [System.ConsoleColor]::White)
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-ColorOutput "============================================================" $Cyan
    Write-ColorOutput "🦂 $Message" $Cyan
    Write-ColorOutput "============================================================" $Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "📋 $Message" $Blue
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" $Green
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" $Red
}

function Test-Docker {
    Write-Step "Checking Docker availability..."
    
    try {
        $dockerVersion = docker --version
        Write-Success "Docker is available: $dockerVersion"
    } catch {
        Write-Error "Docker is not installed or not in PATH"
        exit 1
    }
    
    try {
        docker ps | Out-Null
        Write-Success "Docker daemon is running"
    } catch {
        Write-Error "Docker daemon is not running. Please start Docker Desktop"
        exit 1
    }
}

function Setup-Environment {
    Write-Step "Setting up environment..."
    
    # Create necessary directories
    $directories = @(
        "logs",
        "data/postgres",
        "data/redis",
        "data/grafana",
        "data/prometheus",
        "data/pgadmin"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "Created directory: $dir"
        }
    }
    
    # Create basic .env file if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Step "Creating environment configuration..."
        $envContent = @"
# Scorpius Enterprise Environment Configuration
DB_PASSWORD=scorpius123
REDIS_PASSWORD=scorpius123
JWT_SECRET=scorpius-enterprise-jwt-secret-key-change-in-production
GRAFANA_PASSWORD=admin
PGADMIN_PASSWORD=admin
MYTHX_API_KEY=your-mythx-api-key-here
ENVIRONMENT=development
LOG_LEVEL=INFO
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "Created .env file with default configuration"
        Write-Warning "Please edit .env file with your specific settings if needed"
    }
    
    Write-Success "Environment setup complete"
}

function Start-Infrastructure {
    Write-Step "Starting infrastructure services..."
    
    # Start database and cache first
    docker-compose -f docker/docker-compose.enterprise.yml up -d postgres redis
    
    Write-Step "Waiting for database to be ready..."
    $maxAttempts = 30
    $attempt = 0
    
    do {
        Start-Sleep -Seconds 2
        $attempt++
        Write-Host "." -NoNewline
        try {
            $result = docker-compose -f docker/docker-compose.enterprise.yml exec -T postgres pg_isready -U scorpius 2>$null
            if ($LASTEXITCODE -eq 0) {
                break
            }
        } catch {
            # Continue waiting
        }
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -ge $maxAttempts) {
        Write-Error "Database failed to start within timeout"
        exit 1
    }
    
    Write-Host ""
    Write-Success "Infrastructure services started"
}

function Start-CoreServices {
    Write-Step "Starting core services..."
    
    # Start API Gateway and core services
    docker-compose -f docker/docker-compose.enterprise.yml up -d api-gateway
    
    Write-Step "Waiting for API Gateway to be ready..."
    $maxAttempts = 30
    $attempt = 0
    
    do {
        Start-Sleep -Seconds 2
        $attempt++
        Write-Host "." -NoNewline
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                break
            }
        } catch {
            # Continue waiting
        }
    } while ($attempt -lt $maxAttempts)
    
    Write-Host ""
    if ($attempt -lt $maxAttempts) {
        Write-Success "API Gateway is ready"
    } else {
        Write-Warning "API Gateway may still be starting up"
    }
}

function Start-Services {
    Write-Step "Starting all remaining services..."
    
    # Start all services
    docker-compose -f docker/docker-compose.enterprise.yml up -d
    
    Write-Step "Waiting for services to initialize..."
    Start-Sleep -Seconds 10
    
    Write-Success "All services started"
}

function Show-Status {
    Write-Header "Scorpius Enterprise Platform Status"
    
    # Show running containers
    Write-Step "Service Status:"
    docker-compose -f docker/docker-compose.enterprise.yml ps
    
    Write-Host ""
    Write-ColorOutput "🌐 Service URLs:" $Green
    Write-Host "  • Main Dashboard:     http://localhost:3000" -ForegroundColor White
    Write-Host "  • API Gateway:        http://localhost:8000" -ForegroundColor White
    Write-Host "  • API Documentation:  http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  • Slither Scanner:    http://localhost:8002" -ForegroundColor White
    Write-Host "  • Mythril Scanner:    http://localhost:8003" -ForegroundColor White
    Write-Host "  • MythX Scanner:      http://localhost:8004" -ForegroundColor White
    Write-Host "  • Manticore Scanner:  http://localhost:8005" -ForegroundColor White
    Write-Host "  • Grafana Monitor:    http://localhost:3001" -ForegroundColor White
    Write-Host "  • Prometheus:         http://localhost:9090" -ForegroundColor White
    Write-Host "  • Database Admin:     http://localhost:5050" -ForegroundColor White
    Write-Host "  • Redis Admin:        http://localhost:8081" -ForegroundColor White
    Write-Host ""
    Write-ColorOutput "🔧 Management Commands:" $Blue
    Write-Host "  • View logs:          docker-compose -f docker/docker-compose.enterprise.yml logs -f" -ForegroundColor Gray
    Write-Host "  • Stop services:      .\start-scorpius.ps1 stop" -ForegroundColor Gray
    Write-Host "  • Restart services:   .\start-scorpius.ps1 restart" -ForegroundColor Gray
    Write-Host "  • Clean restart:      .\start-scorpius.ps1 clean" -ForegroundColor Gray
}

function Stop-Services {
    Write-Header "Stopping Scorpius Enterprise Platform"
    
    Write-Step "Stopping all services..."
    docker-compose -f docker/docker-compose.enterprise.yml down
    
    if ($Clean) {
        Write-Step "Cleaning up containers and volumes..."
        docker-compose -f docker/docker-compose.enterprise.yml down -v --remove-orphans
        docker system prune -f
        Write-Success "Clean shutdown complete"
    } else {
        Write-Success "Services stopped"
    }
}

function Restart-Services {
    Write-Header "Restarting Scorpius Enterprise Platform"
    
    Stop-Services
    Start-Sleep -Seconds 5
    Start-All
}

function Start-All {
    Write-Header "Starting Scorpius Enterprise Platform"
    
    Test-Docker
    Setup-Environment
    Start-Infrastructure
    Start-CoreServices
    Start-Services
    Show-Status
    
    Write-Header "🎉 Scorpius Enterprise Platform Started Successfully!"
}

function Show-Help {
    Write-Header "Scorpius Enterprise Platform - Startup Script"
    
    Write-ColorOutput "Usage:" $Yellow
    Write-Host "  .\start-scorpius.ps1 [action] [options]" -ForegroundColor Gray
    Write-Host ""
    Write-ColorOutput "Actions:" $Blue
    Write-Host "  start      - Start all services (default)" -ForegroundColor White
    Write-Host "  stop       - Stop all services" -ForegroundColor White
    Write-Host "  restart    - Restart all services" -ForegroundColor White
    Write-Host "  status     - Show service status" -ForegroundColor White
    Write-Host "  help       - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-ColorOutput "Options:" $Blue
    Write-Host "  -Clean     - Clean shutdown (removes volumes)" -ForegroundColor White
    Write-Host "  -Dev       - Development mode (future use)" -ForegroundColor White
    Write-Host ""
    Write-ColorOutput "Examples:" $Yellow
    Write-Host "  .\start-scorpius.ps1" -ForegroundColor Gray
    Write-Host "  .\start-scorpius.ps1 stop" -ForegroundColor Gray
    Write-Host "  .\start-scorpius.ps1 restart -Clean" -ForegroundColor Gray
}

# Main script execution
switch ($Action.ToLower()) {
    "start" { Start-All }
    "stop" { Stop-Services }
    "restart" { Restart-Services }
    "status" { Show-Status }
    "help" { Show-Help }
    default { 
        Write-Error "Unknown action: $Action"
        Show-Help
        exit 1
    }
}
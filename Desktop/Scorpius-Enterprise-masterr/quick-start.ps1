# Scorpius Enterprise Platform - Quick Start Script for Windows
# This script sets up and launches the complete microservices platform

param(
    [string]$Action = "start"
)

# Configuration
$PlatformName = "Scorpius Enterprise Platform"
$ComposeFile = "docker-compose.yml"
$EnvFile = ".env"

# Functions
function Write-Header {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Blue
    Write-Host "🦂 $PlatformName" -ForegroundColor Blue
    Write-Host "================================================================" -ForegroundColor Blue
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host "📋 $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Test-Requirements {
    Write-Step "Checking requirements..."
    
    # Check Docker
    try {
        $null = Get-Command docker -ErrorAction Stop
    }
    catch {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }
    
    # Check Docker Compose
    try {
        $null = Get-Command docker-compose -ErrorAction Stop
    }
    catch {
        Write-Error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    }
    
    # Check if Docker is running
    try {
        docker info | Out-Null
    }
    catch {
        Write-Error "Docker is not running. Please start Docker Desktop first."
        exit 1
    }
    
    Write-Success "All requirements met"
}

function Initialize-Environment {
    Write-Step "Setting up environment..."
    
    if (-not (Test-Path $EnvFile)) {
        Write-Warning "Environment file not found. Creating from example..."
        Copy-Item ".env.example" $EnvFile
        Write-Warning "Please edit $EnvFile with your configuration before proceeding."
        Read-Host "Press Enter when you're ready to continue"
    }
    
    # Create necessary directories
    $directories = @(
        "logs\api-gateway", "logs\bridge", "logs\mempool", "logs\honeypot", "logs\scanner",
        "logs\mev-bot", "logs\bytecode", "logs\quantum", "logs\time-machine", "logs\reporting",
        "data\postgres", "data\redis", "data\grafana", "data\prometheus",
        "infrastructure\nginx", "infrastructure\monitoring", "infrastructure\ssl"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "Environment setup complete"
}

function Build-Services {
    Write-Step "Building all services..."
    
    Write-Host "This may take several minutes on first run..."
    docker-compose -f $ComposeFile build --parallel
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build services"
        exit 1
    }
    
    Write-Success "All services built successfully"
}

function Start-Database {
    Write-Step "Starting database services..."
    
    docker-compose -f $ComposeFile up -d postgres redis
    
    # Wait for postgres to be ready
    Write-Host "Waiting for PostgreSQL to be ready..."
    do {
        Start-Sleep 1
        Write-Host "." -NoNewline
        $ready = docker-compose -f $ComposeFile exec postgres pg_isready -U scorpius 2>$null
    } while ($LASTEXITCODE -ne 0)
    
    Write-Host ""
    Write-Success "Database services started"
}

function Start-CoreServices {
    Write-Step "Starting core services..."
    
    docker-compose -f $ComposeFile up -d api-gateway
    
    # Wait for API gateway to be ready
    Write-Host "Waiting for API Gateway to be ready..."
    do {
        Start-Sleep 1
        Write-Host "." -NoNewline
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 1 2>$null
            $ready = $response.StatusCode -eq 200
        }
        catch {
            $ready = $false
        }
    } while (-not $ready)
    
    Write-Host ""
    Write-Success "API Gateway started"
}

function Start-Microservices {
    Write-Step "Starting microservices..."
    
    docker-compose -f $ComposeFile up -d bridge-service mempool-service honeypot-service scanner-service mev-bot-service bytecode-service quantum-service time-machine-service reporting-service
    
    Write-Success "Microservices started"
}

function Start-Frontend {
    Write-Step "Starting frontend dashboard..."
    
    docker-compose -f $ComposeFile up -d frontend
    
    Write-Success "Frontend dashboard started"
}

function Start-Monitoring {
    Write-Step "Starting monitoring services..."
    
    docker-compose -f $ComposeFile up -d prometheus grafana
    
    Write-Success "Monitoring services started"
}

function Start-LoadBalancer {
    Write-Step "Starting load balancer..."
    
    docker-compose -f $ComposeFile up -d nginx
    
    Write-Success "Load balancer started"
}

function Wait-ForServices {
    Write-Step "Waiting for all services to be healthy..."
    
    $services = @(
        "http://localhost:8000",   # API Gateway
        "http://localhost:3000",   # Frontend
        "http://localhost:9090",   # Prometheus
        "http://localhost:3001"    # Grafana
    )
    
    foreach ($service in $services) {
        Write-Host "Checking $service..."
        do {
            Start-Sleep 2
            Write-Host "." -NoNewline
            try {
                $response = Invoke-WebRequest -Uri $service -UseBasicParsing -TimeoutSec 1 2>$null
                $ready = $response.StatusCode -eq 200
            }
            catch {
                $ready = $false
            }
        } while (-not $ready)
        Write-Host " ✓"
    }
    
    Write-Success "All services are healthy"
}

function Show-Status {
    Write-Step "Platform Status"
    Write-Host ""
    docker-compose -f $ComposeFile ps
    Write-Host ""
}

function Show-AccessInfo {
    Write-Step "Access Information"
    
    Write-Host ""
    Write-Host "🌐 Web Interfaces:" -ForegroundColor Green
    Write-Host "  • Dashboard:     http://localhost:3000"
    Write-Host "  • API Gateway:   http://localhost:8000"
    Write-Host "  • API Docs:      http://localhost:8000/docs"
    Write-Host "  • Grafana:       http://localhost:3001 (admin/admin123)"
    Write-Host "  • Prometheus:    http://localhost:9090"
    Write-Host ""
    Write-Host "🔌 Service Endpoints:" -ForegroundColor Green
    Write-Host "  • Bridge:        http://localhost:8001"
    Write-Host "  • Mempool:       http://localhost:8002"
    Write-Host "  • Honeypot:      http://localhost:8003"
    Write-Host "  • Scanner:       http://localhost:8004"
    Write-Host "  • MEV Bot:       http://localhost:8005"
    Write-Host "  • Bytecode:      http://localhost:8006"
    Write-Host "  • Quantum:       http://localhost:8007"
    Write-Host "  • Time Machine:  http://localhost:8008"
    Write-Host "  • Reporting:     http://localhost:8009"
    Write-Host ""
    Write-Host "📊 Monitoring:" -ForegroundColor Green
    Write-Host "  • Health Check:  curl http://localhost:8000/health"
    Write-Host "  • Metrics:       curl http://localhost:8000/metrics"
    Write-Host "  • Logs:          docker-compose logs -f [service-name]"
    Write-Host ""
}

function Start-Platform {
    Write-Header
    
    Test-Requirements
    Initialize-Environment
    Build-Services
    Start-Database
    Start-CoreServices
    Start-Microservices
    Start-Frontend
    Start-Monitoring
    Start-LoadBalancer
    Wait-ForServices
    
    Write-Header
    Write-Success "🎉 Scorpius Enterprise Platform started successfully!"
    
    Show-Status
    Show-AccessInfo
    
    Write-Host "💡 Useful Commands:" -ForegroundColor Blue
    Write-Host "  • View logs:     docker-compose logs -f"
    Write-Host "  • Stop platform: docker-compose down"
    Write-Host "  • Restart:       docker-compose restart [service]"
    Write-Host "  • Update:        git pull && docker-compose build && docker-compose up -d"
    Write-Host ""
    Write-Host "Note: On first run, services may take a few minutes to fully initialize." -ForegroundColor Yellow
    Write-Host ""
}

function Stop-Platform {
    Write-Step "Stopping Scorpius Enterprise Platform..."
    docker-compose -f $ComposeFile down
    Write-Success "Platform stopped"
}

function Restart-Platform {
    Write-Step "Restarting Scorpius Enterprise Platform..."
    docker-compose -f $ComposeFile restart
    Write-Success "Platform restarted"
}

function Clean-Platform {
    Write-Warning "This will remove all containers, volumes, and data!"
    $confirmation = Read-Host "Are you sure? (y/N)"
    if ($confirmation -eq "y" -or $confirmation -eq "Y") {
        docker-compose -f $ComposeFile down -v --remove-orphans
        docker system prune -af --volumes
        Write-Success "Platform cleaned"
    }
}

# Main execution based on action
switch ($Action.ToLower()) {
    "start" { Start-Platform }
    "stop" { Stop-Platform }
    "restart" { Restart-Platform }
    "status" { Show-Status }
    "clean" { Clean-Platform }
    default { 
        Write-Host "Usage: .\quick-start.ps1 [start|stop|restart|status|clean]"
        Write-Host "Default action is 'start'"
    }
}

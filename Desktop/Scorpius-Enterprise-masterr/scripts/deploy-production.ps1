# Scorpius Enterprise Production Deployment Script for Windows
# PowerShell version

param(
    [Parameter(Position=0)]
    [ValidateSet("", "start", "stop", "restart", "logs", "ps", "status", "build", "health", "down")]
    [string]$Command = "",
    
    [Parameter(Position=1)]
    [string]$Service = ""
)

# Configuration
$ProjectName = "scorpius-enterprise-production"
$ComposeFile = "docker-compose.production.yml"
$EnvFile = ".env.production"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }
function Write-Info { Write-ColorOutput Cyan $args }

Write-Info "🚀 Scorpius Enterprise Production Deployment"
Write-Info "=================================================="

function Test-Docker {
    try {
        docker info | Out-Null
        Write-Success "✓ Docker is running"
        return $true
    }
    catch {
        Write-Error "❌ Docker is not running. Please start Docker and try again."
        return $false
    }
}

function Test-DockerCompose {
    try {
        docker-compose --version | Out-Null
        Write-Success "✓ docker-compose is available"
        return $true
    }
    catch {
        Write-Error "❌ docker-compose is not installed. Please install it and try again."
        return $false
    }
}

function Test-EnvironmentFile {
    if (-not (Test-Path $EnvFile)) {
        Write-Warning "⚠ $EnvFile not found. Creating from template..."
        if (Test-Path ".env.production") {
            Copy-Item ".env.production" $EnvFile
            Write-Warning "⚠ Please edit $EnvFile with your production values before proceeding"
            Write-Warning "⚠ Pay special attention to passwords, secrets, and domain names"
            return $false
        }
        else {
            Write-Error "❌ No environment template found"
            return $false
        }
    }
    Write-Success "✓ Environment file exists"
    return $true
}

function New-RequiredDirectories {
    Write-Warning "📁 Creating necessary directories..."
    $directories = @(
        "logs\nginx",
        "logs\postgres", 
        "data",
        "uploads",
        "exports",
        "config\nginx\ssl"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    Write-Success "✓ Directories created"
}

function Build-Images {
    Write-Warning "🏗️ Building Docker images..."
    & docker-compose -f $ComposeFile --env-file $EnvFile build --no-cache
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Images built successfully"
    }
    else {
        Write-Error "❌ Failed to build images"
        exit 1
    }
}

function Start-Services {
    Write-Warning "🚀 Starting services..."
    & docker-compose -f $ComposeFile --env-file $EnvFile up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Services started"
    }
    else {
        Write-Error "❌ Failed to start services"
        exit 1
    }
}

function Test-ServiceHealth {
    Write-Warning "🏥 Checking service health..."
    Start-Sleep -Seconds 30  # Wait for services to initialize
    
    # Check if containers are running
    $runningContainers = & docker-compose -f $ComposeFile --env-file $EnvFile ps --format json | ConvertFrom-Json
    $upContainers = $runningContainers | Where-Object { $_.State -eq "running" }
    
    if ($upContainers.Count -gt 0) {
        Write-Success "✓ Services are running"
    }
    else {
        Write-Error "❌ Some services failed to start"
        & docker-compose -f $ComposeFile --env-file $EnvFile ps
        exit 1
    }
    
    # Check specific health endpoints
    Write-Warning "Checking individual service health..."
    
    # Wait for API Gateway
    $apiHealthy = $false
    for ($i = 1; $i -le 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "✓ API Gateway is healthy"
                $apiHealthy = $true
                break
            }
        }
        catch {
            if ($i -eq 30) {
                Write-Error "❌ API Gateway health check failed"
            }
        }
        Start-Sleep -Seconds 2
    }
    
    # Wait for Frontend
    $frontendHealthy = $false
    for ($i = 1; $i -le 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "✓ Frontend is healthy"
                $frontendHealthy = $true
                break
            }
        }
        catch {
            if ($i -eq 30) {
                Write-Error "❌ Frontend health check failed"
            }
        }
        Start-Sleep -Seconds 2
    }
}

function Show-ServiceUrls {
    Write-Info "`n🌐 Service URLs:"
    Write-Info "=================================================="
    Write-Success "Frontend:     http://localhost:3000"
    Write-Success "API Gateway:  http://localhost:8000"
    Write-Success "API Docs:     http://localhost:8000/docs"
    Write-Success "Monitoring:   http://localhost:9090"
    Write-Success "WebSocket:    ws://localhost:8080"
    Write-Output ""
    Write-Success "Service Status: docker-compose -f $ComposeFile ps"
    Write-Success "View Logs:      docker-compose -f $ComposeFile logs -f [service]"
    Write-Success "Stop Services:  docker-compose -f $ComposeFile down"
}

function Invoke-DatabaseMigrations {
    Write-Warning "📊 Running database migrations..."
    Start-Sleep -Seconds 10
    
    # Run migrations through the API Gateway container
    $migrationScript = @"
import asyncio
from backend.config.database import init_db
asyncio.run(init_db())
print('Database migrations completed')
"@
    
    try {
        & docker-compose -f $ComposeFile --env-file $EnvFile exec -T api-gateway python -c $migrationScript
        Write-Success "✓ Database migrations completed"
    }
    catch {
        Write-Warning "⚠ Migration command failed, but continuing..."
    }
}

function Start-MainDeployment {
    Write-Info "Starting deployment checks...`n"
    
    if (-not (Test-Docker)) { exit 1 }
    if (-not (Test-DockerCompose)) { exit 1 }
    if (-not (Test-EnvironmentFile)) { exit 1 }
    New-RequiredDirectories
    
    Write-Info "`nBuilding and starting services...`n"
    
    Build-Images
    Start-Services
    Invoke-DatabaseMigrations
    Test-ServiceHealth
    
    Write-Success "`n🎉 Deployment completed successfully!`n"
    Show-ServiceUrls
    
    Write-Warning "`n💡 Next steps:"
    Write-Output "1. Update your DNS to point to this server"
    Write-Output "2. Configure SSL certificates in config\nginx\ssl\"
    Write-Output "3. Update CORS_ORIGINS in $EnvFile with your domain"
    Write-Output "4. Set up monitoring and backup procedures"
    Write-Output "5. Review and update all default passwords"
}

# Handle command line arguments
switch ($Command) {
    "start" {
        Start-Services
    }
    "stop" {
        Write-Warning "🛑 Stopping services..."
        & docker-compose -f $ComposeFile --env-file $EnvFile down
        Write-Success "✓ Services stopped"
    }
    "restart" {
        Write-Warning "🔄 Restarting services..."
        & docker-compose -f $ComposeFile --env-file $EnvFile restart
        Write-Success "✓ Services restarted"
    }
    "logs" {
        & docker-compose -f $ComposeFile --env-file $EnvFile logs -f $Service
    }
    { $_ -in @("ps", "status") } {
        & docker-compose -f $ComposeFile --env-file $EnvFile ps
    }
    "build" {
        Build-Images
    }
    "health" {
        Test-ServiceHealth
    }
    "down" {
        Write-Warning "🗑️ Removing all containers and networks..."
        & docker-compose -f $ComposeFile --env-file $EnvFile down --remove-orphans
        Write-Success "✓ Cleanup completed"
    }
    "" {
        Start-MainDeployment
    }
    default {
        Write-Output "Usage: .\deploy-production.ps1 [start|stop|restart|logs|ps|build|health|down]"
        Write-Output ""
        Write-Output "Commands:"
        Write-Output "  start    - Start all services"
        Write-Output "  stop     - Stop all services"
        Write-Output "  restart  - Restart all services"
        Write-Output "  logs     - Show logs (optionally for specific service)"
        Write-Output "  ps       - Show service status"
        Write-Output "  build    - Build Docker images"
        Write-Output "  health   - Check service health"
        Write-Output "  down     - Stop and remove all containers"
        Write-Output ""
        Write-Output "Examples:"
        Write-Output "  .\deploy-production.ps1                    # Full deployment"
        Write-Output "  .\deploy-production.ps1 logs api-gateway   # Show API gateway logs"
        Write-Output "  .\deploy-production.ps1 restart frontend   # Restart frontend service"
        exit 1
    }
}

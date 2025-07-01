# Scorpius Enterprise Docker Management
# Comprehensive Docker orchestration for enterprise environment

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [string[]]$Arguments,
    [switch]$Force,
    [switch]$Clean
)

# Configuration
$DockerComposeFile = "docker-compose.enterprise.yml"
$ProjectRoot = $PSScriptRoot | Split-Path -Parent

function Write-Header {
    param([string]$Message)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Show-Help {
    Write-Header "Scorpius Enterprise Docker Management"
    
    Write-Host "Available commands:" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🚀 Startup & Shutdown:" -ForegroundColor Yellow
    Write-Host "  start         - Start all enterprise services" -ForegroundColor White
    Write-Host "  stop          - Stop all services" -ForegroundColor White
    Write-Host "  restart       - Restart all services" -ForegroundColor White
    Write-Host "  down          - Stop and remove containers" -ForegroundColor White
    Write-Host "  up            - Start services in background" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🔧 Development:" -ForegroundColor Yellow
    Write-Host "  dev           - Start development environment" -ForegroundColor White
    Write-Host "  dev-scanners  - Start only scanner plugins" -ForegroundColor White
    Write-Host "  dev-core      - Start core services only" -ForegroundColor White
    Write-Host "  dev-frontend  - Start frontend with hot reload" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🏗️  Build & Deploy:" -ForegroundColor Yellow
    Write-Host "  build         - Build all Docker images" -ForegroundColor White
    Write-Host "  build-scanners - Build scanner plugin images" -ForegroundColor White
    Write-Host "  build-core    - Build core service images" -ForegroundColor White
    Write-Host "  deploy        - Deploy to production" -ForegroundColor White
    Write-Host "  scale         - Scale services" -ForegroundColor White
    Write-Host ""
    
    Write-Host "📊 Monitoring & Logs:" -ForegroundColor Yellow
    Write-Host "  logs          - View all logs" -ForegroundColor White
    Write-Host "  logs-api      - View API gateway logs" -ForegroundColor White
    Write-Host "  logs-scanners - View scanner logs" -ForegroundColor White
    Write-Host "  monitor       - Open monitoring dashboards" -ForegroundColor White
    Write-Host "  health        - Check service health" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🔍 Scanner Management:" -ForegroundColor Yellow
    Write-Host "  scanner-slither   - Manage Slither scanner" -ForegroundColor White
    Write-Host "  scanner-mythril   - Manage Mythril scanner" -ForegroundColor White
    Write-Host "  scanner-mythx     - Manage MythX scanner" -ForegroundColor White
    Write-Host "  scanner-manticore - Manage Manticore scanner" -ForegroundColor White
    Write-Host "  test-scanners     - Test all scanner plugins" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🧹 Maintenance:" -ForegroundColor Yellow
    Write-Host "  clean         - Clean up Docker resources" -ForegroundColor White
    Write-Host "  prune         - Remove unused Docker resources" -ForegroundColor White
    Write-Host "  backup        - Backup data volumes" -ForegroundColor White
    Write-Host "  restore       - Restore from backup" -ForegroundColor White
    Write-Host "  update        - Update all images" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🔧 Utilities:" -ForegroundColor Yellow
    Write-Host "  shell         - Open shell in dev-tools container" -ForegroundColor White
    Write-Host "  exec          - Execute command in container" -ForegroundColor White
    Write-Host "  status        - Show service status" -ForegroundColor White
    Write-Host "  ports         - Show port mappings" -ForegroundColor White
    Write-Host "  help          - Show this help message" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Usage: .\scripts\docker-enterprise.ps1 <command> [arguments]" -ForegroundColor Gray
    Write-Host "Example: .\scripts\docker-enterprise.ps1 start --force" -ForegroundColor Gray
}

function Run-DockerCompose {
    param([string[]]$Args)
    Set-Location $ProjectRoot
    docker-compose @Args
}

function Start-Enterprise {
    Write-Header "Starting Scorpius Enterprise Environment"
    Write-Host "Starting all enterprise services..." -ForegroundColor Yellow
    $composeArgs = @('-f', $DockerComposeFile, 'up', '-d')
    if ($Force) { $composeArgs += '--force-recreate' }
    Run-DockerCompose -Args $composeArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Enterprise environment started successfully!" -ForegroundColor Green
        Show-ServiceStatus
    } else {
        Write-Host "❌ Failed to start enterprise environment" -ForegroundColor Red
    }
}

function Stop-Enterprise {
    Write-Header "Stopping Scorpius Enterprise Environment"
    Write-Host "Stopping all services..." -ForegroundColor Yellow
    Run-DockerCompose -Args @('-f', $DockerComposeFile, 'down')
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Enterprise environment stopped successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to stop enterprise environment" -ForegroundColor Red
    }
}

function Restart-Enterprise {
    Write-Header "Restarting Scorpius Enterprise Environment"
    Stop-Enterprise
    Start-Sleep -Seconds 5
    Start-Enterprise
}

function Build-Enterprise {
    Write-Header "Building Scorpius Enterprise Images"
    Set-Location $ProjectRoot
    
    Write-Host "Building all Docker images..." -ForegroundColor Yellow
    docker-compose -f $DockerComposeFile build --no-cache
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All images built successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to build images" -ForegroundColor Red
    }
}

function Build-Scanners {
    Write-Header "Building Scanner Plugin Images"
    Set-Location $ProjectRoot
    
    $scanners = @("scanner-slither", "scanner-mythril", "scanner-mythx", "scanner-manticore")
    
    foreach ($scanner in $scanners) {
        Write-Host "Building $scanner..." -ForegroundColor Yellow
        docker-compose -f $DockerComposeFile build --no-cache $scanner
    }
    
    Write-Host "✅ Scanner images built successfully!" -ForegroundColor Green
}

function Show-ServiceStatus {
    Write-Header "Service Status"
    Set-Location $ProjectRoot
    
    docker-compose -f $DockerComposeFile ps
}

function Show-Logs {
    param([string]$Service = "all")
    
    Write-Header "Service Logs"
    Set-Location $ProjectRoot
    
    if ($Service -eq "all") {
        docker-compose -f $DockerComposeFile logs -f
    } else {
        docker-compose -f $DockerComposeFile logs -f $Service
    }
}

function Show-ScannerLogs {
    Write-Header "Scanner Plugin Logs"
    Set-Location $ProjectRoot
    
    $scanners = @("scanner-slither", "scanner-mythril", "scanner-mythx", "scanner-manticore")
    
    foreach ($scanner in $scanners) {
        Write-Host "`n=== $scanner ===" -ForegroundColor Cyan
        docker-compose -f $DockerComposeFile logs --tail=20 $scanner
    }
}

function Test-Scanners {
    Write-Header "Testing Scanner Plugins"
    Set-Location $ProjectRoot
    
    $scanners = @{
        "slither" = "http://localhost:8002/health"
        "mythril" = "http://localhost:8003/health"
        "mythx" = "http://localhost:8004/health"
        "manticore" = "http://localhost:8005/health"
    }
    
    foreach ($scanner in $scanners.GetEnumerator()) {
        Write-Host "Testing $($scanner.Key)..." -ForegroundColor Yellow
        try {
            $response = Invoke-WebRequest -Uri $scanner.Value -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $($scanner.Key) is healthy" -ForegroundColor Green
            } else {
                Write-Host "⚠️  $($scanner.Key) returned status $($response.StatusCode)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ $($scanner.Key) is not responding" -ForegroundColor Red
        }
    }
}

function Open-Monitoring {
    Write-Header "Opening Monitoring Dashboards"
    
    $dashboards = @{
        "Grafana" = "http://localhost:3001"
        "Prometheus" = "http://localhost:9090"
        "PgAdmin" = "http://localhost:5050"
        "Redis Commander" = "http://localhost:8081"
    }
    
    foreach ($dashboard in $dashboards.GetEnumerator()) {
        Write-Host "Opening $($dashboard.Key)..." -ForegroundColor Yellow
        Start-Process $dashboard.Value
    }
}

function Check-Health {
    Write-Header "Health Check"
    Set-Location $ProjectRoot
    
    $services = @("api-gateway", "bridge-service", "bytecode-service", "honeypot-service", "mempool-service")
    
    foreach ($service in $services) {
        Write-Host "Checking $service..." -ForegroundColor Yellow
        $status = docker-compose -f $DockerComposeFile ps $service --format "table {{.Status}}"
        Write-Host $status
    }
}

function Clean-Docker {
    Write-Header "Cleaning Docker Resources"
    
    if ($Force) {
        Write-Host "Force cleaning all Docker resources..." -ForegroundColor Yellow
        docker system prune -a --volumes --force
    } else {
        Write-Host "Cleaning unused Docker resources..." -ForegroundColor Yellow
        docker system prune --volumes
    }
    
    Write-Host "✅ Docker cleanup completed!" -ForegroundColor Green
}

function Backup-Data {
    Write-Header "Backing Up Data Volumes"
    Set-Location $ProjectRoot
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "backups/docker_$timestamp"
    
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    $volumes = @("scorpius_postgres_data_enterprise", "scorpius_redis_data_enterprise", "scorpius_prometheus_data_enterprise", "scorpius_grafana_data_enterprise")
    
    foreach ($volume in $volumes) {
        Write-Host "Backing up $volume..." -ForegroundColor Yellow
        docker run --rm -v $volume`:/data -v ${PWD}/$backupDir`:/backup alpine tar czf /backup/$volume.tar.gz -C /data .
    }
    
    Write-Host "✅ Backup completed in $backupDir" -ForegroundColor Green
}

function Open-Shell {
    Write-Header "Opening Development Shell"
    Set-Location $ProjectRoot
    
    Write-Host "Opening shell in dev-tools container..." -ForegroundColor Yellow
    docker-compose -f $DockerComposeFile exec dev-tools /bin/bash
}

function Execute-Command {
    param([string]$Service, [string]$Command)
    
    Write-Header "Executing Command in $Service"
    Set-Location $ProjectRoot
    
    if ($Service -and $Command) {
        docker-compose -f $DockerComposeFile exec $Service $Command
    } else {
        Write-Host "Usage: .\scripts\docker-enterprise.ps1 exec <service> <command>" -ForegroundColor Red
    }
}

function Show-Ports {
    Write-Header "Port Mappings"
    
    $ports = @{
        "API Gateway" = "8000"
        "API Debug" = "8001"
        "Slither Scanner" = "8002"
        "Mythril Scanner" = "8003"
        "MythX Scanner" = "8004"
        "Manticore Scanner" = "8005"
        "Frontend" = "3000"
        "Grafana" = "3001"
        "Prometheus" = "9090"
        "PgAdmin" = "5050"
        "Redis Commander" = "8081"
        "PostgreSQL" = "5432"
        "Redis" = "6379"
    }
    
    foreach ($port in $ports.GetEnumerator()) {
        Write-Host "$($port.Key):`t$($port.Value)" -ForegroundColor White
    }
}

function Start-Development {
    Write-Header "Starting Development Environment"
    Set-Location $ProjectRoot
    
    Write-Host "Starting development services..." -ForegroundColor Yellow
    docker-compose -f $DockerComposeFile up -d redis postgres api-gateway frontend dev-tools
    
    Write-Host "✅ Development environment started!" -ForegroundColor Green
    Show-Ports
}

function Start-Scanners {
    Write-Header "Starting Scanner Plugins"
    Set-Location $ProjectRoot
    
    Write-Host "Starting scanner services..." -ForegroundColor Yellow
    docker-compose -f $DockerComposeFile up -d scanner-slither scanner-mythril scanner-mythx scanner-manticore
    
    Write-Host "✅ Scanner plugins started!" -ForegroundColor Green
    Test-Scanners
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "start" { Start-Enterprise }
    "stop" { Stop-Enterprise }
    "restart" { Restart-Enterprise }
    "down" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile down
    }
    "up" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile up -d
    }
    "dev" { Start-Development }
    "dev-scanners" { Start-Scanners }
    "dev-core" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile up -d redis postgres api-gateway bridge-service bytecode-service
    }
    "dev-frontend" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile up -d frontend
    }
    "build" { Build-Enterprise }
    "build-scanners" { Build-Scanners }
    "build-core" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile build api-gateway bridge-service bytecode-service honeypot-service mempool-service quantum-service time-machine-service
    }
    "deploy" { 
        Write-Header "Deploying to Production"
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile up -d --no-deps
    }
    "scale" { 
        if ($Arguments.Count -ge 2) {
            Set-Location $ProjectRoot
            docker-compose -f $DockerComposeFile up -d --scale $Arguments[0]=$Arguments[1]
        } else {
            Write-Host "Usage: .\scripts\docker-enterprise.ps1 scale <service> <count>" -ForegroundColor Red
        }
    }
    "logs" { Show-Logs }
    "logs-api" { Show-Logs "api-gateway" }
    "logs-scanners" { Show-ScannerLogs }
    "monitor" { Open-Monitoring }
    "health" { Check-Health }
    "scanner-slither" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile logs -f scanner-slither
    }
    "scanner-mythril" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile logs -f scanner-mythril
    }
    "scanner-mythx" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile logs -f scanner-mythx
    }
    "scanner-manticore" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile logs -f scanner-manticore
    }
    "test-scanners" { Test-Scanners }
    "clean" { Clean-Docker }
    "prune" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile down --volumes --remove-orphans
    }
    "backup" { Backup-Data }
    "restore" { 
        Write-Host "Restore functionality not implemented yet" -ForegroundColor Yellow
    }
    "update" { 
        Set-Location $ProjectRoot
        docker-compose -f $DockerComposeFile pull
    }
    "shell" { Open-Shell }
    "exec" { 
        if ($Arguments.Count -ge 2) {
            Execute-Command $Arguments[0] $Arguments[1]
        } else {
            Write-Host "Usage: .\scripts\docker-enterprise.ps1 exec <service> <command>" -ForegroundColor Red
        }
    }
    "status" { Show-ServiceStatus }
    "ports" { Show-Ports }
    "help" { Show-Help }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\scripts\docker-enterprise.ps1 help' for available commands" -ForegroundColor Yellow
        exit 1
    }
} 
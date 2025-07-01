#!/usr/bin/env pwsh
#
# Scorpius Enterprise Management Script
# Common management operations for the vulnerability scanner
#

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "test", "cleanup", "backup")]
    [string]$Action,
    
    [string]$Service = "all",
    [switch]$Follow = $false
)

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Blue }

Write-Host "🔧 Scorpius Enterprise Management" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

switch ($Action) {
    "start" {
        Write-Info "Starting Scorpius services..."
        if ($Service -eq "all") {
            docker-compose up -d
        } else {
            docker-compose up -d $Service
        }
        Write-Success "Services started"
    }
    
    "stop" {
        Write-Info "Stopping Scorpius services..."
        if ($Service -eq "all") {
            docker-compose down
        } else {
            docker-compose stop $Service
        }
        Write-Success "Services stopped"
    }
    
    "restart" {
        Write-Info "Restarting Scorpius services..."
        if ($Service -eq "all") {
            docker-compose restart
        } else {
            docker-compose restart $Service
        }
        Write-Success "Services restarted"
    }
    
    "status" {
        Write-Info "Checking service status..."
        docker-compose ps
        Write-Host ""
        Write-Info "Resource usage:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    }
    
    "logs" {
        Write-Info "Viewing logs for $Service..."
        if ($Follow) {
            if ($Service -eq "all") {
                docker-compose logs -f
            } else {
                docker-compose logs -f $Service
            }
        } else {
            if ($Service -eq "all") {
                docker-compose logs --tail=100
            } else {
                docker-compose logs --tail=100 $Service
            }
        }
    }
    
    "test" {
        Write-Info "Running system tests..."
        
        # Test API health
        Write-Info "Testing API health..."
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Success "API is healthy"
            } else {
                Write-Warning "API returned status: $($response.StatusCode)"
            }
        } catch {
            Write-Error "API health check failed: $($_.Exception.Message)"
        }
        
        # Test Docker plugins
        Write-Info "Testing Docker plugins..."
        if (Test-Path "test_docker_plugins.py") {
            python test_docker_plugins.py
        } else {
            Write-Warning "Plugin test script not found"
        }
        
        # Test database connectivity
        Write-Info "Testing database connectivity..."
        $dbTest = docker-compose exec -T postgres psql -U scorpius -d scorpius -c "SELECT 1;" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database is accessible"
        } else {
            Write-Error "Database connectivity failed"
        }
    }
    
    "cleanup" {
        Write-Warning "Performing system cleanup..."
        Write-Info "Removing stopped containers..."
        docker container prune -f
        
        Write-Info "Removing unused images..."
        docker image prune -f
        
        Write-Info "Removing unused volumes..."
        docker volume prune -f
        
        Write-Info "Removing unused networks..."
        docker network prune -f
        
        Write-Success "Cleanup completed"
    }
    
    "backup" {
        Write-Info "Creating system backup..."
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupDir = "backups/backup_$timestamp"
        
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        
        # Backup database
        Write-Info "Backing up database..."
        docker-compose exec -T postgres pg_dump -U scorpius scorpius > "$backupDir/database.sql"
        
        # Backup configuration
        Write-Info "Backing up configuration..."
        Copy-Item "docker-compose.yml" "$backupDir/"
        Copy-Item ".env" "$backupDir/" -ErrorAction SilentlyContinue
        
        # Backup reports
        Write-Info "Backing up reports..."
        if (Test-Path "reports") {
            Copy-Item "reports" "$backupDir/" -Recurse
        }
        
        Write-Success "Backup created at: $backupDir"
    }
}

Write-Host ""
Write-Host "📋 Available Commands:" -ForegroundColor Yellow
Write-Host "  start    - Start services"
Write-Host "  stop     - Stop services" 
Write-Host "  restart  - Restart services"
Write-Host "  status   - Show service status"
Write-Host "  logs     - View service logs (use -Follow for real-time)"
Write-Host "  test     - Run system tests"
Write-Host "  cleanup  - Clean up Docker resources"
Write-Host "  backup   - Create system backup"
Write-Host ""
Write-Host "📖 Usage Examples:" -ForegroundColor Green
Write-Host "  .\manage.ps1 start"
Write-Host "  .\manage.ps1 logs -Service scorpius-main -Follow"
Write-Host "  .\manage.ps1 stop -Service postgres"

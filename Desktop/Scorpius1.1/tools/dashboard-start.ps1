#!/usr/bin/env pwsh
# Scorpius Dashboard Integration - Quick Start Script
# Starts the integrated dashboard with backend services

param(
    [string]$Environment = "dev",
    [switch]$Build = $false,
    [switch]$Clean = $false,
    [switch]$Logs = $false
)

Write-Host "🚀 Scorpius Dashboard Integration Quick Start" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Set error handling
$ErrorActionPreference = "Stop"

try {
    # Clean up if requested
    if ($Clean) {
        Write-Host "🧹 Cleaning up containers and volumes..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml down -v --remove-orphans
        docker system prune -f
    }

    # Create .env file if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Host "📋 Creating .env file from template..." -ForegroundColor Yellow
        Copy-Item ".env.dev" ".env"
        Write-Host "⚠️  Please review and update .env file with your settings" -ForegroundColor Yellow
    }

    # Build if requested or if images don't exist
    if ($Build) {
        Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml build --parallel
    }

    # Start services based on profile
    Write-Host "🚀 Starting Scorpius Enterprise Platform with Dashboard..." -ForegroundColor Green
    
    $ComposeFiles = @(
        "docker-compose.dev.yml"
    )
    
    $ComposeCmd = "docker-compose"
    foreach ($file in $ComposeFiles) {
        $ComposeCmd += " -f $file"
    }
    
    $Services = @("redis", "postgres", "orchestrator", "api-gateway", "dashboard")
    
    Write-Host "Starting services: $($Services -join ', ')" -ForegroundColor Green
    
    # Start services (remove --profile flag as it's not supported in older Docker Compose versions)
    Invoke-Expression "$ComposeCmd up -d $($Services -join ' ')"
    
    # Wait for services to be ready
    Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Health checks
    Write-Host "🏥 Checking service health..." -ForegroundColor Yellow
    
    $ApiGatewayHealth = try {
        Invoke-RestMethod -Uri "http://localhost:8000/healthz" -TimeoutSec 5
        Write-Host "✅ API Gateway: Healthy" -ForegroundColor Green
        $true
    } catch {
        Write-Host "❌ API Gateway: Not responding" -ForegroundColor Red
        $false
    }
    
    $DashboardHealth = try {
        Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 | Out-Null
        Write-Host "✅ Dashboard: Healthy" -ForegroundColor Green
        $true
    } catch {
        Write-Host "❌ Dashboard: Not responding" -ForegroundColor Red
        $false
    }
    
    # Display access information
    Write-Host ""
    Write-Host "🎉 Scorpius Dashboard Integration Started Successfully!" -ForegroundColor Green
    Write-Host "=================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access Points:" -ForegroundColor Cyan
    Write-Host "   Dashboard:        http://localhost:3000" -ForegroundColor White
    Write-Host "   API Gateway:      http://localhost:8000" -ForegroundColor White
    Write-Host "   API Documentation: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   WebSocket:        ws://localhost:8000/ws" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Admin Tools:" -ForegroundColor Cyan
    Write-Host "   PostgreSQL Admin: http://localhost:5050" -ForegroundColor White
    Write-Host "   Redis Commander:  http://localhost:8081" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Default Login:" -ForegroundColor Cyan
    Write-Host "   Username: admin" -ForegroundColor White
    Write-Host "   Password: admin" -ForegroundColor White
    Write-Host ""
    
    if ($Logs) {
        Write-Host "📋 Following logs (Ctrl+C to stop)..." -ForegroundColor Yellow
        Invoke-Expression "$ComposeCmd logs -f api-gateway dashboard"
    } else {
        Write-Host "💡 Commands:" -ForegroundColor Cyan
        Write-Host "   View logs:    $ComposeCmd logs -f" -ForegroundColor White
        Write-Host "   Stop services: $ComposeCmd down" -ForegroundColor White
        Write-Host "   Restart:      .\dashboard-start.ps1 -Clean" -ForegroundColor White
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Error starting dashboard integration: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Make sure Docker is running" -ForegroundColor White
    Write-Host "   2. Check if ports 3000, 8000, 5432, 6379 are available" -ForegroundColor White
    Write-Host "   3. Try running with -Clean flag to reset" -ForegroundColor White
    Write-Host "   4. Check logs: docker-compose -f docker-compose.dev.yml logs" -ForegroundColor White
    exit 1
}

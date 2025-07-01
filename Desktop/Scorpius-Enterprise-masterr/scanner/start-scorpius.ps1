#!/usr/bin/env pwsh
# Scorpius Enterprise Scanner - Startup Script
# Starts all scanner plugins and backend services

Write-Host "🔥 Starting Scorpius Enterprise Vulnerability Scanner..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Navigate to scanner directory
$scannerPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scannerPath

Write-Host "📂 Working directory: $scannerPath" -ForegroundColor Yellow

# Stop any existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down --remove-orphans

# Build and start all services
Write-Host "🔧 Building and starting all services..." -ForegroundColor Cyan
docker-compose up -d --build

# Wait a moment for services to start
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "📊 Service Status:" -ForegroundColor Cyan
docker-compose ps

# Display service URLs
Write-Host "`n🌐 Service URLs:" -ForegroundColor Green
Write-Host "   Main Scanner API:    http://localhost:8090" -ForegroundColor White
Write-Host "   Slither Plugin:      http://localhost:8091" -ForegroundColor White
Write-Host "   Mythril Plugin:      http://localhost:8092" -ForegroundColor White
Write-Host "   Manticore Plugin:    http://localhost:8093" -ForegroundColor White
Write-Host "   MythX Plugin:        http://localhost:8094" -ForegroundColor White
Write-Host "   PostgreSQL DB:       localhost:5433" -ForegroundColor White
Write-Host "   Redis Cache:         localhost:6380" -ForegroundColor White

Write-Host "`n🚀 Scorpius Enterprise Scanner is now running!" -ForegroundColor Green
Write-Host "📝 View logs with: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "🛑 Stop services with: docker-compose down" -ForegroundColor Yellow

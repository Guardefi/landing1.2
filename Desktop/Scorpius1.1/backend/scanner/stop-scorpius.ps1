#!/usr/bin/env pwsh
# Scorpius Enterprise Scanner - Stop Script
# Stops all scanner plugins and backend services

Write-Host "🛑 Stopping Scorpius Enterprise Scanner..." -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor Red

# Navigate to scanner directory
$scannerPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scannerPath

# Stop all services
Write-Host "🔄 Stopping all services..." -ForegroundColor Yellow
docker-compose down --remove-orphans

# Show final status
Write-Host "📊 Final Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`n✅ Scorpius Enterprise Scanner stopped successfully!" -ForegroundColor Green

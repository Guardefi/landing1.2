#!/usr/bin/env pwsh
<#
.SYNOPSIS
    🦂 FIRE UP SCORPIUS ENTERPRISE - ONE COMMAND STARTUP
    
.DESCRIPTION
    Single command to launch the world's most advanced blockchain security platform.
    This script will start all enterprise services and provide access URLs.
    
.EXAMPLE
    .\FIRE-UP-ENTERPRISE.ps1
#>

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🦂 FIRING UP SCORPIUS ENTERPRISE PLATFORM" -ForegroundColor Yellow
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "🚀 Starting the world's most advanced blockchain security suite..." -ForegroundColor Green

# Check if Docker is running
try {
    $null = docker --version
    Write-Host "✅ Docker is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating environment configuration..." -ForegroundColor Blue
    @"
# Scorpius Enterprise Environment Configuration
POSTGRES_DB=scorpius_enterprise
POSTGRES_USER=scorpius_admin
POSTGRES_PASSWORD=enterprise_secure_password_2024
REDIS_PASSWORD=enterprise_redis_password_2024
MONGODB_PASSWORD=enterprise_mongo_password_2024
JWT_SECRET=enterprise_jwt_secret_2024_very_long_and_secure
API_KEY=enterprise_api_key_2024
ENVIRONMENT=development
LOG_LEVEL=INFO
"@ | Out-File -FilePath ".env" -Encoding UTF8
}

# Start all services
Write-Host "🔄 Starting enterprise services..." -ForegroundColor Blue
docker-compose -f docker/docker-compose.enterprise.yml up -d

# Wait for services to initialize
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# Check service status
Write-Host "`n📊 Service Status:" -ForegroundColor Cyan
docker-compose -f docker/docker-compose.enterprise.yml ps

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🎉 SCORPIUS ENTERPRISE PLATFORM IS READY!" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "🌐 Access Your Enterprise Platform:" -ForegroundColor Yellow
Write-Host "  • Main Dashboard:     http://localhost:3000" -ForegroundColor Cyan
Write-Host "  • API Gateway:        http://localhost:8000" -ForegroundColor Cyan
Write-Host "  • API Documentation:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  • Threat Monitoring:  http://localhost:8007" -ForegroundColor Cyan
Write-Host "  • Elite Security:     http://localhost:8008" -ForegroundColor Cyan
Write-Host "  • AI Forensics:       http://localhost:8009" -ForegroundColor Cyan
Write-Host "  • Quantum Crypto:     http://localhost:8010" -ForegroundColor Cyan
Write-Host "  • MEV Protection:     http://localhost:8011" -ForegroundColor Cyan
Write-Host "  • Integration Hub:    http://localhost:8014" -ForegroundColor Cyan
Write-Host "  • Grafana Monitor:    http://localhost:3001" -ForegroundColor Cyan
Write-Host "  • Database Admin:     http://localhost:5050" -ForegroundColor Cyan
Write-Host "  • Redis Admin:        http://localhost:8081" -ForegroundColor Cyan

Write-Host "`n🔧 Management Commands:" -ForegroundColor Yellow
Write-Host "  • View logs:          docker-compose -f docker/docker-compose.enterprise.yml logs -f" -ForegroundColor Gray
Write-Host "  • Stop services:      docker-compose -f docker/docker-compose.enterprise.yml down" -ForegroundColor Gray
Write-Host "  • Restart services:   docker-compose -f docker/docker-compose.enterprise.yml restart" -ForegroundColor Gray

Write-Host "`n🦂 Welcome to the future of blockchain security!" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Cyan
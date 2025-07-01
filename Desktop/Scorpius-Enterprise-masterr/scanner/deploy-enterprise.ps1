#!/usr/bin/env pwsh
#
# Scorpius Enterprise Vulnerability Scanner - Production Deployment Script
# This script deploys the complete enterprise-grade vulnerability scanning platform
#

param(
    [string]$Environment = "production",
    [switch]$CleanInstall = $false,
    [switch]$SkipBuild = $false,
    [string]$Profile = "full"
)

Write-Host "🔥 Scorpius Enterprise Vulnerability Scanner Deployment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_NAME = "scorpius-enterprise"
$DOCKER_NETWORK = "scorpius-network"
$COMPOSE_PROJECT = "scorpius"

# Colors for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Blue }

try {
    # Step 1: Cleanup existing resources
    if ($CleanInstall) {
        Write-Host "🧹 Performing clean installation..." -ForegroundColor Yellow
        
        Write-Info "Stopping all running containers..."
        docker-compose -f docker-compose.yml down --remove-orphans --volumes 2>$null
        
        Write-Info "Removing old containers..."
        docker container prune -f 2>$null
        
        Write-Info "Removing unused images..."
        docker image prune -f 2>$null
        
        Write-Info "Removing unused volumes..."
        docker volume prune -f 2>$null
        
        Write-Info "Removing unused networks..."
        docker network prune -f 2>$null
        
        Write-Success "Clean installation preparation complete"
    }

    # Step 2: Environment validation
    Write-Host "🔍 Validating environment..." -ForegroundColor Yellow
    
    # Check Docker
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed or not in PATH"
        exit 1
    }
    
    # Check Docker Compose
    if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Error "Docker Compose is not installed or not in PATH"
        exit 1
    }
    
    # Check Docker daemon
    try {
        docker version | Out-Null
        Write-Success "Docker daemon is running"
    }
    catch {
        Write-Error "Docker daemon is not running. Please start Docker Desktop."
        exit 1
    }
    
    Write-Success "Environment validation complete"

    # Step 3: Create required directories
    Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
    
    $directories = @(
        "contracts",
        "reports", 
        "logs",
        "config",
        "data/postgres",
        "data/redis", 
        "data/elasticsearch",
        "data/grafana",
        "data/prometheus"
    )
    
    foreach ($dir in $directories) {
        $fullPath = Join-Path $PWD $dir
        if (!(Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
            Write-Info "Created directory: $dir"
        }
    }
    
    Write-Success "Directory structure created"

    # Step 4: Build Docker images
    if (!$SkipBuild) {
        Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow
        
        # Build main application
        Write-Info "Building Scorpius Enterprise main application..."
        docker build -t scorpius-enterprise -f docker/scorpius/Dockerfile . --no-cache
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to build main Scorpius application"
            exit 1
        }
        
        # Tag with proper naming
        docker tag scorpius-enterprise:latest scorpius/enterprise:latest
        
        Write-Success "Docker images built successfully"
    }

    # Step 5: Create environment file
    Write-Host "⚙️  Configuring environment..." -ForegroundColor Yellow
    
    $envContent = @"
# Scorpius Enterprise Configuration
COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT
SCORPIUS_ENV=$Environment

# Database Configuration
POSTGRES_DB=scorpius
POSTGRES_USER=scorpius
POSTGRES_PASSWORD=scorpius_enterprise_$(Get-Random -Minimum 1000 -Maximum 9999)

# Redis Configuration  
REDIS_PASSWORD=scorpius_redis_$(Get-Random -Minimum 1000 -Maximum 9999)

# Security Keys
JWT_SECRET_KEY=scorpius_jwt_$(Get-Random -Minimum 10000 -Maximum 99999)
ENCRYPTION_KEY=scorpius_enc_$(Get-Random -Minimum 10000 -Maximum 99999)

# External APIs (Optional - set if you have keys)
ANTHROPIC_API_KEY=
MYTHX_API_KEY=
MAINNET_FORK_URL=

# MinIO Configuration
MINIO_ROOT_USER=scorpius
MINIO_ROOT_PASSWORD=scorpius_minio_$(Get-Random -Minimum 1000 -Maximum 9999)

# Network Configuration
SCORPIUS_NETWORK_SUBNET=172.20.0.0/16
"@
    
    Set-Content -Path ".env" -Value $envContent
    Write-Success "Environment configuration created"

    # Step 6: Deploy based on profile
    Write-Host "🚀 Deploying Scorpius Enterprise..." -ForegroundColor Yellow
    
    switch ($Profile) {
        "minimal" {
            Write-Info "Deploying minimal profile (core services only)..."
            docker-compose up -d scorpius-main postgres redis
        }
        "plugins" {
            Write-Info "Deploying with security plugins..."
            docker-compose --profile plugins up -d
        }
        "monitoring" {
            Write-Info "Deploying with monitoring stack..."
            docker-compose --profile monitoring up -d
        }
        "simulation" {
            Write-Info "Deploying with simulation environment..."
            docker-compose --profile simulation up -d
        }
        "full" {
            Write-Info "Deploying full enterprise stack..."
            docker-compose --profile plugins --profile monitoring --profile simulation up -d
        }
        default {
            Write-Info "Deploying core services..."
            docker-compose up -d scorpius-main postgres redis
        }
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Deployment failed"
        exit 1
    }

    # Step 7: Wait for services to be ready
    Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
    
    $maxAttempts = 30
    $attempt = 0
    
    do {
        Start-Sleep -Seconds 2
        $attempt++
        $health = docker-compose ps --services --filter "status=running" | Measure-Object | Select-Object -ExpandProperty Count
        Write-Host "." -NoNewline
        
        if ($attempt -ge $maxAttempts) {
            Write-Error "`nTimeout waiting for services to start"
            break
        }
    } while ($health -lt 3)
    
    Write-Host ""
    Write-Success "Services are starting up"

    # Step 8: Display deployment status
    Write-Host "`n📊 Deployment Status" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    
    # Show running containers
    Write-Info "Running containers:"
    docker-compose ps
    
    Write-Host "`n🌐 Service Endpoints" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    Write-Host "🔗 Scorpius API:      http://localhost:8080" -ForegroundColor Green
    Write-Host "🔗 API Documentation: http://localhost:8080/docs" -ForegroundColor Green
    Write-Host "🔗 Grafana:           http://localhost:3000" -ForegroundColor Green
    Write-Host "🔗 Kibana:            http://localhost:5601" -ForegroundColor Green
    
    Write-Host "`n🔧 Management Commands" -ForegroundColor Cyan
    Write-Host "=====================" -ForegroundColor Cyan
    Write-Host "View logs:     docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "Stop all:      docker-compose down" -ForegroundColor Yellow
    Write-Host "Restart:       docker-compose restart" -ForegroundColor Yellow
    Write-Host "Update:        docker-compose pull && docker-compose up -d" -ForegroundColor Yellow
    
    Write-Host "`n🎉 Scorpius Enterprise Deployment Complete!" -ForegroundColor Green
    Write-Host "The vulnerability scanner is ready for enterprise use." -ForegroundColor Green

}
catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    Write-Host "Check the logs above for details." -ForegroundColor Red
    exit 1
}

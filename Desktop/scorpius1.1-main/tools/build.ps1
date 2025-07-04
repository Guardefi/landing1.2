# Scorpius Enterprise Platform - PowerShell Build Script
# Usage: .\build.ps1 [command]

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Scorpius Enterprise Platform - Build Commands" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Development Commands:" -ForegroundColor Yellow
    Write-Host "  dev-up     - Start development environment"
    Write-Host "  dev-down   - Stop development environment"
    Write-Host "  dev-logs   - Show development logs"
    Write-Host ""
    Write-Host "Production Commands:" -ForegroundColor Yellow
    Write-Host "  prod-up    - Start production environment"
    Write-Host "  prod-down  - Stop production environment"
    Write-Host "  prod-logs  - Show production logs"
    Write-Host ""
    Write-Host "Build Commands:" -ForegroundColor Yellow
    Write-Host "  build      - Build all services"
    Write-Host "  build-dev  - Build development images"
    Write-Host "  build-prod - Build production images"
    Write-Host ""
    Write-Host "Utility Commands:" -ForegroundColor Yellow
    Write-Host "  clean      - Clean up containers and images"
    Write-Host "  test       - Run tests"
    Write-Host "  lint       - Run linting"
    Write-Host "  install    - Install dependencies"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\build.ps1 dev-up"
    Write-Host "  .\build.ps1 prod-build"
    Write-Host "  .\build.ps1 test"
}

function Start-DevEnvironment {
    Write-Host "Starting development environment..." -ForegroundColor Green
    docker-compose -f docker-compose.dev.yml up -d
}

function Stop-DevEnvironment {
    Write-Host "Stopping development environment..." -ForegroundColor Yellow
    docker-compose -f docker-compose.dev.yml down
}

function Show-DevLogs {
    docker-compose -f docker-compose.dev.yml logs -f
}

function Start-ProdEnvironment {
    Write-Host "Starting production environment..." -ForegroundColor Green
    if (-not (Test-Path ".env")) {
        Write-Host "Warning: .env file not found. Using .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env" -Force
    }
    docker-compose -f docker-compose.prod.yml up -d
}

function Stop-ProdEnvironment {
    Write-Host "Stopping production environment..." -ForegroundColor Yellow
    docker-compose -f docker-compose.prod.yml down
}

function Show-ProdLogs {
    docker-compose -f docker-compose.prod.yml logs -f
}

function Build-All {
    Write-Host "Building all services..." -ForegroundColor Green
    docker-compose -f docker-compose.unified.yml build
}

function Build-Dev {
    Write-Host "Building development images..." -ForegroundColor Green
    docker-compose -f docker-compose.dev.yml build
}

function Build-Prod {
    Write-Host "Building production images..." -ForegroundColor Green
    docker-compose -f docker-compose.prod.yml build
}

function Clean-Docker {
    Write-Host "Cleaning up Docker containers and images..." -ForegroundColor Yellow
    docker-compose -f docker-compose.unified.yml down --remove-orphans
    docker system prune -f
    docker volume prune -f
}

function Run-Tests {
    Write-Host "Running tests..." -ForegroundColor Green
    if (Test-Path "pyproject.toml") {
        poetry run pytest
    } else {
        Write-Host "No test configuration found" -ForegroundColor Red
    }
}

function Run-Lint {
    Write-Host "Running linting..." -ForegroundColor Green
    if (Test-Path "pyproject.toml") {
        poetry run black --check .
        poetry run flake8 .
    } else {
        Write-Host "No linting configuration found" -ForegroundColor Red
    }
}

function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Green
    if (Test-Path "pyproject.toml") {
        poetry install
    }
    if (Test-Path "frontend/package.json") {
        Set-Location frontend
        npm install
        Set-Location ..
    }
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "dev-up" { Start-DevEnvironment }
    "dev-down" { Stop-DevEnvironment }
    "dev-logs" { Show-DevLogs }
    "prod-up" { Start-ProdEnvironment }
    "prod-down" { Stop-ProdEnvironment }
    "prod-logs" { Show-ProdLogs }
    "build" { Build-All }
    "build-dev" { Build-Dev }
    "build-prod" { Build-Prod }
    "clean" { Clean-Docker }
    "test" { Run-Tests }
    "lint" { Run-Lint }
    "install" { Install-Dependencies }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use '.\build.ps1 help' to see available commands" -ForegroundColor Yellow
    }
}

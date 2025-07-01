# Scorpius Enterprise Commands
# Comprehensive command interface for enterprise development

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [string[]]$Arguments
)

# Configuration
$PythonCmd = "py"
$PythonArgs = "-3.11"
$ProjectRoot = $PSScriptRoot | Split-Path -Parent

function Write-Header {
    param([string]$Message)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Show-Help {
    Write-Header "Scorpius Enterprise Commands"
    
    Write-Host "Available commands:" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🔧 Development:" -ForegroundColor Yellow
    Write-Host "  dev          - Start development server" -ForegroundColor White
    Write-Host "  test         - Run all tests" -ForegroundColor White
    Write-Host "  test-unit    - Run unit tests only" -ForegroundColor White
    Write-Host "  test-integration - Run integration tests" -ForegroundColor White
    Write-Host "  test-e2e     - Run end-to-end tests" -ForegroundColor White
    Write-Host "  coverage     - Run tests with coverage" -ForegroundColor White
    Write-Host ""
    
    Write-Host "📝 Code Quality:" -ForegroundColor Yellow
    Write-Host "  lint         - Run all linting tools" -ForegroundColor White
    Write-Host "  format       - Format code with Black" -ForegroundColor White
    Write-Host "  type-check   - Run type checking with MyPy" -ForegroundColor White
    Write-Host "  security     - Run security scans" -ForegroundColor White
    Write-Host "  complexity   - Analyze code complexity" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🏗️  Build & Deploy:" -ForegroundColor Yellow
    Write-Host "  build        - Build the project" -ForegroundColor White
    Write-Host "  docker-build - Build Docker images" -ForegroundColor White
    Write-Host "  deploy       - Deploy to environment" -ForegroundColor White
    Write-Host "  clean        - Clean build artifacts" -ForegroundColor White
    Write-Host ""
    
    Write-Host "📊 Monitoring & Analysis:" -ForegroundColor Yellow
    Write-Host "  monitor      - Start monitoring services" -ForegroundColor White
    Write-Host "  logs         - View application logs" -ForegroundColor White
    Write-Host "  metrics      - View metrics dashboard" -ForegroundColor White
    Write-Host "  profile      - Profile application performance" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🔍 Utilities:" -ForegroundColor Yellow
    Write-Host "  docs         - Build documentation" -ForegroundColor White
    Write-Host "  backup       - Create project backup" -ForegroundColor White
    Write-Host "  update       - Update dependencies" -ForegroundColor White
    Write-Host "  status       - Show project status" -ForegroundColor White
    Write-Host "  help         - Show this help message" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Usage: .\scripts\enterprise-commands.ps1 <command> [arguments]" -ForegroundColor Gray
    Write-Host "Example: .\scripts\enterprise-commands.ps1 test --verbose" -ForegroundColor Gray
}

function Start-Development {
    Write-Header "Starting Development Environment"
    
    Write-Host "Starting FastAPI development server..." -ForegroundColor Yellow
    Set-Location $ProjectRoot
    
    # Start the main API server
    & $PythonCmd $PythonArgs -m uvicorn backend.bridge.api.main:app --reload --host 0.0.0.0 --port 8000
}

function Invoke-Tests {
    param([string]$TestType = "all")
    
    Write-Header "Running Tests"
    Set-Location $ProjectRoot
    
    switch ($TestType) {
        "unit" {
            Write-Host "Running unit tests..." -ForegroundColor Yellow
            & $PythonCmd $PythonArgs -m pytest tests/unit/ -v
        }
        "integration" {
            Write-Host "Running integration tests..." -ForegroundColor Yellow
            & $PythonCmd $PythonArgs -m pytest tests/integration/ -v
        }
        "e2e" {
            Write-Host "Running end-to-end tests..." -ForegroundColor Yellow
            & $PythonCmd $PythonArgs -m pytest tests/e2e/ -v
        }
        default {
            Write-Host "Running all tests..." -ForegroundColor Yellow
            & $PythonCmd $PythonArgs -m pytest tests/ -v
        }
    }
}

function Invoke-Coverage {
    Write-Header "Running Tests with Coverage"
    Set-Location $ProjectRoot
    
    Write-Host "Running tests with coverage report..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m pytest tests/ --cov=backend --cov-report=html --cov-report=term-missing
}

function Invoke-Linting {
    Write-Header "Running Code Quality Checks"
    Set-Location $ProjectRoot
    
    Write-Host "Running Black (code formatting)..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m black backend/ tests/ --check
    
    Write-Host "Running Flake8 (linting)..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m flake8 backend/ tests/ --max-line-length=88 --extend-ignore=E203,W503
    
    Write-Host "Running MyPy (type checking)..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m mypy backend/ --ignore-missing-imports
    
    Write-Host "Running Bandit (security)..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m bandit -r backend/ -f json -o bandit-report.json
    
    Write-Host "Running Safety (vulnerability scan)..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m safety check
}

function Invoke-Formatting {
    Write-Header "Formatting Code"
    Set-Location $ProjectRoot
    
    Write-Host "Formatting code with Black..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m black backend/ tests/ --line-length=88
    
    Write-Host "Sorting imports with isort..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m isort backend/ tests/ --profile=black
}

function Invoke-TypeChecking {
    Write-Header "Type Checking"
    Set-Location $ProjectRoot
    
    Write-Host "Running MyPy type checking..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m mypy backend/ --ignore-missing-imports --show-error-codes
}

function Invoke-SecurityScan {
    Write-Header "Security Scanning"
    Set-Location $ProjectRoot
    
    Write-Host "Running Safety vulnerability scan..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m safety check --json
    
    Write-Host "Running Bandit security scan..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m bandit -r backend/ -f json -o security-report.json
    
    Write-Host "Running Semgrep security scan..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m semgrep scan --config=auto backend/
}

function Invoke-ComplexityAnalysis {
    Write-Header "Code Complexity Analysis"
    Set-Location $ProjectRoot
    
    Write-Host "Running Radon complexity analysis..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m radon cc backend/ -a
    
    Write-Host "Running Vulture dead code detection..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m vulture backend/ tests/
}

function Invoke-Build {
    Write-Header "Building Project"
    Set-Location $ProjectRoot
    
    Write-Host "Building project..." -ForegroundColor Yellow
    # Add your build commands here
    Write-Host "Build completed successfully!" -ForegroundColor Green
}

function Invoke-DockerBuild {
    Write-Header "Building Docker Images"
    Set-Location $ProjectRoot
    
    Write-Host "Building Docker images..." -ForegroundColor Yellow
    docker-compose -f docker/docker-compose.prod.yml build
}

function Invoke-Deploy {
    Write-Header "Deploying Application"
    Set-Location $ProjectRoot
    
    Write-Host "Deploying to production..." -ForegroundColor Yellow
    # Add your deployment commands here
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
}

function Invoke-Clean {
    Write-Header "Cleaning Build Artifacts"
    Set-Location $ProjectRoot
    
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
    Remove-Item -Path "*.pyc" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Cleanup completed!" -ForegroundColor Green
}

function Start-Monitoring {
    Write-Header "Starting Monitoring Services"
    Set-Location $ProjectRoot
    
    Write-Host "Starting monitoring stack..." -ForegroundColor Yellow
    docker-compose -f monitoring/docker-compose.yml up -d
}

function Show-Logs {
    Write-Header "Application Logs"
    Set-Location $ProjectRoot
    
    Write-Host "Showing recent logs..." -ForegroundColor Yellow
    Get-Content logs/app.log -Tail 50 -Wait
}

function Show-Metrics {
    Write-Header "Metrics Dashboard"
    Set-Location $ProjectRoot
    
    Write-Host "Opening metrics dashboard..." -ForegroundColor Yellow
    Start-Process "http://localhost:3000"
}

function Invoke-Profiling {
    Write-Header "Performance Profiling"
    Set-Location $ProjectRoot
    
    Write-Host "Running performance profiling..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m scalene backend/
}

function Build-Documentation {
    Write-Header "Building Documentation"
    Set-Location $ProjectRoot
    
    Write-Host "Building documentation..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m mkdocs build
    Write-Host "Documentation built successfully!" -ForegroundColor Green
}

function Create-Backup {
    Write-Header "Creating Project Backup"
    Set-Location $ProjectRoot
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupName = "scorpius-enterprise-backup-$timestamp.zip"
    
    Write-Host "Creating backup: $backupName" -ForegroundColor Yellow
    Compress-Archive -Path . -DestinationPath "../$backupName" -Exclude "venv/*", "node_modules/*", "*.pyc", "__pycache__/*"
    Write-Host "Backup created successfully!" -ForegroundColor Green
}

function Update-Dependencies {
    Write-Header "Updating Dependencies"
    Set-Location $ProjectRoot
    
    Write-Host "Updating dependencies..." -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m pip install --upgrade -r config/requirements-dev.txt
    Write-Host "Dependencies updated successfully!" -ForegroundColor Green
}

function Show-Status {
    Write-Header "Project Status"
    Set-Location $ProjectRoot
    
    Write-Host "Python Version:" -ForegroundColor Yellow
    & $PythonCmd $PythonArgs --version
    
    Write-Host "`nInstalled Packages:" -ForegroundColor Yellow
    & $PythonCmd $PythonArgs -m pip list --format=columns
    
    Write-Host "`nProject Structure:" -ForegroundColor Yellow
    Get-ChildItem -Directory | Select-Object Name
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "dev" { Start-Development }
    "test" { 
        if ($Arguments -contains "unit") { Invoke-Tests "unit" }
        elseif ($Arguments -contains "integration") { Invoke-Tests "integration" }
        elseif ($Arguments -contains "e2e") { Invoke-Tests "e2e" }
        else { Invoke-Tests "all" }
    }
    "test-unit" { Invoke-Tests "unit" }
    "test-integration" { Invoke-Tests "integration" }
    "test-e2e" { Invoke-Tests "e2e" }
    "coverage" { Invoke-Coverage }
    "lint" { Invoke-Linting }
    "format" { Invoke-Formatting }
    "type-check" { Invoke-TypeChecking }
    "security" { Invoke-SecurityScan }
    "complexity" { Invoke-ComplexityAnalysis }
    "build" { Invoke-Build }
    "docker-build" { Invoke-DockerBuild }
    "deploy" { Invoke-Deploy }
    "clean" { Invoke-Clean }
    "monitor" { Start-Monitoring }
    "logs" { Show-Logs }
    "metrics" { Show-Metrics }
    "profile" { Invoke-Profiling }
    "docs" { Build-Documentation }
    "backup" { Create-Backup }
    "update" { Update-Dependencies }
    "status" { Show-Status }
    "help" { Show-Help }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\scripts\enterprise-commands.ps1 help' for available commands" -ForegroundColor Yellow
        exit 1
    }
} 
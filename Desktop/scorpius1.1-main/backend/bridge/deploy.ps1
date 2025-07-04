# Scorpius Bridge Deployment Script for Windows
# PowerShell script for building, testing, and deploying the Scorpius Bridge system

param(
    [string]$Command = "deploy",
    [string]$Environment = "development",
    [string]$Service = ""
)

# Configuration
$PROJECT_NAME = "scorpius-bridge"
$COMPOSE_FILE = "docker-compose.yml"

# Colors for output (using Write-Host)
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Title { param($Message) Write-Host $Message -ForegroundColor Blue }

Write-Title "🌉 Scorpius Bridge Deployment Script"
Write-Title "Environment: $Environment"
Write-Host ""

# Function to check if Docker is running
function Test-Docker {
    Write-Info "Checking Docker..."
    try {
        docker info | Out-Null
        Write-Info "Docker is running ✓"
        return $true
    }
    catch {
        Write-Error "Docker is not running. Please start Docker and try again."
        return $false
    }
}

# Function to check if Docker Compose is available
function Test-DockerCompose {
    Write-Info "Checking Docker Compose..."
    try {
        docker-compose --version | Out-Null
        Write-Info "Docker Compose is available ✓"
        return $true
    }
    catch {
        Write-Error "Docker Compose is not installed. Please install Docker Compose and try again."
        return $false
    }
}

# Function to setup directories
function Initialize-Directories {
    Write-Info "Setting up directories..."
    
    $directories = @(
        "logs",
        "monitoring\grafana\dashboards",
        "monitoring\grafana\datasources", 
        "secrets",
        "nginx",
        "postgres",
        "redis"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Info "Directories created ✓"
}

# Function to generate secrets for production
function New-Secrets {
    if ($Environment -eq "production") {
        Write-Info "Generating production secrets..."
        
        if (!(Test-Path "secrets\secret_key.txt")) {
            $secretKey = [System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
            $secretKey | Out-File -FilePath "secrets\secret_key.txt" -Encoding utf8
            Write-Info "Generated secret_key.txt"
        }
        
        if (!(Test-Path "secrets\jwt_secret.txt")) {
            $jwtSecret = [System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
            $jwtSecret | Out-File -FilePath "secrets\jwt_secret.txt" -Encoding utf8
            Write-Info "Generated jwt_secret.txt"
        }
        
        if (!(Test-Path "secrets\postgres_password.txt")) {
            $pgPassword = [System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(24))
            $pgPassword | Out-File -FilePath "secrets\postgres_password.txt" -Encoding utf8
            Write-Info "Generated postgres_password.txt"
        }
        
        if (!(Test-Path "secrets\grafana_password.txt")) {
            $grafanaPassword = [System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(16))
            $grafanaPassword | Out-File -FilePath "secrets\grafana_password.txt" -Encoding utf8
            Write-Info "Generated grafana_password.txt"
        }
        
        Write-Info "Secrets generated and secured ✓"
    }
}

# Function to create basic configurations
function New-Configs {
    Write-Info "Creating configuration files..."
    
    # Prometheus config
    if (!(Test-Path "monitoring\prometheus.yml")) {
        $prometheusConfig = @"
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'scorpius-bridge'
    static_configs:
      - targets: ['scorpius-bridge:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
"@
        $prometheusConfig | Out-File -FilePath "monitoring\prometheus.yml" -Encoding utf8
        Write-Info "Created prometheus.yml"
    }
    
    # Grafana datasource
    if (!(Test-Path "monitoring\grafana\datasources\prometheus.yml")) {
        $grafanaDatasource = @"
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
"@
        $grafanaDatasource | Out-File -FilePath "monitoring\grafana\datasources\prometheus.yml" -Encoding utf8
        Write-Info "Created Grafana datasource config"
    }
}

# Function to run tests
function Invoke-Tests {
    Write-Info "Running tests..."
    
    # Build test image
    docker build -t "${PROJECT_NAME}-test" --target test .
    
    # Run unit tests
    docker run --rm "${PROJECT_NAME}-test" pytest tests/unit/ -v --cov=scorpius_bridge --cov-report=term-missing
    
    Write-Info "Tests completed ✓"
}

# Function to build the application
function Build-App {
    Write-Info "Building Scorpius Bridge..."
    
    # Choose the right compose file
    if ($Environment -eq "production") {
        $script:COMPOSE_FILE = "docker-compose.prod.yml"
    }
    
    # Build the application
    docker-compose -f $COMPOSE_FILE build --no-cache
    Write-Info "Build completed ✓"
}

# Function to deploy the application
function Deploy-App {
    Write-Info "Deploying Scorpius Bridge..."
    
    # Stop existing containers
    docker-compose -f $COMPOSE_FILE down
    
    # Start the application
    docker-compose -f $COMPOSE_FILE up -d
    
    # Wait for health checks
    Write-Info "Waiting for services to be healthy..."
    Start-Sleep 30
    
    # Check if main service is running
    $status = docker-compose -f $COMPOSE_FILE ps scorpius-bridge
    if ($status -match "Up") {
        Write-Info "Scorpius Bridge is running ✓"
    }
    else {
        Write-Error "Scorpius Bridge failed to start"
        docker-compose -f $COMPOSE_FILE logs scorpius-bridge
        exit 1
    }
}

# Function to show status
function Show-Status {
    Write-Info "Service Status:"
    docker-compose -f $COMPOSE_FILE ps
    
    Write-Host ""
    Write-Info "Available Services:"
    Write-Host "  🌐 API: http://localhost:8000"
    Write-Host "  📊 Metrics: http://localhost:9090 (Prometheus)"
    Write-Host "  📈 Dashboards: http://localhost:3000 (Grafana)"
    
    if ($Environment -eq "development") {
        Write-Host "  🗄️  Database Admin: http://localhost:5050 (pgAdmin)"
        Write-Host "  🔧 WebSocket Test: http://localhost:8000/api/ws/test"
    }
    
    if ($Environment -eq "production") {
        Write-Host "  📋 Logs: http://localhost:5601 (Kibana)"
    }
}

# Function to show logs
function Show-Logs {
    $targetService = if ($Service) { $Service } else { "scorpius-bridge" }
    Write-Info "Showing logs for $targetService..."
    docker-compose -f $COMPOSE_FILE logs -f $targetService
}

# Function to cleanup
function Remove-All {
    Write-Info "Cleaning up..."
    docker-compose -f $COMPOSE_FILE down -v
    docker system prune -f
    Write-Info "Cleanup completed ✓"
}

# Main script logic
switch ($Command.ToLower()) {
    "check" {
        Test-Docker
        Test-DockerCompose
    }
    "setup" {
        if (!(Test-Docker) -or !(Test-DockerCompose)) { exit 1 }
        Initialize-Directories
        New-Secrets
        New-Configs
    }
    "test" {
        if (!(Test-Docker)) { exit 1 }
        Invoke-Tests
    }
    "build" {
        if (!(Test-Docker) -or !(Test-DockerCompose)) { exit 1 }
        Build-App
    }
    "deploy" {
        if (!(Test-Docker) -or !(Test-DockerCompose)) { exit 1 }
        Initialize-Directories
        New-Secrets
        New-Configs
        Build-App
        Deploy-App
        Show-Status
    }
    "redeploy" {
        Deploy-App
        Show-Status
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs
    }
    "stop" {
        docker-compose -f $COMPOSE_FILE down
    }
    "restart" {
        docker-compose -f $COMPOSE_FILE restart
    }
    "cleanup" {
        Remove-All
    }
    "help" {
        Write-Host "Scorpius Bridge Deployment Script"
        Write-Host ""
        Write-Host "Usage: .\deploy.ps1 [command] [-Environment <env>] [-Service <service>]"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  deploy    - Full deployment (default)"
        Write-Host "  redeploy  - Redeploy without rebuilding"
        Write-Host "  build     - Build only"
        Write-Host "  test      - Run tests"
        Write-Host "  setup     - Setup directories and configs"
        Write-Host "  status    - Show service status"
        Write-Host "  logs      - Show logs [service_name]"
        Write-Host "  stop      - Stop all services"
        Write-Host "  restart   - Restart all services"
        Write-Host "  cleanup   - Clean up containers and volumes"
        Write-Host "  check     - Check prerequisites"
        Write-Host "  help      - Show this help"
        Write-Host ""
        Write-Host "Parameters:"
        Write-Host "  -Environment   - deployment environment (development|production)"
        Write-Host "  -Service       - specific service name for logs command"
        Write-Host ""
        Write-Host "Examples:"
        Write-Host "  .\deploy.ps1 deploy -Environment production"
        Write-Host "  .\deploy.ps1 logs -Service redis"
        Write-Host "  .\deploy.ps1 status"
    }
    default {
        Write-Error "Unknown command: $Command"
        Write-Host "Use '.\deploy.ps1 help' for usage information"
        exit 1
    }
}

# Scorpius Vulnerability Scanner Setup Script for Windows
# Enterprise-grade deployment with Docker and simulation capabilities

param(
    [switch]$SkipDocker,
    [switch]$Monitoring,
    [switch]$Storage,
    [switch]$Development
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

# Configuration
$SCORPIUS_VERSION = "1.0.0"
$PYTHON_VERSION = "3.11"

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Write-Header {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Blue
}

Write-Header "🦂 Scorpius Vulnerability Scanner Enterprise Setup"
Write-Header "Version: $SCORPIUS_VERSION"
Write-Header "=================================================="

# Check if running as Administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Warning "This script should be run as Administrator for best results"
    Write-Warning "Some features may not work without elevated privileges"
}

# Check system requirements
function Test-SystemRequirements {
    Write-Status "Checking system requirements..."
    
    # Check Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    if ($osVersion.Major -lt 10) {
        Write-Error "Windows 10 or later is required"
        exit 1
    }
    
    # Check available memory (minimum 8GB recommended)
    $memory = (Get-CimInstance -ClassName Win32_ComputerSystem).TotalPhysicalMemory / 1GB
    if ($memory -lt 8) {
        Write-Warning "System has $([math]::Round($memory, 1))GB RAM. Minimum 8GB recommended for optimal performance"
    }
    
    # Check disk space (minimum 20GB recommended)
    $diskSpace = (Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB
    if ($diskSpace -lt 20) {
        Write-Warning "Available disk space: $([math]::Round($diskSpace, 1))GB. Minimum 20GB recommended"
    }
    
    Write-Status "System requirements check completed"
}

# Install Chocolatey if not present
function Install-Chocolatey {
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Status "Installing Chocolatey package manager..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        refreshenv
    } else {
        Write-Status "Chocolatey is already installed"
    }
}

# Install Docker Desktop if not present
function Install-Docker {
    if (-not $SkipDocker) {
        if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
            Write-Status "Installing Docker Desktop..."
            choco install docker-desktop -y
            Write-Warning "Please restart your computer after Docker Desktop installation completes"
            Write-Warning "Then run this script again to continue setup"
        } else {
            Write-Status "Docker is already installed"
            docker --version
        }
    }
}

# Install Python if not present
function Install-Python {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Status "Installing Python $PYTHON_VERSION..."
        choco install python --version=$PYTHON_VERSION -y
        refreshenv
    } else {
        Write-Status "Python is already installed"
        python --version
    }
}

# Install Git if not present
function Install-Git {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Status "Installing Git..."
        choco install git -y
        refreshenv
    } else {
        Write-Status "Git is already installed"
    }
}

# Setup Python virtual environment
function Setup-PythonEnvironment {
    Write-Status "Setting up Python virtual environment..."
    
    if (-not (Test-Path "venv")) {
        python -m venv venv
    }
    
    & ".\venv\Scripts\Activate.ps1"
    pip install --upgrade pip
    
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
    }
    
    Write-Status "Python environment setup completed"
}

# Create necessary directories
function New-DirectoryStructure {
    Write-Status "Creating necessary directories..."
    
    $directories = @(
        "contracts",
        "reports", 
        "logs",
        "simulation_results",
        "config",
        "exploits"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Status "Directory structure created"
}

# Generate configuration files
function New-ConfigurationFiles {
    Write-Status "Generating configuration files..."
    
    # Create .env file
    if (-not (Test-Path ".env")) {
        $envContent = @"
# Scorpius Configuration
SCORPIUS_ENV=development
SCORPIUS_API_KEY=scorpius-api-token-change-me
SCORPIUS_SECRET_KEY=change-me-to-a-secure-secret-key

# Database
DATABASE_URL=postgresql://scorpius:scorpius_secure_pass@localhost:5432/scorpius

# Redis
REDIS_URL=redis://:scorpius_redis_pass@localhost:6379/0

# Docker
COMPOSE_PROJECT_NAME=scorpius

# External Services
MYTHX_API_KEY=your-mythx-api-key-here
MAINNET_FORK_URL=https://mainnet.infura.io/v3/your-infura-key

# Monitoring
ENABLE_MONITORING=false
GRAFANA_ADMIN_PASSWORD=admin
PROMETHEUS_RETENTION=15d

# Storage
ENABLE_IPFS=false
ENABLE_MINIO=false
MINIO_ROOT_USER=scorpius
MINIO_ROOT_PASSWORD=scorpius_minio_pass
"@
        Set-Content -Path ".env" -Value $envContent
        Write-Status "Created .env configuration file"
        Write-Warning "Please update the .env file with your specific configuration"
    }
    
    # Create logging configuration
    if (-not (Test-Path "config\logging.yaml")) {
        New-Item -ItemType Directory -Path "config" -Force | Out-Null
        $loggingContent = @"
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  detailed:
    format: '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout
  
  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/scorpius.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  scorpius:
    level: DEBUG
    handlers: [console, file]
    propagate: false

root:
  level: INFO
  handlers: [console]
"@
        Set-Content -Path "config\logging.yaml" -Value $loggingContent
        Write-Status "Created logging configuration"
    }
}

# Build Docker images
function Build-DockerImages {
    Write-Status "Building Docker images..."
    
    try {
        # Check if Docker is running
        docker version | Out-Null
        
        # Build plugin images
        docker-compose build slither mythril manticore mythx ethereum-sim
        
        # Build main application
        docker-compose build scorpius-main
        
        Write-Status "Docker images built successfully"
    }
    catch {
        Write-Error "Docker is not running or not installed properly"
        Write-Error "Please ensure Docker Desktop is installed and running"
        exit 1
    }
}

# Initialize database
function Initialize-Database {
    Write-Status "Initializing database..."
    
    # Start database services
    docker-compose up -d postgres redis
    
    # Wait for database to be ready
    Start-Sleep -Seconds 10
    
    Write-Status "Database initialized"
}

# Setup monitoring (optional)
function Setup-Monitoring {
    if ($Monitoring) {
        Write-Status "Setting up monitoring stack..."
        
        # Update .env file
        (Get-Content ".env") -replace "ENABLE_MONITORING=false", "ENABLE_MONITORING=true" | Set-Content ".env"
        
        # Start monitoring services
        docker-compose --profile monitoring up -d
        
        Write-Status "Monitoring stack started"
        Write-Status "Grafana: http://localhost:3000 (admin/admin)"
        Write-Status "Kibana: http://localhost:5601"
        Write-Status "Prometheus: http://localhost:9090"
    }
}

# Setup storage (optional)
function Setup-Storage {
    if ($Storage) {
        Write-Status "Setting up storage services..."
        
        # Update .env file
        (Get-Content ".env") -replace "ENABLE_IPFS=false", "ENABLE_IPFS=true" | Set-Content ".env"
        (Get-Content ".env") -replace "ENABLE_MINIO=false", "ENABLE_MINIO=true" | Set-Content ".env"
        
        # Start storage services
        docker-compose --profile storage up -d
        
        Write-Status "Storage services started"
        Write-Status "MinIO Console: http://localhost:9001"
        Write-Status "IPFS Gateway: http://localhost:8081"
    }
}

# Start core services
function Start-CoreServices {
    Write-Status "Starting core Scorpius services..."
    
    # Start core services
    docker-compose up -d scorpius-main postgres redis
    
    # Wait for services to be ready
    Start-Sleep -Seconds 15
    
    # Health check
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Status "✅ Scorpius API is running at http://localhost:8080"
            Write-Status "✅ API Documentation: http://localhost:8080/docs"
        }
    }
    catch {
        Write-Error "❌ Failed to start Scorpius API"
        Write-Error "Check logs with: docker-compose logs scorpius-main"
    }
}

# Apply security hardening
function Set-SecurityHardening {
    Write-Status "Applying security hardening..."
    
    # Set proper file permissions
    if (Test-Path ".env") {
        icacls ".env" /inheritance:d /grant:r "$env:USERNAME:(R)" | Out-Null
    }
    
    # Create security configuration
    $securityContent = @"
# Security Configuration
api:
  rate_limiting:
    enabled: true
    requests_per_minute: 100
  
  authentication:
    token_expiry: 3600
    require_https: false  # Set to true in production
  
sandbox:
  network_isolation: true
  resource_limits:
    memory: "4g"
    cpu: "2"
  
docker:
  security_options:
    - "no-new-privileges:true"
"@
    Set-Content -Path "config\security.yaml" -Value $securityContent
    
    Write-Status "Security hardening completed"
}

# Print final instructions
function Show-Instructions {
    Write-Host ""
    Write-Header "🎉 Scorpius Vulnerability Scanner Enterprise Setup Complete!"
    Write-Header "=============================================================="
    Write-Host ""
    Write-Header "Quick Start:"
    Write-Host "1. Update configuration: notepad .env"
    Write-Host "2. Start all services: docker-compose up -d"
    Write-Host "3. Access API docs: http://localhost:8080/docs"
    Write-Host ""
    Write-Header "Available Services:"
    Write-Host "• API Server: http://localhost:8080"
    Write-Host "• PostgreSQL: localhost:5432"
    Write-Host "• Redis: localhost:6379"
    Write-Host ""
    Write-Header "Plugin Management:"
    Write-Host "• Initialize plugins: docker-compose --profile plugins up -d"
    Write-Host "• Simulation environment: docker-compose --profile simulation up -d"
    Write-Host ""
    Write-Header "Useful Commands:"
    Write-Host "• View logs: docker-compose logs -f"
    Write-Host "• Stop services: docker-compose down"
    Write-Host "• Update images: docker-compose pull && docker-compose up -d"
    Write-Host ""
    Write-Header "Next Steps:"
    Write-Host "1. Configure your API keys in .env file"
    Write-Host "2. Read the documentation in docs/"
    Write-Host "3. Run your first scan!"
    Write-Host ""
    Write-Warning "Remember to change default passwords in production!"
}

# Main execution
function Main {
    Test-SystemRequirements
    Install-Chocolatey
    Install-Docker
    Install-Python
    Install-Git
    Setup-PythonEnvironment
    New-DirectoryStructure
    New-ConfigurationFiles
    
    if (-not $SkipDocker) {
        Build-DockerImages
        Initialize-Database
    }
    
    Set-SecurityHardening
    
    # Optional components
    Setup-Monitoring
    Setup-Storage
    
    if (-not $SkipDocker) {
        Start-CoreServices
    }
    
    Show-Instructions
}

# Run main function
try {
    Main
}
catch {
    Write-Error "Setup failed: $($_.Exception.Message)"
    Write-Error "Please check the error message above and try again"
    exit 1
}

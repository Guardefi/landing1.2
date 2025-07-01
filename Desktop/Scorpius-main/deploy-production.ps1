#!/usr/bin/env powershell
<#
.SYNOPSIS
    Production deployment script for Scorpius Enterprise Platform
.DESCRIPTION
    Securely deploys Scorpius platform with production-grade security configurations
.PARAMETER Environment
    Target environment (production, staging)
.PARAMETER SkipSecurityCheck
    Skip security validation checks
.PARAMETER GenerateSecrets
    Generate new production secrets
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("production", "staging")]
    [string]$Environment,
    
    [switch]$SkipSecurityCheck = $false,
    [switch]$GenerateSecrets = $false,
    [switch]$BackupData = $true
)

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Color output functions
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Blue }

# Pre-deployment checks
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Success "Docker found: $dockerVersion"
    } catch {
        Write-Error "Docker not found. Please install Docker Desktop."
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Success "Docker Compose found: $composeVersion"
    } catch {
        Write-Error "Docker Compose not found. Please install Docker Compose."
        exit 1
    }
    
    # Check if running as administrator (for production)
    if ($Environment -eq "production") {
        $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
        if (-not $isAdmin) {
            Write-Error "Production deployment requires administrator privileges."
            exit 1
        }
    }
}

# Generate secure production secrets
function New-ProductionSecrets {
    if (-not $GenerateSecrets) {
        Write-Info "Skipping secret generation. Use -GenerateSecrets to create new secrets."
        return
    }
    
    Write-Info "Generating production secrets..."
    
    # Create secrets directory
    $secretsDir = "secrets"
    if (-not (Test-Path $secretsDir)) {
        New-Item -ItemType Directory -Path $secretsDir | Out-Null
    }
    
    # Generate strong random passwords
    function New-SecurePassword {
        param([int]$Length = 32)
        $bytes = New-Object byte[] $Length
        [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
        return [Convert]::ToBase64String($bytes).Substring(0, $Length)
    }
    
    # Generate secrets
    $secrets = @{
        "DB_PASSWORD" = New-SecurePassword -Length 32
        "REDIS_PASSWORD" = New-SecurePassword -Length 32
        "JWT_SECRET" = New-SecurePassword -Length 64
        "GRAFANA_PASSWORD" = New-SecurePassword -Length 16
        "PGADMIN_PASSWORD" = New-SecurePassword -Length 16
    }
    
    # Create .env file
    $envContent = @"
# Scorpius Enterprise Production Environment
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# Database Configuration
DB_PASSWORD=$($secrets.DB_PASSWORD)

# Redis Configuration
REDIS_PASSWORD=$($secrets.REDIS_PASSWORD)

# JWT Configuration
JWT_SECRET=$($secrets.JWT_SECRET)

# Admin Passwords
GRAFANA_PASSWORD=$($secrets.GRAFANA_PASSWORD)
PGADMIN_PASSWORD=$($secrets.PGADMIN_PASSWORD)

# Environment
ENVIRONMENT=$Environment
LOG_LEVEL=INFO

# Security
CORS_ORIGINS=https://yourdomain.com
RATE_LIMITING_ENABLED=true
SECURITY_HEADERS_ENABLED=true
"@
    
    $envContent | Out-File -FilePath ".env.production" -Encoding UTF8
    
    # Set secure permissions
    $acl = Get-Acl ".env.production"
    $acl.SetAccessRuleProtection($true, $false)
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
    $acl.SetAccessRule($rule)
    Set-Acl ".env.production" $acl
    
    Write-Success "Production secrets generated and saved to .env.production"
    Write-Warning "Keep these secrets secure and backed up!"
}

# Security validation
function Test-SecurityConfiguration {
    if ($SkipSecurityCheck) {
        Write-Warning "Skipping security checks (not recommended for production)"
        return
    }
    
    Write-Info "Validating security configuration..."
    
    $issues = @()
    
    # Check if .env file exists
    if (-not (Test-Path ".env.production")) {
        $issues += "Missing .env.production file"
    } else {
        # Check for default passwords
        $envContent = Get-Content ".env.production" -Raw
        
        if ($envContent -match "CHANGE_THIS" -or $envContent -match "scorpius123" -or $envContent -match "admin") {
            $issues += "Default passwords detected in .env.production"
        }
        
        # Check secret lengths
        $envVars = Get-Content ".env.production" | Where-Object { $_ -match "^[^#].*=" }
        foreach ($line in $envVars) {
            $key, $value = $line -split "=", 2
            if ($key -like "*PASSWORD*" -or $key -like "*SECRET*") {
                if ($value.Length -lt 16) {
                    $issues += "Secret '$key' is too short (minimum 16 characters)"
                }
            }
        }
    }
    
    # Check Docker security
    if (-not (docker info --format '{{.SecurityOptions}}' | Select-String "name=seccomp")) {
        $issues += "Docker seccomp security profile not enabled"
    }
    
    if ($issues.Count -gt 0) {
        Write-Error "Security validation failed:"
        foreach ($issue in $issues) {
            Write-Error "  - $issue"
        }
        exit 1
    }
    
    Write-Success "Security validation passed"
}

# Backup existing data
function Backup-ExistingData {
    if (-not $BackupData) {
        return
    }
    
    Write-Info "Creating backup of existing data..."
    
    $backupDir = "backups/$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Backup volumes if they exist
    $volumes = @("scorpius_postgres_data_enterprise", "scorpius_redis_data_enterprise")
    
    foreach ($volume in $volumes) {
        try {
            docker run --rm -v "${volume}:/source:ro" -v "${PWD}/${backupDir}:/backup" alpine tar czf "/backup/${volume}.tar.gz" -C /source .
            Write-Success "Backed up volume: $volume"
        } catch {
            Write-Warning "Could not backup volume: $volume (may not exist)"
        }
    }
    
    Write-Success "Backup completed in $backupDir"
}

# Deploy services
function Start-Production {
    Write-Info "Starting production deployment..."
    
    # Pull latest images
    Write-Info "Pulling latest images..."
    docker-compose -f docker-compose.enterprise.yml pull
    
    # Build custom images
    Write-Info "Building custom images..."
    docker-compose -f docker-compose.enterprise.yml build --no-cache
    
    # Start services with security overlay
    Write-Info "Starting services with security hardening..."
    docker-compose -f docker-compose.enterprise.yml -f docker-compose.security.yml --env-file .env.production up -d
    
    # Wait for services to start
    Write-Info "Waiting for services to initialize..."
    Start-Sleep -Seconds 30
    
    # Health check
    Test-ServiceHealth
}

# Health check function
function Test-ServiceHealth {
    Write-Info "Performing health checks..."
    
    $services = @(
        @{Name="API Gateway"; URL="http://localhost:8000/health"; Timeout=30}
        @{Name="Frontend"; URL="http://localhost:3000"; Timeout=30}
        @{Name="Prometheus"; URL="http://localhost:9090/-/healthy"; Timeout=15}
        @{Name="Grafana"; URL="http://localhost:3001/api/health"; Timeout=15}
    )
    
    $failed = @()
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec $service.Timeout -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "$($service.Name) is healthy"
            } else {
                $failed += $service.Name
                Write-Error "$($service.Name) returned status $($response.StatusCode)"
            }
        } catch {
            $failed += $service.Name
            Write-Error "$($service.Name) health check failed: $($_.Exception.Message)"
        }
    }
    
    if ($failed.Count -eq 0) {
        Write-Success "All services are healthy!"
    } else {
        Write-Error "Health check failed for: $($failed -join ', ')"
        Write-Info "Check service logs with: docker-compose logs [service-name]"
    }
}

# Main deployment flow
function Start-Deployment {
    Write-Info "🚀 Starting Scorpius Enterprise Platform deployment..."
    Write-Info "Environment: $Environment"
    
    try {
        Test-Prerequisites
        New-ProductionSecrets
        Test-SecurityConfiguration
        Backup-ExistingData
        Start-Production
        
        Write-Success "🎉 Deployment completed successfully!"
        Write-Info "Access points:"
        Write-Info "  - Frontend: http://localhost:3000"
        Write-Info "  - API Gateway: http://localhost:8000"
        Write-Info "  - Monitoring: http://localhost:3001"
        Write-Info "  - Documentation: See docs/ directory"
        
    } catch {
        Write-Error "Deployment failed: $($_.Exception.Message)"
        Write-Info "Rolling back changes..."
        docker-compose -f docker-compose.enterprise.yml -f docker-compose.security.yml down
        exit 1
    }
}

# Run deployment
Start-Deployment

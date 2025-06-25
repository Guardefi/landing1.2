#!/usr/bin/env pwsh
# Enhanced Enterprise Deployment Script for Scorpius Vulnerability Scanner
# Builds and deploys all components including plugin APIs and marketplace

param(
    [switch]$Clean = $false,
    [switch]$BuildOnly = $false,
    [switch]$SkipTests = $false,
    [string]$ComposeProfile = "plugins",
    [switch]$Verbose = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Configuration
$PROJECT_NAME = "scorpius-enterprise"

# Colors for output
$RED = "`e[31m"
$GREEN = "`e[32m"
$YELLOW = "`e[33m"
$BLUE = "`e[34m"
$MAGENTA = "`e[35m"
$CYAN = "`e[36m"
$WHITE = "`e[37m"
$RESET = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $WHITE)
    Write-Host "${Color}${Message}${RESET}"
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "🚀 $Message" $CYAN
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" $GREEN
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" $YELLOW
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" $RED
}

function Test-DockerInstallation {
    Write-Step "Checking Docker installation..."
    
    try {
        $dockerVersion = docker --version
        Write-Success "Docker found: $dockerVersion"
        
        $composeVersion = docker-compose --version
        Write-Success "Docker Compose found: $composeVersion"
        
        # Test Docker daemon
        docker ps | Out-Null
        Write-Success "Docker daemon is running"
        
        return $true
    } catch {
        Write-Error "Docker is not properly installed or running"
        Write-Host "Please install Docker Desktop and ensure it's running"
        return $false
    }
}

function Stop-ExistingServices {
    Write-Step "Stopping existing Scorpius services..."
    
    try {
        # Stop all profiles
        docker-compose -p $PROJECT_NAME --profile plugins --profile simulation --profile monitoring down --remove-orphans
        Write-Success "Stopped existing services"
    } catch {
        Write-Warning "No existing services to stop"
    }
}

function Remove-ExistingImages {
    Write-Step "Removing existing Scorpius images..."
    
    try {
        # Remove Scorpius images
        $images = docker images --filter "reference=scorpius/*" --format "{{.Repository}}:{{.Tag}}"
        if ($images) {
            $images | ForEach-Object {
                Write-Host "Removing image: $_"
                docker rmi $_ -f
            }
            Write-Success "Removed existing images"
        } else {
            Write-Host "No existing Scorpius images found"
        }
    } catch {
        Write-Warning "Error removing some images: $_"
    }
}

function Build-PluginImages {
    Write-Step "Building plugin container images..."
    
    $plugins = @(
        @{Name="slither"; Path="docker/slither"; Port=8081},
        @{Name="mythril"; Path="docker/mythril"; Port=8082},
        @{Name="manticore"; Path="docker/manticore"; Port=8083},
        @{Name="mythx"; Path="docker/mythx"; Port=8084}
    )
    
    foreach ($plugin in $plugins) {
        Write-Host "${BLUE}Building $($plugin.Name) plugin...${RESET}"
        
        try {
            docker build -t "scorpius/$($plugin.Name):latest" $plugin.Path
            Write-Success "Built $($plugin.Name) plugin"
        } catch {
            Write-Error "Failed to build $($plugin.Name) plugin: $_"
            throw
        }
    }
    
    Write-Success "All plugin images built successfully"
}

function Build-MainApplication {
    Write-Step "Building main Scorpius application..."
    
    try {
        docker build -t "scorpius/enterprise:latest" -f docker/scorpius/Dockerfile .
        Write-Success "Built main application"
    } catch {
        Write-Error "Failed to build main application: $_"
        throw
    }
}

function Test-PluginAPIs {
    if ($SkipTests) {
        Write-Warning "Skipping API tests"
        return
    }
    
    Write-Step "Testing plugin API endpoints..."
    
    $plugins = @(
        @{Name="slither"; Port=8081},
        @{Name="mythril"; Port=8082},
        @{Name="manticore"; Port=8083},
        @{Name="mythx"; Port=8084}
    )
    
    # Wait for services to start
    Write-Host "Waiting for services to start..."
    Start-Sleep -Seconds 30
    
    foreach ($plugin in $plugins) {
        Write-Host "Testing $($plugin.Name) API..."
        
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:$($plugin.Port)/health" -Method GET -TimeoutSec 10
            if ($response.status -eq "healthy" -and $response.plugin -eq $plugin.Name) {
                Write-Success "$($plugin.Name) API is healthy"
            } else {
                Write-Warning "$($plugin.Name) API returned unexpected response"
            }
        } catch {
            Write-Warning "$($plugin.Name) API not responding: $_"
        }
    }
}

function Test-MainAPI {
    if ($SkipTests) {
        Write-Warning "Skipping main API tests"
        return
    }
    
    Write-Step "Testing main Scorpius API..."
    
    try {
        # Wait for main service
        Start-Sleep -Seconds 10
        
        # Test main API endpoints
        $endpoints = @(
            "http://localhost:8080/docs",
            "http://localhost:8080/api/v1/plugins",
            "http://localhost:8080/api/v1/marketplace/plugins",
            "http://localhost:8080/api/v1/results"
        )
        
        foreach ($endpoint in $endpoints) {
            try {
                $response = Invoke-WebRequest -Uri $endpoint -Method GET -TimeoutSec 10
                if ($response.StatusCode -eq 200) {
                    Write-Success "✓ $endpoint"
                } else {
                    Write-Warning "✗ $endpoint (Status: $($response.StatusCode))"
                }
            } catch {
                Write-Warning "✗ $endpoint (Error: $_)"
            }
        }
    } catch {
        Write-Warning "Main API testing failed: $_"
    }
}

function Show-ServiceStatus {
    Write-Step "Checking service status..."
    
    try {
        docker-compose -p $PROJECT_NAME ps
        Write-Host ""
        Write-ColorOutput "📊 Service URLs:" $MAGENTA
        Write-Host "Main API: http://localhost:8080"
        Write-Host "API Documentation: http://localhost:8080/docs"
        Write-Host "Slither Plugin API: http://localhost:8081"
        Write-Host "Mythril Plugin API: http://localhost:8082"
        Write-Host "Manticore Plugin API: http://localhost:8083"
        Write-Host "MythX Plugin API: http://localhost:8084"
        Write-Host "PostgreSQL: localhost:5432"
        Write-Host "Redis: localhost:6379"
        Write-Host ""
    } catch {
        Write-Error "Failed to get service status: $_"
    }
}

function Show-LogsCommand {
    Write-ColorOutput "📋 Useful Commands:" $MAGENTA
    Write-Host "View logs: docker-compose -p $PROJECT_NAME logs -f"
    Write-Host "Stop services: docker-compose -p $PROJECT_NAME down"
    Write-Host "Restart service: docker-compose -p $PROJECT_NAME restart <service>"
    Write-Host "Shell into container: docker exec -it <container_name> /bin/bash"
    Write-Host ""
}

function Main {
    Write-ColorOutput @"
🔍 Scorpius Enterprise Vulnerability Scanner
   Enhanced Deployment with Plugin APIs & Marketplace
   ================================================
"@ $CYAN
    
    # Validate Docker installation
    if (-not (Test-DockerInstallation)) {
        exit 1
    }
    
    try {
        # Clean up if requested
        if ($Clean) {
            Stop-ExistingServices
            Remove-ExistingImages
        }
        
        # Build images
        Build-PluginImages
        Build-MainApplication
        
        if ($BuildOnly) {
            Write-Success "Build completed successfully!"
            return
        }
        
        # Deploy services
        Write-Step "Deploying Scorpius Enterprise stack..."
        
        $composeArgs = @(
            "-p", $PROJECT_NAME,
            "--profile", $ComposeProfile,
            "up", "-d"
        )
        
        if ($Verbose) {
            $composeArgs += "--verbose"
        }
        
        & docker-compose @composeArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Deployment completed successfully!"
            
            # Test APIs
            Test-PluginAPIs
            Test-MainAPI
            
            # Show status
            Show-ServiceStatus
            Show-LogsCommand
            
            Write-ColorOutput @"

🎉 Scorpius Enterprise is now running!

Key Features Available:
• 🔌 Plugin API endpoints for all scanners
• 🏪 Enhanced plugin marketplace with reviews & ratings  
• 📊 Comprehensive results and simulation APIs
• 🐳 Fully containerized and orchestrated
• 📈 Real-time monitoring and logging
• 🔒 Enterprise-grade security scanning

Access the API documentation at: http://localhost:8080/docs
"@ $GREEN
            
        } else {
            Write-Error "Deployment failed!"
            exit 1
        }
        
    } catch {
        Write-Error "Deployment failed with error: $_"
        Write-Host "Check the logs with: docker-compose -p $PROJECT_NAME logs"
        exit 1
    }
}

# Run main function
Main

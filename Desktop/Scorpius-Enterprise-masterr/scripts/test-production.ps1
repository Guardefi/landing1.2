# Scorpius Enterprise Production Test & Deployment Script
# This script tests the complete production deployment

param(
    [switch]$Build,
    [switch]$Clean,
    [switch]$SkipBuild,
    [int]$Timeout = 300
)

# Configuration
$ProjectName = "scorpius-enterprise-production"
$ComposeFile = "docker-compose.production.yml"
$EnvFile = ".env.production"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }
function Write-Info { Write-ColorOutput Cyan $args }

Write-Info "🧪 Scorpius Enterprise Production Testing"
Write-Info "=========================================="

# Pre-flight checks
function Test-Prerequisites {
    Write-Info "📋 Running pre-flight checks..."
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Success "✓ Docker: $dockerVersion"
    }
    catch {
        Write-Error "❌ Docker not found. Please install Docker."
        exit 1
    }
    
    # Check Docker Compose
    try {
        docker compose version | Out-Null
        Write-Success "✓ Docker Compose is available"
    }
    catch {
        Write-Error "❌ Docker Compose not found."
        exit 1
    }
    
    # Check required files
    $requiredFiles = @(
        "Dockerfile.production",
        "docker-compose.production.yml",
        ".env.production",
        "frontend/package.json",
        "config/requirements-production.txt"
    )
    
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Success "✓ Found: $file"
        }
        else {
            Write-Error "❌ Missing required file: $file"
            exit 1
        }
    }
}

# Clean up function
function Invoke-Cleanup {
    Write-Info "🧹 Cleaning up existing containers..."
    
    try {
        # Stop and remove containers
        docker compose -f $ComposeFile -p $ProjectName down --volumes --remove-orphans 2>$null
        
        # Remove images if requested
        if ($Clean) {
            Write-Info "🗑️ Removing production images..."
            docker images | Select-String $ProjectName | ForEach-Object {
                $imageId = ($_ -split '\s+')[2]
                docker rmi $imageId -f 2>$null
            }
        }
        
        # Prune unused resources
        docker system prune -f --volumes 2>$null
        
        Write-Success "✓ Cleanup completed"
    }
    catch {
        Write-Warning "⚠️ Some cleanup operations failed, continuing..."
    }
}

# Build function
function Invoke-Build {
    Write-Info "🏗️ Building production images..."
    
    try {
        # Build with no cache for fresh build
        docker compose -f $ComposeFile -p $ProjectName build --no-cache --parallel
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✓ Build completed successfully"
        }
        else {
            Write-Error "❌ Build failed with exit code: $LASTEXITCODE"
            exit $LASTEXITCODE
        }
    }
    catch {
        Write-Error "❌ Build process encountered an error: $_"
        exit 1
    }
}

# Deploy function
function Invoke-Deploy {
    Write-Info "🚀 Starting production deployment..."
    
    try {
        # Start services in detached mode
        docker compose -f $ComposeFile -p $ProjectName up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✓ Services started successfully"
        }
        else {
            Write-Error "❌ Deployment failed with exit code: $LASTEXITCODE"
            return $false
        }
        
        return $true
    }
    catch {
        Write-Error "❌ Deployment encountered an error: $_"
        return $false
    }
}

# Health check function
function Test-Health {
    Write-Info "🔍 Running health checks..."
    
    $services = @(
        @{Name="Redis"; Port=6379; Service="redis"},
        @{Name="PostgreSQL"; Port=5432; Service="postgres"},
        @{Name="API Gateway"; Port=8000; Service="api-gateway"},
        @{Name="Frontend"; Port=3000; Service="frontend"},
        @{Name="Nginx"; Port=80; Service="nginx"}
    )
    
    $healthyServices = 0
    $maxWait = $Timeout
    $waited = 0
    
    Write-Info "⏳ Waiting for services to become healthy (timeout: ${maxWait}s)..."
    
    while ($waited -lt $maxWait) {
        $healthyServices = 0
        
        foreach ($service in $services) {
            try {
                $containerStatus = docker compose -f $ComposeFile -p $ProjectName ps --format json | 
                    ConvertFrom-Json | 
                    Where-Object { $_.Service -eq $service.Service } |
                    Select-Object -First 1
                
                if ($containerStatus -and $containerStatus.State -eq "running") {
                    Write-Success "✓ $($service.Name) is running"
                    $healthyServices++
                }
                else {
                    Write-Warning "⏳ $($service.Name) is starting..."
                }
            }
            catch {
                Write-Warning "⏳ $($service.Name) is not ready yet..."
            }
        }
        
        if ($healthyServices -eq $services.Count) {
            Write-Success "🎉 All services are healthy!"
            return $true
        }
        
        Start-Sleep -Seconds 10
        $waited += 10
    }
    
    Write-Error "❌ Health check timeout after ${maxWait}s. $healthyServices/$($services.Count) services healthy."
    return $false
}

# Show status function
function Show-Status {
    Write-Info "📊 Service Status:"
    Write-Info "=================="
    
    try {
        docker compose -f $ComposeFile -p $ProjectName ps
        
        Write-Info ""
        Write-Info "📈 Resource Usage:"
        Write-Info "=================="
        docker compose -f $ComposeFile -p $ProjectName top
        
        Write-Info ""
        Write-Info "🔗 Service URLs:"
        Write-Info "==============="
        Write-Info "Frontend: http://localhost:3000"
        Write-Info "API Gateway: http://localhost:8000"
        Write-Info "API Docs: http://localhost:8000/docs"
        Write-Info "Admin Panel: http://localhost:80"
    }
    catch {
        Write-Error "❌ Failed to get status information"
    }
}

# Main execution
try {
    Test-Prerequisites
    
    if ($Clean -or $Build) {
        Invoke-Cleanup
    }
    
    if (-not $SkipBuild) {
        Invoke-Build
    }
    
    $deploySuccess = Invoke-Deploy
    
    if ($deploySuccess) {
        $healthCheck = Test-Health
        
        if ($healthCheck) {
            Show-Status
            Write-Success "🎉 Production deployment completed successfully!"
            Write-Info "🌐 Access your application at: http://localhost"
        }
        else {
            Write-Error "❌ Health checks failed. Check logs with: docker compose -f $ComposeFile -p $ProjectName logs"
        }
    }
    else {
        Write-Error "❌ Deployment failed"
        exit 1
    }
}
catch {
    Write-Error "❌ Script execution failed: $_"
    exit 1
}

#!/usr/bin/env powershell
<#
.SYNOPSIS
    Security validation script for Scorpius Enterprise Platform
.DESCRIPTION
    Validates security configuration and identifies potential issues
#>

param(
    [string]$Environment = "production",
    [switch]$Detailed = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Blue }

$script:Issues = @()
$script:Warnings = @()
$script:Passed = @()

function Add-Issue { param($Message) $script:Issues += $Message }
function Add-Warning { param($Message) $script:Warnings += $Message }
function Add-Passed { param($Message) $script:Passed += $Message }

function Test-EnvironmentFile {
    Write-Info "Checking environment configuration..."
    
    $envFile = ".env.$Environment"
    if (-not (Test-Path $envFile)) {
        Add-Issue "Missing environment file: $envFile"
        return
    }
    
    $envContent = Get-Content $envFile -Raw
    
    # Check for hardcoded passwords
    $hardcodedPatterns = @(
        "scorpius123",
        "admin",
        "password",
        "secret123",
        "CHANGE_THIS",
        "dev-secret-key",
        "enterprise-secret-key"
    )
    
    foreach ($pattern in $hardcodedPatterns) {
        if ($envContent -match $pattern) {
            Add-Issue "Hardcoded/default credential detected: $pattern"
        }
    }
    
    # Check secret strength
    $envVars = Get-Content $envFile | Where-Object { $_ -match "^[^#].*=" }
    foreach ($line in $envVars) {
        $key, $value = $line -split "=", 2
        if ($key -like "*PASSWORD*" -or $key -like "*SECRET*" -or $key -like "*KEY*") {
            if ($value.Length -lt 16) {
                Add-Issue "Weak secret '$key': minimum 16 characters required"
            } elseif ($value.Length -ge 32) {
                Add-Passed "Strong secret '$key': $($value.Length) characters"
            } else {
                Add-Warning "Moderate secret '$key': $($value.Length) characters (32+ recommended)"
            }
        }
    }
    
    # Check required variables
    $requiredVars = @("DB_PASSWORD", "REDIS_PASSWORD", "JWT_SECRET")
    foreach ($var in $requiredVars) {
        if ($envContent -notmatch "$var=.+") {
            Add-Issue "Missing required environment variable: $var"
        } else {
            Add-Passed "Required variable present: $var"
        }
    }
}

function Test-DockerConfiguration {
    Write-Info "Checking Docker configuration..."
    
    # Check if docker-compose files exist
    $composeFiles = @(
        "docker/docker-compose.enterprise.yml",
        "docker/docker-compose.security.yml"
    )
    
    foreach ($file in $composeFiles) {
        if (Test-Path $file) {
            Add-Passed "Docker compose file found: $file"
            
            # Check for security issues in compose file
            $content = Get-Content $file -Raw
            
            # Check for hardcoded credentials
            if ($content -match "scorpius123|admin(?![a-z])|password123") {
                Add-Issue "Hardcoded credentials in $file"
            }
            
            # Check for exposed debug ports
            if ($content -match '"8001:8001".*debug' -or $content -match 'debug.*port') {
                Add-Issue "Debug port exposed in $file"
            } else {
                Add-Passed "No debug ports exposed in $file"
            }
            
            # Check for security options
            if ($content -match "security_opt:" -and $content -match "no-new-privileges") {
                Add-Passed "Security options configured in $file"
            } else {
                Add-Warning "Missing security hardening options in $file"
            }
            
        } else {
            Add-Issue "Missing Docker compose file: $file"
        }
    }
}

function Test-ContainerSecurity {
    Write-Info "Checking container security..."
    
    try {
        # Check if Docker is running with security features
        $dockerInfo = docker info --format '{{.SecurityOptions}}' 2>$null
        if ($dockerInfo -match "seccomp") {
            Add-Passed "Docker seccomp security profile enabled"
        } else {
            Add-Warning "Docker seccomp security profile not detected"
        }
        
        # Check running containers for security
        $containers = docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" 2>$null
        if ($containers) {
            Add-Passed "Docker containers are running"
            
            # Check if containers are running as root
            $rootContainers = docker ps -q | ForEach-Object {
                $user = docker exec $_ whoami 2>$null
                if ($user -eq "root") {
                    $name = docker inspect $_ --format '{{.Name}}' 2>$null
                    $name -replace '^/', ''
                }
            } | Where-Object { $_ }
            
            if ($rootContainers) {
                Add-Warning "Containers running as root: $($rootContainers -join ', ')"
            } else {
                Add-Passed "No containers running as root user"
            }
        }
        
    } catch {
        Add-Warning "Could not check Docker security (Docker may not be running)"
    }
}

function Test-NetworkSecurity {
    Write-Info "Checking network security..."
    
    try {
        # Check Docker networks
        $networks = docker network ls --format "{{.Name}}" 2>$null
        if ($networks -contains "scorpius-enterprise-network") {
            Add-Passed "Scorpius network exists"
            
            # Check network configuration
            $networkConfig = docker network inspect scorpius-enterprise-network 2>$null | ConvertFrom-Json
            if ($networkConfig.Driver -eq "bridge") {
                Add-Passed "Network using bridge driver"
            }
        } else {
            Add-Warning "Scorpius network not found (services may not be running)"
        }
        
    } catch {
        Add-Warning "Could not check network security"
    }
}

function Test-FilePermissions {
    Write-Info "Checking file permissions..."
    
    # Check sensitive files
    $sensitiveFiles = @(".env.$Environment", "docker-compose.security.yml")
    
    foreach ($file in $sensitiveFiles) {
        if (Test-Path $file) {
            try {
                $acl = Get-Acl $file
                $accessRules = $acl.Access | Where-Object { $_.IdentityReference -like "*Everyone*" -or $_.IdentityReference -like "*Users*" }
                
                if ($accessRules) {
                    Add-Warning "File $file may be readable by too many users"
                } else {
                    Add-Passed "File $file has restricted access"
                }
            } catch {
                Add-Warning "Could not check permissions for $file"
            }
        }
    }
}

function Test-Dependencies {
    Write-Info "Checking for vulnerable dependencies..."
    
    # Check if security report exists
    if (Test-Path "security-report.json") {
        $report = Get-Content "security-report.json" | ConvertFrom-Json
        $highSeverity = $report.results | Where-Object { $_.issue_severity -eq "HIGH" }
        $criticalSeverity = $report.results | Where-Object { $_.issue_severity -eq "CRITICAL" }
        
        if ($criticalSeverity) {
            Add-Issue "$($criticalSeverity.Count) critical security vulnerabilities found"
        }
        
        if ($highSeverity) {
            Add-Warning "$($highSeverity.Count) high severity security vulnerabilities found"
        }
        
        if (-not $highSeverity -and -not $criticalSeverity) {
            Add-Passed "No critical or high severity vulnerabilities in security report"
        }
    } else {
        Add-Warning "No security report found. Run: bandit -r . -f json -o security-report.json"
    }
}

function Show-Results {
    Write-Host "`n" + "="*80 -ForegroundColor Cyan
    Write-Host "🛡️  SECURITY VALIDATION RESULTS" -ForegroundColor Cyan
    Write-Host "="*80 -ForegroundColor Cyan
    
    if ($script:Issues.Count -gt 0) {
        Write-Host "`n❌ CRITICAL ISSUES ($($script:Issues.Count)):" -ForegroundColor Red
        foreach ($issue in $script:Issues) {
            Write-Host "   • $issue" -ForegroundColor Red
        }
    }
    
    if ($script:Warnings.Count -gt 0) {
        Write-Host "`n⚠️  WARNINGS ($($script:Warnings.Count)):" -ForegroundColor Yellow
        foreach ($warning in $script:Warnings) {
            Write-Host "   • $warning" -ForegroundColor Yellow
        }
    }
    
    if ($script:Passed.Count -gt 0 -and $Detailed) {
        Write-Host "`n✅ PASSED CHECKS ($($script:Passed.Count)):" -ForegroundColor Green
        foreach ($passed in $script:Passed) {
            Write-Host "   • $passed" -ForegroundColor Green
        }
    }
    
    Write-Host "`n" + "="*80 -ForegroundColor Cyan
    
    $total = $script:Issues.Count + $script:Warnings.Count + $script:Passed.Count
    $score = if ($total -gt 0) { [math]::Round(($script:Passed.Count / $total) * 100, 1) } else { 0 }
    
    Write-Host "SECURITY SCORE: $score%" -ForegroundColor $(if ($score -ge 90) { "Green" } elseif ($score -ge 70) { "Yellow" } else { "Red" })
    
    if ($script:Issues.Count -eq 0) {
        Write-Host "✅ NO CRITICAL ISSUES FOUND - READY FOR PRODUCTION" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ CRITICAL ISSUES MUST BE RESOLVED BEFORE PRODUCTION" -ForegroundColor Red
        exit 1
    }
}

# Main execution
Write-Host "🔍 Starting security validation for $Environment environment..." -ForegroundColor Cyan

Test-EnvironmentFile
Test-DockerConfiguration
Test-ContainerSecurity
Test-NetworkSecurity
Test-FilePermissions
Test-Dependencies

Show-Results

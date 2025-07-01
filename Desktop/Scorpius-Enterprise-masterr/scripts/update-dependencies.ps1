#!/usr/bin/env powershell
<#
.SYNOPSIS
    Updates vulnerable dependencies in Scorpius Enterprise Platform
.DESCRIPTION
    Updates all Python and Node.js dependencies to secure versions
#>

param(
    [switch]$Force = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Blue }

Write-Info "🔧 Updating vulnerable dependencies..."

# Update Python dependencies
$pythonRequirements = @(
    "config/requirements-dev.txt",
    "services/api-gateway/requirements.txt",
    "packages/core/requirements.txt"
)

foreach ($reqFile in $pythonRequirements) {
    if (Test-Path $reqFile) {
        Write-Info "Updating $reqFile..."
        
        # Read current requirements
        $content = Get-Content $reqFile
        
        # Update specific vulnerable packages
        $updates = @{
            "cryptography" = "cryptography>=41.0.8"
            "aiohttp" = "aiohttp>=3.9.2"
            "gitpython" = "gitpython>=3.1.41"
            "dash" = "dash>=2.17.0"
            "black" = "black>=24.3.0"
            "PyJWT" = "PyJWT>=2.8.0"
            "requests" = "requests>=2.31.0"
        }
        
        $updatedContent = @()
        $updated = @()
        
        foreach ($line in $content) {
            if ($line -match '^([^=<>!]+)') {
                $packageName = $matches[1]
                if ($updates.ContainsKey($packageName)) {
                    $updatedContent += $updates[$packageName]
                    $updated += $packageName
                } else {
                    $updatedContent += $line
                }
            } else {
                $updatedContent += $line
            }
        }
        
        # Add any missing security updates
        foreach ($package in $updates.Keys) {
            if ($package -notin $updated) {
                $updatedContent += $updates[$package]
                $updated += $package
            }
        }
        
        # Write updated requirements
        $updatedContent | Out-File -FilePath $reqFile -Encoding UTF8
        
        Write-Success "Updated packages in ${reqFile}: $($updated -join ', ')"
    }
}

# Update Node.js dependencies
if (Test-Path "frontend/package.json") {
    Write-Info "Updating Node.js dependencies..."
    
    Set-Location frontend
    
    try {
        # Update to latest secure versions
        npm update
        npm audit fix --force
        
        Write-Success "Node.js dependencies updated"
    } catch {
        Write-Warning "Some Node.js updates may require manual intervention"
    } finally {
        Set-Location ..
    }
}

Write-Success "🎉 Dependency updates completed!"
Write-Info "Run security scan again with: bandit -r . -f json -o security-report-updated.json"

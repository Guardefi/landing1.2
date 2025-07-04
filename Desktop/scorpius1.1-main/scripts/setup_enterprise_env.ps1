# Scorpius Enterprise Environment Setup Script
# This script sets up the complete enterprise development environment

param(
    [switch]$Force,
    [switch]$SkipPythonCheck
)

function Write-Header {
    param([string]$Message)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Test-PythonVersion {
    Write-Header "Checking Python Version"
    
    # Check if Python 3.11 is available
    try {
        $python311 = & py -3.11 --version 2>$null
        if ($python311) {
            Write-Host "✓ Python 3.11 found: $python311" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "✗ Python 3.11 not found" -ForegroundColor Red
    }
    
    # Check current Python version
    $currentVersion = & python --version 2>$null
    Write-Host "Current Python version: $currentVersion" -ForegroundColor Yellow
    
    if ($currentVersion -like "*3.13*") {
        Write-Host "⚠️  Warning: Python 3.13 detected. Some packages may not be compatible." -ForegroundColor Yellow
        Write-Host "   Recommended: Use Python 3.11 for full compatibility." -ForegroundColor Yellow
        
        if (-not $SkipPythonCheck) {
            $response = Read-Host "Do you want to continue with Python 3.13? (y/N)"
            if ($response -ne "y" -and $response -ne "Y") {
                Write-Host "Setup aborted. Please install Python 3.11 and try again." -ForegroundColor Red
                exit 1
            }
        }
    }
    
    return $false
}

function Install-PythonDependencies {
    Write-Header "Installing Python Dependencies"
    
    # Determine which Python to use
    $pythonCmd = "python"
    try {
        $testResult = & py -3.11 --version 2>$null
        if ($testResult) {
            $pythonCmd = "py -3.11"
            Write-Host "Using Python 3.11 for installation" -ForegroundColor Green
        } else {
            Write-Host "Using system Python for installation" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Using system Python for installation" -ForegroundColor Yellow
    }
    
    # Upgrade pip first
    Write-Host "Upgrading pip..." -ForegroundColor Yellow
    & $pythonCmd -m pip install --upgrade pip
    
    # Install dependencies
    Write-Host "Installing development dependencies..." -ForegroundColor Yellow
    & $pythonCmd -m pip install -r config/requirements-dev.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        return $false
    }
    
    return $true
}

function Setup-VirtualEnvironment {
    Write-Header "Setting Up Virtual Environment"
    
    # Check if virtual environment exists
    if (Test-Path "venv") {
        if ($Force) {
            Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
            Remove-Item -Recurse -Force "venv"
        } else {
            Write-Host "Virtual environment already exists. Use -Force to recreate." -ForegroundColor Yellow
            return $true
        }
    }
    
    # Determine which Python to use
    $pythonCmd = "python"
    try {
        $testResult = & py -3.11 --version 2>$null
        if ($testResult) {
            $pythonCmd = "py -3.11"
        }
    } catch {
        # Use default python
    }
    
    # Create virtual environment
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $pythonCmd -m venv venv
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        return $false
    }
    
    # Install dependencies in virtual environment
    Write-Host "Installing dependencies in virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\python.exe" -m pip install --upgrade pip
    & "venv\Scripts\python.exe" -m pip install -r config/requirements-dev.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment setup complete" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install dependencies in virtual environment" -ForegroundColor Red
        return $false
    }
    
    return $true
}

function Test-Installation {
    Write-Header "Testing Installation"
    
    # Test Python imports
    $testImports = @(
        "fastapi",
        "uvicorn", 
        "pydantic",
        "pytest",
        "black",
        "flake8",
        "mypy",
        "docker"
    )
    
    $pythonCmd = "python"
    try {
        $testResult = & py -3.11 --version 2>$null
        if ($testResult) {
            $pythonCmd = "py -3.11"
        }
    } catch {
        # Use default python
    }
    
    $failedImports = @()
    
    foreach ($module in $testImports) {
        try {
            $result = & $pythonCmd -c "import $module; print('✓ $module')" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ $module" -ForegroundColor Green
            } else {
                Write-Host "✗ $module" -ForegroundColor Red
                $failedImports += $module
            }
        } catch {
            Write-Host "✗ $module" -ForegroundColor Red
            $failedImports += $module
        }
    }
    
    if ($failedImports.Count -gt 0) {
        Write-Host "`n⚠️  Some modules failed to import:" -ForegroundColor Yellow
        foreach ($module in $failedImports) {
            Write-Host "  - $module" -ForegroundColor Yellow
        }
        return $false
    } else {
        Write-Host "`n✓ All core modules imported successfully" -ForegroundColor Green
        return $true
    }
}

function Setup-GitHooks {
    Write-Header "Setting Up Git Hooks"
    
    try {
        # Install pre-commit hooks
        $pythonCmd = "python"
        try {
            $testResult = & py -3.11 --version 2>$null
            if ($testResult) {
                $pythonCmd = "py -3.11"
            }
        } catch {
            # Use default python
        }
        
        & $pythonCmd -m pre_commit install
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Pre-commit hooks installed" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Pre-commit hooks installation failed" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Could not install pre-commit hooks" -ForegroundColor Yellow
    }
}

function Test-BuildProcess {
    Write-Header "Testing Build Process"
    
    # Test linting
    Write-Host "Testing code linting..." -ForegroundColor Yellow
    $pythonCmd = "python"
    try {
        $testResult = & py -3.11 --version 2>$null
        if ($testResult) {
            $pythonCmd = "py -3.11"
        }
    } catch {
        # Use default python
    }
    
    & $pythonCmd -m flake8 --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Flake8 available" -ForegroundColor Green
    } else {
        Write-Host "✗ Flake8 not available" -ForegroundColor Red
    }
    
    # Test formatting
    & $pythonCmd -m black --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Black available" -ForegroundColor Green
    } else {
        Write-Host "✗ Black not available" -ForegroundColor Red
    }
    
    # Test type checking
    & $pythonCmd -m mypy --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ MyPy available" -ForegroundColor Green
    } else {
        Write-Host "✗ MyPy not available" -ForegroundColor Red
    }
}

function Show-NextSteps {
    Write-Header "Setup Complete - Next Steps"
    
    Write-Host "🎉 Enterprise environment setup completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Activate virtual environment (if created):" -ForegroundColor White
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Test the build process:" -ForegroundColor White
    Write-Host "   .\scripts\enterprise-commands.ps1 test" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Run linting:" -ForegroundColor White
    Write-Host "   .\scripts\enterprise-commands.ps1 lint" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Start development environment:" -ForegroundColor White
    Write-Host "   .\scripts\enterprise-commands.ps1 dev" -ForegroundColor Gray
    Write-Host ""
    Write-Host "5. View available commands:" -ForegroundColor White
    Write-Host "   .\scripts\enterprise-commands.ps1 help" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📚 Documentation:" -ForegroundColor Cyan
    Write-Host "   - Project Structure: docs/enterprise/PROJECT_STRUCTURE.md" -ForegroundColor Gray
    Write-Host "   - Quick Reference: docs/enterprise/QUICK_REFERENCE.md" -ForegroundColor Gray
    Write-Host "   - Next Steps: docs/enterprise/NEXT_STEPS_REPORT.md" -ForegroundColor Gray
}

function Main {
    Write-Host "🚀 Scorpius Enterprise Environment Setup" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    
    # Check Python version
    if (-not $SkipPythonCheck) {
        Test-PythonVersion
    }
    
    # Install dependencies
    if (-not (Install-PythonDependencies)) {
        Write-Host "`n❌ Setup failed during dependency installation" -ForegroundColor Red
        exit 1
    }
    
    # Setup virtual environment (optional)
    $useVenv = Read-Host "Do you want to create a virtual environment? (Y/n)"
    if ($useVenv -ne "n" -and $useVenv -ne "N") {
        if (-not (Setup-VirtualEnvironment)) {
            Write-Host "`n❌ Setup failed during virtual environment creation" -ForegroundColor Red
            exit 1
        }
    }
    
    # Setup Git hooks
    Setup-GitHooks
    
    # Test installation
    if (-not (Test-Installation)) {
        Write-Host "`n⚠️  Some components failed to install properly" -ForegroundColor Yellow
    }
    
    # Test build process
    Test-BuildProcess
    
    # Show next steps
    Show-NextSteps
}

# Run main function
Main 
# Setup script for Scorpius Enhanced Scanner with Hardhat simulation support (Windows)

Write-Host "🔧 Setting up Scorpius Enhanced Vulnerability Scanner..." -ForegroundColor Cyan

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Node.js $nodeVersion found" -ForegroundColor Green
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    Write-Host "   Minimum version required: Node.js 16.x or higher" -ForegroundColor Yellow
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ npm $npmVersion found" -ForegroundColor Green
    } else {
        throw "npm not found"
    }
} catch {
    Write-Host "❌ npm is not installed. Please install npm (usually comes with Node.js)" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
$pythonCmd = $null
foreach ($cmd in @("python", "py", "python3")) {
    try {
        & $cmd --version 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            $pythonVersion = & $cmd --version
            Write-Host "✅ $pythonVersion found" -ForegroundColor Green
            break
        }
    } catch {
        # Continue to next command
    }
}

if (-not $pythonCmd) {
    Write-Host "❌ Python is not installed. Please install Python 3.8 or higher" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Cyan
& $pythonCmd -m pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

# Test Hardhat installation capability
Write-Host "🧪 Testing Hardhat setup capability..." -ForegroundColor Cyan
$tempDir = [System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString()
New-Item -ItemType Directory -Path $tempDir | Out-Null
$originalLocation = Get-Location
Set-Location $tempDir

try {
    # Create minimal package.json for testing
    $packageJson = @{
        name = "hardhat-test"
        version = "1.0.0"
        devDependencies = @{
            "@nomicfoundation/hardhat-toolbox" = "^4.0.0"
            "hardhat" = "^2.19.0"
        }
    } | ConvertTo-Json -Depth 3

    $packageJson | Out-File -FilePath "package.json" -Encoding UTF8

    # Try to install Hardhat (this may take a moment)
    Write-Host "📦 Testing npm install (this may take a moment)..." -ForegroundColor Cyan
    
    $job = Start-Job -ScriptBlock { 
        Set-Location $args[0]
        npm install --silent 2>$null
    } -ArgumentList $tempDir
    
    $job | Wait-Job -Timeout 120 | Out-Null
    
    if ($job.State -eq "Completed" -and $job | Receive-Job) {
        Write-Host "✅ Hardhat installation test successful" -ForegroundColor Green
        
        # Test if Hardhat can initialize
        try {
            npx hardhat --version 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Hardhat is working correctly" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Hardhat installed but may have issues" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⚠️  Hardhat installed but may have issues" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  Hardhat installation test failed or timed out" -ForegroundColor Yellow
        Write-Host "   Simulation features may not work, but other scanner features will function" -ForegroundColor Yellow
    }
    
    $job | Remove-Job -Force
    
} finally {
    # Cleanup
    Set-Location $originalLocation
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Quick Start:" -ForegroundColor Cyan
Write-Host "   1. Run a simple test: python test_enhanced_scanner.py" -ForegroundColor White
Write-Host "   2. Run the demo: python demo_enhanced_scanner.py" -ForegroundColor White
Write-Host "   3. Use the CLI: python -m cli.scanner_cli --help" -ForegroundColor White
Write-Host ""
Write-Host "🔍 For simulation features:" -ForegroundColor Cyan
Write-Host "   - Ensure Node.js 16+ and npm are installed" -ForegroundColor White
Write-Host "   - Internet connection required for Hardhat dependencies" -ForegroundColor White
Write-Host "   - First simulation run may take longer as dependencies download" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Ready to scan for vulnerabilities!" -ForegroundColor Green

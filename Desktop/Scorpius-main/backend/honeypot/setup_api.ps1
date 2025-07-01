# Honeypot Detector API Setup Script for Windows
# Run this script in PowerShell as Administrator

Write-Host "🚀 Setting up Honeypot Detector API for React Dashboard Integration" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

# Check if Python is installed
Write-Host "📋 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check if pip is available
Write-Host "📋 Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ Pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Pip not found. Please install pip" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "🐍 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install development dependencies
Write-Host "📦 Installing development dependencies..." -ForegroundColor Yellow
pip install -r requirements-dev.txt

# Check if MongoDB is running
Write-Host "🍃 Checking MongoDB..." -ForegroundColor Yellow
try {
    $mongoProcess = Get-Process mongod -ErrorAction SilentlyContinue
    if ($mongoProcess) {
        Write-Host "✅ MongoDB is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MongoDB not running. Please start MongoDB or use Docker:" -ForegroundColor Yellow
        Write-Host "   Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️  MongoDB status unknown. Please ensure MongoDB is available" -ForegroundColor Yellow
}

# Check if Redis is available
Write-Host "🔴 Checking Redis..." -ForegroundColor Yellow
Write-Host "⚠️  Please ensure Redis is running on localhost:6379" -ForegroundColor Yellow
Write-Host "   Docker: docker run -d -p 6379:6379 --name redis redis:latest" -ForegroundColor Cyan

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$directories = @("logs", "data", "models")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Directory already exists: $dir" -ForegroundColor Blue
    }
}

Write-Host "`n🎉 Setup completed!" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "1. Ensure MongoDB and Redis are running" -ForegroundColor White
Write-Host "2. Update .env file with your API keys if needed" -ForegroundColor White
Write-Host "3. Run the API: python start_api.py" -ForegroundColor White
Write-Host "4. Visit http://localhost:8000/docs for API documentation" -ForegroundColor White
Write-Host "5. Test with your React dashboard on http://localhost:3000 or :5173" -ForegroundColor White
Write-Host "`n🔗 API Endpoints for React Integration:" -ForegroundColor Yellow
Write-Host "• Health: GET /health" -ForegroundColor Cyan
Write-Host "• Analysis: POST /api/v1/analyze" -ForegroundColor Cyan
Write-Host "• Dashboard Stats: GET /api/v1/dashboard/stats" -ForegroundColor Cyan
Write-Host "• Search: GET /api/v1/dashboard/search" -ForegroundColor Cyan
Write-Host "• Trends: GET /api/v1/dashboard/trends" -ForegroundColor Cyan
Write-Host "`n🔑 API Key: Add 'X-API-Key: honeypot-detector-api-key-12345' to your headers" -ForegroundColor Yellow

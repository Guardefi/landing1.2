# Scorpius Frontend Setup Script for Windows PowerShell
# Run this script to ensure everything is properly configured

Write-Host "🚀 Setting up Scorpius Frontend for Windows..." -ForegroundColor Cyan

# Check if we're in the correct directory
if (!(Test-Path "package.json")) {
    Write-Host "❌ Error: package.json not found. Make sure you're in the frontend directory." -ForegroundColor Red
    Write-Host "   Run: cd frontend" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found package.json" -ForegroundColor Green

# Check Node.js version
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
    
    # Extract version number and check if it's >= 18
    $versionNumber = [version]($nodeVersion -replace 'v', '')
    if ($versionNumber.Major -lt 18) {
        Write-Host "⚠️  Warning: Node.js 18+ recommended. Current: $nodeVersion" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Check npm version
try {
    $npmVersion = npm --version
    Write-Host "✅ npm version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please install npm." -ForegroundColor Red
    exit 1
}

# Clean previous installations
Write-Host "🧹 Cleaning previous installations..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
    Write-Host "   Removed node_modules" -ForegroundColor Yellow
}

if (Test-Path "package-lock.json") {
    Remove-Item -Force "package-lock.json" 
    Write-Host "   Removed package-lock.json" -ForegroundColor Yellow
}

# Clear npm cache
Write-Host "🗑️ Clearing npm cache..." -ForegroundColor Yellow
npm cache clean --force

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
Write-Host "   This may take a few minutes..." -ForegroundColor Yellow

try {
    npm install --legacy-peer-deps
    Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ npm install failed. Trying alternative approach..." -ForegroundColor Red
    
    # Try with different flags
    try {
        npm install --force
        Write-Host "✅ Dependencies installed with --force flag!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Installation failed. Please check your network connection and try again." -ForegroundColor Red
        exit 1
    }
}

# Create environment file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "📄 Creating .env file..." -ForegroundColor Yellow
    @"
# Scorpius Frontend Environment Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_GRAFANA_URL=http://localhost:3001
VITE_PORT=3000

# Optional: Uncomment if using custom backend
# VITE_API_BASE_URL_PRODUCTION=https://your-api.domain.com
# VITE_WS_BASE_URL_PRODUCTION=wss://your-api.domain.com
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Created .env file with default configuration" -ForegroundColor Green
}

# Check if all required files exist
$requiredFiles = @(
    "src/main.tsx",
    "src/App.tsx", 
    "src/index.css",
    "tailwind.config.ts",
    "vite.config.ts"
)

Write-Host "🔍 Checking required files..." -ForegroundColor Cyan
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing: $file" -ForegroundColor Red
    }
}

# Check public directory
if (Test-Path "public") {
    Write-Host "✅ public directory exists" -ForegroundColor Green
} else {
    Write-Host "❌ Missing public directory" -ForegroundColor Red
}

# Check TypeScript configuration
if (Test-Path "tsconfig.json") {
    Write-Host "✅ TypeScript configuration found" -ForegroundColor Green
} else {
    Write-Host "⚠️  TypeScript configuration missing" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Setup complete! You can now run:" -ForegroundColor Green
Write-Host ""
Write-Host "   npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "The application will be available at:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 To check backend integration status:" -ForegroundColor Yellow
Write-Host "   Visit http://localhost:3000/api/status after starting the app" -ForegroundColor Cyan
Write-Host ""

# Offer to start the dev server
$startServer = Read-Host "Would you like to start the development server now? (y/n)"
if ($startServer -eq 'y' -or $startServer -eq 'Y' -or $startServer -eq 'yes') {
    Write-Host "🚀 Starting development server..." -ForegroundColor Cyan
    npm run dev
}

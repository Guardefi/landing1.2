@echo off
echo.
echo 🚀 Setting up Scorpius Frontend for Windows...
echo.

REM Check if we're in the correct directory
if not exist package.json (
    echo ❌ Error: package.json not found. Make sure you're in the frontend directory.
    echo    Run: cd frontend
    pause
    exit /b 1
)

echo ✅ Found package.json

REM Check Node.js version
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('node --version') do set NODE_VERSION=%%a
echo ✅ Node.js version: %NODE_VERSION%

REM Check npm version
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm not found. Please install npm.
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('npm --version') do set NPM_VERSION=%%a
echo ✅ npm version: %NPM_VERSION%

REM Clean previous installations
echo.
echo 🧹 Cleaning previous installations...
if exist node_modules (
    rmdir /s /q node_modules
    echo    Removed node_modules
)

if exist package-lock.json (
    del package-lock.json
    echo    Removed package-lock.json
)

REM Clear npm cache
echo 🗑️ Clearing npm cache...
npm cache clean --force

REM Install dependencies
echo.
echo 📦 Installing dependencies...
echo    This may take a few minutes...
npm install --legacy-peer-deps

if errorlevel 1 (
    echo ❌ npm install failed. Trying alternative approach...
    npm install --force
    if errorlevel 1 (
        echo ❌ Installation failed. Please check your network connection and try again.
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed with --force flag!
) else (
    echo ✅ Dependencies installed successfully!
)

REM Create environment file if it doesn't exist
if not exist .env (
    echo 📄 Creating .env file...
    (
        echo # Scorpius Frontend Environment Configuration
        echo VITE_API_BASE_URL=http://localhost:8000
        echo VITE_WS_BASE_URL=ws://localhost:8000
        echo VITE_GRAFANA_URL=http://localhost:3001
        echo VITE_PORT=3000
        echo.
        echo # Optional: Uncomment if using custom backend
        echo # VITE_API_BASE_URL_PRODUCTION=https://your-api.domain.com
        echo # VITE_WS_BASE_URL_PRODUCTION=wss://your-api.domain.com
    ) > .env
    echo ✅ Created .env file with default configuration
)

REM Check required files
echo.
echo 🔍 Checking required files...
if exist "src\main.tsx" (echo ✅ src\main.tsx) else (echo ❌ Missing: src\main.tsx)
if exist "src\App.tsx" (echo ✅ src\App.tsx) else (echo ❌ Missing: src\App.tsx)
if exist "src\index.css" (echo ✅ src\index.css) else (echo ❌ Missing: src\index.css)
if exist "tailwind.config.ts" (echo ✅ tailwind.config.ts) else (echo ❌ Missing: tailwind.config.ts)
if exist "vite.config.ts" (echo ✅ vite.config.ts) else (echo ❌ Missing: vite.config.ts)

if exist public (echo ✅ public directory exists) else (echo ❌ Missing public directory)
if exist tsconfig.json (echo ✅ TypeScript configuration found) else (echo ⚠️  TypeScript configuration missing)

echo.
echo 🎉 Setup complete! You can now run:
echo.
echo    npm run dev
echo.
echo The application will be available at:
echo    http://localhost:3000
echo.
echo 📊 To check backend integration status:
echo    Visit http://localhost:3000/api/status after starting the app
echo.

set /p START_SERVER="Would you like to start the development server now? (y/n): "
if /i "%START_SERVER%"=="y" (
    echo 🚀 Starting development server...
    npm run dev
) else if /i "%START_SERVER%"=="yes" (
    echo 🚀 Starting development server...
    npm run dev
)

pause

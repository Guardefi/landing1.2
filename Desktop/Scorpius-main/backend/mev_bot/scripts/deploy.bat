@echo off
:: MevGuardian Deployment Script for Windows
:: Automates the deployment process for production environments

echo 🚀 Starting MevGuardian deployment...

:: Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

:: Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

:: Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Copying from .env.example...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your configuration before proceeding.
    pause
)

:: Create necessary directories
echo 📁 Creating directories...
if not exist logs mkdir logs
if not exist config mkdir config
if not exist monitoring\grafana\dashboards mkdir monitoring\grafana\dashboards

:: Build the application
echo 🔨 Building MevGuardian Docker image...
docker-compose build

:: Start the database first
echo 🗄️  Starting database services...
docker-compose up -d postgres redis

:: Wait for database to be ready
echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak >nul

:: Start all services
echo 🚀 Starting all MevGuardian services...
docker-compose up -d

:: Wait for services to start
timeout /t 15 /nobreak >nul

:: Display completion message
echo.
echo 🎉 MevGuardian deployment completed!
echo.
echo 📊 Service URLs:
echo   • MevGuardian API: http://localhost:8000
echo   • API Documentation: http://localhost:8000/docs
echo   • Grafana Dashboard: http://localhost:3000 (admin/admin)
echo   • Prometheus: http://localhost:9090
echo.
echo 📋 Management Commands:
echo   • View logs: docker-compose logs -f
echo   • Stop services: docker-compose down
echo   • Restart: docker-compose restart
echo   • Update: docker-compose pull ^&^& docker-compose up -d
echo.
echo ⚠️  Remember to change default passwords in production!
pause

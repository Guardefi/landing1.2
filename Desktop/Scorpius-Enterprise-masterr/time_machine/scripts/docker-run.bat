@echo off
rem Time Machine Docker Build and Run Script for Windows

echo 🔧 Building Time Machine Docker image...
docker build -t time-machine:latest .

if %ERRORLEVEL% neq 0 (
    echo ❌ Docker build failed!
    exit /b %ERRORLEVEL%
)

echo 🚀 Starting Time Machine with Docker Compose...
docker-compose up -d

if %ERRORLEVEL% neq 0 (
    echo ❌ Docker compose failed!
    exit /b %ERRORLEVEL%
)

echo ✅ Time Machine is starting up!
echo 📊 API will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo 🔗 Blockchain node (Anvil): http://localhost:8545
echo.
echo 📝 View logs with:
echo    docker-compose logs -f time-machine
echo.
echo 🛑 Stop services with:
echo    docker-compose down

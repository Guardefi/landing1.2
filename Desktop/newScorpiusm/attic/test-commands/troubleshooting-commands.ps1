# Troubleshooting and Diagnostic Commands
# These commands help debug issues and diagnose problems

Write-Host "=== TROUBLESHOOTING AND DIAGNOSTIC COMMANDS ===" -ForegroundColor Green

# System Information
Write-Host "`n1. System Information..." -ForegroundColor Yellow

# Python environment info
Write-Host "   - Python environment..." -ForegroundColor Cyan
python --version
python -m pip --version
python -c "import sys; print('Python path:', sys.path)"

# Node.js environment info
Write-Host "   - Node.js environment..." -ForegroundColor Cyan
node --version
npm --version
Get-Location

# System resources
Write-Host "   - System resources..." -ForegroundColor Cyan
python -c "import psutil; print(f'CPU: {psutil.cpu_count()} cores, Memory: {psutil.virtual_memory().total // 1024**3}GB')"

# Service Status Checks
Write-Host "`n2. Service Status Checks..." -ForegroundColor Yellow

# Check if backend server is running
Write-Host "   - Backend server status..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/healthz" -UseBasicParsing -TimeoutSec 5
    Write-Host "Backend: Running (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "Backend: Not running or unreachable" -ForegroundColor Red
}

# Check database connection
Write-Host "   - Database connection..." -ForegroundColor Cyan
python -c "
try:
    from backend.database import engine
    conn = engine.connect()
    print('Database: Connected')
    conn.close()
except Exception as e:
    print(f'Database: Error - {e}')
"

# Check Redis connection
Write-Host "   - Redis connection..." -ForegroundColor Cyan
python -c "
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print('Redis: Connected')
except Exception as e:
    print(f'Redis: Error - {e}')
"

# Log Analysis
Write-Host "`n3. Log Analysis..." -ForegroundColor Yellow

# View recent application logs
Write-Host "   - Recent application logs..." -ForegroundColor Cyan
if (Test-Path "logs/") {
    Get-ChildItem -Path "logs/" -Name "*.log" | ForEach-Object {
        Write-Host "   📄 $_"
        Get-Content -Path "logs/$_" -Tail 10
    }
} else {
    Write-Host "   No log directory found"
}

# View error logs
Write-Host "   - Error logs..." -ForegroundColor Cyan
if (Test-Path "logs/error.log") {
    Write-Host "   Recent errors:"
    Get-Content -Path "logs/error.log" -Tail 20 | Where-Object { $_ -match "ERROR|CRITICAL" }
}

# View access logs
Write-Host "   - Access logs..." -ForegroundColor Cyan
if (Test-Path "logs/access.log") {
    Write-Host "   Recent access:"
    Get-Content -Path "logs/access.log" -Tail 10
}

# Process Diagnostics
Write-Host "`n4. Process Diagnostics..." -ForegroundColor Yellow

# Find Python processes
Write-Host "   - Python processes..." -ForegroundColor Cyan
Get-Process | Where-Object { $_.ProcessName -like "*python*" } | Select-Object Id, ProcessName, CPU, WorkingSet

# Find Node.js processes
Write-Host "   - Node.js processes..." -ForegroundColor Cyan
Get-Process | Where-Object { $_.ProcessName -like "*node*" } | Select-Object Id, ProcessName, CPU, WorkingSet

# Find Docker processes
Write-Host "   - Docker processes..." -ForegroundColor Cyan
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# Port Usage Diagnostics
Write-Host "`n5. Port Usage Diagnostics..." -ForegroundColor Yellow

# Check if ports are in use
Write-Host "   - Port usage..." -ForegroundColor Cyan
$ports = @(8000, 3000, 5432, 6379, 27017)
foreach ($port in $ports) {
    $connection = Test-NetConnection -ComputerName "localhost" -Port $port -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "   Port $port : IN USE" -ForegroundColor Yellow
    } else {
        Write-Host "   Port $port : Available" -ForegroundColor Green
    }
}

# Network connectivity test
Write-Host "   - Network connectivity..." -ForegroundColor Cyan
Test-NetConnection -ComputerName "google.com" -Port 80

# Dependency Issues
Write-Host "`n6. Dependency Issues..." -ForegroundColor Yellow

# Check Python package conflicts
Write-Host "   - Python package conflicts..." -ForegroundColor Cyan
pip check

# List installed Python packages
Write-Host "   - Installed Python packages..." -ForegroundColor Cyan
pip list --format=freeze | Sort-Object

# Check npm package issues
Write-Host "   - npm package issues..." -ForegroundColor Cyan
npm ls --depth=0

# Environment Variable Diagnostics
Write-Host "`n7. Environment Variables..." -ForegroundColor Yellow

# Check critical environment variables
Write-Host "   - Critical env vars..." -ForegroundColor Cyan
$envVars = @("PYTHONPATH", "NODE_ENV", "DATABASE_URL", "REDIS_URL", "SECRET_KEY")
foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "   $var : SET" -ForegroundColor Green
    } else {
        Write-Host "   $var : NOT SET" -ForegroundColor Red
    }
}

# Configuration File Validation
Write-Host "`n8. Configuration Validation..." -ForegroundColor Yellow

# Validate JSON config files
Write-Host "   - JSON validation..." -ForegroundColor Cyan
$jsonFiles = Get-ChildItem -Path . -Filter "*.json" -Recurse | Select-Object -First 5
foreach ($file in $jsonFiles) {
    try {
        $content = Get-Content -Path $file.FullName | ConvertFrom-Json
        Write-Host "   ✅ $($file.Name)" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ $($file.Name) - Invalid JSON" -ForegroundColor Red
    }
}

# Validate YAML config files
Write-Host "   - YAML validation..." -ForegroundColor Cyan
$yamlFiles = Get-ChildItem -Path . -Filter "*.yml" -Recurse | Select-Object -First 5
foreach ($file in $yamlFiles) {
    Write-Host "   📄 $($file.Name)"
}

# Database Diagnostics
Write-Host "`n9. Database Diagnostics..." -ForegroundColor Yellow

# Test database queries
Write-Host "   - Database queries..." -ForegroundColor Cyan
python -c "
try:
    from backend.database import Session
    from backend.models import User
    session = Session()
    count = session.query(User).count()
    print(f'User count: {count}')
    session.close()
except Exception as e:
    print(f'Database query error: {e}')
"

# Check database migrations
Write-Host "   - Migration status..." -ForegroundColor Cyan
try {
    alembic current 2>$null
    Write-Host "   Alembic: Available"
} catch {
    Write-Host "   Alembic: Not configured"
}

# API Endpoint Diagnostics
Write-Host "`n10. API Endpoint Testing..." -ForegroundColor Yellow

# Test all major endpoints
Write-Host "   - API endpoints..." -ForegroundColor Cyan
$endpoints = @(
    @{url="http://localhost:8000/healthz"; name="Health"},
    @{url="http://localhost:8000/readyz"; name="Ready"},
    @{url="http://localhost:8000/metrics"; name="Metrics"},
    @{url="http://localhost:8000/api/auth/status"; name="Auth Status"}
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.url -UseBasicParsing -TimeoutSec 5
        Write-Host "   ✅ $($endpoint.name) : $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ $($endpoint.name) : Failed" -ForegroundColor Red
    }
}

# Performance Diagnostics
Write-Host "`n11. Performance Diagnostics..." -ForegroundColor Yellow

# Memory usage
Write-Host "   - Memory usage..." -ForegroundColor Cyan
$memory = Get-CimInstance -ClassName Win32_ComputerSystem
$totalMemory = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
$availableMemory = [math]::Round((Get-CimInstance -ClassName Win32_PerfRawData_PerfOS_Memory).AvailableBytes / 1GB, 2)
Write-Host "   Total: ${totalMemory}GB, Available: ${availableMemory}GB"

# Disk usage
Write-Host "   - Disk usage..." -ForegroundColor Cyan
Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 } | ForEach-Object {
    $freeSpace = [math]::Round($_.FreeSpace / 1GB, 2)
    $totalSpace = [math]::Round($_.Size / 1GB, 2)
    Write-Host "   Drive $($_.DeviceID) ${freeSpace}GB free of ${totalSpace}GB"
}

# Security Diagnostics
Write-Host "`n12. Security Diagnostics..." -ForegroundColor Yellow

# Check for exposed secrets
Write-Host "   - Secret exposure check..." -ForegroundColor Cyan
$secretPatterns = @("password", "secret", "key", "token", "api_key")
foreach ($pattern in $secretPatterns) {
    $found = Select-String -Path "*.py", "*.js", "*.json", "*.yml" -Pattern $pattern -List 2>$null | Select-Object -First 3
    if ($found) {
        Write-Host "   ⚠️  Found '$pattern' in files - review for secrets"
    }
}

# Container Diagnostics
Write-Host "`n13. Container Diagnostics..." -ForegroundColor Yellow

# Docker system info
Write-Host "   - Docker system..." -ForegroundColor Cyan
try {
    docker version --format "   Docker: {{.Server.Version}}"
    docker system df
} catch {
    Write-Host "   Docker: Not available"
}

# Container health checks
Write-Host "   - Container health..." -ForegroundColor Cyan
docker ps --filter "name=scorpius" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Quick Fix Commands
Write-Host "`n14. Quick Fix Commands..." -ForegroundColor Yellow

Write-Host "   - Restart services..." -ForegroundColor Cyan
Write-Host "     docker-compose restart" -ForegroundColor Gray
Write-Host "     Restart-Service -Name 'ServiceName'" -ForegroundColor Gray

Write-Host "   - Clear caches..." -ForegroundColor Cyan
Write-Host "     npm cache clean --force" -ForegroundColor Gray
Write-Host "     pip cache purge" -ForegroundColor Gray
Write-Host "     docker system prune -f" -ForegroundColor Gray

Write-Host "   - Reset environment..." -ForegroundColor Cyan
Write-Host "     Remove-Item -Path 'node_modules' -Recurse -Force" -ForegroundColor Gray
Write-Host "     npm install" -ForegroundColor Gray
Write-Host "     pip install -r requirements.txt --force-reinstall" -ForegroundColor Gray

# Export Diagnostic Report
Write-Host "`n15. Export Diagnostic Report..." -ForegroundColor Yellow

Write-Host "   - Generate report..." -ForegroundColor Cyan
$reportPath = "diagnostic-report-$(Get-Date -Format 'yyyy-MM-dd-HHmm').txt"
Write-Host "   Report will be saved to: $reportPath"

# Comprehensive diagnostic summary
Write-Host "`n=== DIAGNOSTIC SUMMARY ===" -ForegroundColor Green
Write-Host "✅ = Working correctly
⚠️  = Needs attention  
❌ = Critical issue
📄 = Information only" -ForegroundColor Gray

Write-Host "`n=== COMMON ISSUES & SOLUTIONS ===" -ForegroundColor Red
Write-Host "1. Port already in use: Use 'netstat -ano | findstr :8000' to find process"
Write-Host "2. Module not found: Check virtual environment activation"
Write-Host "3. Database connection refused: Verify database service is running"
Write-Host "4. Permission denied: Run as administrator or check file permissions"
Write-Host "5. Out of memory: Check for memory leaks or increase system memory"

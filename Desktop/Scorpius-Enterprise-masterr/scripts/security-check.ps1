Write-Host "🔍 Scorpius Security Validation" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$issues = @()
$warnings = @()
$passed = @()

# Check environment file
Write-Host "Checking environment configuration..." -ForegroundColor Blue
$envFile = ".env.production"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    
    # Check for hardcoded passwords
    if ($envContent -match "scorpius123|admin[^a-z]|CHANGE_THIS") {
        $issues += "Hardcoded credentials found in $envFile"
    } else {
        $passed += "No hardcoded credentials in $envFile"
    }
    
    # Check required variables
    $requiredVars = @("DB_PASSWORD", "REDIS_PASSWORD", "JWT_SECRET")
    foreach ($var in $requiredVars) {
        if ($envContent -match "$var=.+") {
            $passed += "Required variable present: $var"
        } else {
            $issues += "Missing required variable: $var"
        }
    }
} else {
    $issues += "Missing environment file: $envFile"
}

# Check Docker files
Write-Host "Checking Docker configuration..." -ForegroundColor Blue
$dockerFile = "docker/docker-compose.enterprise.yml"
if (Test-Path $dockerFile) {
    $dockerContent = Get-Content $dockerFile -Raw
    
    # Check for debug ports
    if ($dockerContent -match '"8001:8001"') {
        $issues += "Debug port exposed in $dockerFile"
    } else {
        $passed += "No debug ports in $dockerFile"
    }
    
    # Check for hardcoded passwords
    if ($dockerContent -match "scorpius123") {
        $issues += "Hardcoded passwords in $dockerFile"
    } else {
        $passed += "No hardcoded passwords in $dockerFile"
    }
} else {
    $issues += "Missing Docker compose file: $dockerFile"
}

# Check security file
$securityFile = "docker/docker-compose.security.yml"
if (Test-Path $securityFile) {
    $passed += "Security hardening file exists"
} else {
    $warnings += "Missing security hardening file"
}

# Results
Write-Host "`nSECURITY VALIDATION RESULTS:" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

if ($issues.Count -gt 0) {
    Write-Host "`n❌ CRITICAL ISSUES:" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "   • $issue" -ForegroundColor Red
    }
}

if ($warnings.Count -gt 0) {
    Write-Host "`n⚠️  WARNINGS:" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "   • $warning" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ PASSED CHECKS:" -ForegroundColor Green
foreach ($check in $passed) {
    Write-Host "   • $check" -ForegroundColor Green
}

$total = $issues.Count + $warnings.Count + $passed.Count
$score = if ($total -gt 0) { [math]::Round(($passed.Count / $total) * 100, 1) } else { 0 }

Write-Host "`nSECURITY SCORE: $score%" -ForegroundColor $(if ($score -ge 90) { "Green" } elseif ($score -ge 70) { "Yellow" } else { "Red" })

if ($issues.Count -eq 0) {
    Write-Host "✅ READY FOR PRODUCTION DEPLOYMENT" -ForegroundColor Green
} else {
    Write-Host "❌ RESOLVE CRITICAL ISSUES BEFORE PRODUCTION" -ForegroundColor Red
}

# Scorpius Enterprise Cleanup Script (PowerShell)
# This script performs the actual cleanup operations

Write-Host "🚀 Scorpius Enterprise Project Cleanup" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Create enterprise directory structure
Write-Host "`n🏗️  Creating enterprise directory structure..." -ForegroundColor Yellow

$enterpriseDirs = @(
    "docs/enterprise",
    "docs/api", 
    "docs/deployment",
    "docs/security",
    "docs/compliance",
    "config/environments",
    "config/secrets",
    "scripts/deployment",
    "scripts/maintenance", 
    "scripts/security",
    "tools/development",
    "tools/operations",
    "tools/security",
    "artifacts/logs",
    "artifacts/backups",
    "artifacts/reports",
    "artifacts/test-results",
    "monitoring/dashboards",
    "monitoring/alerts",
    "monitoring/logs",
    ".vscode",
    ".github/workflows",
    ".github/ISSUE_TEMPLATE",
    ".github/PULL_REQUEST_TEMPLATE"
)

foreach ($dir in $enterpriseDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✓ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Directory exists: $dir" -ForegroundColor Yellow
    }
}

# Files to remove (legacy/duplicate)
Write-Host "`n📁 Removing legacy/duplicate files..." -ForegroundColor Yellow

$filesToRemove = @(
    "unified_gateway_backup.py",
    "orchestrator_new_backup.py", 
    "README-new.md",
    "README-DOCKER.md",
    "test_high_impact_coverage.py",
    "test_final_coverage_boost_fixed.py",
    "test_final_coverage_boost.py",
    "test_backend_coverage_boost.py",
    "test_backend_coverage.py",
    "enhanced_coverage_tests.py",
    "comprehensive_bytecode_tests.py",
    "final_test_validation.py",
    "final_coverage_analysis.py",
    "coverage_summary.py",
    "setup_tests.py",
    "run_bytecode_tests.py",
    "fix-npm.ps1",
    "start-services.sh",
    "start-services.ps1",
    "start-everything.ps1",
    "start-all.ps1",
    "package-lock.json",
    "requirements-dev.txt",
    "pyproject.toml"
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "✓ Removed: $file" -ForegroundColor Green
    } else {
        Write-Host "⚠️  File not found: $file" -ForegroundColor Yellow
    }
}

# Files to move to appropriate directories
Write-Host "`n📦 Moving files to appropriate directories..." -ForegroundColor Yellow

$filesToMove = @{
    # Test files -> tests/
    "test_runner.py" = "tests/"
    "test_enterprise_command_router.py" = "tests/"
    "test_comprehensive.py" = "tests/"
    "test_backend_functional.py" = "tests/"
    
    # Docker files -> docker/
    "docker-compose.yml" = "docker/"
    "docker-compose.secure.yml" = "docker/"
    "docker-compose.dev.yml" = "docker/"
    
    # Documentation -> docs/
    "COMPLETION_SUMMARY.md" = "docs/"
    "BYTECODE_TESTS_SUMMARY.md" = "docs/"
    "BACKEND_COVERAGE_REPORT.md" = "docs/"
    
    # Configuration -> config/
    "pytest.ini" = "config/"
    ".coveragerc" = "config/"
    
    # IDE/Editor files -> .vscode/
    "Scorpius-Vulnerability-Scanner.code-workspace" = ".vscode/"
}

foreach ($file in $filesToMove.Keys) {
    $destination = $filesToMove[$file]
    if (Test-Path $file) {
        $destPath = Join-Path $destination (Split-Path $file -Leaf)
        Move-Item $file $destPath -Force
        Write-Host "✓ Moved: $file -> $destPath" -ForegroundColor Green
    } else {
        Write-Host "⚠️  File not found: $file" -ForegroundColor Yellow
    }
}

# Organize artifacts
Write-Host "`n📊 Organizing artifacts..." -ForegroundColor Yellow

# Move report files from docs/ to artifacts/reports/ if they exist
$reportFiles = @(
    "COMPLETION_SUMMARY.md",
    "BYTECODE_TESTS_SUMMARY.md",
    "BACKEND_COVERAGE_REPORT.md"
)

foreach ($reportFile in $reportFiles) {
    $src = Join-Path "docs" $reportFile
    $dst = Join-Path "artifacts/reports" $reportFile
    if (Test-Path $src) {
        Move-Item $src $dst -Force
        Write-Host "✓ Moved report: $src -> $dst" -ForegroundColor Green
    }
}

# Move test files to artifacts/test-results/ if they exist
$testFiles = @(
    "test_runner.py",
    "test_enterprise_command_router.py", 
    "test_comprehensive.py",
    "test_backend_functional.py"
)

foreach ($testFile in $testFiles) {
    $src = Join-Path "tests" $testFile
    $dst = Join-Path "artifacts/test-results" $testFile
    if (Test-Path $src) {
        Move-Item $src $dst -Force
        Write-Host "✓ Moved test result: $src -> $dst" -ForegroundColor Green
    }
}

# Create enterprise configuration templates
Write-Host "`n⚙️  Creating enterprise configuration templates..." -ForegroundColor Yellow

# Create environment configuration template
$envConfig = @"
# Environment Configuration Template
# Copy this file to config/environments/ for each environment

[development]
debug = true
log_level = DEBUG
database_url = "postgresql://user:pass@localhost:5432/scorpius_dev"

[staging]
debug = false
log_level = INFO
database_url = "postgresql://user:pass@staging-db:5432/scorpius_staging"

[production]
debug = false
log_level = WARNING
database_url = "postgresql://user:pass@prod-db:5432/scorpius_prod"
"@

Set-Content -Path "config/environments/config.template.toml" -Value $envConfig
Write-Host "✓ Created: config/environments/config.template.toml" -ForegroundColor Green

# Create secrets template
$secretsTemplate = @"
# Secrets Configuration Template
# Copy this file to config/secrets/ and update with actual values
# NEVER commit actual secrets to version control

[database]
username = "your_db_username"
password = "your_db_password"

[api_keys]
openai_api_key = "your_openai_key"
etherscan_api_key = "your_etherscan_key"

[security]
jwt_secret = "your_jwt_secret"
encryption_key = "your_encryption_key"
"@

Set-Content -Path "config/secrets/secrets.template.toml" -Value $secretsTemplate
Write-Host "✓ Created: config/secrets/secrets.template.toml" -ForegroundColor Green

# Create .gitignore for secrets
$secretsGitignore = @"
# Ignore actual secret files
*.toml
!*.template.toml
.env
*.key
*.pem
*.p12
"@

Set-Content -Path "config/secrets/.gitignore" -Value $secretsGitignore
Write-Host "✓ Created: config/secrets/.gitignore" -ForegroundColor Green

# Create enterprise README
$enterpriseReadme = @"
# Scorpius Enterprise

## Overview
This is the enterprise-ready version of the Scorpius project, featuring:
* Microservices architecture
* Comprehensive monitoring and observability
* Security-first design
* Compliance-ready documentation
* Scalable deployment strategies

## Quick Start

### Prerequisites
* Docker and Docker Compose
* Python 3.9+
* Node.js 16+
* Kubernetes cluster (for production)

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd Scorpius-Enterprise-master

# Install dependencies
pip install -r config/requirements-dev.txt

# Start development environment
docker-compose -f docker/docker-compose.dev.yml up -d

# Run tests
pytest tests/

# Start the application
python scripts/start.py
```

### Production Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/

# Or use Helm
helm install scorpius deploy/helm/
```

## Documentation
* [Architecture](docs/architecture/)
* [API Reference](docs/api/)
* [Deployment Guide](docs/deployment/)
* [Security](docs/security/)
* [Compliance](docs/compliance/)

## Support
For enterprise support, contact: enterprise-support@scorpius.com
"@

Set-Content -Path "README-ENTERPRISE.md" -Value $enterpriseReadme
Write-Host "✓ Created: README-ENTERPRISE.md" -ForegroundColor Green

Write-Host "`n🎉 Cleanup completed successfully!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Review the new structure" -ForegroundColor White
Write-Host "2. Update any hardcoded paths in your code" -ForegroundColor White
Write-Host "3. Update documentation references" -ForegroundColor White
Write-Host "4. Test the build and deployment processes" -ForegroundColor White
Write-Host "5. Update CI/CD pipelines to reflect new paths" -ForegroundColor White 
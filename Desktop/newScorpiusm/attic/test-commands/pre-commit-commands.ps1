# Pre-commit Hook Commands
# These are the main commands for running pre-commit hooks

Write-Host "=== PRE-COMMIT COMMANDS ===" -ForegroundColor Green

# Install pre-commit hooks (run once)
Write-Host "`n1. Installing pre-commit hooks..." -ForegroundColor Yellow
pre-commit install

# Run all pre-commit hooks on all files
Write-Host "`n2. Running all pre-commit hooks on all files..." -ForegroundColor Yellow
pre-commit run --all-files

# Run pre-commit hooks only on staged files (normal usage)
Write-Host "`n3. Running pre-commit hooks on staged files..." -ForegroundColor Yellow
pre-commit run

# Run specific hooks only
Write-Host "`n4. Running specific hooks..." -ForegroundColor Yellow

# Ruff linting only
Write-Host "   - Ruff linting..." -ForegroundColor Cyan
pre-commit run ruff --all-files

# Black formatting only
Write-Host "   - Black formatting..." -ForegroundColor Cyan
pre-commit run black --all-files

# isort import sorting only
Write-Host "   - isort import sorting..." -ForegroundColor Cyan
pre-commit run isort --all-files

# ESLint for JavaScript/TypeScript
Write-Host "   - ESLint..." -ForegroundColor Cyan
pre-commit run eslint --all-files

# Prettier for frontend files
Write-Host "   - Prettier..." -ForegroundColor Cyan
pre-commit run prettier --all-files

# YAML validation
Write-Host "   - YAML validation..." -ForegroundColor Cyan
pre-commit run check-yaml --all-files

# Update pre-commit hooks to latest versions
Write-Host "`n5. Updating pre-commit hooks..." -ForegroundColor Yellow
pre-commit autoupdate

# Clean pre-commit cache (if having issues)
Write-Host "`n6. Cleaning pre-commit cache..." -ForegroundColor Yellow
pre-commit clean

# Skip specific hooks (example)
Write-Host "`n7. Skipping specific hooks (example)..." -ForegroundColor Yellow
Write-Host "   SKIP=ruff pre-commit run --all-files" -ForegroundColor Gray

# Expected successful output:
Write-Host "`n=== EXPECTED SUCCESSFUL OUTPUT ===" -ForegroundColor Green
Write-Host "check yaml...............................................................Passed
check for added large files..............................................Passed
ruff.....................................................................Passed
black....................................................................Passed
isort....................................................................Passed
eslint...................................................................Passed
prettier.................................................................Passed" -ForegroundColor Gray

Write-Host "`n=== TROUBLESHOOTING ===" -ForegroundColor Red
Write-Host "If hooks fail:"
Write-Host "1. Check specific error messages above"
Write-Host "2. Run individual hook commands to isolate issues"
Write-Host "3. Use --verbose flag for more details: pre-commit run --verbose --all-files"
Write-Host "4. Check .pre-commit-config.yaml for configuration issues"

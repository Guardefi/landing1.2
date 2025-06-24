# Linting and Code Quality Commands
# These commands check code quality, formatting, and standards compliance

Write-Host "=== LINTING AND CODE QUALITY COMMANDS ===" -ForegroundColor Green

# Python Linting with Ruff
Write-Host "`n1. Python Linting with Ruff..." -ForegroundColor Yellow

# Check all Python files for lint errors
Write-Host "   - Check all files..." -ForegroundColor Cyan
ruff check .

# Check with auto-fix (safe fixes only)
Write-Host "   - Auto-fix safe issues..." -ForegroundColor Cyan
ruff check . --fix

# Check with unsafe fixes (more aggressive)
Write-Host "   - Auto-fix including unsafe..." -ForegroundColor Cyan
ruff check . --fix --unsafe-fixes

# Check specific error types only
Write-Host "`n2. Check specific error types..." -ForegroundColor Yellow

# Undefined names (critical errors)
Write-Host "   - Undefined names (F821)..." -ForegroundColor Cyan
ruff check . --select F821

# Import errors
Write-Host "   - Import errors (F401, F811)..." -ForegroundColor Cyan
ruff check . --select F401,F811

# Syntax errors
Write-Host "   - Syntax errors (E999)..." -ForegroundColor Cyan
ruff check . --select E999

# Line length issues
Write-Host "   - Line length (E501)..." -ForegroundColor Cyan
ruff check . --select E501

# Security issues
Write-Host "   - Security issues (S)..." -ForegroundColor Cyan
ruff check . --select S

# Python Code Formatting
Write-Host "`n3. Python Code Formatting..." -ForegroundColor Yellow

# Black formatting
Write-Host "   - Black formatting..." -ForegroundColor Cyan
black --check .
Write-Host "   - Apply Black formatting..." -ForegroundColor Cyan
black .

# isort import sorting
Write-Host "   - Check import sorting..." -ForegroundColor Cyan
isort --check-only .
Write-Host "   - Apply import sorting..." -ForegroundColor Cyan
isort .

# JavaScript/TypeScript Linting
Write-Host "`n4. JavaScript/TypeScript Linting..." -ForegroundColor Yellow

# ESLint check
Write-Host "   - ESLint check..." -ForegroundColor Cyan
npx eslint . --ext .js,.ts,.vue

# ESLint auto-fix
Write-Host "   - ESLint auto-fix..." -ForegroundColor Cyan
npx eslint . --ext .js,.ts,.vue --fix

# Prettier formatting
Write-Host "   - Prettier check..." -ForegroundColor Cyan
npx prettier --check .

# Prettier format
Write-Host "   - Prettier format..." -ForegroundColor Cyan
npx prettier --write .

# Configuration File Validation
Write-Host "`n5. Configuration File Validation..." -ForegroundColor Yellow

# YAML files
Write-Host "   - YAML validation..." -ForegroundColor Cyan
# Note: check-yaml is usually run via pre-commit
# For manual check: python -c "import yaml; yaml.safe_load(open('file.yaml'))"

# JSON files
Write-Host "   - JSON validation..." -ForegroundColor Cyan
# For manual check: python -c "import json; json.load(open('file.json'))"

# Docker files
Write-Host "   - Dockerfile linting..." -ForegroundColor Cyan
# hadolint Dockerfile (if hadolint is installed)

# Advanced Ruff Commands
Write-Host "`n6. Advanced Ruff Commands..." -ForegroundColor Yellow

# Show Ruff configuration
Write-Host "   - Show Ruff config..." -ForegroundColor Cyan
ruff config

# Format code with Ruff (alternative to Black)
Write-Host "   - Ruff format..." -ForegroundColor Cyan
ruff format .

# Check Ruff format
Write-Host "   - Check Ruff format..." -ForegroundColor Cyan
ruff format --check .

# Explain specific error codes
Write-Host "   - Explain error codes..." -ForegroundColor Cyan
Write-Host "     ruff rule F821  # Explain F821 error" -ForegroundColor Gray

# Generate Ruff configuration
Write-Host "   - Generate config..." -ForegroundColor Cyan
Write-Host "     ruff config --generate > ruff.toml" -ForegroundColor Gray

# Expected outputs
Write-Host "`n=== EXPECTED SUCCESSFUL OUTPUT ===" -ForegroundColor Green
Write-Host "Ruff: All checks passed. Found 0 errors.
Black: would reformat 0 files
isort: Skipped 0 files
ESLint: No issues found
Prettier: All matched files use Prettier code style!" -ForegroundColor Gray

Write-Host "`n=== COMMON ERROR PATTERNS ===" -ForegroundColor Red
Write-Host "F821: Undefined name 'variable_name'
F401: 'module' imported but unused
E501: Line too long (> 88 characters)
E999: SyntaxError: invalid syntax
F811: Redefinition of unused 'name'" -ForegroundColor Gray

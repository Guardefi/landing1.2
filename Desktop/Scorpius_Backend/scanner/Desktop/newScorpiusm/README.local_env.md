# Local Environment Setup Guide

This guide explains how to set up your local development environment for the Scorpius DeFi Security Platform.

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ with npm
- Python 3.11+
- Git

## Environment Variables Setup

### Option 1: Using Doppler (Recommended for Teams)

1. **Install Doppler CLI**:

   ```bash
   # macOS
   brew install dopplerhq/cli/doppler

   # Linux
   curl -Ls https://cli.doppler.com/install.sh | sh

   # Windows
   scoop install doppler
   ```

2. **Authenticate with Doppler**:

   ```bash
   doppler login
   ```

3. **Setup project secrets**:

   ```bash
   doppler setup --project scorpius --config dev
   ```

4. **Run applications with Doppler**:
   ```bash
   doppler run -- just dev
   ```

### Option 2: Using direnv (Local Development)

1. **Install direnv**:

   ```bash
   # macOS
   brew install direnv

   # Linux
   sudo apt install direnv
   ```

2. **Add direnv to your shell** (add to ~/.bashrc or ~/.zshrc):

   ```bash
   eval "$(direnv hook bash)"  # for bash
   eval "$(direnv hook zsh)"   # for zsh
   ```

3. **Create .envrc file**:
   ```bash
   cp .envrc.example .envrc
   direnv allow
   ```

### Option 3: Manual .env Files

1. **Copy example files**:

   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   cp .env.example .env
   ```

2. **Edit the files** with your values (see sections below).

## Required Environment Variables

### Backend (.env or backend/.env)

```bash
# Database Configuration
DATABASE_URL="postgresql://scorpius:dev_password@localhost:5432/scorpius_dev"
REDIS_URL="redis://localhost:6379/0"

# Security Keys (generate with: openssl rand -hex 32)
SECRET_KEY="${SECRET_KEY}"
JWT_SECRET_KEY="${JWT_SECRET_KEY}"
ENCRYPTION_KEY="${ENCRYPTION_KEY}"

# External APIs (optional for development)
OPENAI_API_KEY="${OPENAI_API_KEY}"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
COINGECKO_API_KEY="${COINGECKO_API_KEY}"

# Blockchain RPC URLs
ETHEREUM_RPC_URL="${ETHEREUM_RPC_URL}"
POLYGON_RPC_URL="${POLYGON_RPC_URL}"
BSC_RPC_URL="${BSC_RPC_URL}"
ARBITRUM_RPC_URL="${ARBITRUM_RPC_URL}"

# Development Settings
DEBUG="true"
LOG_LEVEL="DEBUG"
ENVIRONMENT="development"

# Email Configuration (for notifications)
SMTP_HOST="${SMTP_HOST}"
SMTP_PORT="587"
SMTP_USER="${SMTP_USER}"
SMTP_PASSWORD="${SMTP_PASSWORD}"

# Monitoring (optional)
SENTRY_DSN="${SENTRY_DSN}"
```

### Frontend (.env or frontend/.env)

```bash
# API Configuration
VITE_API_BASE_URL="http://localhost:8000"
VITE_WS_URL="ws://localhost:8000/ws"

# Feature Flags
VITE_ENABLE_AI_FEATURES="true"
VITE_ENABLE_QUANTUM_FEATURES="false"
VITE_ENABLE_MEV_PROTECTION="true"

# External Services
VITE_SENTRY_DSN="${VITE_SENTRY_DSN}"
VITE_ANALYTICS_ID="${VITE_ANALYTICS_ID}"

# Development Settings
VITE_DEBUG="true"
VITE_LOG_LEVEL="debug"
```

### Root Environment (.env)

```bash
# Docker Compose Settings
COMPOSE_PROJECT_NAME="scorpius"
POSTGRES_PASSWORD="dev_password"
REDIS_PASSWORD=""

# Development Ports
FRONTEND_PORT="8080"
BACKEND_PORT="8000"
POSTGRES_PORT="5432"
REDIS_PORT="6379"
GRAFANA_PORT="3000"
PROMETHEUS_PORT="9090"
```

## Secret Generation

### Generate Secure Keys

```bash
# Generate random secrets
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export ENCRYPTION_KEY=$(openssl rand -hex 32)

echo "SECRET_KEY=$SECRET_KEY"
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY"
```

### API Keys Setup

1. **OpenAI API Key** (optional):
   - Visit: https://platform.openai.com/api-keys
   - Create new key starting with `sk-`

2. **Anthropic API Key** (optional):
   - Visit: https://console.anthropic.com/
   - Create new key starting with `sk-ant-`

3. **CoinGecko API Key** (optional):
   - Visit: https://www.coingecko.com/en/api
   - Create new key starting with `CG-`

4. **Blockchain RPC URLs**:
   - **Infura**: https://infura.io/
   - **Alchemy**: https://www.alchemy.com/
   - **QuickNode**: https://www.quicknode.com/

## Development Commands

### With Just (Task Runner)

```bash
# Start full development environment
just dev

# Run tests
just test

# Lint code
just lint

# Reset database
just reset-db

# View logs
just logs
```

### With Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Reset everything
docker-compose down -v && docker-compose up -d
```

### With npm/Python directly

```bash
# Frontend development
cd frontend
npm install
npm run dev

# Backend development
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:

   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres

   # Reset database
   just reset-db
   ```

2. **Redis Connection Errors**:

   ```bash
   # Check if Redis is running
   docker-compose ps redis

   # Clear Redis cache
   docker-compose exec redis redis-cli FLUSHALL
   ```

3. **Frontend Build Errors**:

   ```bash
   # Clear node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Backend Import Errors**:

   ```bash
   # Reinstall Python dependencies
   pip install -r requirements.txt

   # Check Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
   ```

### Logs and Debugging

```bash
# View all service logs
just logs

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Enable debug mode
export DEBUG="true"
export LOG_LEVEL="DEBUG"
```

### Performance Issues

1. **Slow startup**:
   - Ensure Docker has enough resources (8GB+ RAM)
   - Use Docker BuildKit: `export DOCKER_BUILDKIT=1`

2. **High CPU usage**:
   - Limit concurrent workers in development
   - Use `just dev --minimal` for lighter setup

## Security Notes

### Development Security

- **Never commit real API keys** to Git
- **Use placeholders** in documentation
- **Rotate keys regularly** in development
- **Use HTTPS** even in development for external APIs

### Environment Isolation

```bash
# Development
export ENVIRONMENT="development"

# Testing
export ENVIRONMENT="testing"

# Staging
export ENVIRONMENT="staging"
```

## IDE Configuration

### VS Code

1. **Install recommended extensions**:
   - Python
   - TypeScript
   - Docker
   - GitLens

2. **Workspace settings** (`.vscode/settings.json`):
   ```json
   {
     "python.defaultInterpreterPath": "./backend/.venv/bin/python",
     "typescript.preferences.importModuleSpecifier": "relative",
     "docker.enableDockerComposeLanguageService": true
   }
   ```

### PyCharm

1. **Configure Python interpreter**:
   - File → Settings → Project → Python Interpreter
   - Add interpreter from `./backend/.venv/`

2. **Configure Docker Compose**:
   - Services → Docker → Docker Compose
   - Add `docker-compose.yml`

## Quick Verification

After setup, verify everything works:

```bash
# 1. Start services
just dev

# 2. Check health endpoints
curl http://localhost:8000/health    # Backend
curl http://localhost:8080           # Frontend

# 3. Run tests
just test

# 4. Check logs for errors
just logs | grep -i error
```

## Environment Templates

### .envrc (for direnv)

```bash
#!/bin/bash
# Scorpius Development Environment

# Load secrets from external source if available
if command -v doppler &> /dev/null; then
    eval "$(doppler secrets download --no-file --format env)"
else
    # Fallback to local .env file
    if [ -f .env ]; then
        set -a
        source .env
        set +a
    fi
fi

# Development settings
export ENVIRONMENT="development"
export DEBUG="true"
export LOG_LEVEL="DEBUG"

# Add backend to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Development shortcuts
alias dev="just dev"
alias test="just test"
alias lint="just lint"
alias logs="just logs"

echo "🦂 Scorpius development environment loaded"
```

### .env.example

```bash
# Copy this file to .env and fill in your values
# Never commit .env files to Git!

# Required secrets (generate with: openssl rand -hex 32)
SECRET_KEY=
JWT_SECRET_KEY=
ENCRYPTION_KEY=

# External APIs (optional)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
COINGECKO_API_KEY=

# Blockchain RPC URLs
ETHEREUM_RPC_URL=
POLYGON_RPC_URL=
BSC_RPC_URL=
ARBITRUM_RPC_URL=

# Database URLs
DATABASE_URL=postgresql://scorpius:dev_password@localhost:5432/scorpius_dev
REDIS_URL=redis://localhost:6379/0

# Email configuration
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=

# Monitoring (optional)
SENTRY_DSN=
VITE_SENTRY_DSN=
```

---

**Setup Time Target: ≤5 minutes for returning developers, ≤15 minutes for new setup**

For help: Create an issue or contact the development team.

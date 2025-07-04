#!/bin/bash

# Scorpius Enterprise Platform - DevContainer Setup Script
# This script runs after the dev container is created

set -e

echo "🚀 Setting up Scorpius Enterprise Platform development environment..."

# Install project dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
fi

if [ -f "pyproject.toml" ]; then
    pip install -e .
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
if [ -f "frontend/package.json" ]; then
    cd frontend
    npm install
    cd ..
fi

# Set up git hooks
echo "🔧 Setting up git hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    pre-commit install --hook-type commit-msg
fi

# Set up environment files
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Created .env from .env.example"
    fi
fi

if [ ! -f ".env.secure" ]; then
    if [ -f ".env.secure.example" ]; then
        cp .env.secure.example .env.secure
        echo "📝 Created .env.secure from .env.secure.example"
    fi
fi

# Set up database
echo "🗄️  Setting up development database..."
if command -v docker-compose &> /dev/null; then
    if [ -f "docker-compose.dev.yml" ]; then
        echo "Starting database services..."
        docker-compose -f docker-compose.dev.yml up -d postgres redis
        sleep 10
        
        # Run database migrations
        if [ -f "scripts/setup_db.py" ]; then
            python scripts/setup_db.py
        fi
    fi
fi

# Set up Kubernetes development
echo "☸️  Setting up Kubernetes development tools..."
if command -v kubectl &> /dev/null; then
    # Create development namespace
    kubectl create namespace scorpius-dev --dry-run=client -o yaml | kubectl apply -f - || true
    
    # Set up port-forwarding aliases
    echo "Setting up kubectl aliases..."
    echo 'alias kgp="kubectl get pods"' >> ~/.zshrc
    echo 'alias kgs="kubectl get services"' >> ~/.zshrc
    echo 'alias kgd="kubectl get deployments"' >> ~/.zshrc
    echo 'alias kdp="kubectl describe pod"' >> ~/.zshrc
    echo 'alias klf="kubectl logs -f"' >> ~/.zshrc
fi

# Set up monitoring tools
echo "📊 Setting up monitoring tools..."
if [ -f "monitoring/prometheus/prometheus.yml" ]; then
    echo "Prometheus configuration found"
fi

if [ -f "monitoring/grafana/dashboards" ]; then
    echo "Grafana dashboards found"
fi

# Set up development certificates
echo "🔐 Setting up development certificates..."
if [ ! -f "certs/dev-cert.pem" ]; then
    mkdir -p certs
    openssl req -x509 -newkey rsa:4096 -keyout certs/dev-key.pem -out certs/dev-cert.pem -days 365 -nodes -subj "/C=US/ST=CA/L=SF/O=Scorpius/CN=localhost" || echo "OpenSSL not available, skipping cert generation"
fi

# Set up development scripts
echo "📋 Setting up development scripts..."
chmod +x scripts/*.sh 2>/dev/null || echo "No shell scripts found in scripts/"
chmod +x tests/chaos/*.sh 2>/dev/null || echo "No chaos test scripts found"

# Install additional development tools
echo "🛠️  Installing additional development tools..."
pip install --user \
    httpx \
    pytest-xdist \
    pytest-benchmark \
    memory-profiler \
    line-profiler \
    locust \
    bandit \
    safety \
    semgrep || echo "Some tools failed to install, continuing..."

# Set up IDE configuration
echo "💻 Setting up IDE configuration..."
if [ ! -f ".vscode/settings.json" ]; then
    mkdir -p .vscode
    cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "/usr/local/bin/python3",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/node_modules": true
    }
}
EOF
fi

# Set up useful aliases
echo "🔧 Setting up development aliases..."
cat >> ~/.zshrc << EOF

# Scorpius Development Aliases
alias sdev="make dev"
alias stest="make test"
alias slint="make lint"
alias sbuild="make build"
alias sdeploy="make deploy-dev"
alias sclean="make clean"
alias slogs="make logs"
alias sstatus="make status"
alias scost="make cost-analysis"
alias schaos="make chaos-test"

# Docker aliases
alias dps="docker ps"
alias dimg="docker images"
alias dlogs="docker logs -f"
alias dexec="docker exec -it"

# Kubernetes aliases
alias kctx="kubectl config current-context"
alias kns="kubectl config set-context --current --namespace"

# Git aliases
alias gst="git status"
alias gco="git checkout"
alias gcb="git checkout -b"
alias gp="git push"
alias gl="git log --oneline -10"

# Development workflow
alias start-dev="docker-compose -f docker-compose.dev.yml up -d"
alias stop-dev="docker-compose -f docker-compose.dev.yml down"
alias restart-dev="stop-dev && start-dev"
alias dev-shell="docker-compose -f docker-compose.dev.yml exec api-gateway /bin/bash"

EOF

echo "✅ DevContainer setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "  1. Run 'make dev' to start the development environment"
echo "  2. Run 'make test' to run the test suite"
echo "  3. Check 'make help' for all available commands"
echo "  4. Visit http://localhost:8000 for the API Gateway"
echo "  5. Visit http://localhost:3000 for the frontend"
echo ""
echo "📚 Documentation:"
echo "  - Developer Guide: docs/DEVELOPER_GUIDE.md"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - Security Policy: docs/SECURITY_POLICY.md"
echo ""

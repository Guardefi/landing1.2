# Scorpius Reporting Service - Makefile

.PHONY: help install dev test clean build docker-build docker-run lint format security

# Default target
help:
	@echo "Scorpius Reporting Service - Available Commands:"
	@echo ""
	@echo "  install     Install dependencies"
	@echo "  dev         Start development server"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code"
	@echo "  security    Run security checks"
	@echo "  clean       Clean build artifacts"
	@echo "  build       Build application"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run  Run with Docker Compose"
	@echo "  docker-stop Stop Docker Compose"

# Install dependencies
install:
	pip install -r requirements.txt

# Start development server
dev:
	uvicorn app:app --reload --port 8007 --log-level info

# Run tests
test:
	pytest -v

# Run tests with coverage
test-cov:
	pytest --cov=. --cov-report=html --cov-report=term-missing

# Run linting
lint:
	flake8 . --max-line-length=120 --exclude=venv,__pycache__,.pytest_cache
	mypy . --ignore-missing-imports

# Format code
format:
	black . --line-length=120 --exclude="/(venv|__pycache__|\.pytest_cache)/"

# Security checks
security:
	bandit -r . -f json -o security-report.json || true
	safety check

# Clean build artifacts
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

# Build application
build: clean
	python -m build

# Build Docker image
docker-build:
	docker build -t scorpius/reporting:latest .

# Run with Docker Compose
docker-run:
	docker-compose up -d

# Stop Docker Compose
docker-stop:
	docker-compose down

# Initialize development environment
init-dev:
	@echo "Initializing development environment..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file"; fi
	@mkdir -p certs reports/pdf reports/sarif reports/signed templates fonts audit_logs
	@echo "Created directory structure"
	@echo "Run 'make install' to install dependencies"
	@echo "Run 'make dev' to start development server"

# Generate certificates for development
gen-certs:
	@echo "Generating development certificates..."
	@mkdir -p certs
	@openssl genrsa -out certs/signing.key 2048
	@openssl req -new -x509 -key certs/signing.key -out certs/signing.crt -days 365 \
		-subj "/C=US/ST=CA/L=San Francisco/O=Scorpius/CN=Scorpius Reporting Service"
	@echo "Certificates generated in certs/ directory"

# Run full CI pipeline
ci: lint test security
	@echo "CI pipeline completed successfully"

# Database migration (when implemented)
migrate:
	@echo "Running database migrations..."
	# alembic upgrade head

# Seed test data
seed:
	@echo "Seeding test data..."
	python scripts/seed_data.py

# Health check
health:
	@curl -f http://localhost:8007/health || echo "Service not responding"

# Load test
load-test:
	@echo "Running load tests..."
	locust -f tests/load_test.py --host=http://localhost:8007

# Monitoring setup
monitoring:
	@echo "Setting up monitoring..."
	docker-compose -f docker-compose.monitoring.yml up -d

# Backup data
backup:
	@echo "Creating backup..."
	@mkdir -p backup/$(shell date +%Y%m%d)
	@cp -r reports/ backup/$(shell date +%Y%m%d)/
	@cp -r audit_logs/ backup/$(shell date +%Y%m%d)/
	@echo "Backup created in backup/$(shell date +%Y%m%d)/"

# Scorpius Enterprise Platform Makefile

.PHONY: help install install-dev install-enterprise test lint format clean build docker-build docker-run demo status

# Default target
help:
	@echo "Scorpius Enterprise Platform - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install          - Install basic dependencies"
	@echo "  install-dev      - Install development dependencies"
	@echo "  install-enterprise - Install full enterprise stack"
	@echo ""
	@echo "Development:"
	@echo "  test             - Run test suite"
	@echo "  lint             - Run code linting"
	@echo "  format           - Format code with black"
	@echo "  clean            - Clean build artifacts"
	@echo ""
	@echo "Deployment:"
	@echo "  build            - Build distribution packages"
	@echo "  docker-build     - Build Docker image"
	@echo "  docker-run       - Run Docker container"
	@echo "  docker-stack     - Start full Docker stack"
	@echo ""
	@echo "Demonstration:"
	@echo "  demo             - Run enterprise demo"
	@echo "  status           - Check platform status"
	@echo "  cli-help         - Show CLI help"

# Installation targets
install:
	pip install -r requirements.enterprise.txt

install-dev:
	pip install -e .[dev]

install-enterprise:
	pip install -e .[enterprise,quantum,dev]

# Development targets
test:
	pytest tests/ -v --cov=scorpius --cov-report=html

lint:
	flake8 scorpius/ tests/ --max-line-length=88
	mypy scorpius/

format:
	black scorpius/ tests/ demo_enterprise.py
	isort scorpius/ tests/ demo_enterprise.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Build targets
build: clean
	python setup.py sdist bdist_wheel

docker-build:
	docker build -f deployment/Dockerfile.enterprise -t scorpius-enterprise:latest .

docker-run:
	docker run -p 8000:8000 -e SCORPIUS_LOG_LEVEL=INFO scorpius-enterprise:latest

docker-stack:
	cd deployment && docker-compose -f docker-compose.enterprise.yml up -d

docker-stack-down:
	cd deployment && docker-compose -f docker-compose.enterprise.yml down

# Demo and utilities
demo:
	python demo_enterprise.py

status:
	python -c "import asyncio; from scorpius import initialize_scorpius, get_engine; async def check(): await initialize_scorpius(license_key='DEMO'); engine = get_engine(); status = await engine.get_platform_status(); print('Scorpius Status:', status['platform_version'], 'Health:', status['overall_health']); asyncio.run(check())"

cli-help:
	python -m scorpius.cli.main --help

# Configuration
init-config:
	python -c "from scorpius.core.config import ScorpiusConfig; config = ScorpiusConfig(); config.save('my-config.yml'); print('Configuration saved to my-config.yml')"

# Security
security-scan:
	python -c "import asyncio; from scorpius import initialize_scorpius, get_engine; async def scan(): await initialize_scorpius(license_key='DEMO'); engine = get_engine(); result = await engine.security_scan('test-target'); print('Scan result:', result); asyncio.run(scan())"

# Quantum operations
quantum-encrypt:
	python -c "import asyncio; from scorpius import initialize_scorpius, get_engine; async def encrypt(): await initialize_scorpius(license_key='DEMO'); engine = get_engine(); result = await engine.quantum_encrypt(b'Secret message'); print('Encryption result:', result); asyncio.run(encrypt())"

# Enterprise operations
enterprise-report:
	python -c "import asyncio; from scorpius import initialize_scorpius, get_engine; async def report(): await initialize_scorpius(license_key='DEMO'); engine = get_engine(); result = await engine.generate_analytics_report('security', '24h'); print('Analytics report:', result); asyncio.run(report())"

# Documentation
docs:
	@echo "Enterprise Documentation:"
	@echo "  README.md        - Main documentation"
	@echo "  config/          - Configuration examples"
	@echo "  deployment/      - Deployment configurations"
	@echo "  tests/           - Test suite and examples"

# Quick start
quickstart: install-enterprise demo
	@echo ""
	@echo "🎉 Scorpius Enterprise Platform is ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  make status      - Check platform status"
	@echo "  make cli-help    - Explore CLI commands"
	@echo "  make docker-stack - Start full enterprise stack"

# Scorpius Enterprise Platform Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help install dev test lint format clean build deploy health docker-build docker-up docker-down

# Default target
help:
	@echo "Scorpius Enterprise Platform - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install          Install all dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  dev              Start development environment"
	@echo "  dev-core         Start core services only"
	@echo "  dev-api          Start API gateway only"
	@echo "  dev-scanner      Start scanner service"
	@echo "  dev-bridge       Start bridge service"
	@echo ""
	@echo "Code Quality:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  lint             Run linting checks"
	@echo "  format           Format code with black and isort"
	@echo "  type-check       Run type checking with mypy"
	@echo ""
	@echo "Docker Operations:"
	@echo "  docker-build     Build all Docker images"
	@echo "  docker-up        Start all services with Docker Compose"
	@echo "  docker-down      Stop all Docker services"
	@echo "  docker-logs      View Docker logs"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy-dev       Deploy to development environment"
	@echo "  deploy-staging   Deploy to staging environment"
	@echo "  deploy-prod      Deploy to production environment"
	@echo ""
	@echo "Utilities:"
	@echo "  health           Check health of all services"
	@echo "  clean            Clean build artifacts and cache"
	@echo "  backup           Backup database and configurations"
	@echo "  logs             View application logs"
	@echo "  chaos-test       Run chaos engineering tests with Litmus"

# Installation targets
install:
	pip install -r config/requirements-dev.txt

install-dev:
	pip install -r config/requirements-dev.txt
	pre-commit install

# Development targets
dev:
	python scripts/start.py --environment development

dev-core:
	docker-compose -f docker/docker-compose.dev.yml --profile infrastructure --profile core up -d

dev-api:
	docker-compose -f docker/docker-compose.dev.yml --profile infrastructure --profile core --profile gateway up -d

dev-scanner:
	docker-compose -f docker/docker-compose.dev.yml --profile infrastructure --profile scanner up -d

dev-bridge:
	docker-compose -f docker/docker-compose.dev.yml --profile infrastructure --profile bridge up -d

dev-full:
	docker-compose -f docker/docker-compose.dev.yml --profile full up -d

# Testing targets
	test:
		@pip show pytest-cov > /dev/null 2>&1 || pip install pytest-cov
	pytest tests/ -v --cov=backend --cov=packages --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

# Code quality targets
lint:
	flake8 backend/ packages/ scripts/ tests/
	black --check backend/ packages/ scripts/ tests/
	isort --check-only backend/ packages/ scripts/ tests/

format:
	black backend/ packages/ scripts/ tests/
	isort backend/ packages/ scripts/ tests/

type-check:
	mypy backend/ packages/ scripts/

# Docker targets
docker-build:
	docker-compose -f docker/docker-compose.yml build

docker-up:
	docker-compose -f docker/docker-compose.yml --profile full up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	docker-compose -f docker/docker-compose.yml logs -f

docker-clean:
	docker-compose -f docker/docker-compose.yml down -v --remove-orphans
	docker system prune -f

# Kubernetes targets
k8s-dev:
	skaffold dev --profile development

k8s-deploy-staging:
	skaffold run --profile staging

k8s-deploy-prod:
	skaffold run --profile production

# Deployment targets
deploy-dev: docker-build
	ENVIRONMENT=development docker-compose -f docker/docker-compose.yml --profile full up -d

deploy-staging: docker-build
	skaffold run --profile staging

deploy-prod: docker-build
	skaffold run --profile production

# Utility targets
health:
	python scripts/start.py --health-check

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

backup:
	@echo "Creating backup of database and configurations..."
	mkdir -p artifacts/backups/$(shell date +%Y%m%d_%H%M%S)
	docker exec postgres pg_dump -U scorpius scorpius > artifacts/backups/$(shell date +%Y%m%d_%H%M%S)/database.sql
	cp -r config/ artifacts/backups/$(shell date +%Y%m%d_%H%M%S)/
	@echo "Backup completed in artifacts/backups/$(shell date +%Y%m%d_%H%M%S)/"

logs:
	tail -f artifacts/logs/scorpius-startup.log

logs-api:
	docker-compose -f docker/docker-compose.yml logs -f api-gateway

logs-scanner:
	docker-compose -f docker/docker-compose.yml logs -f scanner

logs-bridge:
	docker-compose -f docker/docker-compose.yml logs -f bridge

# Database management
db-migrate:
	alembic upgrade head

db-rollback:
	alembic downgrade -1

db-reset:
	docker-compose -f docker/docker-compose.yml down postgres
	docker volume rm enterprise-platform_postgres_data
	docker-compose -f docker/docker-compose.yml up -d postgres
	sleep 5
	alembic upgrade head

# Monitoring targets
metrics:
	curl -s http://localhost:9090/metrics | head -20

status:
	@echo "Service Status:"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "API Gateway: Down"
	@curl -s http://localhost:8001/health | python -m json.tool || echo "Scanner: Down"
	@curl -s http://localhost:8002/health | python -m json.tool || echo "Bridge: Down"

# Security targets
security-scan:
	safety check
	bandit -r backend/ packages/ scripts/

# Documentation targets
docs-build:
	mkdocs build

docs-serve:
	mkdocs serve

docs-deploy:
	mkdocs gh-deploy

# Release targets
release-patch:
	bump2version patch

release-minor:
	bump2version minor

release-major:
	bump2version major

# Environment-specific shortcuts
local: dev-full

staging: deploy-staging

production: deploy-prod

# Integration targets
integration: ## Run full integration setup
	@echo "Running integration setup..."
	python scripts/integration_setup.py --environment development

integration-staging: ## Run integration setup for staging
	python scripts/integration_setup.py --environment staging

integration-production: ## Run integration setup for production
	python scripts/integration_setup.py --environment production

# Infrastructure targets
infra-init: ## Initialize Terraform infrastructure
	cd infrastructure/terraform && terraform init

infra-plan: ## Plan Terraform infrastructure
	cd infrastructure/terraform && terraform plan

infra-apply: ## Apply Terraform infrastructure
	cd infrastructure/terraform && terraform apply

infra-destroy: ## Destroy Terraform infrastructure
	cd infrastructure/terraform && terraform destroy

# Database targets
db-migrate: ## Run database migrations
	python scripts/migrate.py --environment development

db-migrate-staging: ## Run database migrations for staging
	python scripts/migrate.py --environment staging

db-migrate-prod: ## Run database migrations for production
	python scripts/migrate.py --environment production

db-reset: ## Reset development database
	python scripts/reset_db.py --environment development

# Security targets
security-scan: ## Run security scans
	bandit -r backend/ packages/ scripts/ -f json -o artifacts/reports/bandit-report.json
	safety check --json --output artifacts/reports/safety-report.json
	trivy fs . --format json --output artifacts/reports/trivy-report.json

# Plugin targets
plugin-list: ## List available plugins
	python scripts/plugin_manager.py list

plugin-install: ## Install a plugin (usage: make plugin-install PLUGIN=name)
	python scripts/plugin_manager.py install $(PLUGIN)

plugin-remove: ## Remove a plugin (usage: make plugin-remove PLUGIN=name)
	python scripts/plugin_manager.py remove $(PLUGIN)

# Documentation targets
docs: ## Generate documentation
	@echo "Generating documentation..."
	python scripts/generate_docs.py

docs-serve: ## Serve documentation locally
	cd docs && python -m http.server 8080

docs-deploy: ## Deploy documentation
	mkdocs gh-deploy

# Backup targets
backup: ## Create backup
	python scripts/backup.py --environment development

backup-restore: ## Restore from backup (usage: make backup-restore BACKUP=path)
	python scripts/backup.py --restore $(BACKUP)

# Health and status targets
health: ## Check system health
	python scripts/health_check.py --environment development

status: ## Show system status
	@echo "System Status:"
	@echo "=============="
	docker-compose -f docker/docker-compose.dev.yml ps
	@echo ""
	@echo "Services Health:"
	@curl -s http://localhost:8000/healthz | jq . || echo "API Gateway not available"

# Load testing targets
load-test: ## Run load tests
	cd tests/performance && locust -f locustfile.py --headless --users 100 --spawn-rate 10 --run-time 5m --host http://localhost:8000

stress-test: ## Run stress tests
	cd tests/performance && locust -f locustfile.py --headless --users 500 --spawn-rate 50 --run-time 10m --host http://localhost:8000

# Cleanup targets
clean: ## Clean up development environment
	@echo "Cleaning up..."
	docker-compose -f docker/docker-compose.dev.yml down -v
	docker system prune -f
	rm -rf __pycache__ .pytest_cache .coverage htmlcov/
	rm -f *.log *.json

chaos-test: ## Run chaos engineering tests
	@echo "Running chaos engineering tests..."
	@echo "1. Starting Litmus workflow..."
	kubectl apply -f tests/chaos/litmus-workflow.yaml
	@echo "2. Running disaster recovery drill..."
	bash tests/chaos/disaster-drill-enhanced.sh
	@echo "3. Validating resilience..."
	make verify-resilience

chaos-pod-delete: ## Run pod deletion chaos test
	kubectl apply -f tests/chaos/pod-delete.yaml
	@echo "Pod deletion chaos test started"

chaos-network: ## Run network chaos test
	kubectl apply -f tests/chaos/network-latency.yaml
	@echo "Network latency chaos test started"

chaos-rds: ## Run RDS failover test
	kubectl apply -f tests/chaos/aws-rds-failover.yaml
	@echo "RDS failover chaos test started"

disaster-drill: ## Run comprehensive disaster recovery drill
	bash tests/chaos/disaster-drill-enhanced.sh

verify-resilience: ## Verify system resilience after chaos tests
	@echo "Verifying system resilience..."
	@curl -f http://localhost:8000/healthz || (echo "Health check failed" && exit 1)
	@echo "✅ System resilience verified"

# Cost optimization targets
cost-analysis: ## Run cost analysis and optimization
	@echo "Running cost analysis..."
	python packages/core/src/cost_optimizer.py

cost-optimize: ## Apply cost optimization recommendations
	@echo "Applying cost optimization recommendations..."
	python scripts/apply_cost_optimizations.py

cost-alerts: ## Check cost alerts and budgets
	@echo "Checking cost alerts..."
	kubectl get prometheusrules -n monitoring | grep cost

cost-dashboard: ## Open cost monitoring dashboard
	@echo "Opening cost dashboard..."
	@echo "Grafana: http://localhost:3001/d/cost-overview"
	@echo "OpenCost: http://localhost:9003"

check-cost: ## Check current costs
	@echo "Current cost analysis:"
	@if command -v curl >/dev/null 2>&1; then \
		curl -s "http://localhost:9003/model/allocation?window=1d" | jq '.data[0].totalCost // "N/A"' || echo "OpenCost not available"; \
	else \
		echo "curl not available"; \
	fi

# Developer experience targets
dev-setup: ## Set up complete development environment
	@echo "Setting up development environment..."
	@if [ -f ".devcontainer/scripts/setup.sh" ]; then \
		bash .devcontainer/scripts/setup.sh; \
	else \
		echo "DevContainer setup script not found"; \
	fi

dev-start: ## Start development environment
	@echo "Starting development environment..."
	@if [ -f ".devcontainer/scripts/start.sh" ]; then \
		bash .devcontainer/scripts/start.sh; \
	else \
		docker-compose -f docker/docker-compose.dev.yml up -d; \
	fi

dev-stop: ## Stop development environment
	@echo "Stopping development environment..."
	docker-compose -f docker/docker-compose.dev.yml down

dev-reset: ## Reset development environment
	@echo "Resetting development environment..."
	docker-compose -f docker/docker-compose.dev.yml down -v
	docker system prune -f
	make dev-setup

dev-shell: ## Open development shell
	docker-compose -f docker/docker-compose.dev.yml exec api-gateway /bin/bash

dev-logs: ## Show development logs
	docker-compose -f docker/docker-compose.dev.yml logs -f

dev-status: ## Show development environment status
	@echo "Development Environment Status:"
	@echo "================================"
	@docker-compose -f docker/docker-compose.dev.yml ps
	@echo ""
	@echo "Health Checks:"
	@curl -s http://localhost:8000/healthz | jq . || echo "API Gateway not available"

# Security and compliance targets
security-scan-all: ## Run comprehensive security scans
	@echo "Running comprehensive security scans..."
	make security-test
	make dependency-check
	make container-scan
	make secrets-scan

dependency-check: ## Check for vulnerable dependencies
	@echo "Checking dependencies for vulnerabilities..."
	safety check || echo "Safety check completed with warnings"
	npm audit --audit-level=moderate || echo "NPM audit completed with warnings"

container-scan: ## Scan container images for vulnerabilities
	@echo "Scanning container images..."
	trivy image --severity HIGH,CRITICAL scorpius/api-gateway:latest || echo "Trivy scan completed"

secrets-scan: ## Scan for hardcoded secrets
	@echo "Scanning for secrets..."
	docker run --rm -v "$(PWD):/app" trufflesecurity/trufflehog:latest filesystem /app || echo "Secrets scan completed"

compliance-check: ## Run compliance checks
	@echo "Running compliance checks..."
	python scripts/compliance_checker.py

# Monitoring and observability targets
monitor-setup: ## Set up monitoring stack
	@echo "Setting up monitoring stack..."
	helm upgrade --install prometheus monitoring/helm/prometheus --namespace monitoring --create-namespace
	helm upgrade --install grafana monitoring/helm/grafana --namespace monitoring
	helm upgrade --install opencost infrastructure/helm/opencost --namespace opencost --create-namespace

monitor-status: ## Check monitoring stack status
	@echo "Monitoring Stack Status:"
	@echo "========================"
	kubectl get pods -n monitoring
	kubectl get pods -n opencost

check-metrics: ## Check if metrics are being collected
	@echo "Checking metrics collection..."
	@curl -s "http://localhost:9090/api/v1/query?query=up" | jq '.data.result | length' || echo "Prometheus not available"

check-alerts: ## Check active alerts
	@echo "Active alerts:"
	@curl -s "http://localhost:9090/api/v1/alerts" | jq '.data.alerts[] | select(.state=="firing") | .labels.alertname' || echo "Prometheus not available"

# Performance testing targets
perf-test: ## Run performance tests
	@echo "Running performance tests..."
	cd tests/performance && locust -f locustfile.py --headless --users 100 --spawn-rate 10 --run-time 5m --host http://localhost:8000

stress-test: ## Run stress tests
	cd tests/performance && locust -f locustfile.py --headless --users 500 --spawn-rate 50 --run-time 10m --host http://localhost:8000

benchmark: ## Run benchmark tests
	@echo "Running benchmark tests..."
	python -m pytest tests/benchmarks/ --benchmark-only

# Utility targets
check-health: ## Check overall system health
	@echo "System Health Check:"
	@echo "==================="
	@echo "API Gateway:" && curl -sf http://localhost:8000/healthz | jq '.status' || echo "❌ Down"
	@echo "Frontend:" && curl -sf http://localhost:3000 >/dev/null && echo "✅ Up" || echo "❌ Down"
	@echo "Prometheus:" && curl -sf http://localhost:9090/-/healthy >/dev/null && echo "✅ Up" || echo "❌ Down"
	@echo "Grafana:" && curl -sf http://localhost:3001/api/health | jq '.database' || echo "❌ Down"

verify-all: ## Run all verification checks
	@echo "Running all verification checks..."
	make test
	make lint
	make security-test
	make check-health
	make verify-resilience
	@echo "✅ All verifications passed"

clean-all: ## Deep clean including images
	docker-compose -f docker/docker-compose.dev.yml down -v --rmi all
	docker system prune -af
	rm -rf __pycache__ .pytest_cache .coverage htmlcov/
	rm -f *.log *.json

# Development utilities
shell: ## Open shell in API Gateway container
	docker-compose -f docker/docker-compose.dev.yml exec api-gateway /bin/bash

logs: ## View all service logs
	docker-compose -f docker/docker-compose.dev.yml logs -f

logs-api: ## View API Gateway logs
	docker-compose -f docker/docker-compose.dev.yml logs -f api-gateway

logs-db: ## View database logs
	docker-compose -f docker/docker-compose.dev.yml logs -f postgres

# Reset targets
reset: clean db-reset ## Complete reset of development environment
	@echo "Development environment reset complete"

# CI/CD simulation
ci: lint test security-test ## Simulate CI pipeline locally

cd: build ## Simulate CD pipeline locally
	@echo "CD pipeline simulation complete"

# Production utilities
prod-backup: ## Create production backup
	python scripts/backup.py --environment production

prod-logs: ## View production logs
	kubectl logs -f deployment/api-gateway -n scorpius-production

prod-shell: ## Open shell in production pod
	kubectl exec -it deployment/api-gateway -n scorpius-production -- /bin/bash

# Maintenance targets
update-deps: ## Update dependencies
	pip-compile config/requirements.in
	pip-compile config/requirements-dev.in
	pip install -r config/requirements-dev.txt

version: ## Show version information
	@echo "Scorpius Enterprise Platform"
	@echo "============================"
	@python --version
	@docker --version
	@docker-compose --version
	@kubectl version --client
	@terraform version

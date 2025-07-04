# Makefile for Usage Metering Service

.PHONY: help install test test-unit test-integration lint format check clean docker-build docker-run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt
	pip install -r test-requirements.txt

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest -m "not integration"

test-integration: ## Run integration tests only
	pytest -m integration

test-cov: ## Run tests with coverage
	pytest --cov=backend.usage_metering --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 .
	mypy .
	bandit -r . -x tests/

format: ## Format code
	black .
	isort .

check: lint test ## Run linting and tests

clean: ## Clean up generated files
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build: ## Build Docker image
	docker build -t usage-metering:latest .

docker-run: ## Run Docker container
	docker run -p 8005:8005 --env-file .env usage-metering:latest

dev: ## Start development server
	uvicorn app:app --host 0.0.0.0 --port 8005 --reload

redis-start: ## Start Redis for testing
	docker run -d --name redis-test -p 6379:6379 redis:7-alpine

redis-stop: ## Stop Redis test container
	docker stop redis-test && docker rm redis-test

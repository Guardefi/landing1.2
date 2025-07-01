# Makefile for Enterprise Honeypot Detector

.PHONY: help install dev test lint clean run-api run-worker docker-build docker-run docker-stop

# Default target executed when no arguments are given to make.
help:
	@echo "Enterprise Honeypot Detector"
	@echo ""
	@echo "Usage:"
	@echo "  make install         Install production dependencies"
	@echo "  make dev             Install development dependencies"
	@echo "  make test            Run tests"
	@echo "  make lint            Run linters"
	@echo "  make clean           Clean build artifacts"
	@echo "  make run-api         Run API server"
	@echo "  make run-worker      Run worker process"
	@echo "  make docker-build    Build Docker containers"
	@echo "  make docker-run      Start services with Docker Compose"
	@echo "  make docker-stop     Stop Docker services"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
dev:
	pip install -r requirements.txt -r requirements-dev.txt

# Run tests
test:
	pytest -v tests/

# Run linters
lint:
	flake8 api core database blockchain
	black --check api core database blockchain

# Clean build artifacts
clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf */*/*/__pycache__
	rm -rf .pytest_cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

# Run API server
run-api:
	python -m api.main

# Run worker process
run-worker:
	python -m worker.celery_app worker --loglevel=info

# Build Docker containers
docker-build:
	docker-compose -f docker/docker-compose.yml build

# Start services with Docker Compose
docker-run:
	docker-compose -f docker/docker-compose.yml up -d

# Stop Docker services
docker-stop:
	docker-compose -f docker/docker-compose.yml down

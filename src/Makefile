# Makefile for AI Teddy Bear Project

# Project variables
PROJECT_NAME = ai-teddy-bear
PYTHON = python3
PIP = pip
VENV = venv
VENV_BIN = $(VENV)/bin

# Development environment setup
.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV)
	. $(VENV_BIN)/activate && \
	$(PIP) install --upgrade pip && \
	$(PIP) install -r requirements.txt

# Install development dependencies
.PHONY: dev-install
dev-install:
	$(PIP) install -r requirements-dev.txt

# Run tests
.PHONY: test
test:
	pytest tests/ \
	--cov=src \
	--cov-report=html \
	--cov-fail-under=80

# Run security checks
.PHONY: security
security:
	bandit -r src
	safety check

# Run code formatting
.PHONY: format
format:
	black src tests
	isort src tests
	flake8 src tests

# Lint code
.PHONY: lint
lint:
	pylint src tests

# Generate documentation
.PHONY: docs
docs:
	sphinx-build -b html docs/source docs/build/html

# Clean up build artifacts
.PHONY: clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Docker commands
.PHONY: docker-build
docker-build:
	docker build -t $(PROJECT_NAME) .

.PHONY: docker-run
docker-run:
	docker-compose up --build

.PHONY: docker-down
docker-down:
	docker-compose down

# Database migrations
.PHONY: migrate
migrate:
	python -m scripts.data_migration

# Initialize database
.PHONY: init-db
init-db:
	python -m scripts.initialize_db

# Performance profiling
.PHONY: profile
profile:
	python -m scripts.performance_profile

# System diagnostics
.PHONY: diagnostics
diagnostics:
	python -m scripts.system_diagnostics

# Backup database
.PHONY: backup-db
backup-db:
	python -m scripts.backup_database

# Generate encryption key
.PHONY: gen-key
gen-key:
	python -m scripts.generate_encryption_key

# Generate environment file
.PHONY: gen-env
gen-env:
	python -m scripts.generate_env

# Model benchmarking
.PHONY: benchmark
benchmark:
	python -m scripts.model_benchmark

# Security scan
.PHONY: security-scan
security-scan:
	python -m scripts.security_scan

# Default target
.PHONY: all
all: venv dev-install test lint security

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  venv         - Create virtual environment and install dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  test         - Run tests with coverage"
	@echo "  security     - Run security checks"
	@echo "  format       - Format code with black and isort"
	@echo "  lint         - Run pylint"
	@echo "  docs         - Generate documentation"
	@echo "  clean        - Remove build artifacts"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker containers"
	@echo "  docker-down  - Stop Docker containers"
	@echo "  migrate      - Run database migrations"
	@echo "  init-db      - Initialize database"
	@echo "  profile      - Run performance profiling"
	@echo "  diagnostics  - Run system diagnostics"
	@echo "  backup-db    - Backup database"
	@echo "  gen-key      - Generate encryption key"
	@echo "  gen-env      - Generate environment file"
	@echo "  benchmark    - Run model benchmarking"
	@echo "  security-scan- Run comprehensive security scan"
	@echo "  all          - Run all development tasks"
	@echo "  help         - Show this help message"

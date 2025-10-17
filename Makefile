# Makefile for MCP OAuth Example

# Variables
PYTHON := python3
PIP := pip
SRC_DIR := src
TEST_DIR := tests
SCRIPTS_DIR := scripts
EXAMPLES_DIR := examples

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help message
	@echo "FastMCP OAuth Proxy Example - Development Commands"
	@echo "================================================="
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "Quick Start:"
	@echo "  1. make install"
	@echo "  2. cp .env.example .env  # Edit with your Azure AD details"
	@echo "  3. make run-auth-server  # In terminal 1"
	@echo "  4. make run-mcp-server   # In terminal 2"
	@echo "  5. make run-example      # In terminal 3"

.PHONY: install
install:  ## Install the package in development mode
	$(PIP) install -e .

.PHONY: install-dev
install-dev:  ## Install development dependencies
	$(PIP) install -e ".[dev]"

.PHONY: clean
clean:  ## Remove build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/

.PHONY: format
format:  ## Format code with black
	black $(SRC_DIR) $(TEST_DIR) $(SCRIPTS_DIR) $(EXAMPLES_DIR)

.PHONY: lint
lint:  ## Run code linting with ruff
	ruff check $(SRC_DIR) $(TEST_DIR) $(SCRIPTS_DIR) $(EXAMPLES_DIR)

.PHONY: type-check
type-check:  ## Run type checking with mypy
	mypy $(SRC_DIR)

.PHONY: test
test:  ## Run tests with pytest
	pytest $(TEST_DIR) -v

.PHONY: test-cov
test-cov:  ## Run tests with coverage report
	pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing

.PHONY: check-all
check-all: lint type-check test  ## Run all checks (lint, type-check, test)

.PHONY: run-auth-server
run-auth-server:  ## Start the OAuth authentication server
	$(PYTHON) $(SCRIPTS_DIR)/run_auth_server.py

.PHONY: run-mcp-server
run-mcp-server:  ## Start the protected MCP server
	$(PYTHON) $(SCRIPTS_DIR)/run_mcp_server.py

.PHONY: run-example
run-example:  ## Run the interactive client example
	$(PYTHON) $(EXAMPLES_DIR)/oauth_client_example.py

.PHONY: setup-env
setup-env:  ## Copy .env.example to .env for initial setup
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your Azure AD credentials."; \
	else \
		echo ".env file already exists."; \
	fi

.PHONY: check-env
check-env:  ## Check if required environment variables are set
	@echo "Checking environment configuration..."
	@$(PYTHON) -c "from src.mcp_oauth_example.config import Config; Config.from_env(); print('✅ Environment configuration is valid')"

.PHONY: build
build:  ## Build the package
	$(PYTHON) -m build

.PHONY: release-test
release-test:  ## Upload to test PyPI
	$(PYTHON) -m twine upload --repository testpypi dist/*

.PHONY: release
release:  ## Upload to PyPI
	$(PYTHON) -m twine upload dist/*

.PHONY: dev-setup
dev-setup: install-dev setup-env  ## Complete development environment setup
	@echo "Development environment setup complete!"
	@echo "Next steps:"
	@echo "  1. Edit .env with your Azure AD credentials"
	@echo "  2. Run 'make check-env' to verify configuration"
	@echo "  3. Run 'make run-auth-server' to start the auth server"

.PHONY: docs-serve
docs-serve:  ## Serve documentation locally (if docs are added later)
	@echo "Documentation serving not yet implemented"

# Security check target
.PHONY: security-check
security-check:  ## Run security checks
	$(PIP) install safety bandit
	safety check
	bandit -r $(SRC_DIR)

# Docker targets (for future containerization)
.PHONY: docker-build
docker-build:  ## Build Docker image
	@echo "Docker support not yet implemented"

.PHONY: docker-run
docker-run:  ## Run in Docker container
	@echo "Docker support not yet implemented"
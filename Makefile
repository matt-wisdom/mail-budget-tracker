# Makefile for managing Python project tasks with Poetry

.PHONY: install ruff format test

# Install dependencies using Poetry
install:
	@echo "Installing dependencies..."
	poetry install

# Run Ruff for code formatting and linting
ruff:
	@echo "Running Ruff for linting..."
	poetry run ruff check .

# Format code using Ruff
format:
	@echo "Formatting code with Ruff..."
	poetry run ruff format .

# Run tests using pytest
test:
	@echo "Running tests with pytest..."
	poetry run pytest

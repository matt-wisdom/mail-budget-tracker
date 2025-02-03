.PHONY: install ruff format test coverage

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

# Run tests with coverage and generate an HTML report
coverage:
	@echo "Running tests with coverage..."
	poetry run coverage run -m pytest
	@echo "Generating HTML coverage report..."
	poetry run coverage html
	@echo "Coverage report generated in htmlcov/index.html"

airflow:
	@echo "Starting airflow"
	airflow webserver --port 8080 -D
	airflow scheduler -D
	@echo "Started airflow webserver and scheduler"

airstop:
	@echo "Stopping airflow"
	# pkill -f "airflow scheduler"
	pkill -f "airflow webserver"

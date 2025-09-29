.PHONY: run install clean fix-numpy test test-cov test-verbose test-watch test-integration help

# Default target
help:
	@echo "Available targets:"
	@echo "  run        - Start the Voicify TTS server on port 8001"
	@echo "  install    - Install Python dependencies"
	@echo "  install-voicify-mock - Install mock Voicify for development"
	@echo "  fix-numpy  - Fix NumPy compatibility issue (downgrade to <2.0)"
	@echo "  test       - Run unit tests"
	@echo "  test-cov   - Run tests with coverage report"
	@echo "  test-verbose - Run tests with verbose output"
	@echo "  test-watch - Run tests in watch mode"
	@echo "  test-integration - Run integration tests (no mocks)"
	@echo "  clean      - Clean up generated files"
	@echo "  help       - Show this help message"

# Start the Voicify TTS server
run:
	@echo "Starting Voicify TTS server on port 8001..."
	. venv/bin/activate && python voicify_server.py

# Install Python dependencies
install:
	@echo "Installing Python dependencies..."
	. venv/bin/activate && pip install -r requirements.txt

# Install mock Voicify for development
install-voicify-mock:
	@echo "Installing mock Voicify package for development..."
	. venv/bin/activate && pip install -e mock_voicify/
	@echo "✅ Mock Voicify TTS available for development!"

# Fix NumPy compatibility issue
fix-numpy:
	@echo "Fixing NumPy compatibility issue..."
	. venv/bin/activate && pip install "numpy<2.0.0"

# Run unit tests
test:
	@echo "Running unit tests..."
	. venv/bin/activate && python -m pytest

# Run tests with coverage report
test-cov:
	@echo "Running tests with coverage..."
	. venv/bin/activate && python -m pytest --cov=voicify_server --cov-report=html --cov-report=term

# Run tests with verbose output
test-verbose:
	@echo "Running tests with verbose output..."
	. venv/bin/activate && python -m pytest -v

# Run tests in watch mode (requires pytest-watch)
test-watch:
	@echo "Running tests in watch mode..."
	. venv/bin/activate && python -m pytest_watch

# Run integration tests (no mocks)
test-integration:
	@echo "Running integration tests..."
	. venv/bin/activate && python -m pytest tests/simple_integration_test.py -v

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	rm -f output.wav
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf htmlcov
	rm -rf .coverage

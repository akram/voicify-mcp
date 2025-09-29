.PHONY: run install clean fix-numpy help

# Default target
help:
	@echo "Available targets:"
	@echo "  run        - Start the Voicify TTS server on port 8001"
	@echo "  install    - Install Python dependencies"
	@echo "  fix-numpy  - Fix NumPy compatibility issue (downgrade to <2.0)"
	@echo "  clean      - Clean up generated files"
	@echo "  help       - Show this help message"

# Start the Voicify TTS server
run:
	@echo "Starting Voicify TTS server on port 8001..."
	python voicify_server.py

# Install Python dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Fix NumPy compatibility issue
fix-numpy:
	@echo "Fixing NumPy compatibility issue..."
	pip install "numpy<2.0.0"

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	rm -f output.wav
	rm -rf __pycache__
	rm -rf *.pyc

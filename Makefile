.PHONY: all install test test-python test-bash lint clean help

PYTHON := python3
PIP := pip3

all: help

help:
	@echo "NVIDIA Stability for All Linux"
	@echo ""
	@echo "Usage:"
	@echo "  make install      Install dependencies"
	@echo "  make test         Run all tests"
	@echo "  make test-python  Run Python tests only"
	@echo "  make test-bash    Run Bash tests only"
	@echo "  make lint         Run linters"
	@echo "  make run          Run the tool (requires sudo)"
	@echo "  make run-bash     Run the Bash version (requires sudo)"
	@echo "  make clean        Clean up temporary files"

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

test: test-python test-bash

test-python:
	$(PYTHON) -m pytest tests/test_nvidia_stability.py -v

test-bash:
	bash tests/test_bash.sh

lint:
	$(PYTHON) -m flake8 src/ tests/ --max-line-length=120 --ignore=E501,W503 || true
	shellcheck bin/nvidia-stability.sh || true

run:
	sudo $(PYTHON) src/nvidia_stability.py

run-bash:
	sudo bash bin/nvidia-stability.sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ coverage.xml 2>/dev/null || true

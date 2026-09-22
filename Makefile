# Plain Makefile. No task-runner, no `just`, no `poe`. Works with GNU make on
# Linux/macOS and with the WSL one on Windows. The `make` that ships with some
# Git-for-Windows installs is ancient and may choke on `.PHONY` grouping, but
# the individual targets work.

PY ?= python3
PIP ?= $(PY) -m pip

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Editable install with dev extras
	$(PIP) install -e ".[dev]"

.PHONY: test
test: ## Run the test suite
	$(PY) -m pytest

.PHONY: test-cov
test-cov: ## Run tests with coverage (fails under 90%)
	$(PY) -m pytest --cov=src --cov-report=term-missing

.PHONY: lint
lint: ## Lint with ruff (no autofix)
	$(PY) -m ruff check .

.PHONY: fmt
fmt: ## Format with ruff
	$(PY) -m ruff format .
	$(PY) -m ruff check --fix .

.PHONY: typecheck
typecheck: ## Static type check
	$(PY) -m mypy --ignore-missing-imports src/

.PHONY: check
check: lint typecheck test ## Everything CI runs, locally

.PHONY: run
run: ## Try the CLI on this README
	$(PY) -m src.cli README.md

.PHONY: build
build: ## Build sdist + wheel into dist/
	$(PY) -m build

.PHONY: clean
clean: ## Remove caches and build artifacts
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache htmlcov
	rm -f .coverage coverage.xml
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

.PHONY: clean clean-build clean-pyc clean-test coverage dist docs help install lint lint/flake8 lint/black
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-docs clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-docs:
	rm -rf site/

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint/flake8: ## check style with flake8
	flake8 --extend-ignore "W291,W293,E501,W391,E712,E266,E251" model_ensembler
lint/black: ## check style with black
	black --check model_ensembler

lint: lint/flake8 lint/black ## check style

test: ## run tests quickly with the default Python
	pytest

test-verbose: ## run tests with verbose output
	pytest -v

test-cov: ## run tests with coverage
	pytest --cov=model_ensembler --cov-report=term-missing

coverage: ## check code coverage quickly with the default Python
	coverage run --source model_ensembler -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs:
	mkdocs build
	$(BROWSER) site/index.html

docs-serve: ## serve documentation locally
	mkdocs serve

dist: clean ## builds source and wheel package
	python -m build --sdist
	python -m build --wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

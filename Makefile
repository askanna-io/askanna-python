.DEFAULT_GOAL := help

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts
	rm -fr .ruff_cache/

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache/
	rm -f gl-code-quality-report.json
	rm -f coverage.xml
	rm -f junit.xml

lint: ## check style with flake8
	ruff check .

test: ## run tests with the default Python version
	hatch run +py=3 test:pytest

test-all: ## run tests on every Python version that is supported
	hatch run test:pytest

coverage: ## check code coverage with the default Python version
	hatch run +py=3 test:cov
	open htmlcov/index.html

dist: clean ## builds source and wheel package
	pip install build
	python -m build

install: clean ## install the package to the active Python's site-packages
	pip install .

install-dev: clean ## install the package to the active Python's site-packages
	pip install -e ."[dev]"

uninstall: clean ## uninstall the AskAnna package
	pip freeze | grep -v "^-e" | xargs pip uninstall -y

reinstall: uninstall install ## uninstall and install the AskAnna package

reinstall-dev: uninstall install-dev ## uninstall and install a development environment

help: ## show this message
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

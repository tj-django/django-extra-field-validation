# Self-Documented Makefile see https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

.DEFAULT_GOAL := help

PYTHON	:= /usr/bin/env python
MANAGE_PY   := $(PYTHON) manage.py
PYTHON_PIP  := /usr/bin/env pip
PIP_COMPILE := /usr/bin/env pip-compile
PART := patch

# Put it first so that "make" without argument is like "make help".
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-32s-\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: help

guard-%: ## Checks that env var is set else exits with non 0 mainly used in CI;
	@if [ -z '${${*}}' ]; then echo 'Environment variable $* not set' && exit 1; fi

# --------------------------------------------------------
# ------- Python package (pip) management commands -------
# --------------------------------------------------------

clean-build: ## Clean project build artifacts.
	@echo "Removing build assets..."
	@$(PYTHON) setup.py clean
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info

install: clean-build  ## Install project dependencies.
	@echo "Installing project in dependencies..."
	@$(PYTHON_PIP) install -r requirements.txt

install-lint: pipconf clean-build  ## Install lint extra dependencies.
	@echo "Installing lint extra requirements..."
	@$(PYTHON_PIP) install -e .'[lint]'

install-test: clean-build  ## Install test extra dependencies.
	@echo "Installing test extra requirements..."
	@$(PYTHON_PIP) install -e .'[test]'

install-dev: clean-build  ## Install development extra dependencies.
	@echo "Installing development requirements..."
	@$(PYTHON_PIP) install -e .'[development]' -r requirements.txt
	
install-deploy: clean-build  ## Install deploy extra dependencies.
	@echo "Installing deploy extra requirements..."
	@$(PYTHON_PIP) install -e .'[deploy]'

update-requirements:  ## Updates the requirement.txt adding missing package dependencies
	@echo "Syncing the package requirements.txt..."
	@$(PIP_COMPILE)

# ----------------------------------------------------------
# ---------- Release the project to PyPI -------------------
# ----------------------------------------------------------
increase-version: guard-PART  ## Increase project version
	@bump2version $(PART)
	@git switch -c main

dist: clean  ## builds source and wheel package
	@pip install build twine
	@python -m build

release: dist  ## package and upload a release
	@twine upload dist/*

# ----------------------------------------------------------
# --------- Run project Test -------------------------------
# ----------------------------------------------------------
test:
	@$(MANAGE_PY) test

tox: install-test  ## Run tox test
	@tox

clean-test-all: clean-build  ## Clean build and test assets.
	@rm -rf .tox/
	@rm -rf .pytest_cache/
	@rm test.db


# -----------------------------------------------------------
# --------- Docs ---------------------------------------
# -----------------------------------------------------------
create-docs:
	@npx docsify init ./docs

serve-docs:
	@npx docsify serve ./docs

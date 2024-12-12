.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")

.PHONY: help
help:		## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:		## Show the current environment.
	@echo "Current environment:"
	@echo "Running using $(ENV_PREFIX)"
	@$(ENV_PREFIX)python -V
	@$(ENV_PREFIX)python -m site

.PHONY: install
install:		## Install the project in dev mode.
	@echo "Don't forget to run 'make virtualenv' if you got errors."
	$(ENV_PREFIX)pip install -e .[dev]

.PHONY: fmt
fmt:		## Format code using black & isort.
	$(ENV_PREFIX)isort earth_osm/
	$(ENV_PREFIX)black -l 95 earth_osm/ --exclude \_pb2
	$(ENV_PREFIX)black -l 95 tests/

.PHONY: lint
lint:		## Run pep8, black, mypy linters.
	$(ENV_PREFIX)flake8 --max-line-length 95 earth_osm/ --exclude earth_osm/osmpbf/fileformat_pb2.py,earth_osm/osmpbf/osmformat_pb2.py
	$(ENV_PREFIX)black -l 95 --check earth_osm/ --exclude \_pb2
	$(ENV_PREFIX)black -l 95 --check tests/
	$(ENV_PREFIX)mypy --ignore-missing-imports earth_osm/ --exclude \_pb2 --install-types --non-interactive

.PHONY: test
test:		## Run tests and generate coverage report.
	$(ENV_PREFIX)pytest -v --cov=earth_osm --cov-config= --cov-report= -l --tb=short --maxfail=1 tests/
	$(ENV_PREFIX)coverage report --omit='*_pb2.py'
	$(ENV_PREFIX)coverage xml --omit='*_pb2.py'
	$(ENV_PREFIX)coverage html --omit='*_pb2.py'

.PHONY: watch
watch:		## Run tests on every change.
	ls **/**.py | entr $(ENV_PREFIX)pytest -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: clean
clean:		## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build

.PHONY: virtualenv
virtualenv:		## Create a virtual environment.
	@echo "creating virtualenv ..."
	@rm -rf .venv
	@python3 -m venv .venv
	@./.venv/bin/pip install -U pip
	@./.venv/bin/pip install -e .[dev]
	@echo
	@echo "!!! Please run 'source .venv/bin/activate' to enable the environment !!!"

.PHONY: release
release:		## Create a new tag for release.
	@echo "WARNING: This operation will create a version tag and push to github"
	@read -p "Version? (provide the next x.y.z semver) : " TAG
	@echo "$${TAG}" > earth_osm/VERSION
	@$(ENV_PREFIX)gitchangelog > HISTORY.md
	@git add earth_osm/VERSION HISTORY.md
	@git commit -m "release: version $${TAG} 🚀"
	@echo "creating git tag : $${TAG}"
	@git tag $${TAG}
	@git push -u origin HEAD --tags
	@echo "Github Actions will detect the new tag and release the new version."

.PHONY: api-docs
api-docs:		## Generate the API documentation.
	@if ! git diff-index --quiet HEAD --; then \
		echo "There are uncommitted changes. Stash or commit changes first"; \
	else \
		echo "Generating API documentation..."; \
		$(ENV_PREFIX)pip install .[docs]; \
		$(ENV_PREFIX)lazydocs \
			--output-path="./docs/api-docs" \
			--overview-file="README.md" \
			--src-base-url="https://github.com/pypsa-meets-earth/earth-osm/blob/main/" \
			--ignored-modules osmpbf.fileformat_pb2 \
			--ignored-modules osmpbf.osmformat_pb2 \
			--ignored-modules osmpbf.file \
			--no-watermark \
			earth_osm; \
	fi

.PHONY: docs
docs: api-docs		## Build the documentation.
	@echo "building documentation ..."
	@$(ENV_PREFIX)mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL

.PHONY: docs-gh-deploy
docs-gh-deploy: api-docs		## Serve the documentation.
	@echo "deploying documentation on github ..."
	@$(ENV_PREFIX)mkdocs gh-deploy --force
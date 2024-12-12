# How to develop on this project

PyPSA-meets-Earth is a community driven project so we welcome contributions from everyone.

**You need PYTHON3!**

This instructions are for linux base systems.
For Windows users, we recommend to use the [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

## Setting up your own fork of this repo.

- On github interface click on `Fork` button.
- Clone your fork of this repo. `git clone git@github.com:YOUR_GIT_USERNAME/earth-osm.git`
- Enter the directory `cd earth-osm`
- Add upstream repo `git remote add upstream https://github.com/pypsa-meets-earth/earth-osm`

## Setting up your own virtual environment

Run `make virtualenv` to create a virtual environment.
then activate it with `source .venv/bin/activate`.

## Install the project in develop mode

Run `make install` to install the project in develop mode.

## Run the tests to ensure everything is working

Run `make test` to run the tests.

## Create a new branch to work on your contribution

Run `git checkout -b my_contribution`

## Make your changes

Edit the files using your preferred editor. (we recommend VSCode)

## Format the code

Run `make fmt` to format the code.

## Run the linter

Run `make lint` to run the linter.

## Test your changes

Run `make test` to run the tests.

Ensure code coverage report shows `100%` coverage, add tests to your PR.

## Build the docs locally

Run `make docs` to build the docs.

Ensure your new changes are documented.

## Commit your changes

This project uses [conventional git commit messages](https://www.conventionalcommits.org/en/v1.0.0/).

Example: `fix(package): update setup.py arguments 🎉` (emojis are fine too)

## Push your changes to your fork

Run `git push origin my_contribution`

## Submit a pull request

On github interface, click on `Pull Request` button.

Wait CI to run and one of the developers will review your PR.

## Makefile utilities

This project comes with a `Makefile` that contains a number of useful utility.

```bash 
❯ make
Usage: make <target>

Targets:
help:             ## Show the help.
install:          ## Install the project in dev mode.
fmt:              ## Format code using black & isort.
lint:             ## Run pep8, black, mypy linters.
test:             ## Run tests and generate coverage report.
watch:            ## Run tests on every change.
clean:            ## Clean unused files.
virtualenv:       ## Create a virtual environment.
release:          ## Create a new tag for release.
docs:             ## Build the documentation.
```

## Making a new release

This project uses [semantic versioning](https://semver.org/) and tags releases with `X.Y.Z`
Every time a new tag is created and pushed to the remote repo, github actions will
automatically create a new release on github and trigger a release on PyPI.

For this to work you need to setup a secret called `PIPY_API_TOKEN` on the project settings>secrets, 
this token can be generated on [pypi.org](https://pypi.org/account/).

To trigger a new release all you need to do is.

1. If you have changes to add to the repo
    * Make your changes following the steps described above.
    * Commit your changes following the [conventional git commit messages](https://www.conventionalcommits.org/en/v1.0.0/).
2. Run the tests to ensure everything is working.
4. Run `make release` to create a new tag and push it to the remote repo.

the `make release` will ask you the version number to create the tag, ex: type `0.1.1` when you are asked.

> **CAUTION**:  The make release will change local changelog files and commit all the unstaged changes you have.


### Update API Docs
API Docs should be updated using lazydocs

```bash
lazydocs \
    --output-path="./docs/api-docs" \
    --overview-file="README.md" \
    --src-base-url="https://github.com/pypsa-meets-earth/earth-osm/blob/main/" \
    --ignored-modules osmpbf.fileformat_pb2 \
    --ignored-modules osmpbf.osmformat_pb2 \
    --no-watermark \
    earth_osm
```

We also generate [codecov](https://about.codecov.io/sign-up/) Reports

### Prject Design 

### Documentation (Docs)
MKdocs is used for the main documentation.
Lazydocs is used to automatically generate documentation of the API from the docstrings.

The following mkdocs plugins are used:
- [material-theme](https://squidfunk.github.io/mkdocs-material/)
- [awesome-pages](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin)


#### What is the purpose of the go_to_tmpdir fixture in conftest?
The go_to_tmpdir fixture in conftest creates a temporary directory before each test to perform file system operations in isolation, and removes it after the test. Pytest automatically sets the temporary directory as the working directory before each test, ensuring that any temporary artifacts created during the test will be removed once the test is complete.

#### Why isn't pre-commit used?
The project avoids using pre-commit as it adds an extra dependency and can be a barrier for new contributors. The linting, checks, and formatting are provided as simple commands in the Makefile for ease of understanding and modification. As the project grows, using pre-commit may be considered.

#### Why isn't the CLI using click?
The project's CLI is not using click because it is an external dependency. The goal of this project is to provide a simple and easy-to-understand main entry point for a CLI application without adding any additional dependencies beyond those required for development.

#### Structure

```text
├── Containerfile            # The file to build a container using buildah or docker (currently removed)
├── CONTRIBUTING.md          # Onboarding instructions for new contributors
├── docs                     # Documentation site (add more .md files here)
│   └── index.md             # The index page for the docs site
├── .github                  # Github metadata for repository
│   ├── release_message.sh   # A script to generate a release message
│   └── workflows            # The CI pipeline for Github Actions
├── .gitignore               # A list of files to ignore when pushing to Github
├── HISTORY.md               # Auto generated list of changes to the project
├── LICENSE                  # The license for the project
├── Makefile                 # A collection of utilities to manage the project
├── MANIFEST.in              # A list of files to include in a package
├── mkdocs.yml               # Configuration for documentation site
├── earth_osm                # The main python package for the project
│   ├── eo.py                # The base module for the project
│   ├── __init__.py          # This tells Python that this is a package
│   ├── __main__.py          # The entry point for the project
│   └── VERSION              # The version for the project is kept in a static file
├── README.md                # The main readme for the project
├── pyproject.toml           # Configuration file used by packaging tools
└── tests                    # Unit tests for the project (add mote tests files here)
    ├── conftest.py          # Configuration, hooks and fixtures for pytest
    ├── __init__.py          # This tells Python that this is a test package
    └── test_eo.py           # The base test case for the project

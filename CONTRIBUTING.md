# How to develop on this project

PyPSA-meets-Earth is a community driven project so we welcome contributions from everyone.

**You need PYTHON3!**

This instructions are for linux base systems.
For Windows users, we recommend to use the [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

## Setting up your own fork of this repo.

- On github interface click on `Fork` button.
- Clone your fork of this repo. `git clone git@github.com:YOUR_GIT_USERNAME/earth-osm.git`
- Enter the directory `cd earth-osm`
- Add upstream repo `git remote add upstream https://github.com/pypsa-meets-africa/earth-osm`

## Setting up your own virtual environment

Run `make virtualenv` to create a virtual environment.
then activate it with `source .venv/bin/activate`.

## Install the project in develop mode

Run `make install` to install the project in develop mode.


"""Python setup.py for earth_osm package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("earth_osm", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content

# mirror of dependencies in setup and requirements.txt
install_requires=[
    "geopandas",
    "pandas",
    "tqdm",
    "requests",
    "protobuf>=4.21.1",
]

extras_require={"test": [
    "pytest",
    "coverage",
    "flake8",
    "black",
    "isort",
    "pytest-cov",
    "codecov",
    "mypy>=0.9",
    "gitchangelog",
    "mkdocs",
    "pprint",
    "osmium",
    ]
}

assert read("requirements.txt") == "\n".join(install_requires)
assert read("requirements-test.txt") == "\n".join(extras_require["test"])

setup(
    name="earth_osm",
    version=read("earth_osm", "VERSION"),
    description="Python tool to extract large-amounts of OpenStreetMap data",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="pypsa-meets-earth",
    url="https://github.com/pypsa-meets-earth/earth-osm/",
    packages=find_packages(exclude=["docs", "tests"]),
    include_package_data=True,
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["earth_osm = earth_osm.__main__:main"]
    },
    install_requires=[
        "geopandas",
        "pandas",
        "tqdm",
        "requests",
        "protobuf>=4.21.1",
    ],
    extras_require={"test": [
        "pytest",
        "coverage",
        "flake8",
        "black",
        "isort",
        "pytest-cov",
        "codecov",
        "mypy>=0.9",
        "gitchangelog",
        "mkdocs",
        "osmium",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
)
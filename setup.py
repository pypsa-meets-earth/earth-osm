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


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="earth_osm",
    version=read("earth_osm", "VERSION"),
    description="Awesome earth_osm created by pypsa-meets-earth",
    url="https://github.com/pypsa-meets-earth/earth-osm/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="pypsa-meets-earth",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": ["earth_osm = earth_osm.__main__:main"]
    },
    extras_require={"test": read_requirements("requirements-test.txt")},
)

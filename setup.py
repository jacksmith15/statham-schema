"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from codecs import open
from os import path

from setuptools import (
    find_packages,
    setup,
)

import jsonschema_objects


REQUIREMENTS_FILE_PATH = path.join(
    path.abspath(path.dirname(__file__)), "requirements.txt"
)

with open(REQUIREMENTS_FILE_PATH, "r") as f:
    REQUIREMENTS_FILE = [
        line for line in f.read().splitlines()
        if not line.startswith("#") and not line.startswith("--")
    ]

DEPENDENCY_LINKS = [
    REQUIREMENTS_FILE.pop(index)
    for index, value_ in enumerate(REQUIREMENTS_FILE)
    if "git+ssh" in value_
]

setup(
    name="elucidata-serializers",
    version=jsonschema_objects.__version__,
    description="Tools for generating python objects from json schema definitions.",
    author="Jack Smith",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=REQUIREMENTS_FILE,
    dependency_links=DEPENDENCY_LINKS,
)

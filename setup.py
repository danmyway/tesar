#!/usr/bin/env python3

import os
from setuptools import setup

_CUR_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(_CUR_DIR, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()


setup(
    name="tesar",
    version="2022.11.11",
    packages=["dispatch"],
    install_requires=["envparse", "requests", "copr", "koji"],
    url="https://gitlab.cee.redhat.com/ddiblik/tesar",
    license="",
    author="Daniel Diblik",
    author_email="ddiblik@redhat.com",
    description="Testing farm API requests dispatch.",
    long_description=readme,
    entry_points={
        "console_scripts": "tesar = dispatch.__main__:main",
    },
)

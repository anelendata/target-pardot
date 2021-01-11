#!/usr/bin/env python
from setuptools import setup

VERSION = "0.1.0"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="target-pardot",
    version=VERSION,
    description="Singer.io target for writing data to Pardot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daigo Tanaka, Anelen Co., LLC",
    url="https://github.com/anelendata/target-pardot",

    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",

        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",

        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],

    install_requires=[
        "jsonschema==2.6.0",  # singer-pythin requires exact
        "singer-python>=5.2.0",
        "setuptools>=40.3.0",
        "PyPardot4 @ https://github.com/anelendata/PyPardot4/archive/42e81df45a8838c97e97e7a5cefc80b897e4dc69.zip#egg=PyPardot4-1.1.15"
    ],
    dependency_links=[
    ],
    entry_points="""
    [console_scripts]
    target-pardot=target_pardot:main
    """,
    packages=["target_pardot"],
    package_data = {
        # Use MANIFEST.ini
    },
    include_package_data=True,
)

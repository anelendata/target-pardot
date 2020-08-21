#!/usr/bin/env python
from setuptools import setup

VERSION = "0.1.0b0"

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
        "pardot-api-client @ https://github.com/anelendata/pardot-api-client/tarball/6f2780442ce91faf7ce71d1b7e075eba4ec96175#egg=pardot-api-client",
        "singer-python>=5.2.0",
        "setuptools>=40.3.0",
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

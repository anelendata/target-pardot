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
        "singer-python>=5.2.0",
        "setuptools>=40.3.0",
        "PyPardot4 @ https://github.com/anelendata/PyPardot4/archive/9b073ac3d24a74107c1af28324893452c8d54c95.zip#egg=PyPardot4-1.1.15"
        # "PyPardot4 @ https://github.com/anelendata/PyPardot4/archive/9b073ac3d24a74107c1af28324893452c8d54c95.tar.gz#egg=PyPardot4-1.1.15",
    ],
    dependency_links=[
        # "git+https://github.com/anelendata/PyPardot4.git@9b073ac3d24a74107c1af28324893452c8d54c95#egg=PyPardot4-1.1.15.dev"
        # "git+https://github.com/anelendata/PyPardot4/tarball/9b073ac3d24a74107c1af28324893452c8d54c95#egg=PyPardot4-1.1.15.dev"
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

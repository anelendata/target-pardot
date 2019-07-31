#!/usr/bin/env python
from setuptools import setup

setup(
    name="target_pardot",
    version="0.1.0",
    description="Singer.io target for extracting data",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["target_pardot"],
    install_requires=[
        "singer-python>=5.0.12",
        "pypardot4>=1.1.14",
        "pardot-api-client @ https://github.com/anelendata/pardot-api-client/tarball/master#egg=pardot-api-client",
    ],
    dependency_links=[
    ],
    entry_points="""
    [console_scripts]
    target_pardot=target_pardot:main
    """,
    packages=["target_pardot"],
    package_data = {},
    include_package_data=True,
)

#!/usr/bin/env python

import setuptools
from frost import SOURCE_URL, VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    line.split("==")[0] for line in open("requirements.txt", "r") if ".git" not in line
]

setuptools.setup(
    name="frost",
    version=VERSION,
    author="Firefox Operations Security Team (foxsec)",
    author_email="foxsec+frost@mozilla.com",
    description="tests for checking that third party services the Firefox Operations Security or foxsec team uses are configured correctly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=SOURCE_URL,
    license="MPL2",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Natural Language :: English",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["frost=frost.cli:cli"],},
    include_package_data=True,
)

import setuptools

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="frost",
    version="0.3.1",
    author="Firefox Operations Security Team (foxsec)",
    author_email="foxsec+frost@mozilla.com",
    description="tests for checking that third party services the Firefox Operations Security or foxsec team uses are configured correctly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mozilla/frost",
    license="MPL2",
    packages=setuptools.find_packages(),
    classifiers=[
        "Natural Language :: English",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
)

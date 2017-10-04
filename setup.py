#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-aws',
    version='0.1.0',
    author='Mozilla Services',
    author_email='services-dev@mozilla.com',
    maintainer='Mozilla Services',
    maintainer_email='services-dev@mozilla.com',
    license='Mozilla Public License 2.0',
    url='https://github.com/g-k/pytest-aws',
    description='pytest plugin for testing AWS resource configurations',
    long_description=read('README.md'),
    py_modules=['pytest_aws'],
    install_requires=['pytest>=3.1.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'pytest11': [
            'aws = pytest_aws',
        ],
    },
)

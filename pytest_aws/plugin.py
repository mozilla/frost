#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import botocore


def pytest_addoption(parser):
    botocore.__file__  # satisfy flake8 for now
    group = parser.getgroup('aws')
    group.addoption(
        '--foo',
        action='store',
        dest='dest_foo',
        default='2017',
        help='Set the value for the fixture "bar".'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')


@pytest.fixture
def bar(request):
    return request.config.option.dest_foo

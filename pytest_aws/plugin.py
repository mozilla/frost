#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pytest_aws.client import (
    get_available_regions,
    get_available_profiles,
    get_aws_resource,
)
from pytest_aws.cache import (
    patch_cache_set
)


def pytest_addoption(parser):
    group = parser.getgroup('aws')
    group.addoption(
        '--foo',
        action='store',
        dest='dest_foo',
        default='2017',
        help='Set the value for the fixture "bar".'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')


def pytest_configure(config):
    ""
    patch_cache_set(config)

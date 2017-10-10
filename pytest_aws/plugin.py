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


def pytest_generate_tests(metafunc):
    # TODO: make configurable by ID

    def id_fn(instance):
        return instance['DBInstanceIdentifier']

    for fixture_name in metafunc.fixturenames:
        print(fixture_name)

    if 'rds_snapshot' in metafunc.fixturenames:
        metafunc.parametrize('rds_snapshot', rds_snapshots(metafunc, metafunc.config.cache), ids=id_fn)


def get_most_specific_option(obj, option_name, default=None):
    "Looks up an option from the function, module, CLI, or ini file in that order."

    if hasattr(obj, 'function') and hasattr(obj.function, option_name):
        return getattr(obj.function, option_name)
    elif hasattr(obj, 'module') and hasattr(obj.module, option_name):
        return getattr(obj.module, option_name)
    elif hasattr(obj, 'config'):
        config = obj.config
        try:
            return config.getoption(option_name)
        except ValueError:
            pass

        try:
            return config.getini(option_name)
        except ValueError:
            pass

    return default


rds_snapshots_config = {
    'service': 'rds',
    'method': 'describe_db_snapshots',
    'kwargs': {'IncludeShared': True, 'IncludePublic': True},
    'result_key': 'DBSnapshots',
    # 'id_key': 'DBSnapshotIdentifier',
}

rds_snapshot_attributes_config = {
    'service': 'rds',
    'method': 'describe_db_snapshot_attributes',
    'kwargs': {'DBSnapshotIdentifier': 'DBSnapshots.DBSnapshotIdentifier'},  # TODO: include param as FK?
    'result_key': 'DBSnapshotAttributesResult',
}


@pytest.fixture(scope='module')
def rds_snapshots(metafunc, cache):
    "AWS RDS Snapshots"
    profiles = get_most_specific_option(metafunc, 'profiles', get_available_profiles())
    regions = get_most_specific_option(metafunc, 'regions', get_available_regions())

    return get_aws_resource(profiles, regions, rds_snapshots_config, cache)


@pytest.fixture()
def rds_snapshot_attributes(cache, rds_snapshot):
    "AWS RDS Snapshot Attributes"
    rds_snapshot_attributes_config['kwargs']['DBSnapshotIdentifier'] = rds_snapshot['DBSnapshotIdentifier'].split(':')[-1]
    snapshot_call = rds_snapshot['aws_api_call']

    return next(get_aws_resource([snapshot_call.profile], [snapshot_call.region], rds_snapshot_attributes_config, cache))

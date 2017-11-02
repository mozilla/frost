
import sys
import functools
import os.path
import json

import botocore.exceptions
import pytest


@functools.lru_cache()
def load_resource_operations_config():
    project_root = os.path.dirname(__file__)
    config_file = os.path.join(project_root, 'config', 'aws_fixtures.json')
    return json.load(open(config_file, 'r'))


def get_available_fixtures():
    for fixture_name, fixture_ops in load_resource_operations_config().items():
        yield fixture_name, fixture_ops


def get_fixture_fn(fixture_name, resource_config):
    "Returns a pytest.fixture for an AWS resource"

    def fn(request):
        return request.param

    fn.__name__ = fixture_name
    fn.__doc__ = resource_config['fetch']['docstring']
    fn._aws_resource_config = resource_config

    wrapped_fn = pytest.fixture(name=fixture_name, scope='function')(fn)
    return wrapped_fn


def get_fixture_id(config, fixture_name, fixture_value):
    fixture_config = config.aws_fixtures[fixture_name]

    if 'parametrize_id_source' not in fixture_config or fixture_config['parametrize_id_source'] is None:
        return None

    pid_src = fixture_config.get('parametrize_id_source')
    assert isinstance(pid_src, list) and len(pid_src)
    return fixture_value[pid_src[0]]
    # raise NotImplementedError('No fixture id for {} {}'.format(fixture_name, fixture_value))

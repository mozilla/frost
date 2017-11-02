

import sys
import botocore
import botocore.exceptions
import pytest
from _pytest.mark import MarkInfo, MarkDecorator
import warnings
import itertools


from cache import patch_cache_set
from client import (
    get_client,
    get_aws_resource,
)
from aws_fixtures import (
    load_resource_operations_config,
    get_available_fixtures,
    get_fixture_fn,
    get_fixture_id,
)


def add_fixture_stub(fixture_name, stub_fn):
    # Note: needs to be in a conftest or plugin

    # per https://xr.gs/2017/07/pytest-dynamic-runtime-fixtures-python3/
    # pytest requires a module level fn name to define the fixture
    setattr(sys.modules[__name__], fixture_name, stub_fn)


def pytest_configure(config):
    # monkeypatch cache.set to serialize datetime.datetime's
    patch_cache_set(config)

    aws_fixtures = {}

    # add stub fixtures for aws Describe*, Get*, and List* methods that don't require args
    for fixture_name, operation in get_available_fixtures():
        add_fixture_stub(fixture_name, get_fixture_fn(fixture_name, operation))
        aws_fixtures[fixture_name] = operation

    # TODO: fix this in list_methods.py
    aws_fixtures['s3_bucket_from_list_buckets']['parametrize_id_source'] = ['Name']

    config.aws_fixtures = aws_fixtures
    config.aws_fixture_names = set(config.aws_fixtures.keys())


def get_node_markers(node):
    return {k: v for k, v in node.keywords.items() if isinstance(v, (MarkDecorator, MarkInfo))}


def serialize_marker(marker):
    if isinstance(marker, (MarkDecorator, MarkInfo)):
        return {
            'name': marker.name,
            'args': marker.args,
            'kwargs': marker.kwargs,
        }
    else:
        raise NotImplementedError('Unexpected Marker type %s' % repr(marker))


def pytest_make_parametrize_id(config, val, argname):
    return get_fixture_id(config, argname, val)


def pytest_generate_tests(metafunc):
    config, mod = metafunc.config, metafunc.module
    test_name = metafunc.function.__name__

    profiles, regions = getattr(mod, 'profiles'), getattr(mod, 'regions')
    update_args = getattr(mod, 'update_args', {})
    expect_args = getattr(mod, 'expect_args', {})

    print('collecting', test_name)

    aws_fixture_names = [
        fixture_name for fixture_name in metafunc.fixturenames
        if fixture_name in config.aws_fixture_names
    ]

    fixture_param_values = {}

    for fixture_name in aws_fixture_names:
        fixture_config = config.aws_fixtures[fixture_name]

        hook_name = '_'.join([fixture_name, 'param', 'values'])
        if hasattr(mod, hook_name):  # get params from test module (if any)
            vals = getattr(mod, hook_name)(profiles, regions, fixture_config, config.cache)
        elif 'parametrize_id_source' in fixture_config and fixture_config['parametrize_id_source']:
            vals = get_aws_resource(profiles, regions, fixture_config, config.cache)
        else:
            continue

        fixture_param_values[fixture_name] = vals

    param_values = list(itertools.product(*fixture_param_values.values()))

    # set required args from other fixture values
    missing_aws_fixture_names = [
        fixture_name for fixture_name in aws_fixture_names
        if fixture_name not in fixture_param_values.keys()
    ]

    for i, params in enumerate(param_values):
        new_params = list(params)

        for fixture_name in aws_fixture_names:
            fixture_config = config.aws_fixtures[fixture_name]
            fixture_config['args'] = fixture_config.get('args', [])
            fixture_config['kwargs'] = fixture_config.get('kwargs', {})

            hook_name = '_'.join([fixture_name, 'dependent', 'value'])
            if hasattr(mod, hook_name):  # get params from test module (if any)
                val = getattr(mod, hook_name)(
                    test_name, fixture_config, config.cache, new_params, aws_fixture_names)
                new_params.append(val)
            elif 'parametrize_id_source' not in fixture_config:
                val = list(get_aws_resource(profiles, regions, fixture_config, config.cache))
                new_params.append(val)

        hook_name = '_'.join(['mark', test_name])  # mark skips and fails
        if hasattr(mod, hook_name):
            param_values[i] = getattr(mod, hook_name)(new_params, aws_fixture_names)
        else:
            param_values[i] = tuple(new_params)

    metafunc.parametrize(aws_fixture_names, param_values)


def get_outcome_and_reason(report, markers, call, aws_fixtures):
    xfail = 'xfail' in markers
    xpass = report.passed and xfail

    if call.excinfo and not isinstance(call.excinfo, AssertionError) and isinstance(call.excinfo, Exception):
        return 'errored', call.excinfo
    elif xpass:
        return 'xpassed', markers['xfail']['kwargs'].get('reason', None)
    elif xfail:
        return 'xfailed', markers['xfail']['kwargs'].get('reason', None)
    else:
        return report.outcome, None  # passed, failed, skipped


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    pytest_json = item.config.pluginmanager.getplugin('json')

    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    # only add this during call instead of during any stage
    if report.when == 'call':
        unparametrized_name = item.originalname or item.name

        aws_fixtures = {
            fixture_name: item.funcargs[fixture_name]
            for fixture_name in item.fixturenames
            if fixture_name in item.config.aws_fixture_names
        }

        aws_fixture_ids = [
            get_fixture_id(item.config, fixture_name, fixture) or 'N/A'
            for (fixture_name, fixture) in aws_fixtures.items()
        ]

        markers = {k: serialize_marker(v) for (k, v) in get_node_markers(item).items()}
        outcome, reason = get_outcome_and_reason(report, markers, call, aws_fixtures)

        # add json metadata
        report.test_metadata = dict(
            outcome=outcome,  # 'passed', 'failed', 'skipped', 'xfailed', 'xskipped', or 'errored'
            reason=reason,
            unparametrized_name=unparametrized_name,
            aws_fixtures=aws_fixtures,
            aws_fixture_ids=aws_fixture_ids,
            markers=markers,
            docs=item.function.__doc__,
        )

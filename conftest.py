

import botocore
import pytest

from _pytest.mark import MarkInfo, MarkDecorator
from cache import patch_cache_set
from aws.client import BotocoreClient


botocore_client = None


def pytest_addoption(parser):
    parser.addoption('--aws-profiles',
                     action='append',
                     default=[],
                     help='Set default AWS profiles to use. Defaults to the current AWS profile i.e. [None].')

    parser.addoption('--aws-regions',
                     action='append',
                     default=[],
                     help='Set default AWS regions to use. Defaults to all available ec2 regions')

    parser.addoption('--aws-debug-calls',
                     action='store_true',
                     help='Log AWS API calls. Requires -s')

    parser.addoption('--aws-debug-cache',
                     action='store_true',
                     help='Log whether AWS API calls hit the cache. Requires -s')


def pytest_configure(config):
    global botocore_client

    # monkeypatch cache.set to serialize datetime.datetime's
    patch_cache_set(config)

    profiles, regions = config.getoption('--aws-profiles'), config.getoption('--aws-regions')

    if not len(profiles):
        profiles = None

    if not len(regions):
        regions = None

    botocore_client = BotocoreClient(
        profiles=profiles,
        regions=regions,
        cache=config.cache,
        debug_calls=config.getoption('--aws-debug-calls'),
        debug_cache=config.getoption('--aws-debug-cache'))


## Reporting


def get_node_markers(node):
    return {k: v for k, v in node.keywords.items() if isinstance(v, (MarkDecorator, MarkInfo))}


def serialize_marker(marker):
    if isinstance(marker, (MarkDecorator, MarkInfo)):
        args = ['...skipped...'] if marker.name == 'parametrize' else marker.args
        return {
            'name': marker.name,
            'args': args,
            'kwargs': marker.kwargs,
        }
    else:
        raise NotImplementedError('Unexpected Marker type %s' % repr(marker))


def get_outcome_and_reason(report, markers, call):
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

    markers = {k: serialize_marker(v) for (k, v) in get_node_markers(item).items()}
    outcome, reason = get_outcome_and_reason(report, markers, call)

    # only add this during call instead of during any stage
    if report.when == 'call':
        # item.config

        fixtures = {fixture_name: item.funcargs[fixture_name] for fixture_name in item.fixturenames if fixture_name != 'request'}

        # add json metadata
        report.test_metadata = dict(
            outcome=outcome,  # 'passed', 'failed', 'skipped', 'xfailed', 'xskipped', or 'errored'
            reason=reason,
            unparametrized_name=item.originalname or item.name,
            markers=markers,
            fixtures=fixtures,
        )



import argparse

import pytest

from _pytest.doctest import DoctestItem
from _pytest.mark import MarkInfo, MarkDecorator
from cache import patch_cache_set
from aws.client import BotocoreClient
import exemptions
import severity


botocore_client = None
whitelisted_ports = None


def pytest_addoption(parser):
    parser.addoption('--aws-profiles',
                     nargs='*',
                     help='Set default AWS profiles to use. Defaults to the current AWS profile i.e. [None].')

    parser.addoption('--aws-regions',
                     nargs='*',
                     help='Set default AWS regions to use. Defaults to all available ec2 regions')

    parser.addoption('--aws-debug-calls',
                     action='store_true',
                     help='Log AWS API calls. Requires -s')

    parser.addoption('--aws-debug-cache',
                     action='store_true',
                     help='Log whether AWS API calls hit the cache. Requires -s')

    parser.addoption('--aws-require-tags',
                     nargs='*',
                     default=[],
                     help='EC2 instance tags for the aws.ec2.test_ec2_instance_has_required_tags test to check.')

    parser.addoption('--aws-whitelisted-ports',
                     nargs='*',
                     default=[],
                     help='Additional ports to whitelist for '
                          'aws.ec2.test_ec2_security_group_opens_specific_ports_to_all test.')

    parser.addoption('--offline',
                     action='store_true',
                     default=False,
                     help='Instruct service clients to return empty lists and not make HTTP requests.')

    parser.addoption('--severity-config',
                     type=argparse.FileType('r'),
                     help='Path to a config file specifying test severity levels.')

    parser.addoption('--exemptions-config',
                     type=argparse.FileType('r'),
                     help='Path to a config file specifying test and resource exemptions.')


def pytest_configure(config):
    global botocore_client
    global whitelisted_ports

    # monkeypatch cache.set to serialize datetime.datetime's
    patch_cache_set(config)

    profiles, regions = config.getoption('--aws-profiles'), config.getoption('--aws-regions')

    whitelisted_ports = frozenset([int(port) for port in config.getoption('--aws-whitelisted-ports')])

    botocore_client = BotocoreClient(
        profiles=profiles,
        regions=regions,
        cache=config.cache,
        debug_calls=config.getoption('--aws-debug-calls'),
        debug_cache=config.getoption('--aws-debug-cache'),
        offline=config.getoption('--offline'))

    config.exemptions = exemptions.parse_conf_file(config.getoption('--exemptions-config'))
    config.severity = severity.parse_conf_file(config.getoption('--severity-config'))


def pytest_runtest_setup(item):
    """
    """
    if not isinstance(item, DoctestItem):
        severity.add_severity_marker(item)
        exemptions.add_xfail_marker(item)


# Reporting


def get_node_markers(node):
    return {k: v for k, v in node.keywords.items() if isinstance(v, (MarkDecorator, MarkInfo))}


METADATA_KEYS = [
    'DBInstanceArn',
    'DBInstanceIdentifier',
    'GroupId',
    'OwnerId',
    'TagList',
    'Tags',
    'UserName',
    'VolumeId',
    'VpcId',
    '__pytest_meta',
]


def extract_metadata(resource):
    return {
        metadata_key: resource[metadata_key]
        for metadata_key in METADATA_KEYS
        if metadata_key in resource
    }


def get_metadata_from_funcargs(funcargs):
    metadata = {}
    for k in funcargs:
        if isinstance(funcargs[k], dict):
            metadata = {**metadata, **extract_metadata(funcargs[k])}
    return metadata


def serialize_marker(marker):
    if isinstance(marker, (MarkDecorator, MarkInfo)):
        args = ['...skipped...'] if marker.name == 'parametrize' else marker.args
        kwargs = ['...skipped...'] if marker.name == 'parametrize' else marker.kwargs
        return {
            'name': marker.name,
            'args': args,
            'kwargs': kwargs,
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


def clean_docstring(docstr):
    """
    Transforms a docstring into a properly formatted single line string.

    >>> clean_docstring("\\nfoo\\n    bar\\n")
    'foo bar'
    >>> clean_docstring("foo bar")
    'foo bar'
    """
    return " ".join([word for word in docstr.replace("\n", " ").strip().split(" ") if word != ""])


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # only add this during call instead of during any stage
    if report.when == 'call' and not isinstance(item, DoctestItem):
        metadata = get_metadata_from_funcargs(item.funcargs)
        markers = {k: serialize_marker(v) for (k, v) in get_node_markers(item).items()}
        severity = markers.get('severity', None) and markers.get('severity')['args'][0]
        outcome, reason = get_outcome_and_reason(report, markers, call)
        rationale = markers.get('rationale', None) and \
            clean_docstring(markers.get('rationale')['args'][0])
        description = item._obj.__doc__ and clean_docstring(item._obj.__doc__)

        # add json metadata
        report.test_metadata = dict(
            description=description,
            markers=markers,
            metadata=metadata,
            outcome=outcome,  # 'passed', 'failed', 'skipped', 'xfailed', 'xskipped', or 'errored'
            parametrized_name=item.name,
            rationale=rationale,
            reason=reason,
            severity=severity,
            unparametrized_name=item.originalname,
        )

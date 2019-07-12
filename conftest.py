import argparse
import datetime

import pytest

from _pytest.doctest import DoctestItem
from _pytest.mark import MarkInfo, MarkDecorator
from cache import patch_cache_set
from aws.client import BotocoreClient
from gcp.client import GCPClient
from gsuite.client import GsuiteClient
from heroku.client import HerokuAdminClient
from github.client import GitHubClient

import custom_config


botocore_client = None
gcp_client = None
gsuite_client = None
heroku_client = None
github_client = None


def pytest_addoption(parser):
    parser.addoption('--aws-profiles',
                     nargs='*',
                     help='Set default AWS profiles to use. Defaults to the current AWS profile i.e. [None].')

    parser.addoption('--gcp-project-id',
                     type=str,
                     help='Set GCP project to test. Required for GCP tests.')

    # While only used for Heroku at the moment, GitHub tests are soon to be
    # added, which will also need an "organization" option. Current plan is to
    # reuse this one.
    parser.addoption('--heroku-organization',
                     default="mozillacorporation",
                     type=str,
                     help='Set Heroku organization (aka team) to test.')

    parser.addoption('--github-organization',
                     default="mozilla-services",
                     type=str,
                     help='Set GitHub organization to test.')

    parser.addoption('--debug-calls',
                     action='store_true',
                     help='Log API calls. Requires -s')

    parser.addoption('--debug-cache',
                     action='store_true',
                     help='Log whether API calls hit the cache. Requires -s')

    parser.addoption('--offline',
                     action='store_true',
                     default=False,
                     help='Instruct service clients to return empty lists and not make HTTP requests.')

    parser.addoption('--config',
                     type=argparse.FileType('r'),
                     help='Path to the config file.')


    parser.addoption('--date',
                     type=str,
                     default=datetime.datetime.utcnow().strftime('%Y-%m-%d'),
                     help='Date to test, defaults to UTC now.')

    parser.addoption('--data-dir',
                     type=str,
                     default=".",
                     help='Where to expect & store files.')


def pytest_configure(config):
    global botocore_client
    global gcp_client
    global gsuite_client
    global heroku_client
    global github_client

    # monkeypatch cache.set to serialize datetime.datetime's
    patch_cache_set(config)

    profiles = config.getoption('--aws-profiles')
    project_id = config.getoption('--gcp-project-id')
    heroku_organization = config.getoption('--heroku-organization')
    github_organization = config.getoption('--github-organization')

    botocore_client = BotocoreClient(
        profiles=profiles,
        cache=config.cache,
        debug_calls=config.getoption('--debug-calls'),
        debug_cache=config.getoption('--debug-cache'),
        offline=config.getoption('--offline'))

    gcp_client = GCPClient(
        project_id=project_id,
        cache=config.cache,
        debug_calls=config.getoption('--debug-calls'),
        debug_cache=config.getoption('--debug-cache'),
        offline=config.getoption('--offline'))

    heroku_client = HerokuAdminClient(
        organization=heroku_organization,
        # cache=config.cache,
        cache=None,
        debug_calls=config.getoption('--debug-calls'),
        debug_cache=config.getoption('--debug-cache'),
        offline=config.getoption('--offline'))

    github_client = GitHubClient(
        organization=github_organization,
        report_date=config.getoption('--date'),
        data_dir=config.getoption('--data-dir'),
        # cache=config.cache,
        cache=None,
        debug_calls=config.getoption('--debug-calls'),
        debug_cache=config.getoption('--debug-cache'),
        offline=config.getoption('--offline'))

    config.custom_config = custom_config.CustomConfig(config.getoption('--config'))

    if any(x for x in config.args if 'gsuite' in x):
        gsuite_client = GsuiteClient(domain=config.custom_config.gsuite.domain, offline=config.getoption('--offline'))
    else:
        gsuite_client = GsuiteClient(domain='', offline=True)


@pytest.fixture
def aws_config(pytestconfig):
    return pytestconfig.custom_config.aws


def pytest_runtest_setup(item):
    """
    """
    if not isinstance(item, DoctestItem):
        item.config.custom_config.add_markers(item)


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
    # used for GitHub compliance
    'org',
    'repo',
    'branch',
    'date',
]


def extract_metadata(resource):
    return {
        metadata_key: resource[metadata_key]
        for metadata_key in METADATA_KEYS
        if metadata_key in resource
    }


# it's only considered metadata if both:
#  - the argument is a dictionary, AND
#  - a key is in the list of METADATA_KEYS
def get_metadata_from_funcargs(funcargs):
    metadata = {}
    # also search **kwargs of calling func
    metadata.update(**extract_metadata(funcargs))
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
        #import pudb; pudb.set_trace()
        markers = {k: serialize_marker(v) for (k, v) in get_node_markers(item).items()}
        severity = markers.get('severity', None) and markers.get('severity')['args'][0]
        regression = markers.get('regression', None) and markers.get('regression')['args'][0]
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
            regression=regression,
            unparametrized_name=item.originalname,
        )

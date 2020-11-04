import argparse
import datetime

import pytest

from _pytest.doctest import DoctestItem
from _pytest.mark import Mark, MarkDecorator
from cache import patch_cache_set
from aws.client import BotocoreClient
from gcp.client import GCPClient
from gsuite.client import GsuiteClient

import custom_config

botocore_client = None
gcp_client = None
gsuite_client = None
custom_config_global = None


def pytest_addoption(parser):
    frost_parser = parser.getgroup("Frost", "Frost's custom arguments")
    frost_parser.addoption(
        "--aws-profiles",
        nargs="*",
        help="Set default AWS profiles to use. Defaults to the current AWS profile i.e. [None].",
    )

    frost_parser.addoption(
        "--aws-regions",
        type=str,
        help="Set AWS regions to use as a comma separate list. Defaults to all available AWS regions",
    )

    frost_parser.addoption(
        "--gcp-project-id", type=str, help="Set GCP project to test.",
    )

    frost_parser.addoption(
        "--gcp-folder-id",
        type=str,
        help="Set GCP folder to test. Will test all projects under this folder.",
    )

    # While only used for Heroku at the moment, GitHub tests are soon to be
    # added, which will also need an "organization" option. Current plan is to
    # reuse this one.
    frost_parser.addoption(
        "--organization",
        type=str,
        help="Set organization to test. Used for Heroku tests.",
    )

    frost_parser.addoption(
        "--debug-calls", action="store_true", help="Log API calls. Requires -s"
    )

    frost_parser.addoption(
        "--debug-cache",
        action="store_true",
        help="Log whether API calls hit the cache. Requires -s",
    )

    frost_parser.addoption(
        "--offline",
        action="store_true",
        default=False,
        help="Instruct service clients to return empty lists and not make HTTP requests.",
    )

    frost_parser.addoption(
        "--config", type=argparse.FileType("r"), help="Path to the config file."
    )


def pytest_configure(config):
    global botocore_client
    global gcp_client
    global gsuite_client
    global custom_config_global

    # run with -p 'no:cacheprovider'
    cache = config.cache if hasattr(config, "cache") else None
    if cache:
        # monkeypatch cache.set to serialize datetime.datetime's
        patch_cache_set(config)

    profiles = config.getoption("--aws-profiles")
    aws_regions = (
        config.getoption("--aws-regions").split(",")
        if config.getoption("--aws-regions")
        else []
    )

    project_id = config.getoption("--gcp-project-id")
    folder_id = config.getoption("--gcp-folder-id")
    if project_id is not None and folder_id is not None:
        raise Exception(
            "--gcp-project-id and --gcp-folder-id are mutually exclusive arguments"
        )

    organization = config.getoption("--organization")

    botocore_client = BotocoreClient(
        profiles=profiles,
        regions=aws_regions,
        cache=cache,
        debug_calls=config.getoption("--debug-calls"),
        debug_cache=config.getoption("--debug-cache"),
        offline=config.getoption("--offline"),
    )

    gcp_client = GCPClient(
        project_id=project_id,
        folder_id=folder_id,
        cache=cache,
        debug_calls=config.getoption("--debug-calls"),
        debug_cache=config.getoption("--debug-cache"),
        offline=config.getoption("--offline"),
    )

    custom_config_global = custom_config.CustomConfig(config.getoption("--config"))
    config.custom_config = custom_config_global

    try:
        if any(x for x in config.args if "gsuite" in x):
            gsuite_client = GsuiteClient(
                domain=config.custom_config.gsuite.domain,
                offline=config.getoption("--offline"),
            )
        else:
            gsuite_client = GsuiteClient(domain="", offline=True)
    except AttributeError as e:
        gsuite_client = GsuiteClient(domain="", offline=True)

    # register custom marker for rationale (used in report)
    config.addinivalue_line(
        "markers",
        "rationale(reason): (optional) rationale behind the test. (null if not set)",
    )


@pytest.fixture
def aws_config(pytestconfig):
    return pytestconfig.custom_config.aws


@pytest.fixture
def gcp_config(pytestconfig):
    return pytestconfig.custom_config.gcp


def pytest_runtest_setup(item):
    """
    Add custom markers to pytest tests.
    """
    if not isinstance(item, DoctestItem):
        item.config.custom_config.add_markers(item)


# Reporting


def get_node_markers(node):
    return [m for m in node.iter_markers()]


# METADATA_KEYS are modified by services to specify which metadata is
# relevant for the JSON output. It's unlikely that duplicate keys are
# intended, so failfast
# adapted from
# https://stackoverflow.com/questions/41281346/how-to-raise-error-if-user-tries-to-enter-duplicate-entries-in-a-set-in-python/41281734#41281734
class DuplicateKeyError(Exception):
    pass


class SingleSet(set):
    """Set only allowing values to be added once

    When addition of a duplicate value is detected, the `DuplicateKeyError`
    exception will be raised, all non duplicate values are added to the set.

    Raises:
        DuplicateKeyError - when adding a value already in the set

    >>> ss = SingleSet({1, 2, 3, 4})
    >>> ss.add(3)
    Traceback (most recent call last):
    ...
    conftest.DuplicateKeyError: Value 3 already present
    >>> ss.update({4, 5, 6, 3})
    Traceback (most recent call last):
    ...
    conftest.DuplicateKeyError: Value(s) {3, 4} already present
    >>> ss
    SingleSet({1, 2, 3, 4, 5, 6})
    >>>

    **NB:**
    - duplicate values on initialization are not detected
    >>> ss = SingleSet({1, 2, 3, 4, 3, 2, 1})
    >>> ss
    SingleSet({1, 2, 3, 4})
    """

    def add(self, value):
        if value in self:
            raise DuplicateKeyError("Value {!r} already present".format(value))
        super().add(value)

    def update(self, values):
        error_values = set()
        for value in values:
            if value in self:
                error_values.add(value)
        if error_values:
            # we want the non-duplicate values added
            super().update(values - error_values)
            raise DuplicateKeyError(
                "Value(s) {!r} already present".format(error_values)
            )
        super().update(values)


METADATA_KEYS: SingleSet = SingleSet(
    [
        "DBInstanceArn",
        "DBInstanceIdentifier",
        "GroupId",
        "ImageId",
        "InstanceId",
        "LaunchTime",
        "OwnerId",
        "TagList",
        "Tags",
        "UserName",
        "VolumeId",
        "VpcId",
        "__pytest_meta",
        "displayName",
        "id",
        "kind",
        "members",
        "name",
        "project",
        "projectId",
        "role",
        "uniqueId",
    ]
)


def serialize_datetimes(obj):
    """Serializes datetimes to ISO format strings.

    Used on report test_metadata since pytest-json doesn't let us pass
    options to the serializer.

    >>> from datetime import datetime
    >>> serialize_datetimes({datetime(2000, 1, 1): -1})
    {'2000-01-01T00:00:00': -1}
    >>> serialize_datetimes({'foo': datetime(2000, 1, 1)})
    {'foo': '2000-01-01T00:00:00'}
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, list):
        return [serialize_datetimes(item) for item in obj]
    elif isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            new_obj[serialize_datetimes(k)] = serialize_datetimes(v)
        return new_obj

    return obj


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
    if isinstance(marker, (MarkDecorator, Mark)):
        args = ["...skipped..."] if marker.name == "parametrize" else marker.args
        kwargs = ["...skipped..."] if marker.name == "parametrize" else marker.kwargs
        return {"name": marker.name, "args": args, "kwargs": kwargs}
    else:
        raise NotImplementedError("Unexpected Marker type %s" % repr(marker))


def get_outcome_and_reason(report, markers, call):
    xfail = "xfail" in markers
    xpass = report.passed and xfail

    if (
        call.excinfo
        and not isinstance(call.excinfo, AssertionError)
        and isinstance(call.excinfo, Exception)
    ):
        return "errored", call.excinfo
    elif xpass:
        return "xpassed", markers["xfail"]["kwargs"].get("reason", None)
    elif xfail:
        return "xfailed", markers["xfail"]["kwargs"].get("reason", None)
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
    return " ".join(
        [word for word in docstr.replace("\n", " ").strip().split(" ") if word != ""]
    )


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # only add this during call instead of during any stage
    if report.when == "call" and not isinstance(item, DoctestItem):
        metadata = get_metadata_from_funcargs(item.funcargs)
        markers = {n.name: serialize_marker(n) for n in get_node_markers(item)}
        severity = markers.get("severity", None) and markers.get("severity")["args"][0]
        regression = (
            markers.get("regression", None) and markers.get("regression")["args"][0]
        )
        outcome, reason = get_outcome_and_reason(report, markers, call)
        rationale = markers.get("rationale", None) and clean_docstring(
            markers.get("rationale")["args"][0]
        )
        description = item._obj.__doc__ and clean_docstring(item._obj.__doc__)

        # add json metadata
        report.test_metadata = serialize_datetimes(
            dict(
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
        )

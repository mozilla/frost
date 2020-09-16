from datetime import datetime, timezone

from _pytest.compat import NOTSET
import pytest

from helpers import get_param_id

from aws.elb.resources import elbs_with_attributes


@pytest.mark.elb
@pytest.mark.parametrize(
    "elb_with_attrs",
    elbs_with_attributes(),
    ids=lambda e: get_param_id(e[0], "LoadBalancerName") if e != NOTSET else None,
)
def test_elb_instance_desync_mode(elb_with_attrs):
    """
    Checks ELB HTTP desync mode:

    * is not 'monitor' mode

    >>> test_elb_instance_desync_mode((
    ...     {"LoadBalancerName": "old-doctest-elb", "CreatedTime": datetime(2020, 9, 1).astimezone(tz=timezone.utc), },
    ...     {"AdditionalAttributes": [{"Key": "elb.http.desyncmitigationmode", "Value": "monitor"}]},
    ... ))
    Traceback (most recent call last):
        ...
    AssertionError: ELB old-doctest-elb using desync monitor mode
    assert 'monitor' != 'monitor'
    >>> test_elb_instance_desync_mode((
    ...     {"LoadBalancerName": "new-doctest-elb", "CreatedTime": datetime(2020, 10, 1).astimezone(tz=timezone.utc), },
    ...     {"AdditionalAttributes": [{"Key": "elb.http.desyncmitigationmode", "Value": "monitor"}]},
    ... ))
    Traceback (most recent call last):
        ...
    AssertionError: ELB new-doctest-elb using desync monitor mode
    assert 'monitor' != 'monitor'

    * is 'defensive' or 'strictest' for ELBs created <= 2020-09-01

    >>> test_elb_instance_desync_mode((
    ...     {"LoadBalancerName": "old-doctest-elb", "CreatedTime": datetime(2020, 9, 1).astimezone(tz=timezone.utc), },
    ...     {"AdditionalAttributes": [{"Key": "elb.http.desyncmitigationmode", "Value": "strictest"}]},
    ... ))
    >>> test_elb_instance_desync_mode((
    ...     {"LoadBalancerName": "old-doctest-elb", "CreatedTime": datetime(2020, 9, 1).astimezone(tz=timezone.utc), },
    ...     {"AdditionalAttributes": [{"Key": "elb.http.desyncmitigationmode", "Value": "defensive"}]},
    ... ))

    * is 'strictest' for ELBs created > 2020-09-01

    >>> test_elb_instance_desync_mode((
    ...     {"LoadBalancerName": "new-doctest-elb", "CreatedTime": datetime(2020, 10, 1).astimezone(tz=timezone.utc), },
    ...     {"AdditionalAttributes": [{"Key": "elb.http.desyncmitigationmode", "Value": "strictest"}]},
    ... ))
    >>> test_elb_instance_desync_mode((
    ...     {"LoadBalancerName": "new-doctest-elb", "CreatedTime": datetime(2020, 10, 1).astimezone(tz=timezone.utc), },
    ...     {"AdditionalAttributes": [{"Key": "elb.http.desyncmitigationmode", "Value": "defensive"}]},
    ... ))
    Traceback (most recent call last):
        ...
    AssertionError: ELB new-doctest-elb (created 2020-10-01) using desync mode defensive instead of {'strictest'}
    assert 'defensive' in {'strictest'}

    """
    elb, attrs = elb_with_attrs
    elb_name = elb["LoadBalancerName"]

    for attr in attrs["AdditionalAttributes"]:
        if attr["Key"] == "elb.http.desyncmitigationmode":
            desync_mode = attr["Value"]
            break

    created_time = elb["CreatedTime"]
    assert desync_mode != "monitor", "ELB {} using desync monitor mode".format(elb_name)

    if created_time <= datetime(2020, 9, 1).astimezone(tz=timezone.utc):
        acceptable_modes = {"defensive", "strictest"}
    else:
        acceptable_modes = {"strictest"}

    assert (
        desync_mode in acceptable_modes
    ), "ELB {} (created {}) using desync mode {} instead of {}".format(
        elb_name, created_time.date(), desync_mode, acceptable_modes
    )

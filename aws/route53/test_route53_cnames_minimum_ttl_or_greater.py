import pytest

from aws.route53.resources import zones, cnames
from helpers import get_param_id


MINIMUM_TTL = 600


@pytest.mark.parametrize(
    "cnames", cnames(), ids=lambda record: get_param_id(record, "Name")
)
def test_route53_cnames_minimum_ttl_or_greater(cnames):
    """
    Tests that CNAMEs in Route53 have a TTL of 600 seconds or more.
    """
    assert (
        int(cnames["TTL"]) >= MINIMUM_TTL
    ), f"TTL is below the minimum of {MINIMUM_TTL}, it is currently set to {cnames['TTL']}"

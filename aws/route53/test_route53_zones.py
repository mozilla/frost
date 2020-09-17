import pytest

from aws.route53.resources import zones, cnames
from helpers import get_param_id


@pytest.mark.parametrize(
    "cnames", cnames(), ids=lambda record: get_param_id(record, "Name")
)
def test_route53_cnames(cnames):
    assert int(cnames["TTL"]) >= 600, f"TTL is {cnames['TTL']}"

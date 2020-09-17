import pytest

from aws.route53.resources import zones, cnames


@pytest.mark.parametrize(
    "cnames", cnames(),
)
def test_route53_cnames(cnames):
    assert int(cnames["TTL"]) >= 600, f"{cnames['Name']} TTL is {cnames['TTL']}"

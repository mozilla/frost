import pytest

from aws.route53.resources import zones, cnames

# @pytest.mark.route53
# @pytest.mark.parametrize(
#     "zone", zones(),
# )
# def test_route53_zones(zone):
#     assert (len(zone)) > 0

@pytest.mark.route53
@pytest.mark.parametrize(
    "cnames", cnames(),
)
def test_route53_cnames(cnames):
    assert (len(cnames)) > 0

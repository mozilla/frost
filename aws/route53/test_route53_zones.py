import pytest

from aws.route53.resources import zones, names_in_zone

@pytest.mark.route53
@pytest.mark.parametrize(
    "zone", zones(),
)
def test_route53_zones(zone):
    zone_id = zone['Id'].split('/')[2]
    print(zone_id)
    names_in_zone(zone_id)
    assert (len(zone)) > 0

import pytest

from conftest import botocore_client

from aws.cloudtrail.resources import cloudtrails


@pytest.fixture
def all_cloudtrails():
    return cloudtrails()


@pytest.mark.cloudtrail
@pytest.mark.parametrize("aws_region", botocore_client.get_regions())
def test_cloudtrail_enabled_in_all_regions(aws_region, all_cloudtrails):
    """
    Tests that all regions have an associated cloudtrail or that there is a cloudtrail for all regions.
    """
    assert any(
        trail
        for trail in all_cloudtrails
        if trail["HomeRegion"] == aws_region or trail["IsMultiRegionTrail"]
    )

import pytest

from conftest import botocore_client

from aws.cloudtrail.resources import cloudtrails


@pytest.mark.cloudtrail
@pytest.mark.parametrize('aws_region',
                         botocore_client.regions,
                         ids=lambda region: region)
def test_cloudtrail_enabled_in_all_regions(aws_region):
    """
    Tests that all regions have an associated cloudtrail or that there is a cloudtrail for all regions.
    """
    trails = cloudtrails()
    assert any(
        trail for trail in trails
        if trail['HomeRegion'] == aws_region or trail['IsMultiRegionTrail']
    )

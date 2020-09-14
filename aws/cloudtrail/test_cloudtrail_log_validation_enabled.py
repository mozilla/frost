import pytest

from helpers import get_param_id

from aws.cloudtrail.resources import cloudtrails


@pytest.mark.cloudtrail
@pytest.mark.parametrize(
    "cloudtrail", cloudtrails(), ids=lambda trail: get_param_id(trail, "Name"),
)
def test_cloudtrail_log_validation_enabled(cloudtrail):
    """
    Tests that all Cloudtrails have log validation enabled.
    """
    assert cloudtrail["LogFileValidationEnabled"]

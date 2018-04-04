import pytest

from aws.cloudtrail.resources import cloudtrails


@pytest.mark.cloudtrail
@pytest.mark.parametrize('cloudtrail',
                         cloudtrails(),
                         ids=lambda trail: trail['Name'])
def test_cloudtrail_log_validation_enabled(cloudtrail):
    """
    Tests that all Cloudtrails have log validation enabled.
    """
    assert cloudtrail['LogFileValidationEnabled']

import pytest

from aws.ec2.helpers import ec2_instance_test_id
from aws.ec2.resources import ec2_instances


@pytest.fixture
def required_amis(pytestconfig):
    return frozenset(pytestconfig.custom_config.aws.required_amis)


@pytest.mark.ec2
@pytest.mark.parametrize("ec2_instance", ec2_instances(), ids=ec2_instance_test_id)
def test_ec2_instance_running_required_amis(ec2_instance, required_amis):
    """
    Checks that all EC2 instances are running the required AMIs.
    """
    if len(required_amis) == 0:
        pytest.skip("No required AMIs were provided")

    assert (
        ec2_instance["ImageId"] in required_amis
    ), "EC2 Instance {0[InstanceId]} is running unexpected AMI: {0[ImageId]}".format(
        ec2_instance
    )

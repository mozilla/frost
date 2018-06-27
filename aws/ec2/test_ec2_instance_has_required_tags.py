import pytest

from aws.ec2.helpers import ec2_instance_test_id, ec2_instance_missing_tag_names
from aws.ec2.resources import ec2_instances


@pytest.fixture
def required_tag_names(pytestconfig):
    return frozenset(pytestconfig.custom_config.aws.required_tags)


@pytest.mark.ec2
@pytest.mark.parametrize("ec2_instance", ec2_instances(), ids=ec2_instance_test_id)
def test_ec2_instance_has_required_tags(ec2_instance, required_tag_names):
    """
    Checks that all EC2 instances have the tags with the required names.

    Does not check tag values.
    """
    if len(required_tag_names) == 0:
        pytest.skip("No required tag names were provided")
    missing_tag_names = ec2_instance_missing_tag_names(ec2_instance, required_tag_names)
    assert (
        not missing_tag_names
    ), "EC2 Instance {0[InstanceId]} missing required tags {1!r}".format(
        ec2_instance, missing_tag_names
    )

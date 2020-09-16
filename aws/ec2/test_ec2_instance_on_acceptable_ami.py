import pytest

from aws.ec2.helpers import ec2_instance_test_id
from aws.ec2.resources import ec2_instances, ec2_images_owned_by

from datetime import datetime, timedelta, timezone


@pytest.fixture
def owned_amis(pytestconfig):
    return ec2_images_owned_by(pytestconfig.custom_config.aws.owned_ami_account_ids)


@pytest.fixture
def max_ami_age(pytestconfig):
    return pytestconfig.custom_config.aws.max_ami_age_in_days


@pytest.mark.ec2
@pytest.mark.parametrize("ec2_instance", ec2_instances(), ids=ec2_instance_test_id)
def test_ec2_instance_on_acceptable_ami(ec2_instance, owned_amis, max_ami_age):
    """
    Checks that all EC2 instances are running on acceptable AMIs, meaning
    an AMI that is not older than X days and is owned by us.
    Default is 180 days.
    """
    for tag in ec2_instance["Tags"]:
        if tag["Key"] == "Name":
            instanceName = tag["Value"]

    minAge = datetime.now(timezone.utc) - timedelta(days=max_ami_age)
    foundAmi = False
    for ami in owned_amis:
        if ami["ImageId"] == ec2_instance["ImageId"]:
            assert (
                ami["CreationDate"] > minAge
            ), "Instance {} {} is running on an AMI created on {} that's older than 180 days".format(
                instanceName, ec2_instance["InstanceId"], ami["CreationDate"]
            )
            foundAmi = True
            break

    if not foundAmi:
        assert False, "Instance {} {} uses AMI {} not owned by us".format(
            instanceName, ec2_instance["InstanceId"], ec2_instance["ImageId"]
        )

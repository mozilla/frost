import pytest

from aws.ec2.helpers import ec2_instance_test_id
from aws.ec2.resources import ec2_instances, ec2_images_owned_by

from datetime import datetime, timedelta


@pytest.fixture
def owned_amis():
    return ec2_images_owned_by()


@pytest.mark.ec2
@pytest.mark.parametrize("ec2_instance", ec2_instances(), ids=ec2_instance_test_id)
def test_ec2_instance_on_acceptable_ami(ec2_instance, owned_amis,):
    """
    Checks that all EC2 instances are running on acceptable AMIs, meaning
    an AMI that is no only than 180 and is owned by us.
    """
    for tag in ec2_instance["Tags"]:
        if tag["Key"] == "Name":
            instanceName = tag["Value"]

    nightyDaysAgo = datetime.now() - timedelta(days=180)
    foundAmi = False
    for ami in owned_amis:
        if ami["ImageId"] == ec2_instance["ImageId"]:
            # assert ami age < 180 days
            assert(ami["CreationDate"] > nightyDaysAgo), "Instance {} {} is running on an AMI created on {} that's older than 180 days".format(
                instanceName, ec2_instance["InstanceId"], ami["CreationDate"]
            )
            foundAmi = True
            break

    if not foundAmi:
        assert False, "Instance {} {} uses AMI {} not owned by us".format(
            instanceName, ec2_instance["InstanceId"], ec2_instance["ImageId"]
        )

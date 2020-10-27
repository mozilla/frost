import pytest

from helpers import get_param_id

from aws.ec2.resources import ec2_ebs_volumes
from aws.ec2.helpers import ebs_volume_attached_to_instance


@pytest.mark.ec2
@pytest.mark.parametrize(
    "ec2_ebs_volume", ec2_ebs_volumes(), ids=lambda ebs: get_param_id(ebs, "VolumeId")
)
def test_ec2_ebs_volume_attached_to_instance(ec2_ebs_volume):
    """Normally cloudops would like to have all EBS volumes attached to
    instances once they are created, for the purpose of cost saving, thus we
    have this check. There is a default 90 day grace period though for the ebs
    volumes, e.g. a volume may not be attached to any instance for 90 days.
    """
    assert ebs_volume_attached_to_instance(
        ec2_ebs_volume
    ), f"{ec2_ebs_volume['VolumeId']} is created at {ec2_ebs_volume['CreateTime']}, and is not attached to an instance."

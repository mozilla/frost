import pytest

from helpers import get_param_id

from aws.ec2.resources import ec2_ebs_volumes
from aws.ec2.helpers import is_ebs_volume_piops


@pytest.mark.ec2
@pytest.mark.parametrize(
    "ec2_ebs_volume", ec2_ebs_volumes(), ids=lambda ebs: get_param_id(ebs, "VolumeId")
)
def test_ec2_ebs_volume_not_piops(ec2_ebs_volume):
    assert not is_ebs_volume_piops(ec2_ebs_volume)

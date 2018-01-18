import pytest

from aws.ec2.resources import ec2_ebs_volumes

def is_ebs_volume_encrypted(ec2_ebs_volume):
    return bool(ec2_ebs_volume['Encrypted'])

@pytest.mark.ec2
@pytest.mark.parametrize('ec2_ebs_volume', ec2_ebs_volumes())
def test_ec2_ebs_volume_encrypted(ec2_ebs_volume):
    assert is_ebs_volume_encrypted(ec2_ebs_volume)

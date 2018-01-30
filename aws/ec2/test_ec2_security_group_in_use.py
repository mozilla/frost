import pytest

from aws.ec2.resources import \
    ec2_security_groups_with_in_use_flag

@pytest.mark.ec2
@pytest.mark.parametrize('ec2_security_group',
                         ec2_security_groups_with_in_use_flag(),
                         ids=lambda secgroup: secgroup['GroupName'])
def test_ec2_security_group_in_use(ec2_security_group):
    assert ec2_security_group["InUse"], "Security group is not currently attached to any instance."

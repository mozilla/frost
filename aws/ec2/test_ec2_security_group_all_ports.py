

import pytest


from aws.ec2.resources import (
    ec2_security_groups,
)


def ec2_security_group_has_all_ports(ec2_security_group):
    """
    Check if ec2 security group permits all ports.
    """
    if 'IpPermissions' not in ec2_security_group:
        return False
    try:
        ipp = ec2_security_group['IpPermissions'][0]
    except IndexError:
        return False
    if 'FromPort' not in ipp or 'ToPort' not in ipp:
        return False
    if ipp['FromPort'] <= 1 and ipp['ToPort'] >= 65535:
        return True
    return False


@pytest.mark.ec2
@pytest.mark.parametrize('ec2_security_group',
                         ec2_security_groups(),
                         ids=lambda secgroup: '{0[GroupId]} {0[GroupName]}'.format(secgroup))
def test_ec2_security_group_all_ports(ec2_security_group):
    assert not ec2_security_group_has_all_ports(ec2_security_group)

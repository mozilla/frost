

import pytest

from aws.ec2.helpers import (
    ec2_security_group_test_id,
    ec2_security_group_opens_specific_ports_to_all,
)
from aws.ec2.resources import (
    ec2_security_groups_with_in_use_flag,
)


@pytest.mark.ec2
@pytest.mark.parametrize('ec2_security_group',
                         ec2_security_groups_with_in_use_flag(),
                         ids=ec2_security_group_test_id)
def test_ec2_security_group_opens_specific_ports_to_all(ec2_security_group):
    """Checks whether an EC2 security group includes a permission allowing
    inbound access on specific ports. Excluded ports are 80 and 443.
    """
    if ec2_security_group["InUse"]:
        # Additional ports can be whitelisted with --aws-whitelisted-ports
        assert not ec2_security_group_opens_specific_ports_to_all(ec2_security_group)
    else:
        pytest.skip("Security group not in use")

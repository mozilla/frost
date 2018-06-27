import pytest

from aws.ec2.helpers import ec2_security_group_test_id
from aws.ec2.resources import ec2_security_groups_with_in_use_flag


@pytest.mark.ec2
@pytest.mark.rationale(
    """
Having unused security groups adds cruft in an AWS account, increases the
likelihood of a mistake, and makes security testing harder.
"""
)
@pytest.mark.parametrize(
    "ec2_security_group",
    ec2_security_groups_with_in_use_flag(),
    ids=ec2_security_group_test_id,
)
def test_ec2_security_group_in_use(ec2_security_group):
    """Checks to make sure that the security group
    is currently attached to at least one EC2 instance
    """
    assert ec2_security_group[
        "InUse"
    ], "Security group is not currently attached to any instance."

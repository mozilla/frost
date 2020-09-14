import pytest

from aws.rds.resources import rds_db_security_groups
from aws.rds.helpers import (
    does_rds_db_security_group_grant_public_access,
    get_db_security_group_arn,
)


@pytest.mark.rds
@pytest.mark.parametrize(
    "rds_db_security_group", rds_db_security_groups(), ids=get_db_security_group_arn,
)
def test_rds_db_security_group_does_not_grant_public_access(rds_db_security_group):
    """
    Checks whether any RDS security group allows for inbound
    access from the public internet
    """
    assert not does_rds_db_security_group_grant_public_access(rds_db_security_group)

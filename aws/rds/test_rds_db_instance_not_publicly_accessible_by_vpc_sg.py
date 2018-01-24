import pytest

from aws.rds.resources import (
    rds_db_instances,
    rds_db_instances_vpc_security_groups,
)
from aws.rds.helpers import \
    does_vpc_security_group_grant_public_access


@pytest.mark.rds
@pytest.mark.parametrize(
    ['rds_db_instance', 'ec2_security_groups'],
    zip(rds_db_instances(), rds_db_instances_vpc_security_groups()),
    ids=lambda db_instance: db_instance['DBInstanceIdentifier']
)
def test_rds_db_instance_not_publicly_accessible_by_vpc_security_group(rds_db_instance, ec2_security_groups):
    if not ec2_security_groups:
        assert not rds_db_instance['VpcSecurityGroups']
    else:
        assert set(sg['GroupId'] for sg in ec2_security_groups) == \
          set(sg['VpcSecurityGroupId'] for sg in rds_db_instance['VpcSecurityGroups'])

        assert not any(does_vpc_security_group_grant_public_access(sg) for sg in ec2_security_groups)

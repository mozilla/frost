import pytest

from aws.rds.resources import (
    rds_db_instances_with_tags,
    rds_db_instances_vpc_security_groups,
)
from aws.rds.helpers import (
    does_vpc_security_group_grant_public_access,
    get_db_instance_id,
)


@pytest.mark.rds
@pytest.mark.parametrize(
    ["rds_db_instance", "ec2_security_groups"],
    zip(rds_db_instances_with_tags(), rds_db_instances_vpc_security_groups()),
    ids=lambda db: get_db_instance_id(db)
    if isinstance(db, dict) and "DBInstanceIdentifier" in db
    else "secgroups",
)
def test_rds_db_instance_not_publicly_accessible_by_vpc_security_group(
    rds_db_instance, ec2_security_groups
):
    """
    Checks whether any VPC/EC2 security groups that are attached to an RDS instance
    allow for access from the public internet.
    """
    if not ec2_security_groups:
        assert not rds_db_instance["VpcSecurityGroups"]
    else:
        assert set(sg["GroupId"] for sg in ec2_security_groups) == set(
            sg["VpcSecurityGroupId"] for sg in rds_db_instance["VpcSecurityGroups"]
        )

        assert not any(
            does_vpc_security_group_grant_public_access(sg)
            for sg in ec2_security_groups
        )

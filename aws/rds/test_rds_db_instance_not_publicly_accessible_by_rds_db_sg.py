
import pytest

from aws.rds.resources import (
    rds_db_instances,
    rds_db_instance_db_security_groups,
)
from .test_rds_db_security_group_does_not_grant_public_access import does_rds_db_security_group_grant_public_access


@pytest.mark.rds
@pytest.mark.parametrize(
    ['rds_db_instance', 'rds_db_security_groups'],
    zip(rds_db_instances(), rds_db_instance_db_security_groups()),
    ids=lambda db_instance: db_instance['DBInstanceIdentifier']
)
def test_rds_db_instance_not_publicly_accessible_by_rds_db_security_group(rds_db_instance, rds_db_security_groups):
    if not rds_db_security_groups:
        assert not rds_db_instance['DBSecurityGroups']
    else:
        assert set(sg['DBSecurityGroupName'] for sg in rds_db_security_groups) == \
          set(sg['DBSecurityGroupName'] for sg in rds_db_instance['DBSecurityGroups'])

        assert not any(does_rds_db_security_group_grant_public_access(sg) for sg in rds_db_security_groups)

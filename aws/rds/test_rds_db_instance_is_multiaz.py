
import pytest

from aws.rds.resources import rds_db_instances_with_tags


@pytest.mark.rds
@pytest.mark.parametrize('rds_db_instance',
                         rds_db_instances_with_tags(),
                         ids=lambda db_instance: db_instance['DBInstanceIdentifier'])
def test_rds_db_instance_is_multiaz(rds_db_instance):
    assert rds_db_instance['MultiAZ'] == False, '{} is in a single availability zone'.format(rds_db_instance['DBInstanceIdentifier'])

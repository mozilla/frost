
import pytest


@pytest.mark.rds
def test_rds_db_instance_is_multiaz(rds_db_instance):
    assert rds_db_instance['MultiAZ'] == False, '{} is in a single availability zone'.format(rds_db_instance['DBInstanceIdentifier'])

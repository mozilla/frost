
import pytest

from aws.rds.resources import rds_db_instances


@pytest.mark.rds
@pytest.mark.parametrize('rds_db_instance',
                         rds_db_instances(),
                         ids=lambda db_instance: db_instance['DBInstanceIdentifier'])
def test_rds_db_instance_backup_enabled(rds_db_instance):
    assert rds_db_instance['BackupRetentionPeriod'] > 0, \
        'Backups disabled for {}'.format(rds_db_instance['DBInstanceIdentifier'])

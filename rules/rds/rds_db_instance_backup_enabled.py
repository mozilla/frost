
import pytest


@pytest.mark.rds
def test_rds_db_instance_backup_enabled(rds_db_instance):
    assert rds_db_instance['BackupRetentionPeriod'] > 0, 'Backups disabled for {}'.format(rds_db_instance['DBInstanceIdentifier'])

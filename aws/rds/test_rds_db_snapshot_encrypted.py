import pytest

from aws.rds.resources import rds_db_snapshots
from aws.rds.helpers import is_rds_db_snapshot_encrypted


@pytest.mark.rds
@pytest.mark.parametrize('rds_db_snapshot',
                         rds_db_snapshots(),
                         ids=lambda snapshot: snapshot['DBSnapshotArn'])
def test_rds_db_snapshot_encrypted(rds_db_snapshot):
    assert is_rds_db_snapshot_encrypted(rds_db_snapshot)

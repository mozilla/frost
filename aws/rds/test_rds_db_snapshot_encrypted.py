import pytest

from aws.rds.resources import rds_db_snapshots
from aws.rds.helpers import is_rds_db_snapshot_encrypted, get_db_snapshot_arn


@pytest.mark.rds
@pytest.mark.parametrize(
    "rds_db_snapshot", rds_db_snapshots(), ids=get_db_snapshot_arn,
)
def test_rds_db_snapshot_encrypted(rds_db_snapshot):
    assert is_rds_db_snapshot_encrypted(rds_db_snapshot)

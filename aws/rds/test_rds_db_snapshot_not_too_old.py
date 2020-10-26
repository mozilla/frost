import pytest

from aws.rds.resources import rds_db_snapshots
from aws.rds.helpers import get_db_snapshot_arn, rds_db_snapshot_not_too_old


@pytest.mark.rds
@pytest.mark.parametrize(
    "rds_db_snapshot", rds_db_snapshots(), ids=get_db_snapshot_arn,
)
def test_rds_db_snapshot_not_too_old(rds_db_snapshot):
    assert rds_db_snapshot_not_too_old(
        rds_db_snapshot
    ), f"{rds_db_snapshot['DBSnapshotIdentifier']} is created at {rds_db_snapshot['SnapshotCreateTime']}, and is considered too old."

import pytest

from aws.rds.resources import rds_db_snapshots, rds_db_snapshot_attributes
from aws.rds.helpers import is_rds_db_snapshot_attr_public_access, get_rds_resource_id


@pytest.mark.rds
@pytest.mark.parametrize(
    ["rds_db_snapshot", "rds_db_snapshot_attributes"],
    zip(rds_db_snapshots(), rds_db_snapshot_attributes()),
    ids=get_rds_resource_id,
)
def test_rds_db_snapshot_not_publicly_accessible(
    rds_db_snapshot, rds_db_snapshot_attributes
):
    for attr in rds_db_snapshot_attributes:
        assert not is_rds_db_snapshot_attr_public_access(attr)

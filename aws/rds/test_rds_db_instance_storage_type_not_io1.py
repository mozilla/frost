import pytest

from aws.rds.helpers import get_db_instance_id
from aws.rds.resources import rds_db_instances_with_tags


@pytest.mark.rds
@pytest.mark.parametrize(
    "rds_db_instance", rds_db_instances_with_tags(), ids=get_db_instance_id,
)
def test_rds_db_instance_storage_type_not_io1(rds_db_instance):
    assert (
        rds_db_instance["StorageType"] != "io1"
    ), f"{rds_db_instance['DBInstanceIdentifier']} uses `io1' storage type with IOPs of {rds_db_instance['Iops']}"

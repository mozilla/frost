import pytest

from aws.rds.helpers import get_db_instance_id
from aws.rds.resources import rds_db_instances_with_tags


@pytest.mark.rds
@pytest.mark.parametrize(
    "rds_db_instance", rds_db_instances_with_tags(), ids=get_db_instance_id,
)
def test_rds_db_instance_storage_type_not_piops(rds_db_instance):
    """PIOPs storage type is expensive. Cloudops recommends using gp2 type with
    a volume size that offers the same IOPs as the desired PIOPs type.
    """
    assert not rds_db_instance["StorageType"].startswith(
        "io"
    ), f"{rds_db_instance['DBInstanceIdentifier']} uses PIOPs storage type with IOPs of {rds_db_instance['Iops']}"

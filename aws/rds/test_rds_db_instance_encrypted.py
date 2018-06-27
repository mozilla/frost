import pytest

from aws.rds.resources import rds_db_instances_with_tags
from aws.rds.helpers import is_rds_db_instance_encrypted


@pytest.mark.rds
@pytest.mark.parametrize(
    "rds_db_instance",
    rds_db_instances_with_tags(),
    ids=lambda db_instance: db_instance["DBInstanceIdentifier"],
)
def test_rds_db_instance_encrypted(rds_db_instance):
    assert is_rds_db_instance_encrypted(rds_db_instance)

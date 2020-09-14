import datetime
from botocore.utils import parse_timestamp

import pytest

from aws.rds.helpers import get_db_instance_id
from aws.rds.resources import rds_db_instances_with_tags


@pytest.mark.rds
@pytest.mark.parametrize(
    "rds_db_instance", rds_db_instances_with_tags(), ids=get_db_instance_id,
)
def test_rds_db_instance_is_postgres_with_invalid_certificate(rds_db_instance):
    if rds_db_instance["Engine"] != "postgres":
        pytest.skip("RDS DB instance engine is not Postgres.")

    if rds_db_instance["DBInstanceStatus"] == "creating":
        pytest.skip('RDS DB instance status is still "creating".')

    ict = rds_db_instance["InstanceCreateTime"]
    if isinstance(ict, str):
        ict = parse_timestamp(ict)

    assert ict > datetime.datetime(
        2014, 8, 5, tzinfo=datetime.timezone(datetime.timedelta(), "utc")
    )

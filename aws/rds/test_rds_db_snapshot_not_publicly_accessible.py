
import pytest

from aws.rds.resources import (
    rds_db_snapshots,
    rds_db_snapshots_attributes,
)


def is_rds_db_snapshot_attr_public_access(rds_db_snapshot_attribute):
    """
    Checks whether a RDS snapshot attribute is:

    {
        "AttributeName": "restore",
        "AttributeValues": ["random_aws_account_id", "any"]
    }

    >>> is_rds_db_snapshot_attr_public_access({"AttributeName": "restore", "AttributeValues": ["any"]})
    True
    >>> is_rds_db_snapshot_attr_public_access({"AttributeName": "restore", "AttributeValues": ["aws_account_id"]})
    False
    >>> is_rds_db_snapshot_attr_public_access({"AttributeName": "restore", "AttributeValues": []})
    False
    >>> is_rds_db_snapshot_attr_public_access({"AttributeName": "blorg", "AttributeValues": ["any"]})
    False
    >>> is_rds_db_snapshot_attr_public_access([])
    Traceback (most recent call last):
    ...
    TypeError: list indices must be integers or slices, not str
    >>> is_rds_db_snapshot_attr_public_access(0)
    Traceback (most recent call last):
    ...
    TypeError: 'int' object is not subscriptable
    >>> is_rds_db_snapshot_attr_public_access(None)
    Traceback (most recent call last):
    ...
    TypeError: 'NoneType' object is not subscriptable
    """
    return rds_db_snapshot_attribute['AttributeName'] == 'restore' \
      and 'any' in rds_db_snapshot_attribute['AttributeValues']


@pytest.mark.rds
@pytest.mark.parametrize(
    ['rds_db_snapshot', 'rds_db_snapshot_attributes'],
    zip(rds_db_snapshots(), rds_db_snapshots_attributes()),
    ids=lambda snapshot: snapshot['DBSnapshotArn'])
def test_rds_db_snapshot_not_publicly_accessible(rds_db_snapshot, rds_db_snapshot_attributes):
    for attr in rds_db_snapshot_attributes:
        assert not is_rds_db_snapshot_attr_public_access(attr)

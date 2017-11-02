
import pytest


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
def test_rds_db_snapshot_not_publicly_accessible(rds_db_snapshot, rds_db_snapshot_attributes_result):
    assert rds_db_snapshot['DBSnapshotIdentifier'] == rds_db_snapshot_attributes_result['DBSnapshotIdentifier']

    attrs = rds_db_snapshot_attributes_result['DBSnapshotAttributes']
    assert not any(is_rds_db_snapshot_attr_public_access(attr) for attr in attrs)

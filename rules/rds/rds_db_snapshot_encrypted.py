
import pytest


def is_rds_db_snapshot_encrypted(rds_db_snapshot):
    """
    Checks the RDS snapshot 'Encrypted' value.

    >>> is_rds_db_snapshot_encrypted({'Encrypted': True})
    True
    >>> is_rds_db_snapshot_encrypted({'Encrypted': False})
    False
    >>> is_rds_db_snapshot_encrypted({})
    Traceback (most recent call last):
    ...
    KeyError: 'Encrypted'
    >>> is_rds_db_snapshot_encrypted(0)
    Traceback (most recent call last):
    ...
    TypeError: 'int' object is not subscriptable
    >>> is_rds_db_snapshot_encrypted(None)
    Traceback (most recent call last):
    ...
    TypeError: 'NoneType' object is not subscriptable
    """
    return bool(rds_db_snapshot['Encrypted'])


@pytest.mark.rds
def test_rds_db_snapshot_encrypted(rds_db_snapshot):
    assert is_rds_db_snapshot_encrypted(rds_db_snapshot)

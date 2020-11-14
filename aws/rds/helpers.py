from datetime import datetime
from helpers import get_param_id


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
    return (
        rds_db_snapshot_attribute["AttributeName"] == "restore"
        and "any" in rds_db_snapshot_attribute["AttributeValues"]
    )


def does_rds_db_security_group_grant_public_access(sg):
    """
    Checks an RDS instance for a DB security group with CIDRIP 0.0.0.0/0

    >>> does_rds_db_security_group_grant_public_access(
    ... {"IPRanges": [{"CIDRIP": "127.0.0.1/32", "Status": "authorized"},
    ... {"CIDRIP": "0.0.0.0/0", "Status": "authorized"}]})
    True
    >>> does_rds_db_security_group_grant_public_access({"IPRanges": []})
    False
    """
    return any(
        ipr["CIDRIP"] == "0.0.0.0/0" and ipr["Status"] == "authorized"
        for ipr in sg["IPRanges"]
    )


def does_vpc_security_group_grant_public_access(sg):
    """
    Checks an RDS instance for a VPC security groups with ingress permission ipv4 range 0.0.0.0/0 or ipv6 range :::/0

    >>> does_vpc_security_group_grant_public_access(
    ... {'IpPermissions': [{'Ipv6Ranges': [], 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}]})
    True
    >>> does_vpc_security_group_grant_public_access(
    ... {'IpPermissions': [{'Ipv6Ranges': [], 'IpRanges': []}]})
    False
    >>> does_vpc_security_group_grant_public_access(
    ... {'IpPermissions': [{'Ipv6Ranges': [], 'IpRanges': [{'CidrIp': '192.168.1.0/0'}]}]})
    False
    """
    public_ipv4 = any(
        ipr["CidrIp"] == "0.0.0.0/0"
        for ipp in sg["IpPermissions"]
        for ipr in ipp["IpRanges"]
    )
    public_ipv6 = any(
        ipr["CidrIpv6"] == "::/0"
        for ipp in sg["IpPermissions"]
        for ipr in ipp["Ipv6Ranges"]
    )
    return public_ipv4 or public_ipv6


def is_rds_db_instance_encrypted(rds_db_instance):
    """
    Checks the RDS instance 'StorageEncrypted' value.

    >>> is_rds_db_instance_encrypted({'StorageEncrypted': True})
    True
    >>> is_rds_db_instance_encrypted({'StorageEncrypted': False})
    False
    >>> is_rds_db_instance_encrypted({})
    Traceback (most recent call last):
    ...
    KeyError: 'StorageEncrypted'
    >>> is_rds_db_instance_encrypted(0)
    Traceback (most recent call last):
    ...
    TypeError: 'int' object is not subscriptable
    >>> is_rds_db_instance_encrypted(None)
    Traceback (most recent call last):
    ...
    TypeError: 'NoneType' object is not subscriptable
    """
    return bool(rds_db_instance["StorageEncrypted"])


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
    return bool(rds_db_snapshot["Encrypted"])


def get_db_instance_id(db_instance):
    return get_param_id(db_instance, "DBInstanceIdentifier")


def get_db_snapshot_arn(snapshot):
    return get_param_id(snapshot, "DBSnapshotArn")


def get_db_security_group_arn(sg):
    return get_param_id(sg, "DBSecurityGroupArn")


def get_rds_resource_id(resource):
    if isinstance(resource, dict) and "DBInstanceIdentifier" in resource:
        return get_db_instance_id(resource)
    if isinstance(resource, dict) and "DBSnapshotArn" in resource:
        return get_db_snapshot_arn(resource)
    if isinstance(resource, dict) and "DBSecurityGroupArn" in resource:
        return get_db_security_group_arn(resource)
    if isinstance(resource, dict) and "AttributeName" in resource:
        return get_param_id(resource, "AttributeName")

    if isinstance(resource, list):
        if len(resource) == 0:
            return "empty"
        return get_rds_resource_id(resource[0])

    return None


def rds_db_snapshot_not_too_old(snapshot, snapshot_created_days_ago=365):
    """
    Check a rds snapshot is created "snapshot_created_days_ago".

    >>> from datetime import datetime
    >>> from datetime import timezone

    >>> rds_db_snapshot_not_too_old({"SnapshotCreateTime": datetime.now(timezone.utc)})
    True
    >>> rds_db_snapshot_not_too_old({"SnapshotCreateTime": datetime.fromisoformat("2019-09-11T19:45:22.116+00:00")})
    False
    """
    create_time = snapshot["SnapshotCreateTime"]
    now = datetime.now(tz=create_time.tzinfo)

    if (now - create_time).days < snapshot_created_days_ago:
        return True
    else:
        return False

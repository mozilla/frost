from helpers import get_param_id
from datetime import datetime


def ip_permission_opens_all_ports(ipp):
    """
    Returns True if an EC2 security group IP permission opens all
    ports and False otherwise.

    >>> ip_permission_opens_all_ports({'FromPort': 1, 'ToPort': 65535})
    True
    >>> ip_permission_opens_all_ports({'FromPort': 1, 'ToPort': 965535})
    True
    >>> ip_permission_opens_all_ports({'FromPort': -1, 'ToPort': 20})
    True
    >>> ip_permission_opens_all_ports({'FromPort': 20, 'ToPort': -1})
    True

    >>> ip_permission_opens_all_ports({'ToPort': -1})
    False
    """
    if "FromPort" not in ipp or "ToPort" not in ipp:
        return False

    from_port, to_port = ipp["FromPort"], ipp["ToPort"]

    # -1 indicates all ICMP/ICMPv6 codes
    if from_port == -1 or to_port == -1:
        return True

    if ipp["FromPort"] <= 1 and ipp["ToPort"] >= 65535:
        return True

    return False


def ip_permission_cidr_allows_all_ips(ipp):
    """
    Returns True if any IPv4 or IPv6 range for an EC2 security group
    IP permission opens allows access to or from all IPs and False
    otherwise.

    >>> ip_permission_cidr_allows_all_ips({'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})
    True
    >>> ip_permission_cidr_allows_all_ips({'Ipv6Ranges': [{'CidrIpv6': '::/0'}]})
    True

    >>> ip_permission_cidr_allows_all_ips({'IpRanges': [{'CidrIp': '192.0.1.1/8'}]})
    False
    >>> ip_permission_cidr_allows_all_ips({'Ipv6Ranges': [{'CidrIpv6': '192.0.1.1/8'}]})
    False
    >>> ip_permission_cidr_allows_all_ips({})
    False
    """
    for ip_range in ipp.get("IpRanges", []):
        if ip_range.get("CidrIp", "") == "0.0.0.0/0":
            return True

    for ip_range in ipp.get("Ipv6Ranges", []):
        if ip_range.get("CidrIpv6", "") == "::/0":
            return True

    return False


def ip_permission_grants_access_to_group_with_id(ipp, security_group_id):
    """
    Returns True if an EC2 security group IP permission opens access to
    a security with the given ID and False otherwise.

    >>> ip_permission_grants_access_to_group_with_id(
    ... {'UserIdGroupPairs': [{'GroupId': 'test-sgid'}]}, 'test-sgid')
    True
    >>> ip_permission_grants_access_to_group_with_id(
    ... {'UserIdGroupPairs': [{'GroupId': 'test-sgid'}]}, 'not-test-sgid')
    False
    >>> ip_permission_grants_access_to_group_with_id({}, 'test-sgid')
    False
    """
    for user_id_group_pair in ipp.get("UserIdGroupPairs", []):
        if user_id_group_pair.get("GroupId", None) == security_group_id:
            return True

    return False


def ec2_security_group_opens_all_ports(ec2_security_group):
    """
    Returns True if an ec2 security group includes a permission
    allowing inbound access on all ports and False otherwise
    or if protocol is ICMP.

    >>> ec2_security_group_opens_all_ports(
    ... {'IpPermissions': [{}, {'FromPort': -1,'ToPort': 65536}]})
    True

    >>> ec2_security_group_opens_all_ports(
    ... {'IpPermissions': [{}, {'IpProtocol': 'icmp', 'FromPort': -1,'ToPort': -1}]})
    False
    >>> ec2_security_group_opens_all_ports({})
    False
    """
    if "IpPermissions" not in ec2_security_group:
        return False

    for ipp in ec2_security_group["IpPermissions"]:
        if "IpProtocol" in ipp and ipp["IpProtocol"] in ["icmp", "icmpv6"]:
            continue
        if ip_permission_opens_all_ports(ipp):
            return True

    return False


def ec2_security_group_opens_all_ports_to_self(ec2_security_group):
    """
    Returns True if an ec2 security group includes a permission
    allowing all IPs inbound access on all ports and False otherwise
    or if protocol is ICMP.

    >>> ec2_security_group_opens_all_ports_to_self({
    ... 'GroupId': 'test-sgid',
    ... 'IpPermissions': [
    ...     {'FromPort': 1, 'ToPort': 65535, 'UserIdGroupPairs': [{'GroupId': 'test-sgid'}]},
    ... ]})
    True

    >>> ec2_security_group_opens_all_ports_to_self({
    ... 'GroupId': 'test-sgid',
    ... 'IpPermissions': [
    ...     {'IpProtocol': "icmp", 'FromPort': -1, 'ToPort': -1, 'UserIdGroupPairs': [{'GroupId': 'test-sgid'}]},
    ... ]})
    False
    >>> ec2_security_group_opens_all_ports_to_self({
    ... 'GroupId': 'test-sgid',
    ... 'IpPermissions': [
    ...     {'UserIdGroupPairs': [{'GroupId': 'test-sgid'}]},
    ... ]})
    False
    >>> ec2_security_group_opens_all_ports_to_self({'GroupId': 'test-sgid'})
    False
    >>> ec2_security_group_opens_all_ports_to_self({
    ... 'GroupId': 'test-sgid',
    ... 'IpPermissions': [
    ...     {'UserIdGroupPairs': []},
    ... ]})
    False
    >>> ec2_security_group_opens_all_ports_to_self({})
    False
    >>> ec2_security_group_opens_all_ports_to_self([])
    False
    """
    if "GroupId" not in ec2_security_group:
        return False

    self_group_id = ec2_security_group["GroupId"]

    if "IpPermissions" not in ec2_security_group:
        return False

    for ipp in ec2_security_group["IpPermissions"]:
        if "IpProtocol" in ipp and ipp["IpProtocol"] in ["icmp", "icmpv6"]:
            continue
        if ip_permission_opens_all_ports(
            ipp
        ) and ip_permission_grants_access_to_group_with_id(ipp, self_group_id):
            return True

    return False


def ec2_security_group_opens_all_ports_to_all(ec2_security_group):
    """
    Returns True if an ec2 security group includes a permission
    allowing all IPs inbound access on all ports and False otherwise
    or if protocol is ICMP.

    >>> ec2_security_group_opens_all_ports_to_all({'IpPermissions': [
    ... {'FromPort': -1,'ToPort': 65535,'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
    ... ]})
    True
    >>> ec2_security_group_opens_all_ports_to_all({'IpPermissions': [
    ... {'FromPort': 1,'ToPort': 65535,'Ipv6Ranges': [{'CidrIpv6': '::/0'}]}
    ... ]})
    True

    >>> ec2_security_group_opens_all_ports_to_all({'IpPermissions': [
    ... {'IpProtocol': 'icmp','FromPort': -1,'ToPort': -1,'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
    ... ]})
    False
    >>> ec2_security_group_opens_all_ports_to_all({'IpPermissions': []})
    False
    >>> ec2_security_group_opens_all_ports_to_all({})
    False
    >>> ec2_security_group_opens_all_ports_to_all([])
    False
    """
    if "IpPermissions" not in ec2_security_group:
        return False

    for ipp in ec2_security_group["IpPermissions"]:
        if "IpProtocol" in ipp and ipp["IpProtocol"] in ["icmp", "icmpv6"]:
            continue
        if ip_permission_opens_all_ports(ipp) and ip_permission_cidr_allows_all_ips(
            ipp
        ):
            return True

    return False


def ec2_security_group_opens_specific_ports_to_all(
    ec2_security_group, allowed_ports=None
):
    """
    Returns True if an ec2 security group includes a permission
    allowing all IPs inbound access on specific unsafe ports and False
    otherwise or if protocol is ICMP.

    >>> ec2_security_group_opens_specific_ports_to_all({'IpPermissions': [
    ... {'FromPort': 22,'ToPort': 22,'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
    ... ]})
    True
    >>> ec2_security_group_opens_specific_ports_to_all({'IpPermissions': [
    ... {'FromPort': 234,'ToPort': 432,'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
    ... ]})
    True

    >>> ec2_security_group_opens_specific_ports_to_all({'IpPermissions': [
    ... {'FromPort': 80,'ToPort': 80,'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
    ... ]})
    False
    >>> ec2_security_group_opens_specific_ports_to_all({'IpPermissions': []})
    False
    >>> ec2_security_group_opens_specific_ports_to_all({})
    False
    >>> ec2_security_group_opens_specific_ports_to_all([])
    False
    """
    if allowed_ports is None:
        allowed_ports = []

    if "IpPermissions" not in ec2_security_group:
        return False

    for ipp in ec2_security_group["IpPermissions"]:
        if "IpProtocol" in ipp and ipp["IpProtocol"] in ["icmp", "icmpv6"]:
            continue

        if ip_permission_cidr_allows_all_ips(ipp):
            if "FromPort" not in ipp or "ToPort" not in ipp:
                continue

            from_port, to_port = ipp["FromPort"], ipp["ToPort"]
            if from_port == to_port and from_port in [80, 443]:
                continue

            if from_port == to_port and from_port in allowed_ports:
                continue

            return True

    return False


def ec2_instance_test_id(ec2_instance):
    """A getter fn for test ids for EC2 instances"""
    return (
        "{0[InstanceId]}".format(ec2_instance)
        if isinstance(ec2_instance, dict)
        else None
    )


def ec2_security_group_test_id(ec2_security_group):
    """A getter fn for test ids for EC2 security groups"""
    return (
        "{0[GroupId]} {0[GroupName]}".format(ec2_security_group)
        if isinstance(ec2_security_group, dict)
        else None
    )


def ec2_address_id(ec2_address):
    """Format an Elastic IP address."""
    return get_param_id(ec2_address, "PublicIp")


def is_ebs_volume_encrypted(ebs):
    """
    Checks the EBS volume 'Encrypted' value.

    >>> is_ebs_volume_encrypted({'Encrypted': True})
    True
    >>> is_ebs_volume_encrypted({'Encrypted': False})
    False
    >>> is_ebs_volume_encrypted({})
    Traceback (most recent call last):
    ...
    KeyError: 'Encrypted'
    >>> is_ebs_volume_encrypted(0)
    Traceback (most recent call last):
    ...
    TypeError: 'int' object is not subscriptable
    >>> is_ebs_volume_encrypted(None)
    Traceback (most recent call last):
    ...
    TypeError: 'NoneType' object is not subscriptable
    """
    return ebs["Encrypted"]


def is_ebs_volume_piops(ebs):
    """
    Checks if the EBS volume type is provisioned iops

    >>> is_ebs_volume_piops({'VolumeType': 'io1'})
    True
    >>> is_ebs_volume_piops({'VolumeType': 'standard'})
    False
    >>> is_ebs_volume_piops({})
    Traceback (most recent call last):
    ...
    KeyError: 'VolumeType'
    >>> is_ebs_volume_piops(0)
    Traceback (most recent call last):
    ...
    TypeError: 'int' object is not subscriptable
    >>> is_ebs_volume_piops(None)
    Traceback (most recent call last):
    ...
    TypeError: 'NoneType' object is not subscriptable
    """
    return ebs["VolumeType"].startswith("io")


def is_ebs_snapshot_public(ebs_snapshot):
    """
    Checks if the EBS snapshot's 'CreateVolumePermissions' attribute allows for public creation.

    >>> is_ebs_snapshot_public({'CreateVolumePermissions':[{'Group': 'all'}]})
    True
    >>> is_ebs_snapshot_public({'CreateVolumePermissions':[{'Group': ''}]})
    False
    >>> is_ebs_snapshot_public({'CreateVolumePermissions':[{'foo': 'bar'}]})
    False
    >>> is_ebs_snapshot_public({'CreateVolumePermissions':[]})
    False
    >>> is_ebs_snapshot_public({})
    False
    """
    for p in ebs_snapshot.get("CreateVolumePermissions", []):
        if p.get("Group", "") == "all":
            return True
    return False


def ec2_instance_missing_tag_names(ec2_instance, required_tag_names):
    """
    Returns any tag names that are missing from an EC2 Instance.

    >>> ec2_instance_missing_tag_names({'Tags': [{'Key': 'Name'}]}, frozenset(['Name']))
    frozenset()
    >>> ec2_instance_missing_tag_names({
    ... 'InstanceId': 'iid', 'Tags': [{'Key': 'Bar'}]}, frozenset(['Name']))
    frozenset({'Name'})
    """
    tags = ec2_instance.get("Tags", [])
    instance_tag_names = set(tag["Key"] for tag in tags if "Key" in tag)
    return required_tag_names - instance_tag_names


def ebs_volume_attached_to_instance(ebs, volume_created_days_ago=90):
    """
    Check an ebs volume is attached to an instance. The "volume_created_days_ago"
    parameter allows checking for volumes that were created that many days ago.
    
    >>> from datetime import datetime
    >>> from datetime import timezone

    >>> ebs_volume_attached_to_instance({"CreateTime": datetime.fromisoformat("2020-09-11T19:45:22.116+00:00"), "State": "in-use"})
    True
    >>> ebs_volume_attached_to_instance({"CreateTime": datetime.fromisoformat("2000-09-11T19:45:22.116+00:00"), "State": "in-use"})
    True
    >>> ebs_volume_attached_to_instance({"CreateTime": datetime.now(timezone.utc), "State": "available"})
    True
    >>> ebs_volume_attached_to_instance({"CreateTime": datetime.fromisoformat("2000-09-11T19:45:22.116+00:00"), "State": "available"})
    False
    """
    creation_time = ebs["CreateTime"]
    now = datetime.now(tz=creation_time.tzinfo)

    if (now - creation_time).days > volume_created_days_ago:
        if ebs["State"] == "available":
            return False

    return True


def ebs_snapshot_not_too_old(snapshot, snapshot_started_days_ago=365):
    """
    Check an ebs snapshot is created less than "snapshot_started_days_ago".

    >>> from datetime import datetime
    >>> from datetime import timezone
    >>> from aws.ec2.helpers import ebs_snapshot_not_too_old
    >>> ebs_snapshot_not_too_old({"StartTime": datetime.now(timezone.utc)})
    True
    >>> ebs_snapshot_not_too_old({"StartTime": datetime.fromisoformat("2019-09-11T19:45:22.116+00:00")})
    False
    """
    start_time = snapshot["StartTime"]
    now = datetime.now(tz=start_time.tzinfo)

    if (now - start_time).days < snapshot_started_days_ago:
        return True
    else:
        return False

from collections import defaultdict

from conftest import botocore_client


def ec2_instances():
    "http://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_instances"
    # Note: extracting Reservations.Instances drops EC2-Classic Groups at Reservations.Groups
    return botocore_client.get(
        'ec2', 'describe_instances', [], {})\
        .extract_key('Reservations')\
        .flatten()\
        .extract_key('Instances')\
        .flatten()\
        .values()


def ec2_security_groups():
    "http://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_security_groups"
    return botocore_client.get(
        'ec2', 'describe_security_groups', [], {})\
        .extract_key('SecurityGroups')\
        .flatten()\
        .values()


def ec2_ebs_volumes():
    "http://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_volumes"
    return botocore_client.get(
        'ec2', 'describe_volumes', [], {})\
        .extract_key('Volumes')\
        .flatten()\
        .values()


def ec2_security_groups_with_in_use_flag():
    """Returns security groups with an additional "InUse" key,
    which is True if it is associated with at least one EC2
    instance.
    """
    sec_groups = ec2_security_groups()
    instances = ec2_instances()

    in_use_sec_group_ids = defaultdict(int)
    for instance in instances:
        for attached_sec_group in instance['SecurityGroups']:
            in_use_sec_group_ids[attached_sec_group['GroupId']] += 1

    for sec_group in sec_groups:
        if sec_group["GroupId"] in in_use_sec_group_ids.keys():
            sec_group["InUse"] = True
        else:
            sec_group["InUse"] = False

    return sec_groups

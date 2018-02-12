from collections import defaultdict

from conftest import botocore_client

from aws.elasticache.resources import elasticache_clusters
from aws.elb.resources import (
    elbs,
    elbs_v2,
)
from aws.rds.resources import rds_db_instances
from aws.redshift.resources import redshift_clusters
from aws.elasticsearch.resources import elasticsearch_domains


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

    resources = sum([ec2_instances(), elbs(), elbs_v2(), elasticache_clusters()], [])
    vpc_namespaced_resources = sum([rds_db_instances(), redshift_clusters()], [])

    # Included:
    # - ELBs (v1 and v2?)
    # - RDS
    # - Redshift
    # - ElasticCache

    # TODO:
    # Need to include:
    # - AutoScaling (describe_launch_configurations)
    #
    # - ElasticSearchService
    #   - Are these just ec2 instances?
    # - EMR?
    #   - Are these just ec2 instances?

    in_use_sec_group_ids = defaultdict(int)
    for resource in resources:
        for attached_sec_group in resource.get('SecurityGroups', []):
            if isinstance(attached_sec_group, dict):
                for key in ['SecurityGroupId', 'GroupId']:
                    if key in attached_sec_group:
                        in_use_sec_group_ids[attached_sec_group[key]] += 1
            elif isinstance(attached_sec_group, str):
                in_use_sec_group_ids[attached_sec_group] += 1

    for resource in vpc_namespaced_resources:
        for attached_sec_group in resource['VpcSecurityGroups']:
            in_use_sec_group_ids[attached_sec_group['VpcSecurityGroupId']] += 1

    for domain in elasticsearch_domains():
        for attached_sec_group in domain['VPCOptions']['SecurityGroupIds']:
            in_use_sec_group_ids[attached_sec_group] += 1

    for sec_group in sec_groups:
        if sec_group["GroupId"] in in_use_sec_group_ids.keys():
            sec_group["InUse"] = True
        else:
            sec_group["InUse"] = False

    return sec_groups

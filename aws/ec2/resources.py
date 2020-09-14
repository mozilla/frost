from collections import defaultdict

from conftest import botocore_client

from aws.autoscaling.resources import autoscaling_launch_configurations
from aws.elasticache.resources import elasticache_clusters
from aws.elb.resources import elbs, elbs_v2
from aws.rds.resources import rds_db_instances
from aws.redshift.resources import redshift_clusters
from aws.elasticsearch.resources import elasticsearch_domains


def ec2_instances():
    "http://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_instances"
    # Note: extracting Reservations.Instances drops EC2-Classic Groups at Reservations.Groups
    return (
        botocore_client.get(
            "ec2",
            "describe_instances",
            [],
            {
                "Filters": [
                    {"Name": "instance-state-name", "Values": ["pending", "running"]}
                ]
            },
        )
        .extract_key("Reservations")
        .flatten()
        .extract_key("Instances")
        .flatten()
        .values()
    )


def ec2_security_groups():
    "http://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_security_groups"
    return (
        botocore_client.get("ec2", "describe_security_groups", [], {})
        .extract_key("SecurityGroups")
        .flatten()
        .values()
    )


def ec2_ebs_volumes():
    "http://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_volumes"
    return (
        botocore_client.get("ec2", "describe_volumes", [], {})
        .extract_key("Volumes")
        .flatten()
        .values()
    )


def ec2_ebs_snapshots():
    "http://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_snapshots"
    return (
        botocore_client.get("ec2", "describe_snapshots", [], {"OwnerIds": ["self"]})
        .extract_key("Snapshots")
        .flatten()
        .values()
    )


def ec2_ebs_snapshots_create_permission():
    "https://botocore.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_snapshot_attribute"
    return sum(
        [
            botocore_client.get(
                service_name="ec2",
                method_name="describe_snapshot_attribute",
                call_args=[],
                call_kwargs={
                    "Attribute": "createVolumePermission",
                    "SnapshotId": snapshot["SnapshotId"],
                },
                regions=[snapshot["__pytest_meta"]["region"]],
            ).values()
            for snapshot in ec2_ebs_snapshots()
        ],
        [],
    )


def ec2_flow_logs():
    "https://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_flow_logs"
    return (
        botocore_client.get("ec2", "describe_flow_logs", [], {})
        .extract_key("FlowLogs")
        .flatten()
        .values()
    )


def ec2_vpcs():
    "https://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_vpcs"
    return (
        botocore_client.get("ec2", "describe_vpcs", [], {})
        .extract_key("Vpcs")
        .flatten()
        .values()
    )


def ec2_addresses():
    "https://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_addresses"
    return (
        botocore_client.get("ec2", "describe_addresses", [], {})
        .extract_key("Addresses")
        .flatten()
        .values()
    )


def ec2_security_groups_with_in_use_flag():
    """Returns security groups with an additional "InUse" key,
    which is True if it is associated with at least one resource.

    Possible resources:
    - EC2
    - ELBs (v1 and v2)
    - RDS
    - Redshift
    - ElasticCache
    - ElasticSearchService
    - AutoScaling
    """
    sec_groups = ec2_security_groups()
    in_use_sec_group_ids = defaultdict(int)

    # These resources have their security groups under 'SecurityGroups'.
    # Most of these are a list of dictionaries which include either SecurityGroupId
    # or GroupId, but some have just a list of group ids.
    resources = sum(
        [
            ec2_instances(),
            elbs(),
            elbs_v2(),
            elasticache_clusters(),
            autoscaling_launch_configurations(),
        ],
        [],
    )
    for resource in resources:
        for attached_sec_group in resource.get("SecurityGroups", []):
            if isinstance(attached_sec_group, dict):
                for key in ["SecurityGroupId", "GroupId"]:
                    if key in attached_sec_group:
                        in_use_sec_group_ids[attached_sec_group[key]] += 1
            elif isinstance(attached_sec_group, str):
                in_use_sec_group_ids[attached_sec_group] += 1
            else:
                raise Exception(
                    "Got security group value with a type of %s"
                    % type(attached_sec_group)
                )

    # These resources have two types of security groups, therefore
    # the Vpc ones are namespaced under "VpcSecurityGroups"
    vpc_namespaced_resources = sum([rds_db_instances(), redshift_clusters()], [])
    for resource in vpc_namespaced_resources:
        for attached_sec_group in resource.get("VpcSecurityGroups", []):
            in_use_sec_group_ids[attached_sec_group["VpcSecurityGroupId"]] += 1

    # ElasticSearchService does it a little differently
    for domain in elasticsearch_domains():
        if "VPCOptions" in domain:
            for attached_sec_group in domain["VPCOptions"]["SecurityGroupIds"]:
                in_use_sec_group_ids[attached_sec_group] += 1

    for sec_group in sec_groups:
        if sec_group["GroupId"] in in_use_sec_group_ids.keys():
            sec_group["InUse"] = True
        else:
            sec_group["InUse"] = False

    return sec_groups


def ec2_images_owned_by(account_ids):
    "Returns a list of EC2 images owned by a list of provided account ids"
    return (
        botocore_client.get(
            "ec2",
            "describe_images",
            [],
            {"Filters": [{"Name": "owner-id", "Values": account_ids}]},
        )
        .extract_key("Images")
        .flatten()
        .values()
    )

import itertools

from conftest import botocore_client


def rds_db_instances():
    "http://botocore.readthedocs.io/en/latest/reference/services/rds.html#RDS.Client.describe_db_instances"
    return (
        botocore_client.get("rds", "describe_db_instances", [], {})
        .extract_key("DBInstances")
        .flatten()
        .values()
    )


def rds_db_instance_tags(db):
    "http://botocore.readthedocs.io/en/latest/reference/services/rds.html#RDS.Client.list_tags_for_resource"
    return botocore_client.get_details(
        resource=db,
        service_name="rds",
        method_name="list_tags_for_resource",
        call_args=[],
        call_kwargs={"ResourceName": db["DBInstanceArn"]},
        result_from_error=lambda e, call: [],
    )["TagList"]


def rds_db_instances_with_tags():
    return [
        {**{"TagList": rds_db_instance_tags(db=db)}, **db} for db in rds_db_instances()
    ]


def rds_db_instances_vpc_security_groups():
    "http://botocore.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_security_groups"
    return itertools.chain.from_iterable(
        botocore_client.get_details(
            resource=instance,
            service_name="ec2",
            method_name="describe_security_groups",
            call_args=[],
            call_kwargs={
                "Filters": [
                    {
                        "Name": "group-id",
                        "Values": [
                            sg["VpcSecurityGroupId"]
                            for sg in instance["VpcSecurityGroups"]
                            if sg["Status"] == "active"
                        ],
                    }
                ]
            },
            result_from_error=lambda e, call: {"SecurityGroups": []},
        )["SecurityGroups"]
        for instance in rds_db_instances()
    )


def rds_db_snapshots():
    "http://botocore.readthedocs.io/en/latest/reference/services/rds.html#RDS.Client.describe_db_snapshots"
    return (
        botocore_client.get("rds", "describe_db_snapshots", [], {})
        .extract_key("DBSnapshots")
        .flatten()
        .values()
    )


def rds_db_snapshots_attributes():
    "http://botocore.readthedocs.io/en/latest/reference/services/rds.html#RDS.Client.describe_db_snapshot_attributes"
    empty_attrs = {"DBSnapshotAttributesResult": {"DBSnapshotAttributes": []}}
    return [
        botocore_client.get_details(
            resource="snapshot",
            service_name="rds",
            method_name="describe_db_snapshot_attributes",
            call_args=[],
            call_kwargs={"DBSnapshotIdentifier": snapshot["DBSnapshotIdentifier"]},
            result_from_error=lambda e, call: empty_attrs,  # treat not found as empty list
        )["DBSnapshotAttributesResult"]["DBSnapshotAttributes"]
        for snapshot in rds_db_snapshots()
    ]


def rds_db_security_groups():
    "http://botocore.readthedocs.io/en/latest/reference/services/rds.html#RDS.Client.describe_db_security_groups"
    sgs = []

    for response in botocore_client.get(
        "rds", "describe_db_security_groups", [], {}
    ).values():
        sgs.extend(response["DBSecurityGroups"])

    return sgs

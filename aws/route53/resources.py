from conftest import botocore_client


def zones():
    """
    https://botocore.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.list_hosted_zones
    """
    return (
        botocore_client.get("route53", "list_hosted_zones", [], {})
        .extract_key("HostedZones")
        .flatten()
        .values()
    )


def cnames():
    records = []

    for zone in zones():
        zone_id = zone["Id"].split("/")[2]
        zone_records = (
            botocore_client.get(
                "route53", "list_resource_record_sets", [], {"HostedZoneId": zone_id}
            )
            .extract_key("ResourceRecordSets")
            .flatten()
            .values()
        )
        records.extend([record for record in zone_records if record["Type"] == "CNAME"])

    return records

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
    zone_list = zones()
    print(zone_list)
    for zone in zone_list:
        zone_id = zone['Id'].split('/')[2]

        records = botocore_client.get("route53", "list_resource_record_sets", [], {"HostedZoneId": zone_id}).extract("ResourceRecordSets").flatten().values()

        for record in records:
            print("record: {}".format(record))

    return records

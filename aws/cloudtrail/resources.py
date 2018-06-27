from conftest import botocore_client


def cloudtrails():
    "https://botocore.readthedocs.io/en/latest/reference/services/cloudtrail.html#CloudTrail.Client.describe_trails"
    trails = (
        botocore_client.get("cloudtrail", "describe_trails", [], {})
        .extract_key("trailList")
        .flatten()
        .values()
    )

    # This is due to the fact that if you have a multi region cloudtrail, it will be included for each region.
    unique_trails = []
    for trail in trails:
        if not any(t for t in unique_trails if t["TrailARN"] == trail["TrailARN"]):
            unique_trails.append(trail)

    return unique_trails

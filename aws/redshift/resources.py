from conftest import botocore_client


def redshift_clusters():
    "botocore.readthedocs.io/en/latest/reference/services/redshift.html#Redshift.Client.describe_clusters"
    return (
        botocore_client.get("redshift", "describe_clusters", [], {})
        .extract_key("Clusters")
        .flatten()
        .values()
    )


def redshift_cluster_security_groups():
    "http://botocore.readthedocs.io/en/latest/reference/services/redshift.html#Redshift.Client.describe_cluster_security_groups"  # NOQA
    return (
        botocore_client.get(
            "redshift",
            "describe_cluster_security_groups",
            [],
            {},
            result_from_error=lambda error, call: {"ClusterSecurityGroups": []},
        )
        .extract_key("ClusterSecurityGroups")
        .flatten()
        .values()
    )

from conftest import botocore_client


def elasticache_clusters():
    """
    http://botocore.readthedocs.io/en/latest/reference/services/elasticache.html#ElastiCache.Client.describe_cache_clusters
    """
    return (
        botocore_client.get("elasticache", "describe_cache_clusters", [], {})
        .extract_key("CacheClusters")
        .flatten()
        .values()
    )

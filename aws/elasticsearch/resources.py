from conftest import botocore_client


def elasticsearch_domains():
    """
    http://botocore.readthedocs.io/en/latest/reference/services/es.html#ElasticsearchService.Client.describe_elasticsearch_domains
    """
    # You can only get 5 at a time.
    domains_list = list_elasticsearch_domains()
    domains = []
    for i in range(0, len(domains_list), 5):
        domains += (
            botocore_client.get(
                "es",
                "describe_elasticsearch_domains",
                [],
                {"DomainNames": domains_list[i : i + 5]},
            )
            .extract_key("DomainStatusList")
            .flatten()
            .values()
        )
    return domains


def list_elasticsearch_domains():
    "http://botocore.readthedocs.io/en/latest/reference/services/es.html#ElasticsearchService.Client.list_domain_names"
    return [
        domain["DomainName"]
        for domain in botocore_client.get("es", "list_domain_names", [], {})
        .extract_key("DomainNames")
        .flatten()
        .values()
    ]

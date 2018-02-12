from conftest import botocore_client


def elasticsearch_domains():
    """
    http://botocore.readthedocs.io/en/latest/reference/services/es.html#ElasticsearchService.Client.describe_elasticsearch_domains
    """
    domains = list_elasticsearch_domains()
    print(domains)
    return botocore_client.get(
        'es', 'describe_elasticsearch_domains', [], {'DomainNames': domains})\
        .extract_key('DomainStatusList')\
        .flatten()\
        .values()


def list_elasticsearch_domains():
    "http://botocore.readthedocs.io/en/latest/reference/services/es.html#ElasticsearchService.Client.list_domain_names"
    return [
        domain['DomainName'] for domain in
        botocore_client.get('es', 'list_domain_names', [], {})
        .extract_key('DomainNames')
        .flatten()
        .values()
    ]

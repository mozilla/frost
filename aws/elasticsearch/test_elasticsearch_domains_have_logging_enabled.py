import pytest

from aws.elasticsearch.resources import elasticsearch_domains


@pytest.mark.elasticsearch
@pytest.mark.parametrize(
    "es_domain", elasticsearch_domains(), ids=lambda es_domain: es_domain["ARN"]
)
def test_elasticsearch_domains_have_logging_enabled(es_domain):
    """
    Tests whether an elasticsearch domain has logging enabled.
    """
    assert (
        es_domain.get("LogPublishingOption") is not None
    ), "Logging is disabled for {}".format(es_domain["DomainName"])
    assert es_domain["LogPublishingOptions"]["INDEX_SLOW_LOGS"][
        "Enabled"
    ], "Index Slow Logs are disabled for {}".format(es_domain["DomainName"])
    assert es_domain["LogPublishingOptions"]["SEARCH_SLOW_LOGS"][
        "Enabled"
    ], "Search Slow Logs are disabled for {}".format(es_domain["DomainName"])

from conftest import botocore_client


def elbs():
    """
    http://botocore.readthedocs.io/en/latest/reference/services/elb.html#ElasticLoadBalancing.Client.describe_load_balancers
    """
    return botocore_client.get(
        'elb', 'describe_load_balancers', [], {})\
        .extract_key('LoadBalancerDescriptions')\
        .flatten()\
        .values()


def elbs_v2():
    """
    http://botocore.readthedocs.io/en/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_load_balancers
    """
    return botocore_client.get(
        'elbv2', 'describe_load_balancers', [], {})\
        .extract_key('LoadBalancers')\
        .flatten()\
        .values()

from conftest import botocore_client


def elbs(with_tags=True):
    """
    http://botocore.readthedocs.io/en/latest/reference/services/elb.html#ElasticLoadBalancing.Client.describe_load_balancers
    """
    elbs = (
        botocore_client.get("elb", "describe_load_balancers", [], {})
        .extract_key("LoadBalancerDescriptions")
        .flatten()
        .values()
    )

    if not with_tags:
        return elbs

    elbs_with_tags = []
    for elb in elbs:
        tags = (
            botocore_client.get(
                service_name="elb",
                method_name="describe_tags",
                call_args=[],
                call_kwargs={"LoadBalancerNames": [elb["LoadBalancerName"]]},
                regions=[elb["__pytest_meta"]["region"]],
            )
            .extract_key("TagDescriptions")
            .flatten()
            .values()
        )
        # This check is probably unneeded
        if len(tags) >= 1:
            tags = tags[0]
        if "Tags" in tags:
            elb["Tags"] = tags["Tags"]
        elbs_with_tags.append(elb)

    return elbs_with_tags


def elbs_v2():
    """
    http://botocore.readthedocs.io/en/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_load_balancers
    """
    return (
        botocore_client.get("elbv2", "describe_load_balancers", [], {})
        .extract_key("LoadBalancers")
        .flatten()
        .values()
    )


def elb_attributes(elb):
    """
    https://botocore.amazonaws.com/v1/documentation/api/latest/reference/services/elb.html#ElasticLoadBalancing.Client.describe_load_balancer_attributes
    """
    return (
        botocore_client.get(
            "elb",
            "describe_load_balancer_attributes",
            [],
            call_kwargs={"LoadBalancerName": elb["LoadBalancerName"]},
            regions=[elb["__pytest_meta"]["region"]],
        )
        .extract_key("LoadBalancerAttributes")
        .debug()
        .values()
    )[0]


def elbs_with_attributes():
    return [(elb, elb_attributes(elb),) for elb in elbs(with_tags=False)]

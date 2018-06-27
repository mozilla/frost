from conftest import gcp_client


def firewalls():
    return gcp_client.list("compute", "firewalls")


def networks():
    return gcp_client.list("compute", "networks")


def instances():
    return gcp_client.list("compute", "instances")


def networks_with_instances():
    for network in networks():
        network["instances"] = []
        for instance in instances():
            if network["selfLink"] in [
                interface["network"] for interface in instance["networkInterfaces"]
            ]:
                network["instances"].append(instance)
        if len(network["instances"]):
            yield network


def in_use_firewalls():
    for firewall in firewalls():
        for network in networks_with_instances():
            if (
                network["selfLink"] == firewall["network"]
                and len(network["instances"]) > 0
            ):
                yield firewall

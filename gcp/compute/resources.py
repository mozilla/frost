from conftest import gcp_client


def firewalls():
    return gcp_client.list("compute", "firewalls")


def networks():
    return gcp_client.list("compute", "networks")


def instances():
    return gcp_client.list("compute", "instances")


def clusters():
    results = []
    for project_id in gcp_client.project_list:
        results += gcp_client.list(
            "container",
            "projects.locations.clusters",
            results_key="clusters",
            call_kwargs={"parent": "projects/{}/locations/-".format(project_id)},
        )
    return results


def networks_with_instances():
    allInstances = instances()
    in_use_networks = []
    for network in networks():
        network["instances"] = []
        for instance in allInstances:
            if network["selfLink"] in [
                interface["network"] for interface in instance["networkInterfaces"]
            ]:
                network["instances"].append(instance)
        if len(network["instances"]):
            in_use_networks.append(network)

    return in_use_networks


def in_use_firewalls():
    all_networks = networks_with_instances()
    results = []
    for firewall in firewalls():
        if firewall["disabled"] == True:
            continue
        for network in all_networks:
            if (
                network["selfLink"] == firewall["network"]
                and len(network["instances"]) > 0
            ):
                results.append(firewall)
    return results

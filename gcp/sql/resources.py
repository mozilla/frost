from conftest import gcp_client


def instances():
    return gcp_client.get("sqladmin", "instances", version="v1beta4")

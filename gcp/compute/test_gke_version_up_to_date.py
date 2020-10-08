import pytest

from helpers import get_param_id

from gcp.compute.resources import clusters
from conftest import gcp_client


@pytest.fixture
def server_config():
    return gcp_client.get_project_container_config()


@pytest.mark.gcp_compute
@pytest.mark.parametrize(
    "cluster", clusters(), ids=lambda c: get_param_id(c, "name"),
)
def test_gke_version_up_to_date(cluster, server_config):
    """
    Tests if GKE version is up to date by comparing the
    list of valid master versions to what is
    currently running on the cluster.
    """
    assert (
        cluster["currentMasterVersion"] in server_config["validMasterVersions"]
    ), "Current GKE master version ({}) is not in the list of valid master versions.".format(
        cluster["currentMasterVersion"]
    )
    assert (
        cluster["currentNodeVersion"] in server_config["validMasterVersions"]
    ), "Current GKE node version ({}) is not in the list of valid master versions.".format(
        cluster["currentNodeVersion"]
    )

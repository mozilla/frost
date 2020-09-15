import pytest

from gcp.compute.resources import clusters
from conftest import gcp_client


@pytest.fixture
def allowed_gke_versions(pytestconfig):
    return pytestconfig.custom_config.gcp.allowed_gke_versions


@pytest.mark.gcp_compute
@pytest.mark.parametrize(
    "cluster", clusters(), ids=lambda c: c["name"] if isinstance(c, dict) else None
)
def test_only_allowed_gke_versions(cluster, allowed_gke_versions):
    """
    Tests if GKE version is within allowed list of GKE versions.

    Useful for checking upgrade status after a vulnerability is released, as in:
        - https://cloud.google.com/kubernetes-engine/docs/security-bulletins#gcp-2020-012
    """
    assert (
        cluster["currentMasterVersion"] in allowed_gke_versions
    ), "Current GKE master version ({}) is not in the list of allowed GKE versions.".format(
        cluster["currentMasterVersion"]
    )
    assert (
        cluster["currentNodeVersion"] in allowed_gke_versions
    ), "Current GKE node version ({}) is not in the list of allowed GKE versions.".format(
        cluster["currentNodeVersion"]
    )

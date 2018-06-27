import pytest

from gcp.compute.helpers import does_firewall_open_all_ports_to_all, firewall_id
from gcp.compute.resources import in_use_firewalls


@pytest.mark.gcp_compute
@pytest.mark.parametrize("firewall", in_use_firewalls(), ids=firewall_id)
def test_firewall_opens_all_ports_to_all(firewall):
    """Checks if firewall opens all ports to all IPs"""
    assert not does_firewall_open_all_ports_to_all(firewall)

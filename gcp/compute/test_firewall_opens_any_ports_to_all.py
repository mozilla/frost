import pytest

from gcp.compute.helpers import does_firewall_open_any_ports_to_all, firewall_id
from gcp.compute.resources import in_use_firewalls


@pytest.mark.gcp_compute
@pytest.mark.parametrize("firewall", in_use_firewalls(), ids=firewall_id)
def test_firewall_opens_any_ports_to_all(firewall):
    """
    This test confirms that no ports are open to 0.0.0.0/0 (except
    80 and 443 on any VPC.

    CIS 3.6, 3.7
    """
    assert not does_firewall_open_any_ports_to_all(firewall)

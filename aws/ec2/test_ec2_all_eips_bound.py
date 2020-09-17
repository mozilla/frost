import pytest

from aws.ec2.helpers import ec2_address_id
from aws.ec2.resources import ec2_addresses


@pytest.mark.ec2
@pytest.mark.parametrize("ec2_address", ec2_addresses(), ids=ec2_address_id)
def test_ec2_all_eips_bound(ec2_address):
    """Checks whether all EIPs are bound to instances."""
    assert ec2_address.get("InstanceId"), "No associated instance."

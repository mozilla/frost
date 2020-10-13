import pytest

from helpers import get_param_id

from aws.elb.resources import elbs


@pytest.mark.elb
@pytest.mark.parametrize(
    "elb", elbs(), ids=lambda e: get_param_id(e, "LoadBalancerName"),
)
def test_elb_instances_attached(elb):
    """
    Checks to see that an ELB has attached instances and fails if
    there are 0
    """
    assert len(elb["Instances"]) > 0, "ELB has zero attached instances"

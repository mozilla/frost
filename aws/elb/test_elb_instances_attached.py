import pytest

from aws.elb.resources import elbs


@pytest.mark.elb
@pytest.mark.parametrize(
    "elb", elbs(), ids=lambda e: e["LoadBalancerName"] if isinstance(e, dict) else None,
)
def test_elb_instances_attached(elb):
    """
    Checks to see that an ELB has attached instances and fails if
    there are 0
    """
    assert len(elb["Instances"]) > 0, "ELB has zero attached instances"

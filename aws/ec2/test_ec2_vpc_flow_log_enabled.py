import pytest

from helpers import get_param_id

from aws.ec2.resources import ec2_flow_logs, ec2_vpcs


@pytest.fixture
def all_flow_logs():
    return ec2_flow_logs()


@pytest.mark.ec2
@pytest.mark.parametrize(
    "ec2_vpc", ec2_vpcs(), ids=lambda vpc: get_param_id(vpc, "VpcId"),
)
def test_ec2_vpc_flow_log_enabled(ec2_vpc, all_flow_logs):
    """
    Checks that each VPC has VPC Flow Logs enabled.
    """
    assert any(
        flow_log
        for flow_log in all_flow_logs
        if flow_log["ResourceId"] == ec2_vpc["VpcId"]
    )

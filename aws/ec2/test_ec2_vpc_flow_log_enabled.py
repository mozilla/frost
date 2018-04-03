import pytest

#from aws.ec2.helpers import ()
from aws.ec2.resources import (
    ec2_flow_logs,
    ec2_vpcs
)


@pytest.mark.ec2
@pytest.mark.parametrize('ec2_vpc', ec2_vpcs(), ids=lambda vpc: vpc['VpcId'])
def test_ec2_vpc_flow_log_enabled(ec2_vpc):
    """
    Checks that each VPC has VPC Flow Logs enabled.
    """
    flow_logs = ec2_flow_logs()
    assert any(flow_log for flow_log in flow_logs if flow_log['ResourceId'] == ec2_vpc['VpcId'])

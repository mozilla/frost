import pytest

from helpers import get_param_id

from aws.ec2.resources import ec2_ebs_snapshots
from aws.ec2.helpers import ebs_snapshot_not_too_old


@pytest.mark.ec2
@pytest.mark.parametrize(
    "ec2_ebs_snapshot",
    ec2_ebs_snapshots(),
    ids=lambda ebs: get_param_id(ebs, "SnapshotId"),
)
def test_ec2_ebs_snapshot_not_too_old(ec2_ebs_snapshot):
    assert ebs_snapshot_not_too_old(
        ec2_ebs_snapshot
    ), f"{ec2_ebs_snapshot['SnapshotId']} is started at {ec2_ebs_snapshot['StartTime']}, and is considered too old."

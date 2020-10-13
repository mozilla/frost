import pytest

from helpers import get_param_id

from aws.ec2.resources import ec2_ebs_snapshots_create_permission
from aws.ec2.helpers import is_ebs_snapshot_public


@pytest.mark.ec2
@pytest.mark.parametrize(
    "ec2_ebs_snapshot",
    ec2_ebs_snapshots_create_permission(),
    ids=lambda ebs: get_param_id(ebs, "SnapshotId"),
)
def test_ec2_ebs_snapshot_are_private(ec2_ebs_snapshot):
    assert not is_ebs_snapshot_public(
        ec2_ebs_snapshot
    ), "Snapshot {} is publicly accessible.".format(ec2_ebs_snapshot["SnapshotId"])

import pytest

from aws.redshift.resources import redshift_cluster_security_groups
from aws.redshift.helpers import (
    redshift_cluster_security_group_is_open_to_all_ips,
    redshift_cluster_security_group_test_id,
)


@pytest.mark.redshift
@pytest.mark.parametrize(
    "security_group",
    redshift_cluster_security_groups(),
    ids=redshift_cluster_security_group_test_id,
)
def test_redshift_security_group_does_not_allow_all_ips_access(security_group):
    """Checks whether a redshift cluster grants public access via
    cluster security group.
    """
    assert not redshift_cluster_security_group_is_open_to_all_ips(security_group)

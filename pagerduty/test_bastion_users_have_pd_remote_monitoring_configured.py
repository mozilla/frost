import pytest

from pagerduty.helpers import alternate_names_for_user
from pagerduty.resources import (
    bastion_users,
    users_with_remote_access_escalation_policy_and_extension_configured,
)


@pytest.mark.pagerduty
@pytest.mark.parametrize("bastion_user", bastion_users())
def test_bastion_users_have_pd_remote_monitoring_configured(
    bastion_user, users_with_remote_access_escalation_policy_and_extension_configured
):
    """
    Checks that users with SSH access have pagerduty remote monitoring properly configured.
    """
    assert any(
        username in users_with_remote_access_escalation_policy_and_extension_configured
        for username in alternate_names_for_user(bastion_user)
    ), "bastion user {} is not configured in pagerduty".format(bastion_user)

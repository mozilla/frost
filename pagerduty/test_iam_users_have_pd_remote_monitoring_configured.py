import pytest
from aws.iam.resources import get_all_users_that_can_access_aws_account
from pagerduty.helpers import alternate_names_for_user
from pagerduty.resources import (
    users_with_remote_access_escalation_policy_and_extension_configured,
)


@pytest.mark.pagerduty
@pytest.mark.parametrize("iam_user", list(get_all_users_that_can_access_aws_account()))
def test_iam_users_have_pd_remote_monitoring_configured(
    iam_user, users_with_remote_access_escalation_policy_and_extension_configured
):
    """
    Checks that users with access to an AWS account have pagerduty  remote monitoring properly configured.
    """
    assert any(
        username in users_with_remote_access_escalation_policy_and_extension_configured
        for username in alternate_names_for_user(iam_user)
    ), "iam user {} is not configured in pagerduty".format(iam_user)

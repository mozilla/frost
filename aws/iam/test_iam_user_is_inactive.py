import pytest

from aws.iam.resources import iam_get_credential_report
from aws.iam.helpers import user_is_inactive


@pytest.fixture
def considered_inactive(pytestconfig):
    return pytestconfig.custom_config.aws.considered_inactive()


@pytest.fixture
def grace_period(pytestconfig):
    return pytestconfig.custom_config.aws.grace_period()


@pytest.mark.iam
@pytest.mark.parametrize(
        'iam_user_row',
        iam_get_credential_report(),
        ids=lambda user: user['user'])
def test_iam_user_is_inactive(iam_user_row, considered_inactive, grace_period):
    """Tests if a user is inactive. This is done by checking the last time
    an access key was used or the user logged into the console. If the config
    settings are not present, it defaults to considering a year ago as inactive
    and giving a user a 1 week grace period.
    """
    assert not user_is_inactive(iam_user_row, grace_period, considered_inactive), \
        "User {} hasn't been used since {} and is out of the grace period.".format(
            iam_user_row['user'], considered_inactive.date()
        )

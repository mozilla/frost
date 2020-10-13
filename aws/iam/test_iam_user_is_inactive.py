import pytest

from helpers import get_param_id

from aws.iam.resources import iam_get_credential_report
from aws.iam.helpers import user_is_inactive


@pytest.fixture
def no_activity_since(pytestconfig):
    return pytestconfig.custom_config.aws.no_activity_since()


@pytest.fixture
def created_after(pytestconfig):
    return pytestconfig.custom_config.aws.created_after()


@pytest.mark.iam
@pytest.mark.parametrize(
    "iam_user_row",
    iam_get_credential_report(),
    ids=lambda user: get_param_id(user, "user"),
)
def test_iam_user_is_inactive(iam_user_row, no_activity_since, created_after):
    """Tests if a user is inactive. This is done by checking the last time
    an access key was used or the user logged into the console. If the config
    settings are not present, it defaults to considering a year ago as inactive
    and giving a user a 1 week grace period (created_after).
    """
    assert not user_is_inactive(
        iam_user_row, no_activity_since, created_after
    ), "User {} hasn't been used since {} and is out of the grace period.".format(
        iam_user_row["user"], no_activity_since.date()
    )

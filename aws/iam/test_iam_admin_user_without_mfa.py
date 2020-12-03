import pytest

from aws.iam.helpers import get_iam_resource_id
from aws.iam.resources import iam_admin_login_profiles, iam_admin_mfa_devices


@pytest.mark.iam
@pytest.mark.parametrize(
    ["iam_login_profile", "iam_user_mfa_devices"],
    zip(iam_admin_login_profiles(), iam_admin_mfa_devices()),
    ids=get_iam_resource_id,
)
def test_iam_admin_user_without_mfa(iam_login_profile, iam_user_mfa_devices):
    """Test that all "admin" users with console access also have an MFA device.

    Note: Due to the naive mechanism for determing what an "admin" is, this test
    can easily have both false positives and (more likely) false negatives.
    """
    if bool(iam_login_profile):
        assert len(iam_user_mfa_devices) > 0, "No MFA Device found for {}".format(
            iam_login_profile["UserName"]
        )

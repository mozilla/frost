import pytest

from aws.iam.resources import iam_user_login_profiles, iam_user_mfa_devices


@pytest.mark.iam
@pytest.mark.parametrize(
    ["iam_login_profile", "iam_user_mfa_devices"],
    zip(iam_user_login_profiles(), iam_user_mfa_devices()),
    ids=lambda login: login["UserName"],
)
def test_iam_user_without_mfa(iam_login_profile, iam_user_mfa_devices):
    """Test that all users with console access also have an MFA device.
    """
    if bool(iam_login_profile):
        assert len(iam_user_mfa_devices) > 0, "No MFA Device found for {}".format(
            iam_login_profile["UserName"]
        )

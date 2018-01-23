import pytest

from aws.iam.resources import (
    iam_admin_login_profiles,
    iam_admin_mfa_devices,
)

@pytest.mark.iam
@pytest.mark.parametrize(
        ['iam_login_profile', 'iam_user_mfa_devices'],
        zip(iam_admin_login_profiles(), iam_admin_mfa_devices()),
        ids=lambda login: login['UserName'])
def test_iam_admin_user_without_mfa(iam_login_profile, iam_user_mfa_devices):
    if bool(iam_login_profile):
        assert len(iam_user_mfa_devices) > 0

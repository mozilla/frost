import pytest

from aws.iam.helpers import get_iam_user_name
from aws.iam.resources import iam_admin_users_with_credential_report


@pytest.mark.iam
@pytest.mark.parametrize(
    "iam_admin_user", iam_admin_users_with_credential_report(), ids=get_iam_user_name,
)
def test_iam_admin_user_with_access_key(iam_admin_user):
    """Test that all "admin" users do not have access keys
    associated to their user.

    Note: Due to the naive mechanism for determing what an "admin" is, this test
    can easily have both false positives and (more likely) false negatives.
    """
    assert (
        iam_admin_user["CredentialReport"]["access_key_1_active"] != "true"
    ), "Access key found for admin user: {}".format(iam_admin_user["UserName"])
    assert (
        iam_admin_user["CredentialReport"]["access_key_2_active"] != "true"
    ), "Access key found for admin user: {}".format(iam_admin_user["UserName"])

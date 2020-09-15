import pytest

from helpers import get_param_id

from aws.iam.resources import iam_admin_roles


@pytest.mark.iam
@pytest.mark.parametrize(
    "iam_admin_role",
    iam_admin_roles(),
    ids=lambda role: get_param_id(role, "RoleName"),
)
def test_iam_cross_account_admin_roles_require_mfa(iam_admin_role):
    """Test that all IAM Roles that include admin policies and have cross account
    trust relationships require MFA.

    Note: Due to the naive mechanism for determing what an "admin" is, this test
    can easily have both false positives and (more likely) false negatives.
    """
    for statement in iam_admin_role["AssumeRolePolicyDocument"]["Statement"]:
        if statement["Action"].startswith("sts") and "AWS" in statement["Principal"]:
            assert "Condition" in statement
            assert "aws:MultiFactorAuthPresent" in statement["Condition"]["Bool"]
            assert (
                statement["Condition"]["Bool"]["aws:MultiFactorAuthPresent"] == "true"
            )

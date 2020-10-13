import pytest

from helpers import get_param_id

from gcp.iam.resources import project_iam_bindings


@pytest.mark.gcp_iam
@pytest.mark.parametrize(
    "iam_binding", project_iam_bindings(), ids=lambda r: get_param_id(r, "role"),
)
def test_admin_service_accounts(iam_binding):
    """
    No Service Account should have the `role/editor`
    or `role/owner` roles attached or any roles matching `*Admin`

    CIS 1.4
    """
    if (iam_binding["role"] in ["role/editor", "role/owner"]) or (
        iam_binding["role"].endswith("Admin")
    ):
        for member in iam_binding["members"]:
            assert not member.startswith("serviceAccount")

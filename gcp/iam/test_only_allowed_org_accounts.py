import pytest

from helpers import get_param_id

from gcp.iam.resources import project_iam_bindings


@pytest.fixture
def allowed_org_domains(pytestconfig):
    return pytestconfig.custom_config.gcp.allowed_org_domains


EXCLUDED_ROLES = ["roles/logging.viewer"]


@pytest.mark.gcp_iam
@pytest.mark.parametrize(
    "iam_binding", project_iam_bindings(), ids=lambda r: get_param_id(r, "role"),
)
def test_only_allowed_org_accounts(iam_binding, allowed_org_domains):
    """
    Only allow specified org domains as members within this project, with a few exceptions.
        * Service Accounts are excluded
        * The following roles are excluded:
            - roles/logging.viewer
    """
    if len(allowed_org_domains) == 0:
        assert False, "No allowed org domains specified"

    if iam_binding["role"] not in EXCLUDED_ROLES:
        for member in iam_binding["members"]:
            if not member.startswith("serviceAccount") and not member.startswith(
                "deleted:serviceAccount"
            ):
                assert (
                    member.split("@")[-1] in allowed_org_domains
                ), "{} was found and is not in the allowed_org_domains".format(member)

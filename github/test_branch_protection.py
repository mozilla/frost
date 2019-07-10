"""
Check for branch protection consistancy and compliance
"""
import helpers
import resources
import pyjq
import pytest


@pytest.mark.github_org
@pytest.mark.rationale(
        """
Compliance check: production branches must be protected.
"""
)
@pytest.mark.parametrize(
        "org, repo, repo_state, branch, date",
        resources.org_default_branches(),
)
def test_default_branch_protected(org, repo, repo_state, branch, date):
    org_json = resources.get_org_json(org)
    # by definition, archived repos are protected. This means meta data
    # is out of sync, but that's tested elsewhere
    if helpers.is_repo_archived(org, repo):
        return
    jq_branch_record = f"""
        .[] |  # for each element
        select(.url == "/repos/{org}/{repo}/branches/{branch}") # just this branch
        """
    branch_data = pyjq.all(jq_branch_record, org_json)
    assert len(branch_data) == 1
    assert branch_data[0]["body"]["protected"]

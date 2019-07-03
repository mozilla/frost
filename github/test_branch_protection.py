"""
Check for branch protection consistancy and compliance
"""
import helpers
import resources
import pyjq
import pytest



@pytest.mark.github_org
@pytest.mark.xfail(reason="no repos for org")
@pytest.mark.rationale(
        """
Consistency check for metadata. If we're examining an org, there should
be repos we care about in it. (Warning)
"""
)
@pytest.mark.parametrize(
        "repo_list",
        [(resources.repos_of_interest_for_org()),],
)
def test_repos(repo_list):
    assert len(repo_list) > 0



@pytest.mark.github_org
@pytest.mark.xfail(reason="no default branch for repo")
@pytest.mark.rationale(
        """
Consistency check for data. If we're examining a repository, there
should be a default branch. (Unknown if true when the repo is
degenerate.) (Warning)
"""
)
@pytest.mark.parametrize(
        "repo_default_branches",
        [(resources.org_default_branches()),],
)
def test_org_branches(repo_default_branches):
    assert len(repo_default_branches) > 0


@pytest.mark.github_org
@pytest.mark.rationale(
        """
Compliance check: production branches must be protected.
"""
)
@pytest.mark.parametrize(
        "org, repo, branch, date",
        resources.org_default_branches(),
)
def test_default_branch_protected(org, repo, branch, date):
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



@pytest.mark.github_org
@pytest.mark.xfail(reason="Archived repo in metadata active list")
@pytest.mark.rationale(
        """
Consistency check: branches in metadata should not be archived
"""
)
@pytest.mark.parametrize(
        "org, repo, branch, date",
        resources.org_default_branches(),
)
def test_no_archived_repos_in_active_metadata(org, repo, branch, date):
    assert helpers.is_repo_archived(org, repo)

"""
Check for metadata consistancy

Tests in this file check whether or not our documented state of the
world (foxsec/services/metadata) is consistent with the observed world.
In most cases, that means the metadata hasn't been updated to match the
real world.  

In general, that means the work will fall on secops to get the metadata
corrected.
"""
from github import helpers, resources
import pyjq
import pytest


@pytest.mark.gh_consistency
@pytest.mark.github_org
@pytest.mark.rationale(
    """
Consistency check for metadata. If we're examining an org, there should
be repos we care about in it.
"""
)
@pytest.mark.parametrize("repo_list", [(resources.repos_of_interest_for_org())])
def test_repos(repo_list):
    assert len(repo_list) > 0


@pytest.mark.gh_consistency
@pytest.mark.github_org
@pytest.mark.rationale(
    """
Consistency check for data. If we're examining a repository, there
should be a default branch. (Unknown if true when the repo is
degenerate. This could be a race condition, so leaving as a consistency
check for now.)
"""
)
@pytest.mark.parametrize("repo_default_branches", [(resources.org_default_branches())])
def test_org_branches(repo_default_branches):
    assert len(repo_default_branches) > 0


@pytest.mark.gh_consistency
@pytest.mark.github_org
@pytest.mark.rationale(
    """
Consistency check: repositories in metadata should only be archived if
their status is "deprecated".
"""
)
@pytest.mark.parametrize(
    "org, repo, repo_state, branch, date", resources.org_default_branches()
)
def test_no_archived_repos_in_active_metadata(org, repo, repo_state, branch, date):
    archived = helpers.is_repo_archived(org, repo)
    assert (not archived) or (archived and repo_state == "deprecated")


@pytest.mark.gh_consistency
@pytest.mark.github_org
@pytest.mark.rationale(
    """
Consistency check: repositories in metadata should not have a status of "unknown".
"""
)
@pytest.mark.parametrize(
    "org, repo, repo_state, branch, date", resources.org_default_branches()
)
def test_no_unknown_repos_in_active_metadata(org, repo, repo_state, branch, date):
    assert repo_state != "unknown"


@pytest.mark.gh_consistency
@pytest.mark.github_org
@pytest.mark.rationale(
    """
Consistency check: branches in metadata must exist in repository
"""
)
@pytest.mark.parametrize("org, repo, branch", resources.org_production_branches())
def test_production_branch_existance(org, repo, branch):
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
    # branch may not exist (that's checked elsewhere)
    assert len(branch_data)

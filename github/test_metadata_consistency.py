"""
Check for metadata consistancy

Tests in this file check whether or not our documented state of the
world (foxsec/services/metadata) is consistent with the observed world.
In most cases, that means the metadata hasn't been updated to match the
real world.  

In general, that means the work will fall on secops to get the metadata
corrected.
"""
import helpers
import resources
import pyjq
import pytest



@pytest.mark.github_org
@pytest.mark.rationale(
        """
Consistency check for metadata. If we're examining an org, there should
be repos we care about in it.
"""
)
@pytest.mark.parametrize(
        "repo_list",
        [(resources.repos_of_interest_for_org()),],
)
def test_repos(repo_list):
    assert len(repo_list) > 0



@pytest.mark.github_org
@pytest.mark.rationale(
        """
Consistency check for data. If we're examining a repository, there
should be a default branch. (Unknown if true when the repo is
degenerate. This could be a race condition, so leaving as a consistency
check for now.)
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
Consistency check: repositories in metadata should only be archived if
their status is "deprecated".
"""
)
@pytest.mark.parametrize(
        "org, repo, repo_state, branch, date",
        resources.org_default_branches(),
)
def test_no_archived_repos_in_active_metadata(org, repo, repo_state, branch, date):
    assert helpers.is_repo_archived(org, repo)


@pytest.mark.github_org
@pytest.mark.rationale(
        """
Consistency check: repositories in metadata should not have a status of "unknown".
"""
)
@pytest.mark.parametrize(
        "org, repo, repo_state, branch, date",
        resources.org_default_branches(),
)
def test_no_unknonw_repos_in_active_metadata(org, repo, repo_state, branch, date):
    assert repo_state != "unknown"

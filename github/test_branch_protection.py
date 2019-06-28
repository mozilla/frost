"""
Check for branch protection
"""
import resources as r
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
        [(r.repos_of_interest_for_org()),],
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
        [(r.org_default_branches()),],
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
        r.org_default_branches(),
)
def test_default_branch_protected(org, repo, branch, date):
    org_json = r.get_org_json(org)
    jq_branch_record = f"""
        .[] |  # for each element
        select(.url == "/repos/{org}/{repo}/branches/{branch}") # just this branch
        """
    branch_data = pyjq.all(jq_branch_record, org_json)
    assert len(branch_data) == 1
    assert branch_data[0]["body"]["protected"]

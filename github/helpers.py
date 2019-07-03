import functools

import pyjq
import resources


@functools.lru_cache()
def is_repo_archived(org, repo):
    """
    Return True if repo is archived
    """
    org_json = resources.get_org_json(org)
    jq_script = f"""
    .[] |  # for each element
    select(.url == "/repos/{org}/{repo}") # just this repo
    """
    repo_data = pyjq.all(jq_script, org_json)
    assert len(repo_data) == 1
    return repo_data[0]["body"]["archived"]

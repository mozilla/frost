"""
Check for branch protection
"""
import itertools
import json
import os

import pyjq
import pytest

def test_repos(repos_of_interest_for_org):
    print(f"repos: {len(repos_of_interest_for_org)}")
    assert len(repos_of_interest_for_org) > 0

def test_org_branches(org_default_branches):
    print(f"branches: {len(org_default_branches)}")
    assert len(org_default_branches) > 0

def test_default_branch_protected(org_filler, def_branch, 
        get_org_json, ):
    org_json = get_org_json
    org, repo, branch, _ = def_branch
    jq_branch_record = f"""
        .[] |  # for each element
        select(.url == "/repos/{org}/{repo}/branches/{branch}") # just this branch
        """
    branch_data = pyjq.all(jq_branch_record, org_json)        
    assert len(branch_data) == 1
    assert branch_data[0]["body"]["protected"]

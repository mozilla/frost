#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Any

from .retrieve_github_data import get_repo_branch_protections
from . import validate_compliance
from .conftest import repos_to_check


import pytest


@pytest.mark.parametrize("repo_to_check", repos_to_check())
def test_branch_protection_failures(gql_connection: Any, repo_to_check: str) -> None:
    # given a repository and branch that are supposed to be protected
    line = repo_to_check
    # for line in repos_to_check:
    if "," in line:
        url, branch = line.split(",")
    else:
        url, branch = line, None
    owner, repo = url.split("/")[3:5]
    # when we check the protection settings
    branch_protections = get_repo_branch_protections(gql_connection, f"{owner}/{repo}")
    compliance_level = validate_compliance.validate_branch_protections(
        branch_protections, branch
    )
    # then we find no failures
    failures = [x for x in compliance_level if x.startswith("ERROR:")]
    assert not failures


##def test_branch_protection_warnings(repos_to_check: str) -> None:
##    # given a repository and branch that are supposed to be protected
##    return
##    assert repos_to_check == ""
##    owner, repo = repo_full.split("/")
##    # when we check the protection settings
##    compliance_level = validate_compliance.validate_branch_protections(
##        owner, repo, branch
##    )
##    # then we do not expect any conflict warnings
##    assert "WARNING" not in compliance_level

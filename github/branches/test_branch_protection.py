#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from github.branches.validate_compliance import Criteria
from typing import Any, Optional

from .retrieve_github_data import BranchOfInterest, get_repo_branch_protections
from .retrieve_github_data import repos_to_check
from . import validate_compliance

# from .conftest import repos_to_check


import pytest


def idfn(val: Any) -> Optional[str]:
    string = None
    if isinstance(val, (str,)):
        if val.startswith("https://"):
            string = "/".join(val.split("/")[3:5])
    return string


@pytest.mark.parametrize("repo_to_check", repos_to_check(), ids=idfn)
@pytest.mark.parametrize(
    "criteria", validate_compliance.required_criteria, ids=Criteria.idfn
)
def test_required_protections(
    gql_connection: Any, repo_to_check: BranchOfInterest, criteria: Criteria
) -> None:
    protections = get_repo_branch_protections(
        gql_connection, f"{repo_to_check.owner}/{repo_to_check.repo}"
    )
    rules = protections.protection_rules

    if not rules:
        assert (
            False
        ), f"ERROR:SOGH001:{repo_to_check.owner}/{repo_to_check.repo}:{repo_to_check.branch} has no branch protection"
    else:
        met, message = validate_compliance.validate_branch_protections(
            protections, repo_to_check.branch, criteria
        )
        assert met, message

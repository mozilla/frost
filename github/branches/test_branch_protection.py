#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from github.branches.validate_compliance import Criteria
from typing import Any, Optional

from .retrieve_github_data import get_repo_branch_protections
from . import validate_compliance
from .conftest import repos_to_check


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
    gql_connection: Any, repo_to_check: str, criteria: Criteria
) -> None:
    line = repo_to_check
    # for line in repos_to_check:
    if "," in line:
        url, branch = line.split(",")
    else:
        url, branch = line, None
    owner, repo = url.split("/")[3:5]
    protections = get_repo_branch_protections(gql_connection, f"{owner}/{repo}")
    rules = protections.protection_rules

    if not rules:
        assert False, f"ERROR:SOGH001:{owner}/{repo}:{branch} has no branch protection"
    else:
        met, message = validate_compliance.validate_branch_protections(
            protections, branch, criteria
        )
        assert met, message

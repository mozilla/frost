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
@pytest.mark.parametrize("criteria", validate_compliance.required_criteria)
def test_required_protections(
    gql_connection: Any, repo_to_check: str, criteria: str
) -> None:
    line = repo_to_check
    # for line in repos_to_check:
    if "," in line:
        url, branch = line.split(",")
    else:
        url, branch = line, None
    owner, repo = url.split("/")[3:5]
    rules = get_repo_branch_protections(gql_connection, f"{owner}/{repo}")
    if not rules:
        assert False, f"ERROR:SOGH001:{owner}/{repo}:{branch} has no branch protection"
    else:
        met, message = validate_compliance.validate_branch_protections(
            rules, branch, criteria
        )
        assert met, message

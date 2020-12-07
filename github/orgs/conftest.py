#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# PyTest support for the various GitHub organization checks

# Implementation decisions:
# - defer adding rate limiting support until needed: https://github.com/mozilla/frost/issues/426

from functools import lru_cache
from github.branches.validate_compliance import Criteria
from github.orgs.retrieve_github_data import OrgInfo
import os
import pathlib

from typing import List, Set

import subprocess  # nosec

from sgqlc.endpoint.http import HTTPEndpoint

from conftest import METADATA_KEYS  # noqa: I900


from . import retrieve_github_data
import conftest

METADATA_KEYS.update(OrgInfo.metadata_to_log())
METADATA_KEYS.update(Criteria.metadata_to_log())


@lru_cache(maxsize=32)
def get_branch_info(gql_connection, repo_full_name: str) -> str:
    repo_info = retrieve_github_data.get_repo_branch_protections(
        gql_connection, repo_full_name
    )
    return repo_info

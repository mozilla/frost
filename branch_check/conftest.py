#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Fixtures to fetch data for the various GitHub branch checks

# TODO:
# - convert to logger output
# - add sleep_* for 'core' functionality

# from datetime import datetime
from functools import lru_cache
import os
import pathlib

# import time
from typing import List

# import sys
import subprocess

import pytest

# from sgqlc.operation import Operation  # noqa: I900
from sgqlc.endpoint.http import HTTPEndpoint  # noqa: I900

# from github_schema import github_schema as schema  # noqa: I900

#  import branch_check.retrieve_github_data as retrieve_github_data
import retrieve_github_data


# Data to move to config
DEFAULT_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
EXTENSION_TO_STRIP = ".git"
PATH_TO_METADATA = "~/repos/foxsec/require-branch/services/metadata"


# Data collection routines -- these likely should be a separate python
# package, as they are useful outside of frost as written
@pytest.fixture(scope="session", autouse=True)
def gql_connection():
    token = os.environ["GH_TOKEN"]
    endpoint = HTTPEndpoint(
        DEFAULT_GRAPHQL_ENDPOINT, {"Authorization": "bearer " + token,},
    )
    return endpoint


@pytest.fixture(scope="session")
def repos_to_check() -> List[List[str]]:
    # just shell out for now
    meta_dir = pathlib.Path(os.path.expanduser(PATH_TO_METADATA)).resolve()
    in_files = list(meta_dir.glob("*.json"))

    cmd = [
        "jq",
        "-rc",
        """.codeRepositories[]
                | .url as $url
                | .branchesToProtect[] // ""
                | [$url, . ]
                | @csv
                """,
        *in_files[:3],
    ]

    status = subprocess.run(cmd, capture_output=True)
    # return as array of non-empty, unquoted, "lines"
    return [
        x.translate({ord('"'): None, ord("'"): None})
        for x in status.stdout.decode("utf-8").split("\n")
        if x
    ]


@lru_cache(maxsize=32)
def get_branch_info(gql_connection, repo_full_name: str) -> str:
    repo_info = retrieve_github_data.get_repo_branch_protections(
        gql_connection, repo_full_name
    )
    return repo_info


if __name__ == "__main__":
    if os.environ.get("DEBUG"):
        print(repos_to_check())
        # for name in sys.argv[1:]:
        #     data = get_branch_info(gql_connection(), name)
        #     print(data)

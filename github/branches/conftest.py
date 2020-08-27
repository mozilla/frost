#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# PyTest support for the various GitHub branch checks

# TODO convert to logger output
# TODO add sleep_* for 'core' functionality

from functools import lru_cache
import os
import pathlib
from typing import List
import subprocess

import pytest

from sgqlc.endpoint.http import HTTPEndpoint  # noqa: I900

from . import retrieve_github_data

# Needed to dynamically grab globals
import conftest


def repos_to_check() -> List[str]:
    # just shell out for now
    # TODO: fix ickiness
    #   While there is no network operation done here, we don't want to go
    #   poking around the file system if we're in "--offline" mode
    #   (e.g. doctest mode)
    global github_client
    if conftest.get_client("github").is_offline():
        return []

    # real work
    path_to_metadata = os.environ["PATH_TO_METADATA"]
    meta_dir = pathlib.Path(os.path.expanduser(path_to_metadata)).resolve()
    in_files = list(meta_dir.glob("*.json"))

    cmd = [
        "jq",
        "-rc",
        """.codeRepositories[]
                | select(.status == "active")
                | .url as $url
                | .branchesToProtect[] // ""
                | [$url, . ]
                | @csv
                """,
        *in_files,
    ]

    # python 3.6 doesn't support capture_output
    # status = subprocess.run(cmd, capture_output=True)
    status = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # return as array of non-empty, unquoted, "lines"
    return [
        x.translate({ord('"'): None, ord("'"): None})
        for x in status.stdout.decode("utf-8").split("\n")
        if x
    ]


# we expect to (eventually) make multiple tests against the same branch data
@lru_cache(maxsize=32)
def get_branch_info(gql_connection, repo_full_name: str) -> str:
    assert False
    repo_info = retrieve_github_data.get_repo_branch_protections(
        gql_connection, repo_full_name
    )
    return repo_info


if __name__ == "__main__":
    # TODO add doctests
    pass

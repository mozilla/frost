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
from typing import List, Set

# import sys
import subprocess

import pytest

# from sgqlc.operation import Operation  # noqa: I900
from sgqlc.endpoint.http import HTTPEndpoint  # noqa: I900

# from github_schema import github_schema as schema  # noqa: I900

#  import branch_check.retrieve_github_data as retrieve_github_data
from . import retrieve_github_data


def orgs_to_check() -> Set[str]:
    # just shell out for now
    path_to_metadata = os.environ["PATH_TO_METADATA"]
    meta_dir = pathlib.Path(os.path.expanduser(path_to_metadata)).resolve()
    in_files = list(meta_dir.glob("*.json"))

    cmd = [
        "jq",
        "-rc",
        """.codeRepositories[]
                | select(.status == "active")
                | [.url]
                | @csv
                """,
        *in_files,
    ]

    # python 3.6 doesn't support capture_output
    # status = subprocess.run(cmd, capture_output=True)
    status = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert not status.stderr.decode("utf-8")
    # return as array of non-empty, unquoted, "lines"
    return {
        x.split("/")[3].translate({ord('"'): None, ord("'"): None})
        for x in status.stdout.decode("utf-8").split("\n")
        if x
    }


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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# PyTest support for the various GitHub organization checks

# TODO: convert to logger output
# TODO: add sleep_* for 'core' functionality

from functools import lru_cache
import os
import pathlib

from typing import List, Set

import subprocess

from sgqlc.endpoint.http import HTTPEndpoint  # noqa: I900


from . import retrieve_github_data
import conftest


def orgs_to_check() -> Set[str]:
    # just shell out for now
    #   While there is no network operation done here, we don't want to go
    #   poking around the file system if we're in "--offline" mode
    #   (aka doctest mode)
    if conftest.get_client("github_client").is_offline():
        return []
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

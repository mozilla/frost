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

# Data to move to config
DEFAULT_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
EXTENSION_TO_STRIP = ".git"

# check for all required environment variables so we can fail fast
os.environ["PATH_TO_METADATA"]
os.environ["GH_TOKEN"]


# Data collection routines -- these likely should be a separate python
# package, as they are useful outside of frost as written
@pytest.fixture(scope="session", autouse=True)
def gql_connection():
    token = os.environ["GH_TOKEN"]
    endpoint = HTTPEndpoint(
        DEFAULT_GRAPHQL_ENDPOINT, {"Authorization": "bearer " + token,},
    )
    return endpoint


if __name__ == "__main__":
    if os.environ.get("DEBUG"):
        print(repos_to_check())
        # for name in sys.argv[1:]:
        #     data = get_branch_info(gql_connection(), name)
        #     print(data)

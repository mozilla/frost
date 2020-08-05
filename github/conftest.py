#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Fixtures to fetch data for the various GitHub branch checks

# TODO:
# - convert to logger output
# - add sleep_* for 'core' functionality

from functools import lru_cache
import logging
import os
import pathlib

from typing import List

import subprocess

import pytest

# from sgqlc.operation import Operation  # noqa: I900
from sgqlc.endpoint.http import HTTPEndpoint  # noqa: I900

logger = logging.getLogger(__name__)
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
    # tack on error reporting so it's available everywhere needed
    endpoint.report_download_errors = _report_download_errors
    return endpoint


def _compact_fmt(d):
    s = []
    for k, v in d.items():
        if isinstance(v, dict):
            v = _compact_fmt(v)
        elif isinstance(v, (list, tuple)):
            lst = []
            for e in v:
                if isinstance(e, dict):
                    lst.append(_compact_fmt(e))
                else:
                    lst.append(repr(e))
            s.append("%s=[%s]" % (k, ", ".join(lst)))
            continue
        s.append("%s=%r" % (k, v))
    return "(" + ", ".join(s) + ")"


def _report_download_errors(errors):
    """ error handling for graphql comms """
    logger.error("Document contain %d errors", len(errors))
    for i, e in enumerate(errors):
        msg = e.pop("message")
        extra = ""
        if e:
            extra = " %s" % _compact_fmt(e)
        logger.error("Error #%d: %s%s", i + 1, msg, extra)


if __name__ == "__main__":
    if os.environ.get("DEBUG"):
        print(repos_to_check())
        # for name in sys.argv[1:]:
        #     data = get_branch_info(gql_connection(), name)
        #     print(data)

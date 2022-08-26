#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Fixtures to fetch data for the various GitHub branch checks

# TODO: add doctests

# Implementation decisions:
# - defer adding rate limiting support until needed: https://github.com/mozilla/frost/issues/426


from conftest import github_client
from dataclasses import dataclass
from functools import lru_cache
import logging
import os
from typing import List

import pytest

from sgqlc.endpoint.http import HTTPEndpoint  # noqa: I900
import conftest

logger = logging.getLogger(__name__)
# Data to move to config
DEFAULT_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"


# Data collection routines -- these likely should be a separate python
# package, as they are useful outside of frost as written
@pytest.fixture(scope="session", autouse=True)
def gql_connection():
    # Frost integration -- this routine controls all of our real system access,
    # so we must honor the --offline option to support doctests
    if not conftest.github_client.is_offline():
        # check for all required environment variables so we can fail fast
        # however, we only check once inside a session. This allows import
        # of this module in other contexts, such as running doctests,
        # without irrelevant configuration

        token = os.environ["GH_TOKEN"]
        logger.error("using PAT %s".format(token))
        endpoint = HTTPEndpoint(
            DEFAULT_GRAPHQL_ENDPOINT,
            {
                "Authorization": "bearer " + token,
            },
        )
    else:
        endpoint = {}
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
            s.append("{}=[{}]".format(k, ", ".join(lst)))
            continue
        s.append(f"{k}={v!r}")
    return "(" + ", ".join(s) + ")"


def _report_download_errors(errors):
    """error handling for graphql comms."""
    logger.error("Document contain %d errors", len(errors))
    for i, e in enumerate(errors):
        msg = e.pop("message")
        extra = ""
        if e:
            extra = " %s" % _compact_fmt(e)
        logger.error("Error #%d: %s%s", i + 1, msg, extra)

#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/

import sys
import os
from pathlib import Path


# Pretend we're running from the root of frost
# that lets us use absolute imports, and avoid "beyond package" errors
# TODO: refactor to avoid this (may not be possible)
sys.path.append(str(Path(__file__).resolve().parents[1]))

from github.orgs import retrieve_github_data as org_retrieve_github_data
from github.branches import retrieve_github_data as branch_retrieve_github_data

# org will get metadata orgs if none supplied
org_retrieve_github_data.main()

# branch does not have default, so pass along current command line
# N.B. since that will also happen in pytest's doctest mode, that
#      special case is dealt with in the parse_args function
branch_retrieve_github_data.main()

#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/

import sys
from pathlib import Path


# Pretend we're running from the root of frost
# that lets us use absolute imports, and avoid "beyond package" errors
# TODO: refactor to avoid this (may not be possible)
# TODO: see if this file can be folded into frost's cli wrapper support.
sys.path.append(str(Path(__file__).resolve().parents[1]))

import orgs.retrieve_github_data as org_retrieve_github_data
from github.branches import retrieve_github_data as branch_retrieve_github_data

if __name__ == "__main__":

    sub_command = sys.argv[1]
    del sys.argv[1]
    if sub_command == "orgs":
        # org will get metadata orgs if none supplied
        org_retrieve_github_data.main()
    elif sub_command == "branches":
        # branch does not have default, so pass along current command line
        # N.B. since that will also happen in pytest's doctest mode, that
        #      special case is dealt with in the parse_args function
        branch_retrieve_github_data.main()
    elif sub_command == "--doctest-modules":
        # Another special case
        pass
    else:
        raise SystemError(f"Unknown sub command '{sub_command}'")

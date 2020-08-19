#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Perform actions based on frost results"""

import argparse
import json
import re
from dataclasses import dataclass
from pprint import pprint
from typing import List

import argcomplete

_epilog = ""

# constants
# Sample line
SPEC_DECODER_RE = re.compile(
    r"""
    (?P<path>[^:]+):: # path
    (?P<method>\w+)\[ # method
    (?P<test_name>[^-]+)- # assumes no hyphen in test_name
    (?P<param_id>[^]]+)\]
""",
    re.VERBOSE,
)

# Sample line:
#  E   AssertionError: ERROR:SOGH003:firefox-devtools doesn't meet two factor required - required\n    assert False
ASSERT_DECODER_RE = re.compile(
    r"""
    (E\s+AssertionError:)?\s*  # preamble
    (?P<severity>[^:]+):
    (?P<standard>[^:]+):
    (?P<info>\S+)
""",
    re.VERBOSE | re.MULTILINE,
)


@dataclass
class Action:
    owner: str
    repo: str
    branch: str


def parse_action_string(name: str) -> List[str]:
    """
    comment
    """
    matches = SPEC_DECODER_RE.match(name)
    return matches.groups()


def infer_resource_type(path: str) -> str:
    """infer object type

    This relies on the file system structure of the tests
    We currently assume it is:
        "github/" resource_type "/.*"
    """
    prefix = "github/"
    start = path.find(prefix) + len(prefix)
    end = path.find("/", start)
    resource_type = path[start:end]
    return resource_type


def extract_standard(assert_msg: str) -> str:
    """
    pull standard(s) out of the assert string

    TODO:
    - support more than one result in string
    """
    for item in ASSERT_DECODER_RE.finditer(assert_msg):
        pprint(item.groupdict()["standard"])


def create_branch_action(action_spec: dict) -> Action:
    """Parse pytest info into information needed to open an issue against a
    specific branch"""

    path, method, test_name, param_id = parse_action_string(action_spec["full_name"])
    standard = extract_standard(action_spec["longrepr"])
    url, branch = param_id.split(",")
    owner, repo = url.split("/")[3:5]


def create_org_action(action_spec: dict) -> Action:
    """
    Break out the org info from the json
    """
    found = False
    for item in ASSERT_DECODER_RE.finditer(action_spec["longrepr"]):
        pprint(item.groupdict())
        found = True
    if not found:
        raise KeyError(f"Malformed json {repr(action_spec)}")


def create_action_spec(action_spec: dict) -> Action:
    # for now, just return Action -- later decode may involve inferring what to
    # do ("xpass" detection)
    name = action_spec["full_name"]
    path, _, _, _ = parse_action_string(name)
    resource_type = infer_resource_type(path)
    if resource_type == "orgs":
        action = create_org_action(action_spec)
    elif resource_type == "branches":
        action = create_branch_action(action_spec)
    else:
        raise TypeError(f"unknown resource type '{resource_type}' from '{name}")

    # full name is file_path::method[test_name-parametrize_id]
    pprint(action_spec)
    return action


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, epilog=_epilog)
    # parser.add_argument(
    #     "--debug", action="store_true", help="include dump of all data returned"
    # )
    # parser.add_argument("--owners", action="store_true", help="Also show owners")
    # parser.add_argument("--email", action="store_true", help="include owner email")
    # parser.add_argument(
    #     "--all-my-orgs",
    #     action="store_true",
    #     help="act on all orgs for which you're an owner",
    # )
    # parser.add_argument(
    #     "--names-only",
    #     action="store_true",
    #     help="Only output your org names for which you're an owner",
    # )
    parser.add_argument("json_file", help="frost json output")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    with open(args.json_file, "r") as jf:
        issue_actions = json.loads(jf.read())

    print(f"Processing {len(issue_actions)}")
    for action_spec in issue_actions:
        action = create_action_spec(action_spec)

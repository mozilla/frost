#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Perform actions based on frost results."""

import argparse
import json
import re
from dataclasses import dataclass
import logging
from pprint import pprint
from typing import List, Optional, Sequence, Tuple

# import argcomplete  # type: ignore

logger = logging.getLogger(__name__)

_epilog = ""

# constants
# Sample line:
#   github/branches/test_branch_protection.py::test_required_protections[SOGH001b-admins-firefox-devtools/profiler-server.git,]
SPEC_DECODER_RE = re.compile(
    r"""
    (?P<path>[^:]+):: # path
    (?P<method>\w+)\[ # method
    (?P<standard>[^-]+)- # assumes no hyphen in standard
    (?P<test_name>[^-]+)- # assumes no hyphen in test_name
    (?P<param_id>[^]]+)\]
""",
    re.VERBOSE,
)

# Sample lines:
#  E   AssertionError: ERROR:SOGH003:firefox-devtools doesn't meet two factor required - required\n    assert False
#  E   AssertionError: ERROR:SOGH001:firefox-devtools/profiler-server:master has no SOGH001b admins not restricted rule\n    assert False
ASSERT_DECODER_RE = re.compile(
    r"""
    (E\s+AssertionError:)?\s*  # preamble
    (?P<severity>[^:]+):
    (?P<standard>[^:]+):
    (?P<info>\S+)
""",
    re.VERBOSE | re.MULTILINE,
)

# Work on "info" section of branch. Example:
#  firefox-devtools/profiler-server:master
BRANCH_INFO_DECODER_RE = re.compile(
    r"""
    ^
    (?P<owner>[^/]+)/   # repo owner
    (?P<repo>[^:]+):     # repo name
    (?P<branch>\S+)     # branch name
    $
    """,
    re.VERBOSE,
)


@dataclass
class Action:
    final_status: str = ""  # after frost exemption processing
    base_status: str = ""  # native pytest status
    owner: str = ""
    repo: str = ""
    branch: str = ""
    standard: str = ""
    summary: str = ""
    messages: Optional[List[str]] = None


def parse_action_string(name: str) -> Optional[Sequence[str]]:
    """comment."""
    matches = SPEC_DECODER_RE.match(name)
    return matches.groups() if matches else None


def infer_resource_type(path: str) -> str:
    """infer object type.

    This relies on the file system structure of the tests We currently
    assume it is:     "github/" resource_type "/.*"
    """
    prefix = "github/"
    start = path.find(prefix) + len(prefix)
    end = path.find("/", start)
    resource_type = path[start:end]
    return resource_type


def create_branch_action(action_spec: dict) -> Action:
    """Parse pytest info into information needed to open an issue against a
    specific branch."""

    # most information comes from the (parametrized) name of the test
    test_info = action_spec["name"]
    *_, standard, test_name, param_id = parse_action_string(test_info)
    owner, repo = param_id.split("/")

    # details for branches come from the assertion text
    branch_details = action_spec["call"]["longrepr"]
    errors = []
    branch = "BoGuS"
    for item in ASSERT_DECODER_RE.finditer(branch_details):
        info = item.groupdict()["info"]
        # further parse info
        branch = "BoGuS"
        matches = BRANCH_INFO_DECODER_RE.match(info)
        if matches:
            owner, repo, branch = matches.groups()
        errors.append(
            f"Branch {branch} of {owner}/{repo} failed {standard} {test_name}"
        )

    summary = f"{len(errors)} for {owner}/{repo}:{branch}"
    final_status, base_status = get_status(action_spec)
    action = Action(
        final_status=final_status,
        base_status=base_status,
        owner=owner,
        repo=repo,
        branch=branch,
        standard=standard,
        summary=summary,
        messages=errors,
    )
    return action


def get_status(action_spec: dict) -> Tuple[str, str]:
    final_status = action_spec["call"]["outcome"]
    base_status = action_spec["metadata"][0]["outcome"]
    return final_status, base_status


def create_org_action(action_spec: dict) -> Action:
    """Break out the org info from the json."""
    # TODO check for outcome of xfailed (means exemption no longer needed)
    # most information comes from the (parametrized) name of the test
    test_info = action_spec["name"]
    path, method, standard, test_name, param_id = parse_action_string(test_info)
    org_full_name = param_id
    summary = f"Org {org_full_name} failed {standard} {test_name}"
    final_status, base_status = get_status(action_spec)
    action = Action(
        final_status=final_status,
        base_status=base_status,
        owner=org_full_name,
        standard=standard,
        summary=summary,
    )
    return action


def create_action_spec(action_spec: dict) -> Action:
    # for now, just return Action -- later decode may involve inferring what to
    # do ("xpass" detection -- see GH-325)
    # full name is file_path::method[test_name-parametrize_id]
    name = action_spec["name"]
    path, *_ = parse_action_string(name)
    resource_type = infer_resource_type(path)
    if resource_type == "orgs":
        action = create_org_action(action_spec)
    elif resource_type == "branches":
        action = create_branch_action(action_spec)
    else:
        raise TypeError(f"unknown resource type '{resource_type}' from '{name}")

    return action


def _open_issue(action: Action) -> bool:
    """Report status via a GitHub issue.

    Used for actions which relate to a specific repository
    TODO support grouping actions for same main issue.
        i.e. SOGH001[abc] should all report under same issue

    Args:
        action (Action): Information about the type of problem

    Returns:
        bool: True if processed successfully
    """
    logger.info(
        f"GitHub issue regarding {action.standard} relating to {action.owner}/{action.repo}"
    )
    return True


def _alert_owners(action: Action) -> bool:
    """Contact org owners.

    Unsure how to do this - may be slack or email to secops. There is no good native way in GitHub.

    Args:
        action (Action): Information about the type of problem

    Returns:
        bool: True if processed successfully
    """
    logger.info(
        f"Contacting owners regarding {action.standard} relating to org {action.owner}."
    )
    return True


dispatch_table = {
    "SOGH001": _open_issue,
    "SOGH001b": _open_issue,
    "SOGH002": _open_issue,
    "SOGH003": _alert_owners,
}


def perform_action(action: Action) -> bool:
    """Initiate the appropriate action.

    Args:
        action (Action): All the data needed to perform the action

    Returns:
        bool: True if action completed successfully
    """
    if action.standard in dispatch_table:
        return dispatch_table[action.standard](action)
    else:
        logger.error(f"No action defined for standard '{action.standard}'")
        return False


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, epilog=_epilog)
    parser.add_argument("json_file", help="frost json output")
    # argcomplete.autocomplete(parser)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    args = parse_args()

    with open(args.json_file) as jf:
        pytest_report = json.loads(jf.read())

    issue_actions = pytest_report["report"]["tests"]
    print(f"Processing {len(issue_actions)} test results")
    for action_spec in issue_actions:
        if action_spec["call"]["outcome"] == "passed":
            continue
        action = create_action_spec(action_spec)
        # TODO integrate actual issue handling
        # print(action)
        perform_action(action)

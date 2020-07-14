#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import List

from .retrieve_github_data import RepoBranchProtections, BranchProtectionRule

# define the criteria we care about. Identify each critera with a string that will
# appear in the results.
required_criteria = [
    "admins restricted",
]
optional_criteria = [
    "limited commiters",
    # "commit signing",  # may not be knowable
]
warning_criteria = [
    "rule conflicts",
]


def find_applicable_rules(
    data: RepoBranchProtections, branch: str
) -> List[BranchProtectionRule]:
    result = []
    for rule in data.protection_rules:
        for ref_name in rule.matching_branches:
            if branch == ref_name.name:
                result.append(rule)
                break
    return result


def meets_criteria(protections: List[BranchProtectionRule], criteria: str) -> bool:
    met = True
    # ugly implementation for now
    if criteria == "admins restricted":
        met = all(r.is_admin_enforced for r in protections)
    elif criteria == "limited commiters":
        met = all(r.push_actor_count > 0 for r in protections)
    elif criteria == "rule conflicts":
        met = all(r.rule_conflict_count == 0 for r in protections)
    else:
        print(f"ERROR: no support for '{criteria}'")
    return met


def validate_branch_protections(data: RepoBranchProtections, branch: str) -> List[str]:
    """
        Validate the protections

        Returns an array of all the issues found
    """

    results = []

    # if the production branch is not specified, use the default name
    if not branch:
        branch = data.default_branch_ref.name

    # Multiple steps to validate - first, is the branch even covered
    active_rules = find_applicable_rules(data, branch)

    if not active_rules:
        results.append(
            f"ERROR: no branch protection for '{data.name_with_owner}:{branch}'"
        )
    else:
        # see if at least one rule matches each criteria
        for criteria in required_criteria:
            if not meets_criteria(active_rules, criteria):
                results.append(
                    f"ERROR: no {criteria} for branch '{data.name_with_owner}:{branch}' (required)"
                )
        for criteria in optional_criteria:
            if not meets_criteria(active_rules, criteria):
                results.append(
                    f"FYI: no {criteria} for branch '{data.name_with_owner}:{branch}' (optional)"
                )

    # regardless of match, we'll also warn on conflicting rules
    for criteria in warning_criteria:
        if not meets_criteria(active_rules, criteria):
            results.append(
                f"WARNING: {criteria} for branch '{data.name_with_owner}:{branch}'"
            )

    return results

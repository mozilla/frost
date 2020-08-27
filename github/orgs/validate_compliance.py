#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Any, List, Optional, Tuple
from dataclasses import dataclass

from .retrieve_github_data import OrgInfo


@dataclass
class Criteria:
    standard_number: str  # as defined in messages file. alpha-numeric
    slug: str  # id to match. alpha-numeric
    description: str  # whatever you want

    @staticmethod
    def idfn(val: Any) -> Optional[str]:
        """ provide ID for pytest Parametrization
        """
        if isinstance(val, (Criteria,)):
            return f"{val.standard_number}-{val.slug}"
        return None

    def __str__(self: Any) -> str:
        return f"{self.standard_number} {self.description}"


# define the criteria we care about. Identify each critera with a string that will
# appear in the results.
required_criteria: List[Criteria] = [
    Criteria("SOGH003", "2fa", "two factor required"),  # SOGH003
]
optional_criteria: List[Criteria] = [
    # "commit signing",  # may not be knowable
]
warning_criteria: List[Criteria] = []


def meets_criteria(org_info: OrgInfo, criteria: Criteria) -> bool:
    met = True
    # ugly implementation for now
    if criteria.slug == "2fa":
        met = org_info.requires_two_factor_authentication
    else:
        met = False
    return met


def validate_org_info(data: OrgInfo, criteria: Criteria) -> Tuple[bool, str]:
    """
        Validate the protections

    """

    results = []

    for criteria in required_criteria:
        if not meets_criteria(data, criteria):
            results.append(
                f"ERROR:SOGH003:{data.login} doesn't meet {criteria} - required"
            )
    for criteria in warning_criteria:
        if not meets_criteria(data, criteria):
            results.append(
                f"Warning:SOGH003:{data.login} doesn't meet {criteria} - suggested"
            )
    for criteria in optional_criteria:
        if not meets_criteria(data, criteria):
            results.append(
                f"FYI:SOGH003:{data.login} doesn't meet {criteria} - optional"
            )

    return len(results) == 0, "\n".join(results)
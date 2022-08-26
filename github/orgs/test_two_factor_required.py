#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Any, List

import pytest

from github.orgs.validate_compliance import Criteria
from .retrieve_github_data import get_all_org_data, OrgInfo
from . import validate_compliance


@pytest.mark.parametrize("org_info", get_all_org_data(), ids=OrgInfo.idfn)
@pytest.mark.parametrize(
    "criteria", validate_compliance.required_criteria, ids=Criteria.idfn
)
def test_require_2fa(
    gql_connection: Any,
    org_info: List[OrgInfo],
    criteria: validate_compliance.Criteria,
) -> None:
    # we only care about orgs that exist for this criteria
    # renamed orgs or stale data cases are handled in different tests
    if org_info:
        met, message = validate_compliance.validate_org_info(org_info, criteria)
        assert met, message

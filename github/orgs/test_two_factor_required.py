#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from github.orgs.validate_compliance import Criteria
from typing import Any, Optional

from .retrieve_github_data import get_org_info
from . import validate_compliance
from .conftest import orgs_to_check


import pytest


@pytest.mark.parametrize("org_to_check", orgs_to_check())
@pytest.mark.parametrize(
    "criteria", validate_compliance.required_criteria, ids=Criteria.idfn
)
def test_require_2fa(
    gql_connection: Any, org_to_check: str, criteria: validate_compliance.Criteria
) -> None:
    info = get_org_info(gql_connection, f"{org_to_check}")
    if info:
        met, message = validate_compliance.validate_org_info(info, criteria)
        assert met, message

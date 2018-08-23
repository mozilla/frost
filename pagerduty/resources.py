

import functools
import json
from pathlib import Path

import pytest


@pytest.fixture
def users_with_remote_access_escalation_policy_and_extension_configured(pytestconfig):
    p = Path(".")
    users = set()
    for user_file in p.glob(
        pytestconfig.custom_config.pagerduty.users_with_remote_access_monitoring
    ):
        with user_file.open("r") as fin:
            for user in json.load(fin):
                users.add(user["email"].split("@", 1)[0])

    return users


@functools.lru_cache()
def bastion_users():
    p = Path(".")
    users = set()
    for user_file in p.glob(pytest.config.custom_config.pagerduty.bastion_users):
        with user_file.open("r") as fin:
            for user, val in json.load(fin).items():
                if val.get("ensure", None) != "absent":
                    users.add(user)

    return sorted(list(users))


@functools.lru_cache()
def alternate_usernames():
    with open(pytest.config.custom_config.pagerduty.alternate_usernames, "r") as fin:
        return json.load(fin)

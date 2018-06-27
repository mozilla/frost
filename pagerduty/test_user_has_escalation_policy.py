

import os

import pytest
import pygerduty.v2


PD_RO_KEY = os.environ.get("pagerdutyRoKey", None)


def pd_client():
    if not PD_RO_KEY:
        return None
    return pygerduty.v2.PagerDuty(PD_RO_KEY)


def pd_users():
    pager = pd_client()
    if not pager:
        return []

    return pager.users.list()


def pd_users_escalation_policies():
    pager = pd_client()
    if not pager:
        return []

    return [
        pager.escalation_policies.list(user_ids=[user["id"]]) for user in pd_users()
    ]


@pytest.mark.pagerduty
@pytest.mark.skipif(
    lambda: not PD_RO_KEY,
    reason='Env var "pagerdutyRoKey" of Pagerduty API key not found.',
)
@pytest.mark.parametrize(
    ["pd_user", "pd_user_escalation_policy"],
    zip(pd_users(), pd_users_escalation_policies()),
)
def test_user_has_ooh_escalation_policy(pd_user, pd_user_escalation_policy):
    assert (
        pd_user_escalation_policy
    ), "{} does not have an out of hours escalation policy in Pagerduty".format(
        pd_user
    )

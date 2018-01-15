

import os

import pytest
import pygerduty.v2


pager = pygerduty.v2.PagerDuty(os.environ['pagerdutyRoKey'])


def pd_users():
    global pager
    return pager.users.list()


def pd_users_escalation_policies():
    global pager
    return [
        pager.escalation_policies.list(user_ids=[user['id']])
        for user in pd_users()
    ]


@pytest.mark.pagerduty
@pytest.mark.xfail
@pytest.mark.parametrize([
    'pd_user',
    'pd_user_escalation_policy',
], zip(pd_users(), pd_users_escalation_policies()))
def test_user_has_ooh_escalation_policy(
        pd_user,
        pd_user_escalation_policy):
    assert pd_user_escalation_policy, \
      '{} does not have an out of hours escalation policy in Pagerduty'.format(pd_user)

from dateutil.parser import parse

import pytest

from gsuite.admin.resources import list_users


@pytest.fixture
def no_activity_since(pytestconfig):
    return pytestconfig.custom_config.gsuite.no_activity_since()


@pytest.mark.gsuite_admin
@pytest.mark.parametrize('user', list_users(), ids=lambda u: u['primaryEmail'])
def test_admin_user_is_inactive(user, no_activity_since):
    """TODO"""
    if user['lastLoginTime'] != '1970-01-01T00:00:00.000Z':
        assert parse(user['lastLoginTime']) > no_activity_since

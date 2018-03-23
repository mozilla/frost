import pytest

from gsuite.admin.resources import list_users
from gsuite.admin.helpers import user_is_inactive


@pytest.fixture
def no_activity_since(pytestconfig):
    return pytestconfig.custom_config.gsuite.no_activity_since()


@pytest.mark.gsuite_admin
@pytest.mark.parametrize('user', list_users(), ids=lambda u: u['primaryEmail'])
def test_admin_user_is_inactive(user, no_activity_since):
    """Tests whether user is active by checking lastLoginTime"""
    assert user_is_inactive(user, no_activity_since)

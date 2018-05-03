#!/usr/bin/env python3


import pytest
from heroku_2fa import have_creds, find_users_missing_2fa, find_affected_apps


@pytest.fixture
def affected_users():
    return find_users_missing_2fa().items()


@pytest.fixture
def affected_apps():
    users = find_users_missing_2fa()
    return find_affected_apps(users).items()


@pytest.mark.heroku
@pytest.mark.skipif(not have_creds(),
                    reason='No credentials for heroku')
@pytest.mark.parametrize(
    'role_user',
    ["{}: {}".format(role, email) for role, emails in affected_users()
     for email in emails])
def test_users_have_2fa_enabled(role_user):
    assert not role_user


@pytest.mark.heroku
@pytest.mark.skipif(not have_creds(),
                    reason='No credentials for heroku')
@pytest.mark.parametrize(
    'app_user',
    ["{}: {}".format(app, email) for app, emails in affected_apps()
     for email in emails])
def test_no_apps_impacted(app_user):
    assert not app_user

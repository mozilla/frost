# TODO: discover why/how the exemptions.py & regressions.py processess screw up
#       normal pytest operations.  All the fixtures below could/should be in
#       the heroku/conftest.py file, and no mark.parametrize would be needed on
#       the actual tests.
#
#       With the local conftest.py setup, the tests work, but the warnings are
#       quite noisy. :/  We're trading off (for the moment at least) test
#       readability for output readability.

# code for heroku/conftest.py START
import pytest
import resources


@pytest.fixture
def affected_users():
    roles = resources.users_no_2fa()
    assert isinstance(roles, type([]))
    role = roles[0]
    assert isinstance(role, type({}))
    return role


@pytest.fixture
def affected_apps():
    apps = resources.app_users_no_2fa()
    assert isinstance(apps, type([]))
    app = apps[0]
    assert isinstance(app, type({}))
    return app


@pytest.fixture
def role_user():
    l = [(role, email) for role, emails in affected_users().items()
         for email in emails]
    assert len(l) > 0
    return l


@pytest.fixture
def app_user():
    l = [(app, email) for app, emails in affected_apps().items()
         for email in emails]
    assert len(l) > 0
    return l


# ##def pytest_generate_tests(metafunc):
# ##    if 'role_user' in metafunc.fixturenames:
# ##        metafunc.parametrize('role_user', role_user())
# ##    elif 'app_user' in metafunc.fixturenames:
# ##        metafunc.parametrize('app_user', app_user())

# code for heroku/conftest.py END
@pytest.mark.heroku
@pytest.mark.parametrize('role_user', role_user())
def test_users_have_2fa_enabled(role_user):
    assert not role_user


@pytest.mark.heroku
@pytest.mark.parametrize('app_user', app_user())
def test_no_apps_impacted(app_user):
    assert not app_user

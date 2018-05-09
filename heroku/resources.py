
from conftest import heroku_client


def users_no_2fa():
    """
    """
    raw = heroku_client.get(
        'all', [], {})
    just_key = raw.extract_key(heroku_client.data_set_names.ROLE_USER, [])
    datum = just_key.results or [{}]
    return datum
    # ##return heroku_client.get(
    # ##    'all', [], {})\
    # ##    .extract_key('role_users')\
    # ##    .flatten()\
    # ##    .values()


def app_users_no_2fa():
    """
    """
    raw = heroku_client.get(
        'all', [], {})
    just_key = raw.extract_key(heroku_client.data_set_names.APP_USER, [])
    datum = just_key.results or [{}]
    return datum
    # ##return heroku_client.get(
    # ##    'all', [], {})\
    # ##    .extract_key('app_users')\
    # ##    .flatten()\
    # ##    .values()

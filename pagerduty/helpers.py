

from pagerduty.resources import alternate_usernames


def alternate_names_for_user(username):
    """
    Returns a list of the username and any alternates or nicknames for it
    """
    return [username] + alternate_usernames().get(username, [])

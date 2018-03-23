from dateutil.parser import parse


def user_is_inactive(user, no_activity_since):
    """
    Compares the lastLoginTime with no_activity_since.
    """
    return parse(user['lastLoginTime']) > no_activity_since

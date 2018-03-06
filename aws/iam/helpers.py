from dateutil.parser import parse


def user_is_inactive(iam_user, no_activity_since, created_after):
    """
    Returns False if any of these are true:
        - The user was created after the passed in "created_after" datetime.
        - The user has used either potentially active access keys since the date
          that is "no_activity_since"
        - The user has logged into the AWS console since the date that is
          "no_activity_since"
    else it will return True.

    >>> from datetime import datetime
    >>> no_activity_since = datetime(2017, 1, 1)
    >>> created_after = datetime(2018, 1, 8)

    User considered active due to being created after the created_after datetime.
    >>> user_is_inactive({'user_creation_time': '2018-01-10'}, created_after, no_activity_since)
    False

    User considered active due to usage of access key 1 after no_activity_since
    >>> user_is_inactive({
    ...     'user_creation_time': '2016-01-10',
    ...     'access_key_1_active': 'true',
    ...     'access_key_1_last_used_date': '2017-06-01',
    ... }, no_activity_since, created_after)
    False

    User considered active due to usage of access key 2 after no_activity_since
    >>> user_is_inactive({
    ...     'user_creation_time': '2010-01-10',
    ...     'access_key_1_active': 'true',
    ...     'access_key_1_last_used_date': '2014-06-01',
    ...     'access_key_2_active': 'true',
    ...     'access_key_2_last_used_date': '2017-02-01',
    ... }, no_activity_since, created_after)
    False

    User considered active due to usage of password after no_activity_since
    >>> user_is_inactive({
    ...     'user_creation_time': '2010-01-10',
    ...     'access_key_1_active': 'true',
    ...     'access_key_1_last_used_date': '2014-06-01',
    ...     'access_key_2_active': 'false',
    ...     'access_key_2_last_used_date': 'N/A',
    ...     'password_enabled': 'true',
    ...     'password_last_used': '2017-09-01',
    ... }, no_activity_since, created_after)
    False

    User considered inactive due to the only usage (access key 1) being before no_activity_since
    and user being created before created_after
    >>> user_is_inactive({
    ...     'user_creation_time': '2016-01-10',
    ...     'access_key_1_active': 'true',
    ...     'access_key_1_last_used_date': '2016-06-01',
    ...     'access_key_2_active': 'false',
    ...     'access_key_2_last_used_date': 'N/A',
    ...     'password_enabled': 'false',
    ...     'password_last_used': 'N/A',
    ... }, no_activity_since, created_after)
    True

    User considered inactive due to the only usage (password) being before no_activity_since
    and user being created before created_after
    >>> user_is_inactive({
    ...     'user_creation_time': '2016-01-10',
    ...     'access_key_1_active': 'false',
    ...     'access_key_1_last_used_date': 'N/A',
    ...     'access_key_2_active': 'false',
    ...     'access_key_2_last_used_date': 'N/A',
    ...     'password_enabled': 'true',
    ...     'password_last_used': '2016-06-01',
    ... }, no_activity_since, created_after)
    True
    """

    if parse(iam_user['user_creation_time']) > created_after:
        return False

    if is_credential_active(iam_user['access_key_1_active'], iam_user['access_key_1_last_used_date']) and \
            parse(iam_user['access_key_1_last_used_date']) > no_activity_since:
        return False

    if is_credential_active(iam_user['access_key_2_active'], iam_user['access_key_2_last_used_date']) and \
            parse(iam_user['access_key_2_last_used_date']) > no_activity_since:
        return False

    if is_credential_active(iam_user['password_enabled'], iam_user['password_last_used']) and \
            parse(iam_user['password_last_used']) > no_activity_since:
        return False

    return True


def is_credential_active(credential_active, credential_last_used):
    return credential_active == 'true' and \
            credential_last_used not in ['N/A', 'no_information']

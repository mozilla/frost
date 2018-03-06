from dateutil.parser import parse


def user_is_inactive(iam_user, grace_period, considered_inactive):
    """
    Returns False if any of these are true:
        - The user was created less than the grace period
        - The user has used either possibly active access keys since the date
          that is "considered_inactive"
        - The user has logged into the AWS console since the date that is
          "considered_inactive"
    else it will return True.

    >>> from datetime import datetime
    >>> grace_period = datetime(2018, 1, 8)
    >>> considered_inactive = datetime(2017, 1, 1)

    >>> user_is_inactive({'user_creation_time': '2018-01-10'}, grace_period, considered_inactive)
    False

    >>> user_is_inactive({
    ...     'user_creation_time': '2016-01-10',
    ...     'access_key_1_active': 'true',
    ...     'access_key_1_last_used_date': '2017-06-01',
    ... }, grace_period, considered_inactive)
    False

    >>> user_is_inactive({
    ...     'user_creation_time': '2010-01-10',
    ...     'access_key_1_active': 'true',
    ...     'access_key_1_last_used_date': '2014-06-01',
    ...     'access_key_2_active': 'true',
    ...     'access_key_2_last_used_date': '2017-02-01',
    ... }, grace_period, considered_inactive)
    False

    >>> user_is_inactive({
    ...     'user_creation_time': '2010-01-10',
    ...     'access_key_1_active': 'true',
    ...     'access_key_1_last_used_date': '2014-06-01',
    ...     'access_key_2_active': 'false',
    ...     'access_key_2_last_used_date': 'N/A',
    ...     'password_enabled': 'true',
    ...     'password_last_used': '2017-09-01',
    ... }, grace_period, considered_inactive)
    False

    >>> user_is_inactive({
    ...     'user_creation_time': '2016-01-10',
    ...     'access_key_1_active': 'true',
    ...     'access_key_1_last_used_date': '2016-06-01',
    ...     'access_key_2_active': 'false',
    ...     'access_key_2_last_used_date': 'N/A',
    ...     'password_enabled': 'false',
    ...     'password_last_used': 'N/A',
    ... }, grace_period, considered_inactive)
    True

    >>> user_is_inactive({
    ...     'user_creation_time': '2016-01-10',
    ...     'access_key_1_active': 'false',
    ...     'access_key_1_last_used_date': 'N/A',
    ...     'access_key_2_active': 'false',
    ...     'access_key_2_last_used_date': 'N/A',
    ...     'password_enabled': 'true',
    ...     'password_last_used': '2016-06-01',
    ... }, grace_period, considered_inactive)
    True
    """

    if parse(iam_user['user_creation_time']) > grace_period:
        return False

    if iam_user['access_key_1_active'] == 'true' and iam_user['access_key_1_last_used_date'] != 'N/A':
        if parse(iam_user['access_key_1_last_used_date']) > considered_inactive:
            return False
    if iam_user['access_key_2_active'] == 'true' and iam_user['access_key_2_last_used_date'] != 'N/A':
        if parse(iam_user['access_key_2_last_used_date']) > considered_inactive:
            return False
    if iam_user['password_enabled'] == 'true' and \
            iam_user['password_last_used'] not in ['N/A', 'no_information']:
        if parse(iam_user['password_last_used']) > considered_inactive:
            return False

    return True

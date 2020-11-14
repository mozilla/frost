from datetime import datetime
from dateutil.parser import parse

from helpers import get_param_id


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

    if parse(iam_user["user_creation_time"]) > created_after:
        return False

    if (
        is_credential_active(
            iam_user["access_key_1_active"], iam_user["access_key_1_last_used_date"]
        )
        and parse(iam_user["access_key_1_last_used_date"]) > no_activity_since
    ):
        return False

    if (
        is_credential_active(
            iam_user["access_key_2_active"], iam_user["access_key_2_last_used_date"]
        )
        and parse(iam_user["access_key_2_last_used_date"]) > no_activity_since
    ):
        return False

    if (
        is_credential_active(
            iam_user["password_enabled"], iam_user["password_last_used"]
        )
        and parse(iam_user["password_last_used"]) > no_activity_since
    ):
        return False

    return True


def is_credential_active(credential_active, credential_last_used):
    return credential_active == "true" and credential_last_used not in [
        "N/A",
        "no_information",
    ]


def is_access_key_expired(iam_access_key, access_key_expiration_date):
    """
    Compares the CreateDate of the access key with the datetime object passed
    in as `access_key_expiration_date` and returns True if the CreateDate is
    before the `access_key_expiration_date` datetime object.

    Returns False if the Status of the key is not `Active`, as though it may
    have expired, it cannot be used.

    >>> from datetime import datetime
    >>> access_key_expiration_date = datetime(2018, 1, 8)

    >>> is_access_key_expired({'Status': 'Inactive'}, access_key_expiration_date)
    False
    >>> is_access_key_expired({'Status': 'Active', 'CreateDate': datetime(2018, 1, 9)}, access_key_expiration_date)
    False
    >>> is_access_key_expired({'Status': 'Active', 'CreateDate': datetime(2020, 1, 9)}, access_key_expiration_date)
    False

    >>> is_access_key_expired({'Status': 'Active', 'CreateDate': datetime(2018, 1, 7)}, access_key_expiration_date)
    True
    >>> is_access_key_expired({'Status': 'Active', 'CreateDate': datetime(2000, 1, 9)}, access_key_expiration_date)
    True
    """

    if iam_access_key["Status"] != "Active":
        return False

    assert isinstance(iam_access_key["CreateDate"], datetime)
    return access_key_expiration_date > iam_access_key["CreateDate"]


def get_iam_user_name(login):
    return get_param_id(login, "UserName")


def get_iam_resource_id(resource):
    if isinstance(resource, dict) and "UserName" in resource:
        return get_iam_user_name(resource)
    if isinstance(resource, list):
        if len(resource) == 0:
            return "empty"
    return None

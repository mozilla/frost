from conftest import botocore_client


def iam_users():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_users"
    return botocore_client.get(
        'iam', 'list_users', [], {})\
        .extract_key('Users')\
        .flatten()\
        .values()


def iam_inline_policies(username):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_user_policies"
    return botocore_client.get(
        'iam', 'list_user_policies', [], {'UserName': username})\
        .extract_key('PolicyNames')\
        .flatten()\
        .values()


def iam_managed_policies(username):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_attached_user_policies"
    return botocore_client.get(
        'iam', 'list_attached_user_policies', [], {'UserName': username})\
        .extract_key('AttachedPolicies')\
        .flatten()\
        .values()


def iam_user_groups(username):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_groups_for_user"
    return botocore_client.get(
        'iam', 'list_groups_for_user', [], {'UserName': username})\
        .extract_key('Groups')\
        .flatten()\
        .values()


def iam_user_group_inline_policies(username):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_group_policies"
    return [
        botocore_client
        .get('iam', 'list_group_policies', [], {'GroupName': group['GroupName']})
        .extract_key('PolicyNames')
        .flatten()
        .values()
        for group in iam_user_groups(username)
    ]


def iam_user_group_managed_policies(username):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_attached_group_policies"
    return [
        botocore_client
        .get('iam', 'list_attached_group_policies', [], {'GroupName': group['GroupName']})
        .extract_key('AttachedPolicies')
        .flatten()
        .values()
        for group in iam_user_groups(username)
    ]


def iam_all_user_policies(username):
    '''
    Gets all policies that can be attached to a user. This includes:
        - Inline policies on the user
        - Managed policies on the user
        - Inline policies on the group that the user is in
        - Managed policies on the group that the user is in

    Inline policy API calls just return the name of the policy, so we create a single key dictionary to
    allow for standard access to the policy name ({'PolicyName': policy_name})
    '''
    inline = []
    inline_policies = [iam_inline_policies(username=username) + iam_user_group_inline_policies(username=username)]
    for policies in inline_policies:
        for policy_name in policies:
            if isinstance(policy_name, str):
                inline += {'PolicyName': policy_name}

    managed = [
        policy for policies in
        iam_managed_policies(username=username) + iam_user_group_managed_policies(username=username)
        for policy in policies
    ]

    return inline + managed


def iam_users_with_policies():
    return [
        {
            **{'Policies': iam_all_user_policies(username=user['UserName'])},
            **user,
        } for user in iam_users()
    ]


def iam_admin_login_profiles():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.get_login_profile"
    return iam_login_profiles([user for user in iam_users_with_policies() if user_is_admin(user)])


def iam_admin_mfa_devices():
    "botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_mfa_devices"
    return iam_mfa_devices([user for user in iam_users_with_policies() if user_is_admin(user)])


def iam_user_login_profiles():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.get_login_profile"
    return iam_login_profiles([user for user in iam_users()])


def iam_user_mfa_devices():
    "botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_mfa_devices"
    return iam_mfa_devices([user for user in iam_users()])


def iam_login_profiles(users):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.get_login_profile"
    return [
        botocore_client
        .get('iam',
             'get_login_profile',
             [],
             {'UserName': user['UserName']},
             result_from_error=lambda error, call: {'LoginProfile': None})
        .extract_key('LoginProfile')
        .values()[0]
        for user in users
    ]


def iam_mfa_devices(users):
    "botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_mfa_devices"
    return [
        botocore_client
        .get('iam',
             'list_mfa_devices',
             [],
             {'UserName': user['UserName']})
        .extract_key('MFADevices')
        .values()[0]
        for user in users
    ]


# FIXME
# Substring matching is _not_ enough of a check, but works for testing.
# The truth is that we probably shouldn't depend too much on the concept
# of an "admin" in AWS, since that's not how the ACL's really work. We
# should probably move towards concepts like "has write access", "can
# read secrets", etc.
def user_is_admin(user):
    for policy in user['Policies']:
        if isinstance(policy, dict):
            if 'admin' in policy.get('PolicyName', '').lower():
                return True

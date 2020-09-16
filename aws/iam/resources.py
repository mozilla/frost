import csv
import itertools
import time

import pytest

from conftest import botocore_client, custom_config_global


def iam_users():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_users"
    return (
        botocore_client.get("iam", "list_users", [], {})
        .extract_key("Users")
        .flatten()
        .values()
    )


def iam_admin_users():
    return [
        user for user in iam_users_with_policies_and_groups() if user_is_admin(user)
    ]


def iam_inline_policies(user):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_user_policies"
    return botocore_client.get_details(
        user, "iam", "list_user_policies", [], {"UserName": user["UserName"]}
    )["PolicyNames"]


def iam_managed_policies(user):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_attached_user_policies"
    return botocore_client.get_details(
        user, "iam", "list_attached_user_policies", [], {"UserName": user["UserName"]}
    )["AttachedPolicies"]


def iam_user_groups(user):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_groups_for_user"
    return botocore_client.get_details(
        user, "iam", "list_groups_for_user", [], {"UserName": user["UserName"]}
    )["Groups"]


def iam_user_group_inline_policies(user):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_group_policies"
    return [
        botocore_client.get_details(
            group, "iam", "list_group_policies", [], {"GroupName": group["GroupName"]}
        )["PolicyNames"]
        for group in iam_user_groups(user)
    ]


def iam_user_group_managed_policies(user):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_attached_group_policies"
    return [
        botocore_client.get_details(
            group,
            "iam",
            "list_attached_group_policies",
            [],
            {"GroupName": group["GroupName"]},
        )["AttachedPolicies"]
        for group in iam_user_groups(user)
    ]


def iam_all_user_policies(user):
    """
    Gets all policies that can be attached to a user. This includes:
        - Inline policies on the user
        - Managed policies on the user
        - Inline policies on the group that the user is in
        - Managed policies on the group that the user is in

    Inline policy API calls just return the name of the policy, so we create a single key dictionary to
    allow for standard access to the policy name ({'PolicyName': policy_name})
    """
    inline = []
    inline_policies = [iam_inline_policies(user) + iam_user_group_inline_policies(user)]
    for policies in inline_policies:
        for policy_name in policies:
            if isinstance(policy_name, str):
                inline.append({"PolicyName": policy_name})

    managed = [
        policy
        for policies in iam_managed_policies(user)
        + iam_user_group_managed_policies(user)
        for policy in policies
    ]

    return inline + managed


def iam_users_with_policies():
    return [{"Policies": iam_all_user_policies(user), **user} for user in iam_users()]


def iam_users_with_policies_and_groups():
    """Users with their associated Policies and Groups"""
    return [
        {"Groups": iam_user_groups(user), **user} for user in iam_users_with_policies()
    ]


def iam_admin_login_profiles():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.get_login_profile"
    return iam_login_profiles(iam_admin_users())


def iam_admin_mfa_devices():
    "botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_mfa_devices"
    return iam_mfa_devices(iam_admin_users())


def iam_user_login_profiles():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.get_login_profile"
    return iam_login_profiles(user for user in iam_users())


def iam_user_mfa_devices():
    "botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_mfa_devices"
    return iam_mfa_devices(user for user in iam_users())


def iam_login_profiles(users):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.get_login_profile"
    return [
        botocore_client.get_details(
            user,
            "iam",
            "get_login_profile",
            [],
            {"UserName": user["UserName"]},
            result_from_error=lambda error, call: {"LoginProfile": None},
        )["LoginProfile"]
        for user in users
    ]


def iam_mfa_devices(users):
    "botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_mfa_devices"
    return [
        botocore_client.get_details(
            user, "iam", "list_mfa_devices", [], {"UserName": user["UserName"]}
        )["MFADevices"]
        for user in users
    ]


def iam_roles():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_roles"
    return (
        botocore_client.get("iam", "list_roles", [], {})
        .extract_key("Roles")
        .flatten()
        .values()
    )


def iam_all_role_policies(role):
    return [
        {"PolicyName": policy_name} for policy_name in iam_role_inline_policies(role)
    ] + iam_role_managed_policies(role)


def iam_roles_with_policies():
    return [{"Policies": iam_all_role_policies(role), **role} for role in iam_roles()]


def iam_role_inline_policies(role):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_role_policies"
    return botocore_client.get_details(
        role, "iam", "list_role_policies", [], {"RoleName": role["RoleName"]}
    )["PolicyNames"]


def iam_role_managed_policies(role):
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_attached_role_policies"
    return botocore_client.get_details(
        role, "iam", "list_attached_role_policies", [], {"RoleName": role["RoleName"]}
    )["AttachedPolicies"]


def iam_admin_roles():
    return [role for role in iam_roles_with_policies() if user_is_admin(role)]


def iam_access_keys_for_user(user):
    "https://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_access_keys"
    return botocore_client.get_details(
        user, "iam", "list_access_keys", [], {"UserName": user["UserName"]}
    )["AccessKeyMetadata"]


def iam_get_all_access_keys():
    return itertools.chain.from_iterable(
        iam_access_keys_for_user(user) for user in iam_users()
    )


def iam_generate_credential_report():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.generate_credential_report"
    results = botocore_client.get(
        "iam", "generate_credential_report", [], {}, do_not_cache=True
    ).values()
    if results:
        return results[0].get("State")
    return ""


def iam_get_credential_report():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.get_credential_report"
    # the story of the wack api
    while True:
        cred_report_state = iam_generate_credential_report()
        if cred_report_state not in ["STARTED", "INPROGRESS"]:
            break
        time.sleep(2)

    # We want this to blow up if it can't get the "Content"
    results = botocore_client.get(
        "iam", "get_credential_report", [], {}, do_not_cache=True
    ).values()
    if not results:
        return []
    content = results[0]["Content"]
    decoded_content = content.decode("utf-8")
    return list(csv.DictReader(decoded_content.split("\n")))


# (ajvb) I'm not a big fan of this, but it seems to be the easiest way to
# only have to call `get_credential_report` once since it is not easily cacheable.
def iam_admin_users_with_credential_report():
    """Returns all "admin" users with an additional "CredentialReport" key,
    which is a dict containing their row in the Credentials Report.
    """
    admins = iam_admin_users()
    credential_report = iam_get_credential_report()

    for admin in admins:
        for user in credential_report:
            if admin["UserName"] == user["user"]:
                admin["CredentialReport"] = user
                break

    return admins


def user_is_admin(user):
    for policy in user["Policies"]:
        if isinstance(policy, dict):
            if policy.get("PolicyName", "") in custom_config_global.aws.admin_policies:
                return True

    for group in user.get("Groups", []):
        if isinstance(group, dict):
            if group.get("GroupName", "") in custom_config_global.aws.admin_groups:
                return True

    return False


def get_all_users_that_can_access_aws_account():
    """
    Returns users with console or API access to an AWS account.
    """
    profile_usernames = [
        profile["UserName"]
        for profile in iam_user_login_profiles()
        if profile is not None
    ]
    access_key_usernames = [
        akey["UserName"]
        for akey in iam_get_all_access_keys()
        if akey["Status"] == "Active"
    ]
    return set(profile_usernames + access_key_usernames)

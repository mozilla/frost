from conftest import botocore_client

def iam_users():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_users"
    return botocore_client\
      .get('iam', 'list_users', [], {})\
      .extract_key('Users')\
      .flatten()\
      .values()

def iam_login_profiles():
    "http://botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.get_login_profile"
    return [
        botocore_client\
        .get('iam',
             'get_login_profile',
             [],
             {'UserName': user['UserName']},
             result_from_error=lambda error, call: {'LoginProfile': None})\
        .extract_key('LoginProfile')\
        .values()[0]
        for user in iam_users()
    ]

def iam_mfa_devices():
    "botocore.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_mfa_devices"
    return [
        botocore_client\
        .get('iam',
             'list_mfa_devices',
             [],
             {'UserName': user['UserName']})\
        .extract_key('MFADevices')\
        .values()[0]
        for user in iam_users()
    ]

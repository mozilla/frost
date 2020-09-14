from dateutil.parser import isoparse

from aws.iam.resources import iam_users, iam_inline_policies


def test_iam_users():
    assert iam_users() == [
        {
            "Arn": "arn:aws:iam::123456789012:user/hobbes",
            "CreateDate": isoparse("1985-11-18T00:01:10+00:00"),
            "PasswordLastUsed": isoparse("2018-01-09T20:43:00+00:00"),
            "Path": "/",
            "UserId": "H0BBIHMA0CZ0R0K0MN00C",
            "UserName": "tigerone",
            "__pytest_meta": {"profile": "example-account", "region": "us-east-1"},
        },
        {
            "Arn": "arn:aws:iam::123456789012:user/calvin",
            "CreateDate": isoparse("1985-11-18T00:01:10+00:00"),
            "PasswordLastUsed": isoparse("2008-01-09T20:43:00+00:00"),
            "Path": "/",
            "UserId": "CALCIHMA0CZ0R0K0MN00C",
            "UserName": "spacemanspiff",
            "__pytest_meta": {"profile": "example-account", "region": "us-east-1"},
        },
    ]


def test_iam_inline_policies_for_user_without_policies():
    # extracts empty 'PolicyNames'
    assert iam_inline_policies(username="tigerone") == []

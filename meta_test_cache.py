from datetime import datetime
from dateutil.parser import parse

import pytest


TEST_IAM_USERS = [
    {
        "Arn": "arn:aws:iam::123456789012:user/hobbes",
        "CreateDate": parse("1985-11-18T00:01:10+00:00", ignoretz=True),
        "PasswordLastUsed": parse("2018-01-09T20:43:00+00:00", ignoretz=True),
        "NotARealField": datetime.utcnow(),
        "Path": "/",
        "UserId": "H0BBIHMA0CZ0R0K0MN00C",
        "UserName": "tigerone",
        "__pytest_meta": {"profile": "example-account", "region": "us-east-1"},
    }
]


@pytest.fixture
def uncached_iam_users():
    return TEST_IAM_USERS


@pytest.fixture
def cached_iam_users(request):
    request.config.cache.set("cached_iam_users", TEST_IAM_USERS)
    return request.config.cache.get("cached_iam_users", None)


def test_cache_serializes_and_deserializes_datetimes(
    cached_iam_users, uncached_iam_users
):
    assert cached_iam_users == uncached_iam_users

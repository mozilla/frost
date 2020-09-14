import pytest

from aws.iam.resources import iam_get_all_access_keys
from aws.iam.helpers import get_iam_user_name, is_access_key_expired


@pytest.fixture
def access_key_expiration_date(pytestconfig):
    return pytestconfig.custom_config.aws.get_access_key_expiration_date()


@pytest.mark.iam
@pytest.mark.parametrize(
    "iam_access_key", iam_get_all_access_keys(), ids=get_iam_user_name,
)
def test_iam_access_key_is_old(iam_access_key, access_key_expiration_date):
    assert not is_access_key_expired(iam_access_key, access_key_expiration_date)

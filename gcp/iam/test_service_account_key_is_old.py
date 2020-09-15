import pytest

from helpers import get_param_id

from gcp.iam.resources import all_service_account_keys
from gcp.iam.helpers import is_service_account_key_old


@pytest.mark.gcp_iam
@pytest.mark.parametrize(
    "service_account_key",
    all_service_account_keys(),
    ids=lambda key: get_param_id(key, "name"),
)
def test_service_account_key_is_old(service_account_key):
    """Tests if the Service Account Key is older than 90 days"""
    assert is_service_account_key_old(service_account_key)

import pytest

from helpers import get_param_id

from gcp.sql.resources import instances


@pytest.mark.gcp_sql
@pytest.mark.parametrize(
    "sql_instance", instances(), ids=lambda instance: get_param_id(instance, "name"),
)
def test_sql_instance_ssl_required(sql_instance):
    """Test CloudSQL Instance requires SSL"""
    assert (
        sql_instance.get("settings").get("ipConfiguration").get("requireSsl", False)
    ), "CloudSQL Instance {0[name]} does not require SSL".format(sql_instance)

import pytest

from helpers import get_param_id

from gcp.sql.resources import instances


@pytest.mark.gcp_sql
@pytest.mark.parametrize(
    "sql_instance", instances(), ids=lambda instance: get_param_id(instance, "name"),
)
def test_sql_instance_private_ip_required(sql_instance):
    """
    Test CloudSQL Instance requires Private IP to connect

    CIS 6.2
    """
    assert (
        sql_instance.get("settings").get("ipConfiguration").get("privateNetwork", None)
    ), "CloudSQL Instance {0[name]} does not have a private network configured.".format(
        sql_instance
    )

    assert (
        sql_instance.get("settings").get("ipConfiguration").get("ipv4Enabled", None)
        == False
    ), "CloudSQL Instance {0[name]} has a public IPv4 enabled.".format(sql_instance)

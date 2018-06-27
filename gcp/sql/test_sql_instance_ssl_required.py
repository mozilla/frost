import pytest

from gcp.sql.resources import instances


@pytest.mark.gcp_sql
@pytest.mark.parametrize(
    "sql_instance", instances(), ids=lambda instance: instance["name"]
)
def test_sql_instance_ssl_required(sql_instance):
    """Test CloudSQL Instance requires SSL"""
    assert sql_instance.get("settings").get("ipConfiguration").get("requireSsl")

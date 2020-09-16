import pytest

from helpers import get_param_id

from gcp.sql.resources import instances


@pytest.mark.gcp_sql
@pytest.mark.parametrize(
    "sql_instance", instances(), ids=lambda instance: get_param_id(instance, "name"),
)
def test_sql_instance_automatic_backup_enabled(sql_instance):
    """Test CloudSQL Instance has Automatic Backup Enabled"""
    assert sql_instance.get("settings").get("backupConfiguration").get("enabled")
    if "MYSQL" in sql_instance.get("databaseVersion"):
        assert (
            sql_instance.get("settings")
            .get("backupConfiguration")
            .get("binaryLogEnabled")
        )

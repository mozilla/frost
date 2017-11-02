
import pytest


@pytest.mark.rds
def test_rds_db_instance_minor_version_updates_enabled(rds_db_instance):
    """
    Enable automatic minor version updates (e.g. 5.6.26 to 5.6.27) during maintenance windows to receive security patches.

    Only checked for maria, mysql, and postgres dbs.

    http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Upgrading.html
    """
    if rds_db_instance['Engine'] not in ['mariadb', 'mysql', 'postgres']:
        pytest.skip(reason='Engine type %s does not support minor version updates.' % rds_db_instance['Engine'])

    assert rds_db_instance['AutoMinorVersionUpgrade'] == True, 'Minor version automatic upgrades disabled for {}'.format(rds_db_instance['DBInstanceIdentifier'])

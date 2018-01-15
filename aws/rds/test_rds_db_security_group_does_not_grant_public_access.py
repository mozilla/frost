

import pytest

from aws.rds.resources import rds_db_security_groups


def does_rds_db_security_group_grant_public_access(sg):
    """
    Checks an RDS instance for a DB security group with CIDRIP 0.0.0.0/0

    >>> does_rds_db_security_group_grant_public_access({"IPRanges": [{"CIDRIP": "127.0.0.1/32", "Status": "authorized"}, {"CIDRIP": "0.0.0.0/0", "Status": "authorized"}]})
    True
    >>> does_rds_db_security_group_grant_public_access({"IPRanges": []})
    False
    """
    return any(ipr['CIDRIP'] == '0.0.0.0/0' and ipr['Status'] == 'authorized' for ipr in sg['IPRanges'])


@pytest.mark.rds
@pytest.mark.parametrize(
    'rds_db_security_group',
    rds_db_security_groups(),
    ids=lambda sg: sg['DBSecurityGroupArn'])
def test_rds_db_security_group_does_not_grant_public_access(rds_db_security_group):
    assert not does_rds_db_security_group_grant_public_access(rds_db_security_group)

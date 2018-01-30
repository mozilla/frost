

from conftest import botocore_client


def redshift_cluster_security_groups():
    "http://botocore.readthedocs.io/en/latest/reference/services/redshift.html#Redshift.Client.describe_cluster_security_groups"
    return botocore_client\
      .get('redshift', 'describe_cluster_security_groups', [], {})\
      .extract_key('ClusterSecurityGroups')\
      .flatten()\
      .values()


import functools

import pytest

import client
from config_helpers import *
from rules import *

# Add your profile and region here
profiles = ['stage']
regions = ['us-east-1']


## Update API calls before their results are parameterized
rds_db_snapshot_param_values = functools.partial(add_kwargs, {'IncludeShared': True, 'IncludePublic': True})


## Define how to set kwargs and filters for resources that depend on other fixtures

ec2_security_groups_dependent_value = get_dependent_value_by_rds_db_instance_vpc_security_group_ids

rds_db_snapshot_attributes_result_dependent_value = get_dependent_value_by_rds_db_snapshot_id
rds_db_security_groups_dependent_value = get_dependent_value_by_rds_db_security_group_names

s3_status_from_get_bucket_versioning_dependent_value = functools.partial(get_dependent_value_by_s3_bucket_name, None)
s3_mfa_delete_dependent_value = functools.partial(get_dependent_value_by_s3_bucket_name, None)
s3_logging_enabled_dependent_value = functools.partial(get_dependent_value_by_s3_bucket_name, None)

s3_grant_from_get_bucket_acl_dependent_value = functools.partial(get_dependent_value_by_s3_bucket_name, None)

s3_error_document_dependent_value = functools.partial(get_dependent_value_by_s3_bucket_name, website_not_found_to_none)
s3_index_document_dependent_value = functools.partial(get_dependent_value_by_s3_bucket_name, website_not_found_to_none)
s3_redirect_all_requests_to_dependent_value = functools.partial(get_dependent_value_by_s3_bucket_name, website_not_found_to_none)

s3_policy_dependent_value = functools.partial(get_dependent_value_by_s3_bucket_name, bucket_policy_not_found_to_none)
s3_cors_rules_dependent_value = functools.partial(get_dependent_value_by_s3_bucket_name, cors_policy_not_found_to_none)


## mark warning level tests where failures are OK
mark_test_s3_bucket_versioning_mfa_delete_enabled = set_xfail
mark_test_s3_bucket_versioning_enabled = set_xfail
mark_test_s3_bucket_web_hosting_disabled = set_xfail
mark_test_s3_bucket_logging_enabled = set_xfail
mark_test_s3_bucket_no_world_acl = set_xfail
mark_test_s3_bucket_cors_disabled = set_xfail

mark_test_rds_db_instance_backup_enabled = set_xfail
mark_test_rds_db_instance_encrypted = set_xfail
mark_test_rds_db_instance_is_multiaz = set_xfail
mark_test_rds_db_instance_minor_version_updates_enabled = set_xfail

mark_test_rds_db_snapshot_encrypted = set_xfail


def mark_test_rds_db_instance_not_publicly_accessible_by_vpc_security_group(params, aws_fixture_names):
    db = params[aws_fixture_names.index('rds_db_instance')]
    if db['DBInstanceArn'] == 'arn:aws:rds:us-east-1:1234567890123:db:public-db': # example public db
        return pytest.mark.xfail(params, reason='warn level')
    else:
        return params  # pass

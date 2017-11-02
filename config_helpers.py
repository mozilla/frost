

import botocore.exceptions
import pytest

import client


## Helper functions

def fix_snapshot_id(sid):
    new_sid = sid.rsplit(':', 1)[-1] if 'arn' in sid else sid
    # print('fixing id', sid, 'to', new_sid)
    return new_sid


def add_kwargs(kwargs, profiles, regions, fixture_config, cache):
    if 'kwargs' not in fixture_config['fetch']:
        fixture_config['fetch']['kwargs'] = {}

    fixture_config['fetch']['kwargs'].update(kwargs)

    yield from client.get_aws_resource(profiles, regions, fixture_config, cache)


def set_xfail(params, aws_fixture_names):
    return pytest.mark.xfail(params, reason='warn level')


def website_not_found_to_none(error, fixtrue_config):
    if error.response['Error']['Code'] == 'NoSuchWebsiteConfiguration':
        return {k: None for k in fixture_config['result_key']}
    else:
        raise error


def bucket_policy_not_found_to_none(error, fixture_config):
    if error.response['Error']['Code'] == 'NoSuchBucketPolicy':
        return {k: None for k in fixture_config['result_key']}
    else:
        raise error


def cors_policy_not_found_to_none(error, fixture_config):
    if error.response['Error']['Code'] == 'NoSuchCORSConfiguration':
        return {k: None for k in fixture_config['result_key']}
    else:
        raise error



def get_dependent_value_by_s3_bucket_name(result_from_error, test_name, fixture_config, cache, new_params, aws_fixture_names):
    parent = new_params[aws_fixture_names.index('s3_bucket_from_list_buckets')]
    parent_call = parent['aws_api_call']

    fixture_config['kwargs']['Bucket'] = parent['Name']

    return next(client.get_aws_resource([parent_call.profile],
                                        [parent_call.region],
                                        fixture_config,
                                        cache,
                                        result_from_error))


def get_dependent_value_by_rds_db_security_group_names(test_name, fixture_config, cache, new_params, aws_fixture_names):
    # TODO: handle tests that don't filter on rds_db_instance

    parent = new_params[aws_fixture_names.index('rds_db_instance')]
    parent_call = parent['aws_api_call']

    sgs = []
    for sg in parent['DBSecurityGroups']:
        fixture_config['kwargs']['DBSecurityGroupName'] = sg['DBSecurityGroupName']
        sgs.extend(client.get_aws_resource([parent_call.profile], [parent_call.region], fixture_config, cache))

    return sgs


def get_dependent_value_by_rds_db_snapshot_id(test_name, fixture_config, cache, new_params, aws_fixture_names):
    # TODO: handle tests that don't filter on rds_db_snapshot

    parent = new_params[aws_fixture_names.index('rds_db_snapshot')]
    parent_call = parent['aws_api_call']

    fixture_config['kwargs']['DBSnapshotIdentifier'] = fix_snapshot_id(parent['DBSnapshotIdentifier'])

    return next(client.get_aws_resource([parent_call.profile], [parent_call.region], fixture_config, cache))


def get_dependent_value_by_rds_db_instance_vpc_security_group_ids(test_name, fixture_config, cache, new_params, aws_fixture_names):
    # TODO: handle tests that don't filter on rds_db_instance

    parent = new_params[aws_fixture_names.index('rds_db_instance')]
    parent_call = parent['aws_api_call']

    fixture_config['kwargs'] = {'Filters': [{'Name': 'group-id', 'Values': [
        sg['VpcSecurityGroupId'] for sg in parent['VpcSecurityGroups'] if sg['Status'] == 'active'
    ]}]}
    return list(client.get_aws_resource([parent_call.profile], [parent_call.region], fixture_config, cache))

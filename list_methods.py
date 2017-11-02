

from pprint import pprint


import functools
import json
import os
import os.path
import sys
import warnings

import botocore

import botocore.model
import botocore.session


@functools.lru_cache()
def get_session(profile):
    """Returns a new or cached botocore session for the AWS profile."""
    if profile == 'None':  # hack for assume role prod
        profile = None

    # can raise botocore.exceptions.ProfileNotFound
    return botocore.session.Session(profile=profile)


@functools.lru_cache()
def get_available_profiles(profile='default'):
    return get_session(profile=profile).available_profiles


@functools.lru_cache()
def get_available_regions(profile='default'):
    return get_session(profile=profile).get_available_regions('ec2')


@functools.lru_cache()
def get_available_services(profile='default'):
    return get_session(profile=profile).get_available_services()


@functools.lru_cache()
def get_client(profile, region, service):
    """Returns a new or cached botocore service client for the AWS profile, region, and service.

    Warns when a service is not available for a region, which means we
    need to update botocore or skip that call for that region.
    """
    session = get_session(profile)

    if region not in session.get_available_regions(service):
        warnings.warn('service {} not available in {}'.format(service, region))

    return session.create_client(service, region_name=region)


@functools.lru_cache()
def load_resource_operations_config():
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_file = os.path.join(project_root, 'config', 'resource_operations.json')
    return json.load(open(config_file, 'r'))


def get_available_fixtures():
    config = load_resource_operations_config()
    for service, resources in config.items():
        for resource, operations in resources.items():
            yield service, resource, operations



def is_read_operation(method_name):
    return method_name.startswith('Get') or method_name.startswith('List') or method_name.startswith('Describe')


def is_pagination_name(name):
    pagination_keys = set([
      'Marker',
      'NextToken',
      'nextToken',
      'NextMarker',
      'nextMarker',
      'nextPageToken',
      'NextPageToken',
      'NextPageMarker',
      'NextUploadIdMarker',
      'NextContinuationToken',
      'IsTruncated',
      'Truncated',
      'ContinuationToken',
      'PaginationToken',
      'marker',
      'NumResults',
    ])
    if name in pagination_keys:
        return True

    substrs = [
        'HasMore',
        'hasMore',
    ]

    for substr in substrs:
        if substr in name:
            return True

    prefixes = [
        'max',
        'Max',
    ]
    for prefix in prefixes:
        if name.startswith(prefix):
            return True

    return False


def is_resource_name(name):
    return not is_pagination_name(name)


def get_input_args(op_model):
    if hasattr(op_model, 'input_shape') and op_model.input_shape:
        required_args = op_model.input_shape.required_members
        optional_args = op_model.input_shape.members
    else:
        required_args = []
        optional_args = []
    return required_args, optional_args


def get_members(output):
    if isinstance(output, botocore.model.StringShape):
        return [output.name]

    elif isinstance(output, botocore.model.ListShape):
        return [output.member.name]

    elif isinstance(output, botocore.model.StructureShape):
        return output.members

    else:
        raise NotImplementedError('? %s' % output)

def get_list_resource_id_path(output, required_args=None, optional_args=None):
    if isinstance(output, botocore.model.StringShape):
        return [output.name]

    elif isinstance(output, botocore.model.ListShape):
        return [].extend(get_list_resource_id_path(output.member))

    elif isinstance(output, botocore.model.StructureShape):
        for member in output.members:
            if required_args and any(member in argname for argname in required_args):
                return [member]

        for member in output.members:
            if optional_args and any(member in argname for argname in optional_args):
                return [member]

        for member in output.members:
            if 'id' in member.lower():
                return [member]

        for member in output.members:
            if 'arn' in member.lower():
                return [member]

    return None


def get_result_path(output, path=None):
    if path is None:
        path = [output]

    if isinstance(output, botocore.model.ListShape):
        path.append(output.member.name)
        return get_result_path(output.member, path)

    raise NotImplementedError('Unexpected shape model %s' % output)


def add_operation(fixtures, fixture_name, operation):
    if fixture_name not in fixtures:
        fixtures[fixture_name] = []

    operations = fixtures[fixture_name]

    # print('adding fixture', fixture_name)
    # pprint(operation)

    assert operation not in operations
    operations.append(operation)


def add_operations(fixtures, output_name, output_model, fetch_config):
    # e.g. waf-regional -> waf_regional to make it a valid python var name
    fixture_service_name = fetch_config['service_name'].replace('-', '_')

    # add fixture containing all results
    add_operation(fixtures,
                  fixture_service_name + '_' + botocore.xform_name(output_name),
                  dict(fetch=fetch_config,
                       result_key=output_name,
                       output_shape=repr(output_model)))

    # add fixture for each result
    if isinstance(output_model, botocore.model.ListShape):
        list_item_output_model = output_model.member

        parametrize_id = get_list_resource_id_path(list_item_output_model, fetch_config['required_args'], fetch_config['all_args'])

        # if fixture_service_name == 'rds':
        #     print(fixture_service_name,
        #           fetch_config['method_name'],
        #           fetch_config['required_args'],
        #           fetch_config['all_args'],
        #           # get_members(list_item_output_model),
        #           parametrize_id)

        add_operation(fixtures,
                      fixture_service_name + '_' + botocore.xform_name(list_item_output_model.name),
                      dict(fetch=fetch_config,
                           parametrize_id_source=parametrize_id,
                           result_key=output_name,  # JSON key to extract result
                           output_shape=repr(list_item_output_model)))


def _write_fixture_config():
    """
    Using the default profile and us-east-1, builds and writes a JSON
    config file to stdout for pytest-aws to lookup operations that
    return a given service's resource.

    Has the format:

    {
        <botocore AWS service name with dashes to underscores e.g. rds>_<AWS resource_name e.g. instance, bucket>: [
          {
            'service_name': <botocore AWS service name unmodified>,
            'method_name': <read operation for fetching the resource beginning with Describe, Get, or List e.g. ListS3Buckets, DescribeEC2Instances>,
            'required_args': [
              <CamelCase argument name>,
              ...
            ],
            'all_args': <repr of optional args input shape>,
            'result_path': [],  # JSON key to extract args from response
            'id_path': [], keys to extract args from response
            'output_shape': repr(output),
          }
        ]
    }

    Regenerate when botocore is updated.
    """
    fixtures = {}

    for service in get_available_services(profile='default'):
        client = get_client('default', 'us-east-1', service)

        for op_name in client.meta.service_model.operation_names:

            if not is_read_operation(op_name):
                continue

            op_model = client.meta.service_model.operation_model(op_name)
            if not op_model:
                raise Exception("No op model for {}".format(op_name))
                continue

            required_args, all_args = get_input_args(op_model)

            fetch_config = dict(
                service_name=service,
                method_name=botocore.xform_name(op_name),
                required_args=required_args,
                all_args=[arg for arg in all_args if not is_pagination_name(arg)],
            )
            fetch_config['docstring'] = '{0[service_name]}.{0[method_name]}({0[required_args]})'.format(fetch_config)

            for output_name in op_model.output_shape.members:
                # print(op_name, output_name, is_resource_name(output_name))

                if not is_resource_name(output_name):
                    continue

                output_model = op_model.output_shape.members[output_name]
                add_operations(fixtures, output_name, output_model, fetch_config)


    # flatten the dict and find a unique name for each output
    unique_fixtures = {}
    for fixture_name, operations in fixtures.items():
        # sort by # of required args
        operations.sort(key=lambda op: len(op['fetch']['required_args']))

        if len(operations) == 1:
            unique_fixtures[fixture_name] = operations[0]
        else:
            for operation in operations:
                unique_fixtures[fixture_name + '_from_' + operation['fetch']['method_name']] = operation

    json.dump(unique_fixtures, sys.stdout, indent=4, sort_keys=True)


def main():
    warnings.filterwarnings("ignore")
    _write_fixture_config()


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

import os
from collections import namedtuple
import functools
import itertools
import warnings

import botocore
import botocore.exceptions
import botocore.session


@functools.lru_cache()
def get_session(profile):
    """Returns a new or cached botocore session for the AWS profile."""

    if 'AWS_PROFILE' in os.environ and os.environ['AWS_PROFILE'] == profile:
        profile = 'default'

    # can raise botocore.exceptions.ProfileNotFound
    return botocore.session.Session(profile=profile)


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


@functools.lru_cache(maxsize=1)
def get_available_profiles(profile='default'):
    return get_session(profile=profile).available_profiles


@functools.lru_cache(maxsize=1)
def get_available_regions(profile='default'):
    return get_session(profile=profile).get_available_regions('ec2')


def reify_response(resp):
    """
    If botocore is lazily loading some response data force top-level attrs to a dict.
    """
    # TODO: find out wtf botocore is actually doing or use its internal methods
    return {k: v for (k, v) in resp.items()}


def full_results(client, method, args, kwargs):
    """Returns JSON results for an AWS botocore call. Flattens paginated results (if any)."""
    if client.can_paginate(method):
        paginator = client.get_paginator(method)
        return paginator.paginate(*args, **kwargs).build_full_result()
    else:
        return reify_response(getattr(client, method)(*args, **kwargs))


AWSAPICall = namedtuple('AWSAPICall', 'profile region service method args kwargs')
default_call = AWSAPICall(*[None] * (len(AWSAPICall._fields) - 2) + [[], {}])


def cache_key(call):
    """Returns the fullname (directory and filename) for an AWS API call."""

    return ':'.join([
        'pytest_aws',
        call.profile,
        call.region,
        call.service,
        call.method,
        ','.join(call.args),
        ','.join('{}={}'.format(k, v) for (k, v) in call.kwargs.items()),
    ]) + '.json'


def get_aws_resource(profiles, regions, call_config, cache, result_from_error=None):
    """Generates AWS API JSON responses for all profiles and regions (list params) for a given api_call config (dict param).

    TODO: describe API call config.

    From the reponse extracts result_key and injects the api call
    namedtuple under the aws_api_call key to allow dependent requests to
    use the same profile and region.
    """

    for profile, region in itertools.product(profiles, regions):
        call = default_call._replace(
            profile=profile,
            region=region,
            service=call_config['fetch']['service_name'],
            method=call_config['fetch']['method_name'],
            args=call_config.get('args', []),
            kwargs=call_config.get('kwargs', {}))

        ckey = cache_key(call)
        # print('calling', call, ckey)
        cached_result = cache.get(ckey, None)
        # assert cached_result
        if cached_result:
            result = cached_result
        else:
            client = get_client(call.profile, call.region, call.service)
            try:
                result = full_results(client, call.method, call.args, call.kwargs)
            except botocore.exceptions.ClientError as e:
                if result_from_error is None:
                    raise e
                else:
                    result = result_from_error(e, call_config)
            cache.set(cache_key(call), result)

        keyed_result = result.get(call_config['result_key'])
        if isinstance(keyed_result, list):
            for result in keyed_result:
                result['aws_api_call'] = call
                yield result
        elif isinstance(keyed_result, dict):
            keyed_result['aws_api_call'] = call
            yield keyed_result
        else:
            # assuming all primitives are leaf nodes
            yield keyed_result

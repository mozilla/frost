# -*- coding: utf-8 -*-


from collections import namedtuple
import functools
import itertools
import warnings

import botocore
import botocore.session


@functools.lru_cache()
def get_session(profile):
    """Returns a new or cached botocore session for the AWS profile."""
    if profile == 'None':  # hack for assume role prod
        profile = None

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
    # "profiles/{0.profile}/regions/{0.region}/services/{0.service}/methods/{0.method}_{0.kwargs}.json"
    return ':'.join([
        'pytest_aws',
        call.profile,
        call.region,
        call.service,
        call.method,
        ','.join(call.args),
        ','.join('{}={}'.format(k, v) for (k, v) in call.kwargs.items()),
    ])


def get_aws_resource(profiles, regions, api_call, cache):
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
            service=api_call['service'],
            method=api_call['method'],
            args=api_call.get('args', []),
            kwargs=api_call.get('kwargs', {}))

        cached = cache.get(cache_key(call), None)
        if cached:
            result = cached
        else:
            client = get_client(call.profile, call.region, call.service)
            result = full_results(client, call.method, call.args, call.kwargs)
            cache.set(cache_key(call), result)

        keyed_result = result.get(api_call['result_key'])
        if type(keyed_result) is list:
            for result in keyed_result:
                result['aws_api_call'] = call
                yield result
        else:
            keyed_result['aws_api_call'] = call
            yield keyed_result

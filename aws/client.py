# -*- coding: utf-8 -*-

import os
from collections import namedtuple
import functools
import itertools
import warnings

import botocore
import botocore.exceptions
import botocore.session


SERVICES_WITHOUT_REGIONS = ["iam", "s3"]


@functools.lru_cache()
def get_session(profile=None):
    """Returns a new or cached botocore session for the AWS profile."""

    # If AWS_PROFILE is set and does not match what we want, unset this variable before
    # we proceed.
    if 'AWS_PROFILE' in os.environ and os.environ['AWS_PROFILE'] != profile:
        del os.environ['AWS_PROFILE']
        # If the AWS_PROFILE was incorrect, these are probably incorrect as well.
        for envvar in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']:
            if envvar in os.environ:
                del os.environ[envvar]

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

    return session.create_client(
        service,
        region_name=region,
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', None),
        aws_session_token=os.environ.get('AWS_SESSION_TOKEN', None)
    )


@functools.lru_cache(maxsize=1)
def get_available_profiles(profile=None):
    return get_session(profile=profile).available_profiles


@functools.lru_cache(maxsize=1)
def get_available_regions(profile=None):
    return get_session(profile=profile).get_available_regions('ec2')


@functools.lru_cache()
def get_available_services(profile=None):
    return get_session(profile=profile).get_available_services()


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
        str(call.profile),
        str(call.region),
        str(call.service),
        str(call.method),
        ','.join(call.args),
        ','.join('{}={}'.format(k, v) for (k, v) in call.kwargs.items()),
    ]) + '.json'


def get_aws_resource(service_name,
                     method_name,
                     call_args,
                     call_kwargs,
                     cache,
                     profiles,
                     regions,
                     result_from_error=None,
                     debug_calls=False,
                     debug_cache=False):
    """
    Fetches and yields AWS API JSON responses for all profiles and regions (list params)
    """
    for profile, region in itertools.product(profiles, regions):
        call = default_call._replace(profile=profile,
                                     region=region,
                                     service=service_name,
                                     method=method_name,
                                     args=call_args,
                                     kwargs=call_kwargs)
        ckey = cache_key(call)

        if debug_calls:
            print('calling', call)

        cached_result = cache.get(ckey, None)
        if debug_cache and cached_result is not None:
            print('found cached value for', ckey)

        if cached_result is not None:
            result = cached_result
        else:
            client = get_client(call.profile, call.region, call.service)
            try:
                result = full_results(client, call.method, call.args, call.kwargs)
                result['__pytest_meta'] = dict(profile=call.profile, region=call.region)
            except botocore.exceptions.ClientError as error:
                if result_from_error is None:
                    raise error
                else:
                    if debug_calls:
                        print('error fetching resource', error, call)

                    result = result_from_error(error, call)

            if debug_cache:
                print('setting cache value for', ckey)

            cache.set(ckey, result)

        yield result


class BotocoreClient:

    def __init__(self, profiles, regions, cache, debug_calls, debug_cache):
        self.profiles = profiles or [None]
        self.regions = regions or get_available_regions()
        self.cache = cache

        self.debug_calls = debug_calls
        self.debug_cache = debug_cache

        self.results = []

    def get(self,
            service_name,
            method_name,
            call_args,
            call_kwargs,
            profiles=None,
            regions=None,
            result_from_error=None):

        # TODO:
        # For services that don't have the concept of regions,
        # we don't want to do the exact same test N times where
        # N is the number of regions. But the below hardcoding
        # is not a very clean solution to this.
        if service_name in SERVICES_WITHOUT_REGIONS:
            regions = ["us-east-1"]

        self.results = list(get_aws_resource(
            service_name,
            method_name,
            call_args,
            call_kwargs,
            profiles=profiles or self.profiles,
            regions=regions or self.regions,
            cache=self.cache,
            result_from_error=result_from_error,
            debug_calls=self.debug_calls,
            debug_cache=self.debug_cache))

        return self

    def values(self):
        "Returns the wrapped value"
        return self.results

    def extract_key(self, key, default=None):
        """
        From an iterable of dicts returns the value with the given
        keys discarding other values:

        [{'id': 1}, {'id': 2}] -> [1, 2]

        When the key does not exist it returns the second arg which defaults to None:

        [{'id': 1}, {}] -> [1, None]

        Propagates the '__pytest_meta' key to dicts and list items.
        """
        tmp = []
        for result in self.results:
            keyed_result = default

            if key in result:
                keyed_result = result[key]
                if isinstance(keyed_result, list):
                    for item in keyed_result:
                        # Added for IAM inline policies call, as it
                        # returns a list of strings.
                        if not isinstance(item, str):
                            item['__pytest_meta'] = result['__pytest_meta']
                elif isinstance(keyed_result, dict):
                    keyed_result['__pytest_meta'] = result['__pytest_meta']

            # skip setting metadata for primitives
            tmp.append(keyed_result)

        self.results = tmp
        return self

    def flatten(self):
        "Flattens one level of a nested list: [[A], [B]] -> [A, B]"
        self.results = sum(self.results, [])
        return self

    def debug(self):
        print(self.results)
        return self

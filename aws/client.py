# -*- coding: utf-8 -*-

import functools
import itertools
import os
import warnings
from collections import namedtuple
from hashlib import md5
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    NamedTuple,
    Union,
)

import _pytest.cacheprovider
import botocore
import botocore.exceptions
import botocore.session

SERVICES_WITHOUT_REGIONS = ["iam", "s3", "route53"]


@functools.lru_cache()
def get_session(profile: Optional[str] = None) -> botocore.session.Session:
    """Returns a new or cached botocore session for the AWS profile."""

    # If AWS_PROFILE is set and does not match what we want, unset this variable before
    # we proceed.
    if "AWS_PROFILE" in os.environ and os.environ["AWS_PROFILE"] != profile:
        warnings.warn(
            "$AWS_PROFILE and --aws-profile do not match. Using --aws-profile value {}".format(
                profile
            )
        )
        del os.environ["AWS_PROFILE"]

    # can raise botocore.exceptions.ProfileNotFound
    return botocore.session.Session(profile=profile)


@functools.lru_cache()
def get_client(profile: str, region: str, service: str) -> botocore.client.BaseClient:
    """Returns a new or cached botocore service client for the AWS profile, region, and service.

    Warns when a service is not available for a region, which means we
    need to update botocore or skip that call for that region.
    """
    session = get_session(profile)

    if (
        region not in session.get_available_regions(service)
        and service not in SERVICES_WITHOUT_REGIONS
    ):
        warnings.warn("service {} not available in {}".format(service, region))

    return session.create_client(service, region_name=region)


@functools.lru_cache(maxsize=1)
def get_available_profiles(profile: Optional[str] = None) -> Iterable[str]:
    profiles: Iterable[str] = get_session(profile=profile).available_profiles
    return profiles


@functools.lru_cache(maxsize=1)
def get_available_regions(profile: Optional[str] = None) -> List[str]:
    regions: List[str] = get_session(profile=profile).get_available_regions("ec2")
    return regions


@functools.lru_cache()
def get_available_services(profile: Optional[str] = None) -> Iterable[str]:
    services: Iterable[str] = get_session(profile=profile).get_available_services()
    return services


@functools.lru_cache()
def get_account_id(profile: str) -> str:
    sts = get_client(profile, "us-east-1", "sts")
    identity = sts.get_caller_identity()
    account_id: str = identity["Account"]
    return account_id


def full_results(
    client: botocore.client.BaseClient,
    method: str,
    args: List[str],
    kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    """Returns JSON results for an AWS botocore call. Flattens paginated results (if any)."""
    if client.can_paginate(method):
        paginator = client.get_paginator(method)
        full_result: Dict[str, Any] = paginator.paginate(
            *args, **kwargs
        ).build_full_result()
        return full_result
    else:
        single_result: Dict[str, Any] = getattr(client, method)(*args, **kwargs)
        return single_result


class AWSAPICall(NamedTuple):
    profile: Optional[str] = None
    region: Optional[str] = None
    service: Optional[str] = None
    method: Optional[str] = None
    args: List[str] = []
    kwargs: Dict[str, Any] = {}


default_call = AWSAPICall()


def cache_key(call: AWSAPICall) -> str:
    """Returns the fullname (directory and filename) for an AWS API call.

    >>> cache_key(default_call._replace(
    ... profile='profile',
    ... region='region',
    ... service='service_name',
    ... method='method_name',
    ... args=['arg1', 'arg2'],
    ... kwargs=dict(kwarg1=True)))
    'pytest_aws/profile/region/service_name/method_name/9965c005f623cd9130dd5a6dbdee87de.json'
    """
    path = "/".join(
        [
            "pytest_aws",
            str(call.profile if call.profile is not None else get_account_id(None)),
            str(call.region),
            str(call.service),
            str(call.method),
        ]
    )

    arguments = ":".join(
        [
            ",".join(call.args),
            ",".join("{}={}".format(k, v) for (k, v) in call.kwargs.items()),
        ]
    )

    filename = md5(str.encode(arguments)).hexdigest() + ".json"

    return f"{path}/{filename}"


def get_aws_resource(
    service_name: str,
    method_name: str,
    call_args: List[str],
    call_kwargs: Dict[str, Any],
    cache: Optional[_pytest.cacheprovider.Cache],
    profiles: List[Optional[str]],
    regions: List[str],
    result_from_error: Optional[Callable[[Any, Any], Any]] = None,
    debug_calls: bool = False,
    debug_cache: bool = False,
) -> Generator[Dict[str, Any], None, None]:
    """
    Fetches and yields AWS API JSON responses for all profiles and regions (list params)
    """
    assert isinstance(profiles, list)
    assert isinstance(regions, list)
    for profile, region in itertools.product(profiles, regions):
        call = default_call._replace(
            profile=profile,
            region=region,
            service=service_name,
            method=method_name,
            args=call_args,
            kwargs=call_kwargs,
        )

        if debug_calls:
            print("calling", call)

        result = None
        if cache is not None:
            ckey = cache_key(call)
            result = cache.get(ckey, None)

            if debug_cache and result is not None:
                print("found cached value for", ckey)

        if result is None:
            client = get_client(call.profile, call.region, call.service)
            assert isinstance(call.method, str)
            try:
                result = full_results(client, call.method, call.args, call.kwargs)
                result["__pytest_meta"] = dict(profile=call.profile, region=call.region)
            except botocore.exceptions.ClientError as error:
                if result_from_error is None:
                    raise error
                else:
                    if debug_calls:
                        print("error fetching resource", error, call)

                    result = result_from_error(error, call)

            if cache is not None:
                if debug_cache:
                    print("setting cache value for", ckey)

                cache.set(ckey, result)

        yield result


class BotocoreClient:
    def __init__(
        self: "BotocoreClient",
        profiles: List[Optional[str]],
        regions: Optional[List[str]],
        cache: _pytest.cacheprovider.Cache,
        debug_calls: bool,
        debug_cache: bool,
        offline: bool,
    ):
        self.profiles = profiles or [None]
        self.cache = cache

        self.debug_calls = debug_calls
        self.debug_cache = debug_cache
        self.offline = offline

        if offline:
            self.regions = ["us-east-1"]
        elif regions:
            self.regions = regions
        else:
            self.regions = get_available_regions()

        self.results: Iterable[Union[Dict[str, Any], List[Any]]] = []

    def get_regions(self: "BotocoreClient") -> List[str]:
        if self.offline:
            return []
        return self.regions

    def get(
        self: "BotocoreClient",
        service_name: str,
        method_name: str,
        call_args: List[str],
        call_kwargs: Dict[str, Any],
        profiles: Optional[List[Optional[str]]] = None,
        regions: Optional[List[str]] = None,
        result_from_error: Optional[Callable[[Any, Any], Any]] = None,
        do_not_cache: bool = False,
    ) -> "BotocoreClient":

        # TODO:
        # For services that don't have the concept of regions,
        # we don't want to do the exact same test N times where
        # N is the number of regions. But the below hardcoding
        # is not a very clean solution to this.
        if service_name in SERVICES_WITHOUT_REGIONS:
            regions = ["us-east-1"]

        if self.offline:
            self.results = []
        else:
            self.results = list(
                get_aws_resource(
                    service_name,
                    method_name,
                    call_args,
                    call_kwargs,
                    profiles=profiles or self.profiles,
                    regions=regions or self.regions,
                    cache=self.cache if not do_not_cache else None,
                    result_from_error=result_from_error,
                    debug_calls=self.debug_calls,
                    debug_cache=self.debug_cache,
                )
            )

        return self

    def values(self: "BotocoreClient") -> Iterable[Any]:
        """Returns the wrapped value

        >>> c = BotocoreClient([None], None, None, None, None, offline=True)
        >>> c.results = []
        >>> c.values()
        []
        """
        return self.results

    def extract_key(
        self: "BotocoreClient", key: str, default: Any = None
    ) -> "BotocoreClient":
        """
        From an iterable of dicts returns the value with the given
        keys discarding other values:

        >>> c = BotocoreClient([None], None, None, None, None, offline=True)
        >>> c.results = [{'id': 1}, {'id': 2}]
        >>> c.extract_key('id').results
        [1, 2]

        When the key does not exist it returns the second arg which defaults to None:

        >>> c = BotocoreClient([None], None, None, None, None, offline=True)
        >>> c.results = [{'id': 1}, {}]
        >>> c.extract_key('id').results
        [1, None]


        Propagates the '__pytest_meta' key to dicts and lists of dicts:

        >>> c = BotocoreClient([None], None, None, None, None, offline=True)
        >>> c.results = [{'Attrs': {'Name': 'Test'}, '__pytest_meta': {'meta': 'dict'}}]
        >>> c.extract_key('Attrs').results
        [{'Name': 'Test', '__pytest_meta': {'meta': 'dict'}}]
        >>> c.results = [{'Tags': [{'Name': 'Test', 'Value': 'Tag'}], '__pytest_meta': {'meta': 'dict'}}]
        >>> c.extract_key('Tags').results
        [[{'Name': 'Test', 'Value': 'Tag', '__pytest_meta': {'meta': 'dict'}}]]

        But not to primitives:

        >>> c.results = [{'PolicyNames': ['P1', 'P2']}]
        >>> c.extract_key('PolicyNames').results
        [['P1', 'P2']]


        Errors when the outer dict is missing a meta key:

        >>> c = BotocoreClient([None], None, None, None, None, offline=True)
        >>> c.results = [{'Attrs': {'Name': 'Test'}}]
        >>> c.extract_key('Attrs')
        Traceback (most recent call last):
        ...
        KeyError: '__pytest_meta'
        """
        assert isinstance(self.results, list)
        tmp = []
        for result in self.results:
            keyed_result = default

            if key in result:
                keyed_result = result[key]
                if isinstance(keyed_result, list):
                    for item in keyed_result:
                        # Added for IAM inline policies call, as it
                        # returns a list of strings.
                        if isinstance(item, dict):
                            item["__pytest_meta"] = result["__pytest_meta"]
                elif isinstance(keyed_result, dict):
                    keyed_result["__pytest_meta"] = result["__pytest_meta"]

            # skip setting metadata for primitives
            tmp.append(keyed_result)

        self.results = tmp
        return self

    def flatten(self: "BotocoreClient") -> "BotocoreClient":
        """
        Flattens one level of a nested list:

        >>> c = BotocoreClient([None], None, None, None, None, offline=True)
        >>> c.results = [['A', 1], ['B']]
        >>> c.flatten().values()
        ['A', 1, 'B']

        Only works for a list of lists:

        >>> c.results = [{'A': 1}, {'B': 2}]
        >>> c.flatten().values()
        Traceback (most recent call last):
        ...
        TypeError: can only concatenate list (not "dict") to list
        """
        assert isinstance(self.results, list)
        self.results = sum(self.results, [])
        return self

    def debug(self: "BotocoreClient") -> "BotocoreClient":
        print(self.results)
        return self

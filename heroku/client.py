# from herokuadmintools import verify_access, session
from herokuadmintools import find_users_missing_2fa, find_affected_apps


def cache_key(organization, method, *args, **kwargs):
    """Returns the fullname (directory and filename) for a Heroku API call.

    >>> cache_key(
    ... 'organization_name',
    ... 'method_name',
    ... 'arg1', 'arg2',
    ... kwarg1=True,
    ... )
    'pytest_heroku:organization_name:method_name:arg1,arg2:kwarg1=True.json'
    """
    return ':'.join([
        'pytest_heroku',
        str(organization),
        str(method),
        ','.join(args),
        ','.join('{}={}'.format(k, v) for (k, v) in kwargs.items()),
    ]) + '.json'


def get_heroku_resource(organization,
                        method_name,
                        call_args,
                        call_kwargs,
                        cache=None,
                        result_from_error=None,
                        debug_calls=False,
                        debug_cache=False):
    """
    Fetches and return final data

    TODO: more refactoring of herokuadmintools needed, so can:
        - cache all members
        - cache all apps of member
    """
    if debug_calls:
        print('calling', method_name, 'on', organization)

    result = None
    if cache is not None:
        ckey = cache_key(organization, method_name)
        result = cache.get(ckey, None)

        if debug_cache and result is not None:
            print('found cached value for', ckey)

    if result is None:
        # convert from defaultdict with values as sets
        users = {k: list(v) for k, v in
                 find_users_missing_2fa(organization).items()}
        apps = {k: list(v) for k, v in
                find_affected_apps(users, organization).items()}
        result = [{
            HerokuDataSets.ROLE_USER: users,
            HerokuDataSets.APP_USER: apps,
        }]

        if cache is not None:
            if debug_cache:
                print('setting cache value for', ckey)

            cache.set(ckey, result)

    return result


class HerokuDataSets:
    # We use an IntEnum so keys can be ordered, which is done deep in some
    # libraries when we use the enums as dict keys
    ROLE_USER = 1  # tuple of (role, user)
    APP_USER = 2   # tuple of (app, user)


class HerokuAdminClient:

    # ensure we have access from instance
    data_set_names = HerokuDataSets

    def __init__(self,
                 organization,
                 cache,
                 debug_calls,
                 debug_cache,
                 offline):
        self.organization = organization
        self.cache = cache

        self.debug_calls = debug_calls
        self.debug_cache = debug_cache
        self.offline = offline

        self.results = []

    def get(self,
            method_name,
            call_args,
            call_kwargs,
            result_from_error=None,
            do_not_cache=False):

        if self.offline:
            self.results = []
        else:
            self.results = list(get_heroku_resource(
                self.organization,
                method_name,
                call_args,
                call_kwargs,
                cache=self.cache if not do_not_cache else None,
                result_from_error=result_from_error,
                debug_calls=self.debug_calls,
                debug_cache=self.debug_cache))

        return self

    def find_users_missing_2fa(self):
        return self.extract_key(HerokuDataSets.ROLE_USER, {})

    def find_affected_apps(self):
        return self.extract_key(HerokuDataSets.APP_USER, {})

    def values(self):
        """Returns the wrapped value

        >>> c = HerokuAdminClient([None], None, None, None, offline=True)
        >>> c.results = []
        >>> c.values()
        []
        """
        return self.results

    def extract_key(self, key, default=None):
        """
        From an iterable of dicts returns the value with the given
        keys discarding other values:

        >>> c = HerokuAdminClient([None], None, None, None, offline=True)
        >>> c.results = [{'id': 1}, {'id': 2}]
        >>> c.extract_key('id').results
        [1, 2]

        When the key does not exist it returns the second arg which defaults to None:

        >>> c = HerokuAdminClient([None], None, None, None, offline=True)
        >>> c.results = [{'id': 1}, {}]
        >>> c.extract_key('id').results
        [1, None]

        But not to primitives:

        >>> c.results = [{'PolicyNames': ['P1', 'P2']}]
        >>> c.extract_key('PolicyNames').results
        [['P1', 'P2']]
        """
        tmp = []
        for result in self.results:
            keyed_result = default

            if key in result:
                keyed_result = result[key]

            tmp.append(keyed_result)

        self.results = tmp
        return self

    def flatten(self):
        """
        Flattens one level of a nested list:

        >>> c = HerokuAdminClient([None], None, None, None, offline=True)
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
        self.results = sum(self.results, [])
        return self

    def debug(self):
        print(self.results)
        return self

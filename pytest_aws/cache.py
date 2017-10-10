

import datetime
import json

import py


def json_iso_datetimes(obj):
    """JSON serializer for objects not serializable by default json module."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

    raise TypeError("Unserializable type %s" % type(obj))


def datetime_encode_set(self, key, value):
    """ save value for the given key.

    :param key: must be a ``/`` separated value. Usually the first
    name is the name of your plugin or your application.
    :param value: must be of any combination of basic
    python types, including nested types
    like e. g. lists of dictionaries.
    """
    path = self._getvaluepath(key)
    try:
        path.dirpath().ensure_dir()
    except (py.error.EEXIST, py.error.EACCES):
        self.config.warn(
            code='I9', message='could not create cache path %s' % (path,)
            )
        return
    try:
        f = path.open('w')
    except py.error.ENOTDIR:
        self.config.warn(
            code='I9', message='cache could not write path %s' % (path,))
    else:
        with f:
            self.trace("cache-write %s: %r" % (key, value,))
            json.dump(value, f, indent=4, sort_keys=True, default=json_iso_datetimes)


def patch_cache_set(config):
    _cache = config.cache

    def cache_set(k, v):
        datetime_encode_set(_cache, k, v)

    config.cache.set = cache_set


"""
Patch for pytest cache to serialize datetime.datetime
"""

import datetime
import json

import py
from _pytest.compat import _PY2 as PY2


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
        path.parent.mkdir(exist_ok=True, parents=True)
    except (IOError, OSError):
        self.warn("could not create cache path {path}", path=path)
        return
    try:
        f = path.open("wb" if PY2 else "w")
    except (IOError, OSError):
        self.warn("cache could not write path {path}", path=path)
    else:
        with f:
            json.dump(value, f, indent=2, sort_keys=True, default=json_iso_datetimes)
            self._ensure_readme()


def patch_cache_set(config):
    _cache = config.cache

    def cache_set(k, v):
        datetime_encode_set(_cache, k, v)

    config.cache.set = cache_set

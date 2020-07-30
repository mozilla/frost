"""
Patch for pytest cache to serialize datetime.datetime
"""

import datetime
import functools
import json

import py
from dateutil.parser import parse


def json_iso_datetimes(obj):
    """JSON serializer for objects not serializable by default json
    module."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

    raise TypeError("Unserializable type %s" % type(obj))


def json_iso_datetime_string_to_datetime(obj):
    """JSON object hook that converts object vals from ISO datetime
    strings to python datetime.datetime`s if possible."""

    for k, v in obj.items():
        if not isinstance(v, str):
            continue

        try:
            obj[k] = parse(v, ignoretz=True)
        except (OverflowError, ValueError):
            pass

    return obj


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
        f = path.open("w")
    except (IOError, OSError):
        self.warn("cache could not write path {path}", path=path)
    else:
        with f:
            json.dump(value, f, indent=2, sort_keys=True, default=json_iso_datetimes)
            self._ensure_supporting_files()


def datetime_encode_get(self, key, default):
    """ return cached value for the given key.  If no value
    was yet cached or the value cannot be read, the specified
    default is returned.

    :param key: must be a ``/`` separated value. Usually the first
         name is the name of your plugin or your application.
    :param default: must be provided in case of a cache-miss or
         invalid cache values.
    """
    path = self._getvaluepath(key)
    try:
        with path.open("r") as f:
            return json.load(f, object_hook=json_iso_datetime_string_to_datetime)
    except (ValueError, IOError, OSError):
        return default


def patch_cache_set(config):
    config.cache.set = functools.partial(datetime_encode_set, config.cache)
    config.cache.get = functools.partial(datetime_encode_get, config.cache)

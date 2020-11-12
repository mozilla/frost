"""
Patch for pytest cache to serialize datetime.datetime
"""

import datetime
import functools
import json
from typing import Any, Dict, Union, Tuple

from dateutil.parser import isoparse
import _pytest
import _pytest.cacheprovider


def json_iso_datetimes(obj: Any) -> str:
    """JSON serializer for objects not serializable by default json
    module."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

    raise TypeError(f"Unserializable type {type(obj)}")


def json_iso_datetime_string_to_datetime(obj: Dict[Any, Any]) -> Dict[Any, Any]:
    """JSON object hook that converts object vals from ISO datetime
    strings to python datetime.datetime`s if possible."""

    for k, v in obj.items():
        if not isinstance(v, str):
            continue

        try:
            obj[k] = isoparse(v)
        except (OverflowError, ValueError):
            pass

    return obj


def datetime_encode_set(
    self: _pytest.cacheprovider.Cache,
    key: str,
    value: Union[str, int, float, Dict[Any, Any], Tuple[Any]],
) -> None:
    """save value for the given key.

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


def datetime_encode_get(
    self: _pytest.cacheprovider.Cache, key: str, default: Any
) -> Any:
    """return cached value for the given key.  If no value
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


def patch_cache_set(config: _pytest.config.Config) -> None:
    assert config.cache, "pytest does not have a cache configured to patch"
    # types ignored due to https://github.com/python/mypy/issues/2427
    config.cache.set = functools.partial(datetime_encode_set, config.cache)  # type: ignore
    config.cache.get = functools.partial(datetime_encode_get, config.cache)  # type: ignore

from typing import Any, Optional


def get_param_id(obj: Any, key: str) -> Optional[str]:
    """
    Returns the params test parameter ID or None
    """
    # avoid confusing "TypeError: 'NotSetType' object is not subscriptable" errors
    if not hasattr(obj, "__getitem__"):
        return None

    try:
        return obj[key]
    except KeyError:
        return None

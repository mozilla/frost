from collections import defaultdict
from datetime import date
import re
import warnings

import pytest


def load(rules):
    """Marks tests as xfail based on test name and ID.

    Parses the exemptions section of the conf file and returns a two level dict with format:

    {<test_name>:
        {<test_id>: (<exemption expiration>, <exemption reason>)
        ...
        }
    ...
    }

    Examples:

    >>> load([
    ... {
    ... 'test_name': 'test_foo',
    ... 'test_param_id': 'foo-id',
    ... 'expiration_day': date(2050, 1, 1),
    ... 'reason': 'in prod never allow foo'
    ... }
    ... ]) == {'test_foo': {'foo-id': ('2050-01-01', 'in prod never allow foo')}}
    True

    >>> load([
    ... {
    ... 'test_name': '*test_foo',
    ... 'test_param_id': 'foo-id',
    ... 'expiration_day': date(2050, 1, 1),
    ... 'reason': 'in prod never allow foo'
    ... }
    ... ]) == {'*test_foo': {'foo-id': ('2050-01-01', 'in prod never allow foo')}}
    True

    >>> load([
    ... {
    ... 'test_name': 'test_foo',
    ... 'test_param_id': 'foo-id',
    ... 'expiration_day': date(2050, 1, 1),
    ... 'reason': 'in prod never allow foo'
    ... },
    ... {
    ... 'test_name': 'test_foo',
    ... 'test_param_id': 'bar-id',
    ... 'expiration_day': date(2050, 1, 1),
    ... 'reason': 'in prod never allow bar'
    ... }
    ... ]) == {
    ... 'test_foo': {
    ... 'foo-id': ('2050-01-01', 'in prod never allow foo'),
    ... 'bar-id': ('2050-01-01', 'in prod never allow bar')}}
    True


    Duplicate test name and IDs are ignored with a warning:

    >>> load([
    ... {
    ... 'test_name': 'test_foo',
    ... 'test_param_id': 'foo-id',
    ... 'expiration_day': date(2050, 1, 1),
    ... 'reason': 'in prod never allow foo'
    ... },
    ... {
    ... 'test_name': 'test_foo',
    ... 'test_param_id': 'foo-id',
    ... 'expiration_day': date(2051, 1, 1),
    ... 'reason': 'in prod never allow foo another'
    ... }
    ... ]) == {'test_foo': {'foo-id': ('2050-01-01', 'in prod never allow foo')}}
    True
    >>> # UserWarning: Exemptions: test_name: test_foo | test_id: foo-id | Skipping duplicate test name and ID

    Does not check that test name and IDs exist (since names might not
    be collected and IDs can require an HTTP call).
    """
    processed_rules = defaultdict(dict)

    if not rules:
        return processed_rules

    for rule in rules:
        test_name, test_id = rule["test_name"], rule["test_param_id"]
        expiration, reason = rule["expiration_day"], rule["reason"]

        if expiration < date.today():
            warnings.warn(
                "Exemptions: test_name: {} | test_id: {} | Skipping rule with expiration day in the past {!r}".format(
                    test_name, test_id, expiration
                )
            )
            continue

        if test_id in processed_rules[test_name]:
            warnings.warn(
                "Exemptions: test_name: {} | test_id: {} | Skipping duplicate test name and ID".format(
                    test_name, test_id
                )
            )
            continue

        processed_rules[test_name][test_id] = (str(expiration), reason)

    return processed_rules


def add_xfail_marker(item):
    """
    Adds xfail markers for test names and ids specified in the exemptions conf.
    """
    if not item.get_closest_marker("parametrize"):
        warnings.warn(
            "Skipping exemption checks for test without resource name {!r}".format(
                item.name
            )
        )
        return

    test_exemptions = item.config.custom_config.exemptions.get(item.originalname, None)

    test_id = item.name
    try:
        # test_admin_user_is_inactive[gsuiteuser@example.com]
        test_id = item.name.split("[")[1][:-1]
    except IndexError:
        warnings.warn(
            "Exemption check failed: was unable to parse parametrized test name:",
            item.name,
        )
        return

    if test_exemptions:
        if test_id in test_exemptions:
            expiration, reason = test_exemptions[test_id]
            item.add_marker(
                pytest.mark.xfail(reason=reason, strict=True, expiration=expiration)
            )
            return

        # Check for any substring matchers
        for exemption_test_id in test_exemptions:
            if exemption_test_id.startswith("*"):
                substring = exemption_test_id[1:]
                if re.search(substring, test_id):
                    expiration, reason = test_exemptions[exemption_test_id]
                    item.add_marker(
                        pytest.mark.xfail(
                            reason=reason, strict=True, expiration=expiration
                        )
                    )
                    return

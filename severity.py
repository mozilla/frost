from collections import defaultdict
import warnings

import pytest


# parseable severity levels in order of increasing badness
SEVERITY_LEVELS = ["INFO", "WARN", "ERROR"]


def load(rules):
    """
    Parses severities section of the conf file and returns a dict of test name to severity level for tests.

    >>> load([{'test_name': 'test_foo', 'severity': 'ERROR'}])
    {'test_foo': 'ERROR'}
    >>> load([{'test_name': '*', 'severity': 'INFO'}])  # doctest:+ELLIPSIS
    defaultdict(<function load.<locals>.<lambda> at 0x...>, {})
    >>> load([
    ... {'test_name': 'test_foo', 'severity': 'ERROR'}, {'test_name': 'test_bar', 'severity': 'INFO'}
    ... ]) == {'test_foo': 'ERROR', 'test_bar': 'INFO'}
    True

    Invalid severity levels are skipped with a warning:

    >>> load([{'test_name': 'test_foo', 'severity': 'AHHH!'}])
    {}
    >>> # UserWarning: Line 0: Skipping line with invalid severity level 'AHHH!'


    Duplicate test names are ignored with a warning:

    >>> load([
    ... {'test_name': 'test_foo', 'severity': 'ERROR'}, {'test_name': 'test_foo', 'severity': 'INFO'}
    ... ]) == {'test_foo': 'ERROR'}
    True
    >>> # UserWarning: Line 1: Skipping line with duplicate test name 'test_foo'

    Does not check that test names exist (since they might not be collected).
    """
    # dict of test name to severity level
    processed_rules = {}

    if not rules:
        return processed_rules

    for rule in rules:
        test_name, severity = rule["test_name"], rule["severity"]

        if severity not in SEVERITY_LEVELS:
            warnings.warn(
                "test_name: {} | Skipping line with invalid severity level {!r}".format(
                    test_name, severity
                )
            )
            continue

        if test_name in processed_rules:
            warnings.warn(
                "test_name: {} | Skipping line with duplicate test name".format(
                    test_name
                )
            )
            continue

        processed_rules[test_name] = severity

    if "*" in processed_rules:
        rules_with_default = defaultdict(
            lambda: processed_rules["*"], **processed_rules
        )
        del rules_with_default["*"]
        return rules_with_default
    else:
        return processed_rules


def add_severity_marker(item):
    """
    Adds severity markers as specified in the severity conf.

    Warns when overriding an existing test severity.
    """
    test_name_for_matching = item.originalname or item.name

    if test_name_for_matching in item.config.custom_config.severities:
        conf_severity = item.config.custom_config.severities[test_name_for_matching]
        test_severity = item.get_closest_marker("severity")
        if test_severity and test_severity.args[0] != conf_severity:
            warnings.warn(
                "Overriding existing severity {} for test {}".format(
                    test_severity, test_name_for_matching
                )
            )

        item.add_marker(pytest.mark.severity(conf_severity))

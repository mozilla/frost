

from collections import defaultdict
import warnings

import pytest


# parseable severity levels in order of increasing badness
SEVERITY_LEVELS = [
    'INFO',
    'WARN',
    'ERROR',
]


def parse_conf_file(conf_fd):
    """
    Parses an open severity conf file and returns a dict of test name to severity level for tests.

    The files consist of:

    comment lines that have the format:

    '#'<anything>\n

    test severity lines that have either of the formats:

    <test matcher><whitespace><severity>\n

    <test matcher><whitespace><severity><whitespace><comment>\n

    where:

    <anything> := is any non newline character
    <test matcher> := is an unparametrized test name or '*' to match all tests
    <severity> := is one of INFO, WARN, or ERROR
    <whitespace> := anything str.split i.e. one or more ' ', '\t', or '\n' chars

    >>> from io import StringIO
    >>> parse_conf_file(StringIO('# comment'))
    {}
    >>> parse_conf_file(StringIO('test_foo ERROR in prod never allow foo'))
    {'test_foo': 'ERROR'}
    >>> parse_conf_file(StringIO('* INFO'))  # doctest:+ELLIPSIS
    defaultdict(<function parse_conf_file.<locals>.<lambda> at 0x...>, {})
    >>> parse_conf_file(StringIO('test_foo ERROR\\ntest_bar INFO'))
    {'test_foo': 'ERROR', 'test_bar': 'INFO'}

    Short lines are skipped with a warning:

    >>> parse_conf_file(StringIO('invalid'))
    {}
    >>> # UserWarning: Line 0: Skipping line with fewer than 2 tab delimited parts.


    Invalid severity levels are skipped with a warning:

    >>> parse_conf_file(StringIO('test AHHH!'))
    {}
    >>> # UserWarning: Line 0: Skipping line with invalid severity level 'AHHH!'


    Duplicate test names are ignored with a warning:

    >>> parse_conf_file(StringIO('test_foo INFO\\ntest_foo WARN'))
    {'test_foo': 'INFO'}
    >>> # UserWarning: Line 1: Skipping line with duplicate test name 'test_foo'

    Does not check that test names exist (since they might not be collected).
    """
    # dict of test name to severity level
    rules = {}

    if not conf_fd:
        return rules

    for line_number, line in enumerate(conf_fd):
        if line.startswith('#'):
            continue

        line_parts = line.split()
        if len(line_parts) < 2:
            warnings.warn('Line {}: Skipping line with fewer than 2 tab delimited parts.'.format(line_number))
            continue

        test_name, severity = line_parts[0], line_parts[1]
        if severity not in SEVERITY_LEVELS:
            warnings.warn('Line {}: Skipping line with invalid severity level {!r}'.format(line_number, severity))
            continue

        if test_name in rules:
            warnings.warn('Line {}: Skipping line with duplicate test name {!r}'.format(line_number, test_name))
            continue

        rules[test_name] = severity

    if '*' in rules:
        rules_with_default = defaultdict(lambda: rules['*'], **rules)
        del rules_with_default['*']
        return rules_with_default
    else:
        return rules


def add_severity_marker(item):
    """
    Adds severity markers as specified in the severity conf.

    Warns when overriding an existing test severity.
    """
    test_name_for_matching = item.originalname or item.name

    if test_name_for_matching in item.config.severity:
        conf_severity = item.config.severity[test_name_for_matching]
        test_severity = item.get_marker("severity")
        if test_severity and test_severity.args[0] != conf_severity:
            warnings.warn('Overriding existing severity {} for test {}'.format(
                test_severity, test_name_for_matching))

        item.add_marker(pytest.mark.severity(conf_severity))
